"""Python venv + requirements on remote."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class PythonEnvModule(BaseModule):
    name = "python-env"
    description = "Create Python virtualenv and install requirements"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        path = config.get("path", "/opt/app/venv")
        requirements = config.get("requirements", [])
        req_file = config.get("requirements_file")
        executor.run(
            host,
            "apt-get install -y -qq python3-venv python3-pip || true",
            sudo=True,
            check=False,
        )
        executor.run(host, f"python3 -m venv {path}", sudo=True, check=False)
        if req_file:
            executor.run(host, f"{path}/bin/pip install -r {req_file}", sudo=True, check=False)
        for p in requirements:
            executor.run(host, f"{path}/bin/pip install {p}", sudo=True, check=False)
        return True
