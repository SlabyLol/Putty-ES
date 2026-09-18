"""HTTP health checks from the control machine via remote curl."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class HealthcheckModule(BaseModule):
    name = "healthcheck"
    description = "Run HTTP/TCP health checks on the host"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        urls: List[str] = config.get("urls", [])
        ports: List[int] = config.get("ports", [])
        for u in urls:
            code, out, _ = executor.run(
                host,
                f"curl -sS -o /dev/null -w '%{{http_code}}' --max-time 10 '{u}' || echo fail",
                check=False,
            )
            # non-fatal
        for p in ports:
            executor.run(
                host,
                f"(echo >/dev/tcp/127.0.0.1/{p}) >/dev/null 2>&1 && echo port_{p}_ok || echo port_{p}_down",
                check=False,
            )
        return True
