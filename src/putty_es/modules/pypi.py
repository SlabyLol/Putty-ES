"""
PyPI / Python package management module.
Installs packages into system Python or a virtual environment.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class PyPIModule(BaseModule):
    name = "pypi"
    description = "Install Python packages from PyPI (pip) on remote hosts"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        packages: List[str] = config.get("packages", [])
        venv: str | None = config.get("venv")  # optional path to virtualenv
        upgrade: bool = config.get("upgrade", False)
        user: bool = config.get("user", False)

        if not packages:
            return True

        # Ensure pip is available
        code, _, _ = executor.run(host, "python3 -m pip --version", check=False)
        if code != 0:
            # Try to bootstrap pip
            executor.run(
                host,
                "python3 -m ensurepip --upgrade || curl -sS https://bootstrap.pypa.io/get-pip.py | python3",
                sudo=True,
                check=False,
            )

        pkg_str = " ".join(packages)
        flags = []
        if upgrade:
            flags.append("--upgrade")
        if user:
            flags.append("--user")

        flag_str = " ".join(flags)

        if venv:
            # Create venv if needed and install into it
            executor.run(host, f"python3 -m venv {venv}", check=False)
            cmd = f"{venv}/bin/pip install {flag_str} {pkg_str}"
        else:
            cmd = f"python3 -m pip install {flag_str} {pkg_str}"

        executor.run(host, cmd, sudo=not user and not venv)
        return True
