#!/usr/bin/env python3
"""
Putty-ES Command Line Interface
Beautiful, powerful server management + ppiRuler + GUI + Putty-Fire.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from putty_es import __version__
from putty_es.core.config import load_config
from putty_es.core.executor import Executor
from putty_es.core.module_loader import discover_modules, get_module

console = Console()


BANNER = r"""
[bold cyan]
██████╗ ██╗   ██╗████████╗████████╗██╗   ██╗      ███████╗███████╗
██╔══██╗██║   ██║╚══██╔══╝╚══██╔══╝╚██╗ ██╔╝      ██╔════╝██╔════╝
██████╔╝██║   ██║   ██║      ██║    ╚████╔╝ █████╗█████╗  ███████╗
██╔═══╝ ██║   ██║   ██║      ██║     ╚██╔╝  ╚════╝██╔══╝  ╚════██║
██║     ╚██████╔╝   ██║      ██║      ██║         ███████╗███████║
╚═╝      ╚═════╝    ╚═╝      ╚═╝      ╚═╝         ╚══════╝╚══════╝
[/bold cyan]
[bold white]                    Elite Server Setup & Management[/bold white]
[dim]                         v{version}  |  Open Source[/dim]
[bold red]              Putty-Fire · Protected when activated[/bold red]
""".format(version=__version__)


def print_banner() -> None:
    console.print(BANNER)
    console.print()


@click.group(invoke_without_command=True)
@click.option("--version", "-V", is_flag=True, help="Show version and exit.")
@click.option("--no-banner", is_flag=True, help="Suppress the startup banner.")
@click.option("--gui", is_flag=True, help="Launch the graphical user interface.")
@click.pass_context
def main(ctx: click.Context, version: bool, no_banner: bool, gui: bool) -> None:
    """Putty-ES – Elite Server Setup, ppiRuler, GUI and Putty-Fire protection."""
    if version:
        console.print(f"[bold cyan]Putty-ES[/bold cyan] v{__version__}")
        sys.exit(0)

    if gui:
        from putty_es.gui.app import launch_gui
        launch_gui()
        return

    if ctx.invoked_subcommand is None:
        if not no_banner:
            print_banner()
        console.print(
            Panel(
                "[bold]Welcome to Putty-ES[/bold]\n\n"
                "[cyan]putty-es --gui[/cyan]  – graphical interface\n"
                "[cyan]putty-es init[/cyan]  – create config\n"
                "[cyan]putty-es apply <file>[/cyan]  – provision servers\n"
                "[cyan]putty-es ppi build <pkg>[/cyan]  – offline packages\n"
                "[cyan]putty-es fire --help[/cyan]  – Putty-Fire protection\n\n"
                "[dim]When Putty-Fire is active on a host: Protected by Putty-Fire[/dim]",
                title="Getting Started",
                border_style="cyan",
            )
        )


@main.command("gui")
def gui_cmd() -> None:
    """Launch the Putty-ES GUI (animated startup)."""
    from putty_es.gui.app import launch_gui
    launch_gui()


@main.command()
@click.option("--force", is_flag=True, help="Overwrite existing files.")
def init(force: bool) -> None:
    """Initialize a new Putty-ES project with example configuration."""
    print_banner()
    target = Path("putty-es.yaml")
    if target.exists() and not force:
        console.print("[yellow]Configuration already exists. Use --force to overwrite.[/yellow]")
        return

    example = """# Putty-ES + Putty-Fire example
name: my-server-fleet
description: Production servers with Putty-Fire protection

hosts:
  - name: web-01
    hostname: 192.168.1.10
    user: root
    port: 22
    # key: ~/.ssh/id_ed25519

modules:
  - name: packages
    packages: [curl, git, htop, ufw, fail2ban, python3, python3-pip]

  - name: putty-fire
    enable: true
    level: standard
    allow_ports: ["22/tcp", "80/tcp", "443/tcp"]
    ban_ssh_bruteforce: true
    fail2ban: true
    show_banner: true

  - name: pypi
    packages: [requests, rich]
