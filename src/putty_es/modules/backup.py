"""Backup module – scheduled and one-shot backups."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class BackupModule(BaseModule):
    name = "backup"
    description = "Create directory/file backups and optional cron schedules"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        targets: List[str] = config.get("paths", ["/etc", "/var/www"])
        dest = config.get("destination", "/var/backups/putty-es")
        keep = int(config.get("keep", 7))
        schedule = config.get("schedule")  # e.g. "0 3 * * *"
        executor.run(host, f"mkdir -p {dest}", sudo=True, check=False)
        stamp = "$(date +%Y%m%d-%H%M%S)"
        for p in targets:
            name = p.strip("/").replace("/", "_") or "root"
            archive = f"{dest}/{name}-{stamp}.tar.gz"
            executor.run(
                host,
                f"tar -czf {archive} -C / {p.lstrip('/')} 2>/dev/null || true",
                sudo=True,
                check=False,
            )
        # prune old
        executor.run(
            host,
            f"ls -1t {dest}/*.tar.gz 2>/dev/null | tail -n +{keep + 1} | xargs -r rm -f",
            sudo=True,
            check=False,
        )
        if schedule:
            cmd = f"tar -czf {dest}/auto-$(date +\\%Y\\%m\\%d).tar.gz {' '.join(targets)} 2>/dev/null"
            executor.run(
                host,
                f"(crontab -l 2>/dev/null | grep -v putty-es-backup; echo '{schedule} {cmd} # putty-es-backup') | crontab -",
                sudo=True,
                check=False,
            )
        return True
