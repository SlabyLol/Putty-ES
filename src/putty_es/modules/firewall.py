"""
Firewall management module (ufw / firewalld).
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class FirewallModule(BaseModule):
    name = "firewall"
    description = "Configure firewall (ufw or firewalld)"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        enable = config.get("enable", True)
        allow: List[str] = config.get("allow", [])
        deny: List[str] = config.get("deny", [])

        fw = self._detect_firewall(host, executor)

        if fw == "ufw":
            if enable:
                executor.run(host, "ufw --force enable", sudo=True)
            for rule in allow:
                executor.run(host, f"ufw allow {rule}", sudo=True)
            for rule in deny:
                executor.run(host, f"ufw deny {rule}", sudo=True)
        elif fw == "firewalld":
            if enable:
                executor.run(host, "systemctl enable --now firewalld", sudo=True)
            for rule in allow:
                # Simple port/protocol support
                executor.run(
                    host,
                    f"firewall-cmd --permanent --add-port={rule} || firewall-cmd --permanent --add-service={rule}",
                    sudo=True,
                    check=False,
                )
            executor.run(host, "firewall-cmd --reload", sudo=True)
        else:
            # Fallback: just open ports with iptables (basic)
            for rule in allow:
                if "/" in rule:
                    port, proto = rule.split("/", 1)
                    executor.run(
                        host,
                        f"iptables -A INPUT -p {proto} --dport {port} -j ACCEPT",
                        sudo=True,
                        check=False,
                    )

        return True

    def _detect_firewall(self, host: "Host", executor: "Executor") -> str | None:
        code, _, _ = executor.run(host, "command -v ufw", check=False)
        if code == 0:
            return "ufw"
        code, _, _ = executor.run(host, "command -v firewall-cmd", check=False)
        if code == 0:
            return "firewalld"
        return None
