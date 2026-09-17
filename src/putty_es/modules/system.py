"""
System configuration module (hostname, timezone, users, services).
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class SystemModule(BaseModule):
    name = "system"
    description = "System settings: hostname, timezone, services, sysctl"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        if "hostname" in config:
            hostname = config["hostname"]
            executor.run(host, f"hostnamectl set-hostname {hostname}", sudo=True, check=False)
            # Fallback for older systems
            executor.run(
                host,
                f"echo {hostname} > /etc/hostname && hostname {hostname}",
                sudo=True,
                check=False,
            )

        if "timezone" in config:
            tz = config["timezone"]
            executor.run(host, f"timedatectl set-timezone {tz}", sudo=True, check=False)

        # Enable/start services
        services: List[str] = config.get("services", [])
        for svc in services:
            executor.run(host, f"systemctl enable --now {svc}", sudo=True, check=False)

        # Sysctl settings
        sysctl: dict[str, Any] = config.get("sysctl", {})
        for key, value in sysctl.items():
            executor.run(
                host,
                f"sysctl -w {key}={value}",
                sudo=True,
                check=False,
            )

        return True
