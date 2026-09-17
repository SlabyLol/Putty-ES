"""
Cron job management module.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class CronModule(BaseModule):
    name = "cron"
    description = "Manage cron jobs for users"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        jobs: List[dict] = config.get("jobs", [])

        for job in jobs:
            user = job.get("user", "root")
            schedule = job.get("schedule")  # e.g. "0 2 * * *"
            command = job.get("command")
            name = job.get("name", "putty-es-job")

            if not schedule or not command:
                continue

            # Add job with a marker comment so it is idempotent
            marker = f"# putty-es:{name}"
            line = f"{schedule} {command} {marker}"

            # Remove old entry with same marker, then add
            executor.run(
                host,
                f"(crontab -u {user} -l 2>/dev/null | grep -v '{marker}'; echo '{line}') | crontab -u {user} -",
                sudo=True,
                check=False,
            )

        return True
