"""Swap file management."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class SwapModule(BaseModule):
    name = "swap"
    description = "Create and enable a swap file"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        size = config.get("size", "2G")  # fallocate style
        path = config.get("path", "/swapfile")
        swappiness = config.get("swappiness", 10)
        executor.run(
            host,
            f"test -f {path} || (fallocate -l {size} {path} || dd if=/dev/zero of={path} bs=1M count=2048); "
            f"chmod 600 {path} && mkswap {path} && swapon {path} || true",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            f"grep -q '{path}' /etc/fstab || echo '{path} none swap sw 0 0' >> /etc/fstab",
            sudo=True,
            check=False,
        )
        executor.run(host, f"sysctl -w vm.swappiness={swappiness}", sudo=True, check=False)
        return True
