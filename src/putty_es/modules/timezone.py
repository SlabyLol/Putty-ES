"""Timezone and NTP."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class TimezoneModule(BaseModule):
    name = "timezone"
    description = "Set timezone and enable NTP time sync"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        tz = config.get("timezone", "UTC")
        ntp = config.get("ntp", True)
        executor.run(host, f"timedatectl set-timezone {tz}", sudo=True, check=False)
        if ntp:
            executor.run(
                host,
                "timedatectl set-ntp true 2>/dev/null || "
                "(apt-get install -y -qq chrony && systemctl enable --now chrony) || true",
                sudo=True,
                check=False,
            )
        return True
