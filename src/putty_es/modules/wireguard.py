"""WireGuard VPN install helper."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class WireguardModule(BaseModule):
    name = "wireguard"
    description = "Install WireGuard tools and enable IP forwarding"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        executor.run(
            host,
            "apt-get install -y -qq wireguard wireguard-tools || dnf install -y wireguard-tools || true",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            "sysctl -w net.ipv4.ip_forward=1; "
            "grep -q 'net.ipv4.ip_forward=1' /etc/sysctl.d/99-wireguard.conf 2>/dev/null || "
            "echo net.ipv4.ip_forward=1 > /etc/sysctl.d/99-wireguard.conf",
            sudo=True,
            check=False,
        )
        executor.run(host, "mkdir -p /etc/wireguard && chmod 700 /etc/wireguard", sudo=True, check=False)
        return True
