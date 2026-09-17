"""
Certbot / Let's Encrypt SSL certificate module.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class CertbotModule(BaseModule):
    name = "certbot"
    description = "Obtain and renew Let's Encrypt certificates via Certbot"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        install = config.get("install", True)
        email = config.get("email", "admin@example.com")
        domains: List[str] = config.get("domains", [])
        nginx = config.get("nginx", True)  # use nginx plugin
        agree = config.get("agree_tos", True)

        if install:
            executor.run(
                host,
                "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq certbot python3-certbot-nginx || "
                "dnf install -y certbot python3-certbot-nginx || true",
                sudo=True,
                check=False,
            )

        if not domains:
            return True

        domain_args = " ".join(f"-d {d}" for d in domains)
        tos = "--agree-tos" if agree else ""
        plugin = "--nginx" if nginx else "--standalone"

        cmd = (
            f"certbot certonly {plugin} {tos} --non-interactive "
            f"--email {email} {domain_args} --redirect || "
            f"certbot --nginx {tos} --non-interactive --email {email} {domain_args}"
        )
        executor.run(host, cmd, sudo=True, check=False)

        # Enable renew timer if available
        executor.run(
            host,
            "systemctl enable --now certbot.timer 2>/dev/null || true",
            sudo=True,
            check=False,
        )
        return True
