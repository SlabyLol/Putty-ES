"""Message of the day / login banner."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
import base64
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class MotdModule(BaseModule):
    name = "motd"
    description = "Set custom MOTD / login banner"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        text = config.get(
            "text",
            "Welcome – managed by Putty-ES\n",
        )
        if config.get("putty_fire_line", True):
            text = text.rstrip() + "\nProtected by Putty-Fire\n"
        b64 = base64.b64encode(text.encode()).decode()
        executor.run(
            host,
            f"echo '{b64}' | base64 -d > /etc/motd",
            sudo=True,
            check=False,
        )
        return True
