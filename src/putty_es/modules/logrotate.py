"""Logrotate rules."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
import base64
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class LogrotateModule(BaseModule):
    name = "logrotate"
    description = "Install logrotate configs for app logs"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        jobs: List[dict] = config.get("jobs", [])
        for j in jobs:
            name = j.get("name", "app")
            path = j.get("path", "/var/log/app/*.log")
            rotate = j.get("rotate", 14)
            body = f"""{path} {{
    daily
    missingok
    rotate {rotate}
    compress
    delaycompress
    notifempty
    copytruncate
}}
"""
            b64 = base64.b64encode(body.encode()).decode()
            executor.run(
                host,
                f"echo '{b64}' | base64 -d > /etc/logrotate.d/putty-es-{name}",
                sudo=True,
                check=False,
            )
        return True
