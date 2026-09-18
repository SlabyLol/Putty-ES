"""Load or blacklist kernel modules."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class KernelModulesModule(BaseModule):
    name = "kernel-modules"
    description = "Load useful modules or blacklist dangerous ones"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        load: List[str] = config.get("load", [])
        blacklist: List[str] = config.get("blacklist", [])
        for m in load:
            executor.run(host, f"modprobe {m} || true", sudo=True, check=False)
        for m in blacklist:
            executor.run(
                host,
                f"echo 'blacklist {m}' > /etc/modprobe.d/blacklist-putty-es-{m}.conf",
                sudo=True,
                check=False,
            )
        return True
