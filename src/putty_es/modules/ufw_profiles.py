"""Named UFW security profiles."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

PROFILES = {
    "web": ["22/tcp", "80/tcp", "443/tcp"],
    "db": ["22/tcp", "5432/tcp", "3306/tcp"],
    "mail": ["22/tcp", "25/tcp", "587/tcp", "993/tcp"],
    "vpn": ["22/tcp", "1194/udp", "51820/udp"],
    "locked": ["22/tcp"],
}

class UfwProfilesModule(BaseModule):
    name = "ufw-profiles"
    description = "Apply named UFW profiles (web, db, mail, vpn, locked)"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        profile = config.get("profile", "web")
        ports = PROFILES.get(profile, PROFILES["web"])
        extra = config.get("extra_ports", [])
        ports = list(ports) + list(extra)
        executor.run(host, "ufw --force reset", sudo=True, check=False)
        executor.run(host, "ufw default deny incoming", sudo=True, check=False)
        executor.run(host, "ufw default allow outgoing", sudo=True, check=False)
        for p in ports:
            executor.run(host, f"ufw allow {p}", sudo=True, check=False)
        executor.run(host, "ufw --force enable", sudo=True, check=False)
        return True
