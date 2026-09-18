"""Caddy web server."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
import base64
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class CaddyModule(BaseModule):
    name = "caddy"
    description = "Install Caddy and write a simple Caddyfile"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        domain = config.get("domain", ":80")
        root = config.get("root", "/var/www/html")
        reverse = config.get("reverse_proxy")
        executor.run(
            host,
            "command -v caddy >/dev/null || ("
            "apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https; "
            "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg; "
            "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list; "
            "apt-get update -qq && apt-get install -y -qq caddy) || true",
            sudo=True,
            check=False,
        )
        if reverse:
            body = f"{domain} {{\n    reverse_proxy {reverse}\n}}\n"
        else:
            body = f"{domain} {{\n    root * {root}\n    file_server\n}}\n"
        b64 = base64.b64encode(body.encode()).decode()
        executor.run(
            host,
            f"echo '{b64}' | base64 -d > /etc/caddy/Caddyfile && systemctl enable --now caddy && systemctl reload caddy",
            sudo=True,
            check=False,
        )
        return True
