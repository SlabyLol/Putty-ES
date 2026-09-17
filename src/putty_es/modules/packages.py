"""
System package management module (apt, dnf, yum, apk, pacman).
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class PackagesModule(BaseModule):
    name = "packages"
    description = "Install / remove system packages (apt, dnf, yum, apk, pacman)"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        action = config.get("action", "install")
        packages: List[str] = config.get("packages", [])

        if not packages:
            return True

        # Detect package manager
        pm = self._detect_package_manager(host, executor)
        if not pm:
            raise RuntimeError("Could not detect package manager on remote host")

        if action == "install":
            cmd = self._install_cmd(pm, packages)
        elif action == "remove":
            cmd = self._remove_cmd(pm, packages)
        elif action == "update":
            cmd = self._update_cmd(pm)
        else:
            raise ValueError(f"Unknown action: {action}")

        executor.run(host, cmd, sudo=True)
        return True

    def _detect_package_manager(self, host: "Host", executor: "Executor") -> str | None:
        checks = [
            ("apt-get", "apt"),
            ("dnf", "dnf"),
            ("yum", "yum"),
            ("apk", "apk"),
            ("pacman", "pacman"),
        ]
        for binary, name in checks:
            code, _, _ = executor.run(host, f"command -v {binary}", check=False)
            if code == 0:
                return name
        return None

    def _install_cmd(self, pm: str, packages: List[str]) -> str:
        pkgs = " ".join(packages)
        if pm == "apt":
            return f"DEBIAN_FRONTEND=noninteractive apt-get update -qq && apt-get install -y -qq {pkgs}"
        if pm == "dnf":
            return f"dnf install -y {pkgs}"
        if pm == "yum":
            return f"yum install -y {pkgs}"
        if pm == "apk":
            return f"apk add --no-cache {pkgs}"
        if pm == "pacman":
            return f"pacman -Sy --noconfirm {pkgs}"
        raise ValueError(f"Unsupported package manager: {pm}")

    def _remove_cmd(self, pm: str, packages: List[str]) -> str:
        pkgs = " ".join(packages)
        if pm == "apt":
            return f"DEBIAN_FRONTEND=noninteractive apt-get remove -y -qq {pkgs}"
        if pm == "dnf":
            return f"dnf remove -y {pkgs}"
        if pm == "yum":
            return f"yum remove -y {pkgs}"
        if pm == "apk":
            return f"apk del {pkgs}"
        if pm == "pacman":
            return f"pacman -R --noconfirm {pkgs}"
        raise ValueError(f"Unsupported package manager: {pm}")

    def _update_cmd(self, pm: str) -> str:
        if pm == "apt":
            return "DEBIAN_FRONTEND=noninteractive apt-get update -qq && apt-get upgrade -y -qq"
        if pm == "dnf":
            return "dnf upgrade -y"
        if pm == "yum":
            return "yum update -y"
        if pm == "apk":
            return "apk update && apk upgrade"
        if pm == "pacman":
            return "pacman -Syu --noconfirm"
        raise ValueError(f"Unsupported package manager: {pm}")
