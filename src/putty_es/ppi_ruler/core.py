"""
Core engine of ppiRuler.
Handles package download, analysis and orchestration of builds.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.text import Text

from putty_es.ppi_ruler.builder import PackageBuilder
from putty_es.ppi_ruler.animator import StartupAnimator, InstallerAnimator

console = Console()


class PPIRuler:
    """
    Python Package Implementor Ruler.

    Downloads a package from PyPI and produces clean, offline-runnable
    artifacts in multiple formats.
    """

    def __init__(
        self,
        package: str,
        version: Optional[str] = None,
        output_dir: Path | str = "./ppi_output",
        targets: Optional[List[str]] = None,
    ) -> None:
        self.package = package
        self.version = version
        self.output_dir = Path(output_dir).resolve()
        self.targets = targets or ["exe", "linux", "html", "ini"]
        self.workdir: Optional[Path] = None
        self.meta: Dict[str, Any] = {}

    def run(self, animated: bool = True) -> Path:
        """Full pipeline: download → analyze → build → package."""
        if animated:
            animator = StartupAnimator()
            animator.play()

        self.output_dir.mkdir(parents=True, exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]ppiRuler pipeline", total=5)

            # 1. Create temp workdir
            progress.update(task, description="[cyan]Preparing workspace…")
            self.workdir = Path(tempfile.mkdtemp(prefix="ppi_ruler_"))
            progress.advance(task)

            # 2. Download package
            progress.update(task, description=f"[cyan]Downloading {self.package}…")
            wheel_or_sdist = self._download_package()
            progress.advance(task)

            # 3. Extract & analyze
            progress.update(task, description="[cyan]Analyzing package…")
            self._analyze(wheel_or_sdist)
            progress.advance(task)

            # 4. Build all targets
            progress.update(task, description="[cyan]Building targets…")
            builder = PackageBuilder(
                package=self.package,
                version=self.meta.get("version", self.version or "latest"),
                source_dir=self.workdir,
                output_dir=self.output_dir,
                meta=self.meta,
            )
            artifacts = builder.build(self.targets)
            progress.advance(task)

            # 5. Finalize
            progress.update(task, description="[cyan]Finalizing…")
            self._write_manifest(artifacts)
            progress.advance(task)

        # Cleanup workdir
        if self.workdir and self.workdir.exists():
            shutil.rmtree(self.workdir, ignore_errors=True)

        console.print()
        console.print(
            Panel(
                f"[bold green]✓ ppiRuler finished successfully[/bold green]\n\n"
                f"Package : [cyan]{self.package}[/cyan]\n"
                f"Version : [cyan]{self.meta.get('version', 'unknown')}[/cyan]\n"
                f"Output  : [cyan]{self.output_dir}[/cyan]\n"
                f"Targets : {', '.join(self.targets)}",
                title="ppiRuler",
                border_style="green",
            )
        )
        return self.output_dir

    def _download_package(self) -> Path:
        """Download the package from PyPI using pip download."""
        import subprocess
        import sys

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            "--dest",
            str(self.workdir),
            self.package if not self.version else f"{self.package}=={self.version}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to download package:\n{result.stderr}")

        # Find the downloaded file
        files = list(self.workdir.glob("*.whl")) + list(self.workdir.glob("*.tar.gz"))
        if not files:
            raise RuntimeError("No package file was downloaded.")
        return files[0]

    def _analyze(self, package_file: Path) -> None:
        """Extract metadata and prepare source."""
        import zipfile
        import tarfile

        extract_dir = self.workdir / "extracted"
        extract_dir.mkdir()

        if package_file.suffix == ".whl":
            with zipfile.ZipFile(package_file, "r") as zf:
                zf.extractall(extract_dir)
        else:
            with tarfile.open(package_file, "r:gz") as tf:
                tf.extractall(extract_dir)

        # Try to read metadata
        meta: Dict[str, Any] = {"name": self.package, "version": self.version or "unknown"}

        # Look for METADATA or PKG-INFO
        for meta_file in extract_dir.rglob("METADATA"):
            content = meta_file.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                if line.startswith("Name:"):
                    meta["name"] = line.split(":", 1)[1].strip()
                elif line.startswith("Version:"):
                    meta["version"] = line.split(":", 1)[1].strip()
                elif line.startswith("Summary:"):
                    meta["summary"] = line.split(":", 1)[1].strip()
            break

        for meta_file in extract_dir.rglob("PKG-INFO"):
            content = meta_file.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                if line.startswith("Name:"):
                    meta["name"] = line.split(":", 1)[1].strip()
                elif line.startswith("Version:"):
                    meta["version"] = line.split(":", 1)[1].strip()
            break

        self.meta = meta

        # Copy extracted content to a clean source tree for building
        src = self.workdir / "src"
        src.mkdir()
        # Move the top-level package dirs
        for item in extract_dir.iterdir():
            if item.is_dir() and not item.name.endswith(".dist-info") and not item.name.endswith(".egg-info"):
                shutil.copytree(item, src / item.name, dirs_exist_ok=True)

    def _write_manifest(self, artifacts: List[Path]) -> None:
        """Write a clean manifest of everything that was produced."""
        manifest = {
            "package": self.meta.get("name", self.package),
            "version": self.meta.get("version", "unknown"),
            "summary": self.meta.get("summary", ""),
            "targets": self.targets,
            "artifacts": [str(p.relative_to(self.output_dir)) for p in artifacts],
            "generated_by": "ppiRuler (Putty-ES)",
        }
        (self.output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
