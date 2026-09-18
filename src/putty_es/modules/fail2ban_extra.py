"""Extra fail2ban jails (nginx, ssh, recidive)."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
import base64
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class Fail2banExtraModule(BaseModule):
    name = "fail2ban-extra"
    description = "Extra fail2ban jails for nginx and recidive bans"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        nginx = config.get("nginx", True)
        recidive = config.get("recidive", True)
        parts = ["[DEFAULT]\nbantime = 3600\nfindtime = 600\nmaxretry = 5\n"]
        if nginx:
            parts.append(
                "[nginx-http-auth]\nenabled = true\nport = http,https\nlogpath = /var/log/nginx/error.log\n"
            )
            parts.append(
                "[nginx-botsearch]\nenabled = true\nport = http,https\nlogpath = /var/log/nginx/access.log\n"
            )
        if recidive:
            parts.append(
                "[recidive]\nenabled = true\nlogpath = /var/log/fail2ban.log\nbantime = 86400\nfindtime = 86400\nmaxretry = 3\n"
            )
        body = "\n".join(parts)
        b64 = base64.b64encode(body.encode()).decode()
        executor.run(
            host,
            f"mkdir -p /etc/fail2ban/jail.d && echo '{b64}' | base64 -d > /etc/fail2ban/jail.d/putty-es-extra.conf && "
            f"systemctl restart fail2ban 2>/dev/null || true",
            sudo=True,
            check=False,
        )
        return True
