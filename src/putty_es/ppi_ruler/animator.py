"""
Clean animated startup and installer sequences for ppiRuler.
"""

from __future__ import annotations

import time
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.style import Style

console = Console()


class StartupAnimator:
    """Beautiful animated startup sequence."""

    FRAMES = [
        r"""
   ╔══════════════════════════════════════╗
   ║                                      ║
   ║          p p i R u l e r             ║
   ║                                      ║
   ║     Python Package Implementor       ║
   ║              Ruler                   ║
   ║                                      ║
   ╚══════════════════════════════════════╝
        """,
        r"""
   ╔══════════════════════════════════════╗
   ║                                      ║
   ║         ░p░p░i░R░u░l░e░r░            ║
   ║                                      ║
   ║     Python Package Implementor       ║
   ║              Ruler                   ║
   ║                                      ║
   ╚══════════════════════════════════════╝
        """,
        r"""
   ╔══════════════════════════════════════╗
   ║                                      ║
   ║        ▒p▒p▒i▒R▒u▒l▒e▒r▒             ║
   ║                                      ║
   ║     Python Package Implementor       ║
   ║              Ruler                   ║
   ║                                      ║
   ╚══════════════════════════════════════╝
        """,
        r"""
   ╔══════════════════════════════════════╗
   ║                                      ║
   ║       ▓p▓p▓i▓R▓u▓l▓e▓r▓              ║
   ║                                      ║
   ║     Python Package Implementor       ║
   ║              Ruler                   ║
   ║                                      ║
   ╚══════════════════════════════════════╝
        """,
        r"""
   ╔══════════════════════════════════════╗
   ║                                      ║
   ║      █p█p█i█R█u█l█e█r█               ║
   ║                                      ║
   ║     Python Package Implementor       ║
   ║              Ruler                   ║
   ║                                      ║
   ╚══════════════════════════════════════╝
        """,
    ]

    def play(self, delay: float = 0.18) -> None:
        console.clear()
        with Live(console=console, refresh_per_second=15) as live:
            for frame in self.FRAMES:
                text = Text(frame, style="bold cyan")
                live.update(Align.center(text))
                time.sleep(delay)

            final = Text(
                r"""
   ╔══════════════════════════════════════╗
   ║                                      ║
   ║         ppiRuler  v1.0               ║
   ║                                      ║
   ║   Python Package Implementor Ruler   ║
   ║                                      ║
   ║     Offline · Clean · Powerful       ║
   ║                                      ║
   ╚══════════════════════════════════════╝
                """,
                style="bold bright_cyan",
            )
            live.update(Align.center(final))
            time.sleep(0.7)

        console.print()


class InstallerAnimator:
    """Animated installer progress for the final distribution."""

    def __init__(self, package: str, version: str) -> None:
        self.package = package
        self.version = version

    def play(self) -> None:
        steps = [
            "Preparing clean workspace",
            "Downloading package from PyPI",
            "Extracting & analyzing",
            "Generating INI configuration",
            "Building Windows artifacts",
            "Building Linux artifacts",
            "Creating HTML launcher",
            "Writing manifest",
            "Finalizing offline package",
        ]

        console.print()
        console.print(
            Panel(
                f"[bold]Installing offline package[/bold]\n"
                f"[cyan]{self.package}[/cyan] v{self.version}",
                border_style="cyan",
            )
        )

        with Live(console=console, refresh_per_second=10) as live:
            for i, step in enumerate(steps, 1):
                bar = "█" * i + "░" * (len(steps) - i)
                content = Text.from_markup(
                    f"\n  [cyan]{bar}[/cyan]  {i}/{len(steps)}\n\n"
                    f"  → {step}…\n"
                )
                live.update(content)
                time.sleep(0.35)

        console.print("[bold green]  ✓ Installation sequence complete[/bold green]\n")
