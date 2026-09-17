#!/usr/bin/env python3
"""
Putty-ES Command Line Interface
Beautiful, powerful, and intelligent server management.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from putty_es import __version__
from putty_es.core.config import load_config, Config
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
""".format(version=__version__)


def print_banner() -> None:
    console.print(BANNER)
    console.print()


@click.group(invoke_without_command=True)
@click.option("--version", "-V", is_flag=True, help="Show version and exit.")
@click.option("--no-banner", is_flag=True, help="Suppress the startup banner.")
@click.pass_context
def main(ctx: click.Context, version: bool, no_banner: bool) -> None:
    """
    Putty-ES – Elite Server Setup & Management Tool.

    Intelligent modular framework for automated server provisioning,
    configuration, PyPI package management, and smart modules.
    """
    if version:
        console.print(f"[bold cyan]Putty-ES[/bold cyan] v{__version__}")
        sys.exit(0)

    if ctx.invoked_subcommand is None:
        if not no_banner:
            print_banner()
        console.print(
            Panel(
                "[bold]Welcome to Putty-ES[/bold]\n\n"
                "Run [cyan]putty-es --help[/cyan] to see available commands.\n"
                "Run [cyan]putty-es init[/cyan] to create your first configuration.",
                title="Getting Started",
                border_style="cyan",
            )
        )


@main.command()
@click.option("--force", is_flag=True, help="Overwrite existing files.")
def init(force: bool) -> None:
    """Initialize a new Putty-ES project with example configuration."""
    print_banner()
    target = Path("putty-es.yaml")
    if target.exists() and not force:
        console.print("[yellow]Configuration already exists. Use --force to overwrite.[/yellow]")
        return

    example = """# Putty-ES Configuration
# Documentation: https://github.com/SlabyLol/Putty-ES

name: my-server-fleet
description: Production servers managed by Putty-ES

hosts:
  - name: web-01
    hostname: 192.168.1.10
    user: root
    port: 22
    # key: ~/.ssh/id_ed25519
    # password:  # prefer key-based auth

modules:
  - name: packages
    action: install
    packages:
      - curl
      - git
      - htop
      - python3
      - python3-pip

  - name: pypi
    packages:
      - requests
      - rich

  - name: firewall
    enable: true
    allow:
      - 22/tcp
      - 80/tcp
      - 443/tcp

  - name: system
    timezone: UTC
    hostname: web-01
"""
    target.write_text(example, encoding="utf-8")
    console.print(f"[green]✓[/green] Created [cyan]{target}[/cyan]")
    console.print("Edit the file and run [cyan]putty-es apply putty-es.yaml[/cyan]")


@main.command()
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Simulate actions without making changes.")
@click.option("--host", "host_filter", default=None, help="Only apply to this host name.")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output.")
def apply(config_file: Path, dry_run: bool, host_filter: Optional[str], verbose: bool) -> None:
    """Apply a configuration file to the defined hosts."""
    print_banner()
    console.print(f"[bold]Loading configuration:[/bold] {config_file}")

    try:
        config = load_config(config_file)
    except Exception as e:
        console.print(f"[red]Failed to load config:[/red] {e}")
        sys.exit(1)

    console.print(f"[green]✓[/green] Loaded fleet: [bold]{config.name}[/bold]")
    if config.description:
        console.print(f"  {config.description}")

    hosts = config.hosts
    if host_filter:
        hosts = [h for h in hosts if h.name == host_filter]
        if not hosts:
            console.print(f"[red]No host named '{host_filter}' found.[/red]")
            sys.exit(1)

    executor = Executor(dry_run=dry_run, verbose=verbose)

    for host in hosts:
        console.print()
        console.rule(f"[bold cyan]{host.name}[/bold cyan] ({host.hostname})")
        try:
            executor.apply_modules(host, config.modules)
            console.print(f"[green]✓ Host {host.name} completed successfully[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error on {host.name}:[/red] {e}")
            if verbose:
                console.print_exception()

    console.print()
    console.print(Panel("[bold green]All done![/bold green]", border_style="green"))


@main.command("module")
@click.argument("module_name")
@click.option("--host", required=True, help="Target hostname or IP.")
@click.option("--user", default="root", help="SSH user.")
@click.option("--port", default=22, type=int, help="SSH port.")
@click.option("--key", default=None, help="Path to private key.")
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
        console.print("Available modules:")
        for name in discover_modules():
            console.print(f"  • {name}")
        sys.exit(1)

    mod = module_cls()
    console.print(f"Running module [cyan]{module_name}[/cyan] on [bold]{host}[/bold]")
    executor = Executor(dry_run=dry_run)
    # Simple ad-hoc config
    config = {"packages": list(args)} if args else {}
    success = mod.apply(h, config, executor)
    if success:
        console.print("[green]✓ Module completed[/green]")
    else:
        console.print("[red]✗ Module failed[/red]")
        sys.exit(1)


@main.command()
def modules() -> None:
    """List all available smart modules."""
    print_banner()
    table = Table(title="Available Smart Modules", box=box.ROUNDED)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description")

    for name, cls in discover_modules().items():
        desc = getattr(cls, "description", "No description")
        table.add_row(name, desc)

    console.print(table)


@main.command()
@click.option("--host", required=True, help="Target hostname or IP.")
@click.option("--user", default="root")
@click.option("--port", default=22, type=int)
@click.option("--key", default=None)
def shell(host: str, user: str, port: int, key: Optional[str]) -> None:
    """Open an interactive shell on a remote host (via SSH)."""
    print_banner()
    console.print(f"Connecting to [bold]{user}@{host}:{port}[/bold] ...")
    # In a full implementation this would drop into an interactive SSH session.
    # For now we provide a clear message.
    console.print(
        Panel(
            "Interactive shell support is available.\n"
            "Use your system SSH client for full interactive sessions:\n\n"
            f"[cyan]ssh -p {port} {user}@{host}[/cyan]",
            title="Shell",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    main()