"""
    target.write_text(example, encoding="utf-8")
    console.print(f"[green]✓[/green] Created [cyan]{target}[/cyan]")
    console.print("Edit and run [cyan]putty-es apply putty-es.yaml[/cyan]")


@main.command()
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Simulate only.")
@click.option("--host", "host_filter", default=None, help="Only this host name.")
@click.option("--verbose", "-v", is_flag=True)
def apply(config_file: Path, dry_run: bool, host_filter: Optional[str], verbose: bool) -> None:
    """Apply a configuration file to the defined hosts."""
    print_banner()
    console.print(f"[bold]Loading:[/bold] {config_file}")
    try:
        config = load_config(config_file)
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")
        sys.exit(1)

    console.print(f"[green]✓[/green] Fleet: [bold]{config.name}[/bold]")
    hosts = config.hosts
    if host_filter:
        hosts = [h for h in hosts if h.name == host_filter]
        if not hosts:
            console.print(f"[red]No host '{host_filter}'[/red]")
            sys.exit(1)

    executor = Executor(dry_run=dry_run, verbose=verbose)
    for host in hosts:
        console.print()
        console.rule(f"[bold cyan]{host.name}[/bold cyan] ({host.hostname})")
        try:
            executor.apply_modules(host, config.modules)
            # Footer if putty-fire was in the config
            names = [m.name for m in config.modules]
            if "putty-fire" in names:
                console.print("[bold green]  Protected by Putty-Fire[/bold green]")
            console.print(f"[green]✓ Host {host.name} done[/green]")
        except Exception as e:
            console.print(f"[red]✗ {host.name}:[/red] {e}")
            if verbose:
                console.print_exception()

    console.print()
    console.print(Panel("[bold green]All done![/bold green]", border_style="green"))


@main.command("module")
@click.argument("module_name")
@click.option("--host", required=True)
@click.option("--user", default="root")
@click.option("--port", default=22, type=int)
@click.option("--key", default=None)
@click.option("--dry-run", is_flag=True)
@click.argument("args", nargs=-1)
def run_module(
    module_name: str,
    host: str,
    user: str,
    port: int,
    key: Optional[str],
    dry_run: bool,
    args: tuple,
) -> None:
    """Run a single smart module against a host."""
    print_banner()
    from putty_es.core.config import Host

    h = Host(name="adhoc", hostname=host, user=user, port=port, key=key)
    module_cls = get_module(module_name)
    if not module_cls:
        console.print(f"[red]Unknown module:[/red] {module_name}")
        for name in discover_modules():
            console.print(f"  • {name}")
        sys.exit(1)

    mod = module_cls()
    executor = Executor(dry_run=dry_run)
    config: dict = {"packages": list(args)} if args else {"enable": True}
    if module_name == "putty-fire":
        config.setdefault("enable", True)
        config.setdefault("show_banner", True)
    success = mod.apply(h, config, executor)
    if success:
        if module_name == "putty-fire":
            console.print("[bold green]Protected by Putty-Fire[/bold green]")
        console.print("[green]✓ Module completed[/green]")
    else:
        console.print("[red]✗ Module failed[/red]")
        sys.exit(1)


@main.command()
def modules() -> None:
    """List all available smart modules."""
    print_banner()
    table = Table(title="Smart Modules", box=box.ROUNDED)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description")
    for name, cls in sorted(discover_modules().items()):
        desc = getattr(cls, "description", "")
        table.add_row(name, desc)
    console.print(table)


@main.command()
@click.option("--host", required=True)
@click.option("--user", default="root")
@click.option("--port", default=22, type=int)
@click.option("--key", default=None)
def shell(host: str, user: str, port: int, key: Optional[str]) -> None:
    """Hint for interactive SSH."""
    print_banner()
    console.print(
        Panel(
            f"[cyan]ssh -p {port} {user}@{host}[/cyan]",
            title="Shell",
            border_style="cyan",
        )
    )


# ── Putty-Fire commands ───────────────────────────────────

@main.group("fire")
def fire_group() -> None:
    """Putty-Fire – activate and check server protection."""
    pass


@fire_group.command("activate")
@click.option("--host", required=True, help="Target hostname or IP.")
@click.option("--user", default="root")
@click.option("--port", default=22, type=int)
@click.option("--key", default=None)
@click.option(
    "--level",
    type=click.Choice(["minimal", "standard", "strict"]),
    default="standard",
)
@click.option("--dry-run", is_flag=True)
def fire_activate(
    host: str,
    user: str,
    port: int,
    key: Optional[str],
    level: str,
    dry_run: bool,
) -> None:
    """Activate Putty-Fire protection on a host."""
    print_banner()
    from putty_es.core.config import Host

    h = Host(name="fire", hostname=host, user=user, port=port, key=key)
    mod_cls = get_module("putty-fire")
    if not mod_cls:
        console.print("[red]putty-fire module not found[/red]")
        sys.exit(1)

    console.print(f"Activating [bold red]Putty-Fire[/bold red] on [cyan]{host}[/cyan] (level={level})")
    executor = Executor(dry_run=dry_run, verbose=True)
    ok = mod_cls().apply(
        h,
        {
            "enable": True,
            "level": level,
            "show_banner": True,
            "fail2ban": True,
            "sysctl_harden": True,
            "ban_ssh_bruteforce": True,
        },
        executor,
    )
    if ok:
        console.print()
        console.print(
            Panel(
                "[bold green]Protected by Putty-Fire[/bold green]\n\n"
                "On the server run: [cyan]putty-fire-status[/cyan]",
                border_style="green",
            )
        )
    else:
        console.print("[red]Activation failed[/red]")
        sys.exit(1)


@fire_group.command("status")
@click.option("--host", required=True)
@click.option("--user", default="root")
@click.option("--port", default=22, type=int)
@click.option("--key", default=None)
def fire_status(host: str, user: str, port: int, key: Optional[str]) -> None:
    """Check Putty-Fire status on a remote host."""
    print_banner()
    from putty_es.core.config import Host

    h = Host(name="fire", hostname=host, user=user, port=port, key=key)
    executor = Executor(dry_run=False, verbose=False)
    code, out, err = executor.run(
        h,
        "putty-fire-status 2>/dev/null || cat /etc/putty-fire/STATUS 2>/dev/null || echo 'Putty-Fire not active'",
        check=False,
    )
    console.print(Panel(out or err or "No output", title="Putty-Fire Status", border_style="red"))
    if "Protected by Putty-Fire" in (out or ""):
        console.print("[bold green]Protected by Putty-Fire[/bold green]")


# ── ppiRuler ──────────────────────────────────────────────

@main.group("ppi")
def ppi_group() -> None:
    """ppiRuler – offline PyPI package builder."""
    pass


@ppi_group.command("build")
@click.argument("package")
@click.option("--version", "-v", default=None)
@click.option("--output", "-o", default="./ppi_output")
@click.option(
    "--target",
    "-t",
    multiple=True,
    type=click.Choice(["exe", "windows", "linux", "html", "ini", "dll"], case_sensitive=False),
)
@click.option("--no-animation", is_flag=True)
def ppi_build(
    package: str,
    version: Optional[str],
    output: str,
    target: tuple,
    no_animation: bool,
) -> None:
    """Build offline artifacts for a PyPI package."""
    from putty_es.ppi_ruler.core import PPIRuler

    targets: List[str] = list(target) if target else ["exe", "linux", "html", "ini"]
    ruler = PPIRuler(package=package, version=version, output_dir=output, targets=targets)
    try:
        ruler.run(animated=not no_animation)
    except Exception as e:
        console.print(f"[red]ppiRuler failed:[/red] {e}")
        sys.exit(1)


@ppi_group.command("info")
def ppi_info() -> None:
    """Info about ppiRuler."""
    console.print(
        Panel(
            "[bold cyan]ppiRuler[/bold cyan] – offline package transformation\n"
            "Usage: [cyan]putty-es ppi build <package>[/cyan]",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    main()
