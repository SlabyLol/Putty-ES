"""Set system hostname."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class HostnameModule(BaseModule):
    name = "hostname"
    description = "Set system hostname cleanly"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        name = config.get("name") or config.get("hostname")
        if not name:
            return True
        executor.run(host, f"hostnamectl set-hostname {name}", sudo=True, check=False)
        executor.run(
            host,
            f"echo {name} > /etc/hostname; "
            f"grep -q '{name}' /etc/hosts || echo '127.0.1.1 {name}' >> /etc/hosts",
            sudo=True,
            check=False,
        )
        return True
