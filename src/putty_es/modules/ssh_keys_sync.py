"""Sync multiple SSH public keys to a user."""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class SshKeysSyncModule(BaseModule):
    name = "ssh-keys-sync"
    description = "Ensure a list of public keys is present for a user"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        user = config.get("user", "root")
        keys: List[str] = config.get("keys", [])
        home = "/root" if user == "root" else f"/home/{user}"
        executor.run(
            host,
            f"mkdir -p {home}/.ssh && chmod 700 {home}/.ssh && touch {home}/.ssh/authorized_keys && chmod 600 {home}/.ssh/authorized_keys",
            sudo=True,
            check=False,
        )
        for k in keys:
            k = k.strip()
            if not k:
                continue
            executor.run(
                host,
                f"grep -qF '{k}' {home}/.ssh/authorized_keys || echo '{k}' >> {home}/.ssh/authorized_keys",
                sudo=True,
                check=False,
            )
        if user != "root":
            executor.run(host, f"chown -R {user}:{user} {home}/.ssh", sudo=True, check=False)
        return True
