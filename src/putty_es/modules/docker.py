"""
Docker module – install Docker and manage containers/images.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class DockerModule(BaseModule):
    name = "docker"
    description = "Install Docker Engine and manage images / containers"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        install = config.get("install", True)
        images: List[str] = config.get("images", [])
        containers: List[dict] = config.get("containers", [])

        if install:
            # Quick official install script (works on most Linux distros)
            code, _, _ = executor.run(host, "command -v docker", check=False)
            if code != 0:
                executor.run(
                    host,
                    "curl -fsSL https://get.docker.com | sh",
                    sudo=True,
                )
                executor.run(host, "systemctl enable --now docker", sudo=True, check=False)

        for image in images:
            executor.run(host, f"docker pull {image}", sudo=True, check=False)

        for c in containers:
            name = c.get("name")
            image = c.get("image")
            ports = c.get("ports", [])
            env = c.get("env", {})
            restart = c.get("restart", "unless-stopped")

            if not name or not image:
                continue

            # Stop & remove if exists
            executor.run(host, f"docker rm -f {name}", sudo=True, check=False)

            port_args = " ".join(f"-p {p}" for p in ports)
            env_args = " ".join(f"-e {k}={v}" for k, v in env.items())

            cmd = f"docker run -d --name {name} --restart {restart} {port_args} {env_args} {image}"
            executor.run(host, cmd, sudo=True)

        return True
