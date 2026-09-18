"""Docker Compose project deploy."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
import base64
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class DockerComposeModule(BaseModule):
    name = "docker-compose"
    description = "Write docker-compose.yml and up -d"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        path = config.get("path", "/opt/stack")
        compose = config.get("compose_yaml", "")
        if not compose:
            return True
        executor.run(host, f"mkdir -p {path}", sudo=True, check=False)
        b64 = base64.b64encode(compose.encode()).decode()
        executor.run(
            host,
            f"echo '{b64}' | base64 -d > {path}/docker-compose.yml",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            f"cd {path} && (docker compose up -d || docker-compose up -d)",
            sudo=True,
            check=False,
        )
        return True
