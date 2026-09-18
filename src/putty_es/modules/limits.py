"""System resource limits (limits.conf)."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
import base64
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class LimitsModule(BaseModule):
    name = "limits"
    description = "Configure /etc/security/limits.d for nofile/nproc"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        nofile = config.get("nofile", 65535)
        nproc = config.get("nproc", 65535)
        body = f"* soft nofile {nofile}\n* hard nofile {nofile}\n* soft nproc {nproc}\n* hard nproc {nproc}\n"
        b64 = base64.b64encode(body.encode()).decode()
        executor.run(
            host,
            f"echo '{b64}' | base64 -d > /etc/security/limits.d/99-putty-es.conf",
            sudo=True,
            check=False,
        )
        return True
