"""
Basic monitoring & health-check module.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class MonitoringModule(BaseModule):
    name = "monitoring"
    description = "Install basic monitoring tools and health-check scripts"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        tools: List[str] = config.get(
            "tools",
            ["htop", "iotop", "nethogs", "ncdu", "sysstat"],
        )
        install_node_exporter = config.get("node_exporter", False)

        # Install tools
        pkg_str = " ".join(tools)
        if pkg_str:
            executor.run(
                host,
                f"DEBIAN_FRONTEND=noninteractive apt-get install -y -qq {pkg_str} || "
                f"dnf install -y {pkg_str} || yum install -y {pkg_str} || true",
                sudo=True,
                check=False,
            )

        # Simple health-check script
        script = """#!/bin/bash
# Putty-ES health check
echo "=== System Health $(date) ==="
echo "Uptime: $(uptime)"
echo "Memory:"
free -h
echo "Disk:"
df -h /
echo "Load: $(cat /proc/loadavg)"
"""
        import base64

        b64 = base64.b64encode(script.encode()).decode()
        executor.run(
            host,
            f"echo '{b64}' | base64 -d > /usr/local/bin/putty-es-health && chmod +x /usr/local/bin/putty-es-health",
            sudo=True,
            check=False,
        )

        if install_node_exporter:
            # Minimal node_exporter install (optional)
            executor.run(
                host,
                "id node_exporter >/dev/null 2>&1 || useradd -r -s /bin/false node_exporter",
                sudo=True,
                check=False,
            )
            # User can extend this later

        return True
