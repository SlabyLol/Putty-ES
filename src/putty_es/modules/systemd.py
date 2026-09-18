"""Systemd unit management."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
import base64
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class SystemdModule(BaseModule):
    name = "systemd"
    description = "Install and enable custom systemd service units"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        units: List[dict] = config.get("units", [])
        for u in units:
            name = u.get("name")
            if not name:
                continue
            description = u.get("description", name)
            exec_start = u.get("exec_start")
            user = u.get("user", "root")
            after = u.get("after", "network.target")
            restart = u.get("restart", "always")
            if not exec_start:
                continue
            content = f"""[Unit]
Description={description}
After={after}

[Service]
Type=simple
User={user}
ExecStart={exec_start}
Restart={restart}
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
            b64 = base64.b64encode(content.encode()).decode()
            path = f"/etc/systemd/system/{name}.service"
            executor.run(
                host,
                f"echo '{b64}' | base64 -d > {path} && systemctl daemon-reload && "
                f"systemctl enable --now {name}",
                sudo=True,
                check=False,
            )
        return True
