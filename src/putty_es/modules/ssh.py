"""
SSH hardening and key management module.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class SSHModule(BaseModule):
    name = "ssh"
    description = "SSH hardening, key deployment, and configuration"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        # Deploy authorized keys
        keys: List[str] = config.get("authorized_keys", [])
        if keys:
            # Ensure .ssh directory
            executor.run(host, "mkdir -p ~/.ssh && chmod 700 ~/.ssh", check=False)
            for key in keys:
                # Append if not present
                executor.run(
                    host,
                    f'grep -qF "{key}" ~/.ssh/authorized_keys 2>/dev/null || echo "{key}" >> ~/.ssh/authorized_keys',
                    check=False,
                )
            executor.run(host, "chmod 600 ~/.ssh/authorized_keys", check=False)

        # Hardening options
        harden = config.get("harden", False)
        if harden:
            # Disable password auth, root login, etc. (careful!)
            settings = {
                "PasswordAuthentication": "no",
                "PermitRootLogin": "prohibit-password",
                "PubkeyAuthentication": "yes",
                "X11Forwarding": "no",
            }
            for k, v in settings.items():
                executor.run(
                    host,
                    f"sed -i 's/^#*{k}.*/{k} {v}/' /etc/ssh/sshd_config",
                    sudo=True,
                    check=False,
                )
            executor.run(host, "systemctl reload sshd || systemctl reload ssh", sudo=True, check=False)

        return True
