"""
Nginx configuration & site management module.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class NginxModule(BaseModule):
    name = "nginx"
    description = "Install and configure Nginx sites / reverse proxies"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        install = config.get("install", True)
        sites: List[dict] = config.get("sites", [])
        remove_default = config.get("remove_default", True)

        if install:
            # Ensure nginx is installed via packages module logic or direct
            code, _, _ = executor.run(host, "command -v nginx", check=False)
            if code != 0:
                executor.run(
                    host,
                    "DEBIAN_FRONTEND=noninteractive apt-get update -qq && apt-get install -y -qq nginx || "
                    "dnf install -y nginx || yum install -y nginx",
                    sudo=True,
                    check=False,
                )

        if remove_default:
            executor.run(host, "rm -f /etc/nginx/sites-enabled/default", sudo=True, check=False)

        for site in sites:
            name = site.get("name", "default")
            server_name = site.get("server_name", "_")
            root = site.get("root", "/var/www/html")
            listen = site.get("listen", 80)
            proxy_pass = site.get("proxy_pass")  # e.g. http://127.0.0.1:8000
            ssl = site.get("ssl", False)

            conf_path = f"/etc/nginx/sites-available/{name}"
            enabled_path = f"/etc/nginx/sites-enabled/{name}"

            if proxy_pass:
                body = f"""
server {{
    listen {listen};
    server_name {server_name};

    location / {{
        proxy_pass {proxy_pass};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
""".strip()
            else:
                body = f"""
server {{
    listen {listen};
    server_name {server_name};
    root {root};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ =404;
    }}
}}
""".strip()

            # Write config via a here-doc over SSH
            escaped = body.replace("'", "'\\''")
            executor.run(
                host,
                f"bash -c 'cat > {conf_path} << '\''EOF'\''\n{body}\nEOF'",
                sudo=True,
                check=False,
            )
            executor.run(host, f"ln -sf {conf_path} {enabled_path}", sudo=True, check=False)

        executor.run(host, "nginx -t && systemctl reload nginx", sudo=True, check=False)
        executor.run(host, "systemctl enable --now nginx", sudo=True, check=False)
        return True
