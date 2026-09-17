"""
Package builder – creates clean offline artifacts for multiple targets.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

console = Console()


class PackageBuilder:
    """Builds standalone artifacts from an extracted Python package."""

    def __init__(
        self,
        package: str,
        version: str,
        source_dir: Path,
        output_dir: Path,
        meta: Dict[str, Any],
    ) -> None:
        self.package = package
        self.version = version
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.meta = meta
        self.artifacts: List[Path] = []

    def build(self, targets: List[str]) -> List[Path]:
        for target in targets:
            console.print(f"  → Building target [cyan]{target}[/cyan]")
            if target in ("exe", "windows"):
                self._build_windows()
            elif target in ("linux", "bin"):
                self._build_linux()
            elif target == "html":
                self._build_html()
            elif target == "ini":
                self._build_ini()
            elif target == "dll":
                self._build_dll_stub()
            else:
                console.print(f"    [yellow]Unknown target '{target}', skipping[/yellow]")
        return self.artifacts

    def _build_windows(self) -> None:
        """Create a Windows-oriented standalone using PyInstaller when available."""
        out = self.output_dir / "windows"
        out.mkdir(parents=True, exist_ok=True)

        # Generate a clean entry-point script
        entry = self.source_dir / "_ppi_entry.py"
        entry.write_text(
            textwrap.dedent(
                f'''
                #!/usr/bin/env python3
                """Auto-generated entry point by ppiRuler for {self.package}"""
                import sys
                import runpy

                def main():
                    try:
                        # Try common entry points
                        runpy.run_module("{self.package}", run_name="__main__")
                    except Exception:
                        print("{self.package} v{self.version}")
                        print("Package loaded offline by ppiRuler.")
                        print("No __main__ entry point found – import the package in your code.")

                if __name__ == "__main__":
                    main()
                '''
            ).strip(),
            encoding="utf-8",
        )

        # Try PyInstaller if present
        try:
            import PyInstaller  # noqa: F401

            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                "--onefile",
                "--clean",
                "--name",
                f"{self.package}-{self.version}",
                "--distpath",
                str(out),
                "--workpath",
                str(self.source_dir / "_build"),
                "--specpath",
                str(self.source_dir),
                str(entry),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                exe = out / f"{self.package}-{self.version}.exe"
                if exe.exists() or (out / f"{self.package}-{self.version}").exists():
                    self.artifacts.append(out)
                    console.print("    [green]✓ Windows executable built with PyInstaller[/green]")
                    return
        except ImportError:
            pass

        # Fallback: clean portable launcher + package copy
        launcher = out / f"{self.package}.bat"
        launcher.write_text(
            textwrap.dedent(
                f"""
                @echo off
                title {self.package} v{self.version} – powered by ppiRuler
                echo.
                echo  ========================================
                echo   {self.package} v{self.version}
                echo   Offline package by ppiRuler (Putty-ES)
                echo  ========================================
                echo.
                python -c "import {self.package}; print('{self.package} ready')" 2>nul || (
                    echo Package files are located in the same folder.
                    echo Add this folder to PYTHONPATH or install the package.
                )
                pause
                """
            ).strip(),
            encoding="utf-8",
        )
        # Copy package source
        pkg_src = self.source_dir / "src"
        if pkg_src.exists():
            shutil.copytree(pkg_src, out / "package", dirs_exist_ok=True)
        else:
            shutil.copytree(self.source_dir, out / "package", dirs_exist_ok=True)

        self.artifacts.append(out)
        console.print("    [green]✓ Windows portable package created[/green]")

    def _build_linux(self) -> None:
        """Create a Linux standalone binary / portable package."""
        out = self.output_dir / "linux"
        out.mkdir(parents=True, exist_ok=True)

        entry = self.source_dir / "_ppi_entry_linux.py"
        entry.write_text(
            textwrap.dedent(
                f'''
                #!/usr/bin/env python3
                """Auto-generated entry point by ppiRuler for {self.package}"""
                import runpy
                import sys

                def main():
                    try:
                        runpy.run_module("{self.package}", run_name="__main__")
                    except Exception:
                        print("{self.package} v{self.version}")
                        print("Offline package generated by ppiRuler.")

                if __name__ == "__main__":
                    main()
                '''
            ).strip(),
            encoding="utf-8",
        )

        # Try PyInstaller
        try:
            import PyInstaller  # noqa: F401

            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                "--onefile",
                "--clean",
                "--name",
                f"{self.package}-{self.version}",
                "--distpath",
                str(out),
                "--workpath",
                str(self.source_dir / "_build_linux"),
                str(entry),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.artifacts.append(out)
                console.print("    [green]✓ Linux binary built with PyInstaller[/green]")
                return
        except ImportError:
            pass

        # Fallback shell launcher
        launcher = out / f"{self.package}"
        launcher.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env bash
                # {self.package} v{self.version} – offline launcher by ppiRuler
                DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
                export PYTHONPATH="$DIR/package:${{PYTHONPATH}}"
                echo "========================================"
                echo "  {self.package} v{self.version}"
                echo "  Offline package by ppiRuler"
                echo "========================================"
                python3 -c "import {self.package}; print('{self.package} ready')" 2>/dev/null || {{
                    echo "Package sources are in $DIR/package"
                }}
                """
            ).strip(),
            encoding="utf-8",
        )
        launcher.chmod(0o755)

        pkg_src = self.source_dir / "src"
        if pkg_src.exists():
            shutil.copytree(pkg_src, out / "package", dirs_exist_ok=True)
        else:
            shutil.copytree(self.source_dir, out / "package", dirs_exist_ok=True)

        self.artifacts.append(out)
        console.print("    [green]✓ Linux portable package created[/green]")

    def _build_html(self) -> None:
        """Generate a clean HTML launcher that can run the package concept in browser context."""
        out = self.output_dir / "html"
        out.mkdir(parents=True, exist_ok=True)

        html = textwrap.dedent(
            f"""\
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8" />
              <meta name="viewport" content="width=device-width, initial-scale=1.0" />
              <title>{self.package} v{self.version} – ppiRuler</title>
              <style>
                :root {{
                  --bg: #0d1117;
                  --card: #161b22;
                  --accent: #58a6ff;
                  --text: #e6edf3;
                  --muted: #8b949e;
                }}
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                  font-family: 'Segoe UI', system-ui, sans-serif;
                  background: var(--bg);
                  color: var(--text);
                  min-height: 100vh;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  overflow: hidden;
                }}
                .container {{
                  background: var(--card);
                  border: 1px solid #30363d;
                  border-radius: 16px;
                  padding: 2.5rem;
                  max-width: 520px;
                  width: 90%;
                  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
                  animation: fadeIn 0.8s ease-out;
                }}
                @keyframes fadeIn {{
                  from {{ opacity: 0; transform: translateY(20px); }}
                  to {{ opacity: 1; transform: translateY(0); }}
                }}
                h1 {{
                  font-size: 1.6rem;
                  margin-bottom: 0.3rem;
                  background: linear-gradient(90deg, var(--accent), #a371f7);
                  -webkit-background-clip: text;
                  -webkit-text-fill-color: transparent;
                }}
                .version {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem; }}
                .badge {{
                  display: inline-block;
                  background: #238636;
                  color: white;
                  padding: 0.2rem 0.6rem;
                  border-radius: 999px;
                  font-size: 0.75rem;
                  margin-bottom: 1.2rem;
                }}
                p {{ line-height: 1.6; color: var(--muted); margin-bottom: 1.2rem; }}
                .code {{
                  background: #0d1117;
                  border: 1px solid #30363d;
                  border-radius: 8px;
                  padding: 1rem;
                  font-family: ui-monospace, monospace;
                  font-size: 0.85rem;
                  overflow-x: auto;
                  margin-bottom: 1.2rem;
                }}
                .footer {{
                  font-size: 0.8rem;
                  color: var(--muted);
                  text-align: center;
                  margin-top: 1.5rem;
                }}
                .pulse {{
                  width: 12px; height: 12px;
                  background: #3fb950;
                  border-radius: 50%;
                  display: inline-block;
                  margin-right: 8px;
                  animation: pulse 1.5s infinite;
                }}
                @keyframes pulse {{
                  0% {{ box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.7); }}
                  70% {{ box-shadow: 0 0 0 10px rgba(63, 185, 80, 0); }}
                  100% {{ box-shadow: 0 0 0 0 rgba(63, 185, 80, 0); }}
                }}
              </style>
            </head>
            <body>
              <div class="container">
                <div class="badge"><span class="pulse"></span> Offline Ready</div>
                <h1>{self.package}</h1>
                <div class="version">v{self.version} · generated by ppiRuler</div>
                <p>
                  This package was transformed into a clean offline distribution.
                  All required files are local – no network requests to package servers.
                </p>
                <div class="code">
                  # Python usage (after adding package/ to PYTHONPATH)<br>
                  import {self.package}<br><br>
                  # Or run the generated executable / launcher<br>
                  # from the windows/ or linux/ folder
                </div>
                <p style="font-size:0.9rem">
                  For full browser execution consider Pyodide or a WebAssembly build.
                  This HTML file serves as a clean documentation & status page.
                </p>
                <div class="footer">
                  Powered by <strong>ppiRuler</strong> · Putty-ES
                </div>
              </div>
            </body>
            </html>
            """
        )
        (out / "index.html").write_text(html, encoding="utf-8")
        self.artifacts.append(out)
        console.print("    [green]✓ HTML launcher & status page created[/green]")

    def _build_ini(self) -> None:
        """Generate clean INI configuration files."""
        out = self.output_dir / "config"
        out.mkdir(parents=True, exist_ok=True)

        ini_content = textwrap.dedent(
            f"""\
            ; ============================================================
            ;  {self.package} v{self.version}
            ;  Configuration generated by ppiRuler (Putty-ES)
            ;  Clean offline package – no remote fetches required
            ; ============================================================

            [package]
            name = {self.package}
            version = {self.version}
            summary = {self.meta.get('summary', '')}
            generated_by = ppiRuler

            [runtime]
            offline = true
            python_required = >=3.10
            entry_point = {self.package}

            [paths]
            package_dir = ./package
            windows_launcher = ../windows/{self.package}.bat
            linux_launcher = ../linux/{self.package}
            html_status = ../html/index.html

            [options]
            # Add any custom runtime options here
            verbose = false
            log_level = INFO
            """
        )
        ini_path = out / f"{self.package}.ini"
        ini_path.write_text(ini_content, encoding="utf-8")

        # Also a generic settings.ini
        settings = textwrap.dedent(
            """\
            [general]
            app_name = ppiRuler Package
            auto_update = false
            check_remote = false

            [ui]
            theme = dark
            animation = true
            """
        )
        (out / "settings.ini").write_text(settings, encoding="utf-8")

        self.artifacts.append(out)
        console.print("    [green]✓ INI configuration files created[/green]")

    def _build_dll_stub(self) -> None:
        """Create a placeholder / documentation for DLL usage (Windows)."""
        out = self.output_dir / "windows"
        out.mkdir(parents=True, exist_ok=True)

        readme = textwrap.dedent(
            f"""\
            # DLL / Native Extension Notes – {self.package}

            ppiRuler has prepared a clean offline package.

            If the original package contains compiled extensions (.pyd / .so),
            they are included in the package/ folder.

            For true DLL generation of pure-Python packages, consider:
            - Nuitka (--module)
            - Cython
            - or keep using the generated .exe / launcher

            This file is intentionally a clean documentation stub so that
            the distribution remains transparent and auditable.
            """
        )
        (out / "DLL_NOTES.txt").write_text(readme, encoding="utf-8")
        console.print("    [green]✓ DLL notes / stub created[/green]")
