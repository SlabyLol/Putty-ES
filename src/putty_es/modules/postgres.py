"""PostgreSQL basic setup."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class PostgresModule(BaseModule):
    name = "postgres"
    description = "Install PostgreSQL and create databases/users"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        executor.run(
            host,
            "apt-get install -y -qq postgresql postgresql-contrib || dnf install -y postgresql-server || true",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            "systemctl enable --now postgresql 2>/dev/null || true",
            sudo=True,
            check=False,
        )
        databases: List[dict] = config.get("databases", [])
        for db in databases:
            name = db.get("name")
            user = db.get("user", name)
            password = db.get("password", "changeme")
            if not name:
                continue
            executor.run(
                host,
                f"sudo -u postgres psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='{user}'\" | grep -q 1 || "
                f"sudo -u postgres psql -c \"CREATE USER {user} WITH PASSWORD '{password}';\"",
                sudo=True,
                check=False,
            )
            executor.run(
                host,
                f"sudo -u postgres psql -tc \"SELECT 1 FROM pg_database WHERE datname='{name}'\" | grep -q 1 || "
                f"sudo -u postgres psql -c \"CREATE DATABASE {name} OWNER {user};\"",
                sudo=True,
                check=False,
            )
        return True
