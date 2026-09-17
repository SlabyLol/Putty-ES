"""
Remote execution engine for Putty-ES.
Handles SSH connections and command execution with dry-run support.
"""

from __future__ import annotations

from typing import Any, List, Optional

from rich.console import Console

from putty_es.core.config import Host, ModuleConfig
from putty_es.core.module_loader import get_module

console = Console()


class Executor:
    """Executes modules against hosts over SSH."""

    def __init__(self, dry_run: bool = False, verbose: bool = False) -> None:
        self.dry_run = dry_run
        self.verbose = verbose
        self._connections: dict[str, Any] = {}

    def connect(self, host: Host) -> Any:
        """Establish or reuse an SSH connection."""
        key = f"{host.user}@{host.hostname}:{host.port}"
        if key in self._connections:
            return self._connections[key]

        if self.dry_run:
            console.print(f"  [dim][dry-run] would connect to {key}[/dim]")
            return None

        try:
            import paramiko

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_kwargs: dict[str, Any] = {
                "hostname": host.hostname,
                "port": host.port,
                "username": host.user,
                "timeout": 15,
            }
            if host.key:
                connect_kwargs["key_filename"] = host.key
            if host.password:
                connect_kwargs["password"] = host.password

            client.connect(**connect_kwargs)
            self._connections[key] = client
            if self.verbose:
                console.print(f"  [green]Connected[/green] to {key}")
            return client
        except Exception as e:
            console.print(f"  [red]Connection failed:[/red] {e}")
            raise

    def run(
        self,
        host: Host,
        command: str,
        check: bool = True,
        sudo: bool = False,
    ) -> tuple[int, str, str]:
        """
        Execute a command on the remote host.

        Returns (exit_code, stdout, stderr).
        """
        if sudo and not command.startswith("sudo "):
            command = f"sudo {command}"

        if self.dry_run:
            console.print(f"  [dim][dry-run] {command}[/dim]")
            return 0, "", ""

        client = self.connect(host)
        if client is None:
            return 0, "", ""

        if self.verbose:
            console.print(f"  [dim]$ {command}[/dim]")

        stdin, stdout, stderr = client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")

        if check and exit_code != 0:
            raise RuntimeError(f"Command failed (exit {exit_code}): {command}\n{err}")

        return exit_code, out, err

    def apply_modules(self, host: Host, modules: List[ModuleConfig]) -> None:
        """Apply a list of modules to a single host."""
        for mod_cfg in modules:
            name = mod_cfg.name
            console.print(f"  → Module [cyan]{name}[/cyan]")

            module_cls = get_module(name)
            if module_cls is None:
                console.print(f"    [yellow]Warning: module '{name}' not found, skipping[/yellow]")
                continue

            module = module_cls()
            # Convert pydantic model to dict, excluding the name
            cfg = mod_cfg.model_dump(exclude={"name"})

            try:
                success = module.apply(host, cfg, self)
                if success:
                    console.print(f"    [green]✓[/green] {name}")
                else:
                    console.print(f"    [red]✗[/red] {name} reported failure")
            except Exception as e:
                console.print(f"    [red]✗ {name}: {e}[/red]")
                raise

    def close(self) -> None:
        """Close all open connections."""
        for client in self._connections.values():
            try:
                client.close()
            except Exception:
                pass
        self._connections.clear()

    def __del__(self) -> None:
        self.close()
