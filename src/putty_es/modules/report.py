"""Generate inventory report."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class ReportModule(BaseModule):
    name = "report"
    description = "Write a system inventory report"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        path = config.get("path", "/var/log/putty-es-report.txt")
        executor.run(
            host,
            f"{{
              echo Putty-ES Report $(date);
              uname -a;
              lsb_release -a 2>/dev/null || cat /etc/os-release;
              free -h;
              df -h;
              ip -br a 2>/dev/null;
              systemctl list-units --type=service --state=running 2>/dev/null | head -40;
              echo Protected by Putty-Fire: $(test -f /etc/putty-fire/STATUS && echo YES || echo NO);
            }} > {path}",
            sudo=True,
            check=False,
        )
        return True
