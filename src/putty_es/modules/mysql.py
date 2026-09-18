"""MySQL/MariaDB setup."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class MysqlModule(BaseModule):
    name = "mysql"
    description = "Install MariaDB/MySQL and create databases"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        root_pass = config.get("root_password", "")
        executor.run(
            host,
            "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq mariadb-server || "
            "dnf install -y mariadb-server || true",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            "systemctl enable --now mariadb 2>/dev/null || systemctl enable --now mysql || true",
            sudo=True,
            check=False,
        )
        for db in config.get("databases", []):
            name = db.get("name")
            user = db.get("user", name)
            password = db.get("password", "changeme")
            if not name:
                continue
            executor.run(
                host,
                f"mysql -e \"CREATE DATABASE IF NOT EXISTS `{name}`; "
                f"CREATE USER IF NOT EXISTS '{user}'@'localhost' IDENTIFIED BY '{password}'; "
                f"GRANT ALL ON `{name}`.* TO '{user}'@'localhost'; FLUSH PRIVILEGES;\" 2>/dev/null || true",
                sudo=True,
                check=False,
            )
        return True
