"""Node.js / npm install."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class NodejsModule(BaseModule):
    name = "nodejs"
    description = "Install Node.js (NodeSource or distro) and global npm packages"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        version = config.get("version", "20")
        packages: List[str] = config.get("global_packages", [])
        executor.run(
            host,
            f"command -v node >/dev/null || ("
            f"curl -fsSL https://deb.nodesource.com/setup_{version}.x | bash - && "
            f"apt-get install -y -qq nodejs) || apt-get install -y -qq nodejs npm || true",
            sudo=True,
            check=False,
        )
        for p in packages:
            executor.run(host, f"npm install -g {p}", sudo=True, check=False)
        return True
