"""Clone git repos for deploy."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class GitDeployModule(BaseModule):
    name = "git-deploy"
    description = "Clone or pull git repositories to deploy paths"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        repos: List[dict] = config.get("repos", [])
        executor.run(host, "command -v git >/dev/null || apt-get install -y -qq git", sudo=True, check=False)
        for r in repos:
            url = r.get("url")
            path = r.get("path")
            branch = r.get("branch", "main")
            if not url or not path:
                continue
            executor.run(
                host,
                f"if [ -d {path}/.git ]; then git -C {path} fetch && git -C {path} checkout {branch} && git -C {path} pull; "
                f"else mkdir -p $(dirname {path}) && git clone -b {branch} {url} {path}; fi",
                sudo=True,
                check=False,
            )
        return True
