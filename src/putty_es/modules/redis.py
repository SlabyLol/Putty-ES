"""Redis server setup."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class RedisModule(BaseModule):
    name = "redis"
    description = "Install and configure Redis server"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        bind = config.get("bind", "127.0.0.1")
        port = config.get("port", 6379)
        requirepass = config.get("password")
        executor.run(
            host,
            "apt-get install -y -qq redis-server || dnf install -y redis || true",
            sudo=True,
            check=False,
        )
        if requirepass:
            executor.run(
                host,
                f"sed -i 's/^#*requirepass.*/requirepass {requirepass}/' /etc/redis/redis.conf 2>/dev/null || "
                f"sed -i 's/^#*requirepass.*/requirepass {requirepass}/' /etc/redis.conf 2>/dev/null || true",
                sudo=True,
                check=False,
            )
        executor.run(
            host,
            f"sed -i 's/^bind .*/bind {bind}/' /etc/redis/redis.conf 2>/dev/null || true",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            "systemctl enable --now redis-server 2>/dev/null || systemctl enable --now redis || true",
            sudo=True,
            check=False,
        )
        return True
