"""SSH pre-login banner."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
import base64
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class SshdBannerModule(BaseModule):
    name = "sshd-banner"
    description = "Set SSH login banner (legal/warning + Putty-Fire line)"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        text = config.get(
            "text",
            "Authorized access only. Protected by Putty-Fire.\n",
        )
        b64 = base64.b64encode(text.encode()).decode()
        executor.run(
            host,
            f"echo '{b64}' | base64 -d > /etc/ssh/putty-es-banner && "
            f"sed -i 's|^#*Banner .*|Banner /etc/ssh/putty-es-banner|' /etc/ssh/sshd_config && "
            f"grep -q '^Banner /etc/ssh/putty-es-banner' /etc/ssh/sshd_config || "
            f"echo 'Banner /etc/ssh/putty-es-banner' >> /etc/ssh/sshd_config && "
            f"systemctl reload sshd 2>/dev/null || systemctl reload ssh || true",
            sudo=True,
            check=False,
        )
        return True
