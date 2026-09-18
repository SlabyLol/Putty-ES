"""Disk cleanup."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class CleanupModule(BaseModule):
    name = "cleanup"
    description = "Clean apt cache, old logs, temp files"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        executor.run(
            host,
            "apt-get clean 2>/dev/null; apt-get autoremove -y -qq 2>/dev/null; "
            "journalctl --vacuum-time=7d 2>/dev/null; "
            "rm -rf /tmp/* /var/tmp/* 2>/dev/null; true",
            sudo=True,
            check=False,
        )
        return True
