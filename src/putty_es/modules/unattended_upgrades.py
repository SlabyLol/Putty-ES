"""Automatic security updates (Debian/Ubuntu)."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class UnattendedUpgradesModule(BaseModule):
    name = "unattended-upgrades"
    description = "Enable automatic security updates on Debian/Ubuntu"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        executor.run(
            host,
            "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq unattended-upgrades apt-listchanges || true",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            "dpkg-reconfigure -plow unattended-upgrades 2>/dev/null || "
            "echo 'unattended-upgrades unattended-upgrades/enable_auto_updates boolean true' | debconf-set-selections",
            sudo=True,
            check=False,
        )
        return True
