"""
User & group management module.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class UsersModule(BaseModule):
    name = "users"
    description = "Create / manage system users, groups and SSH keys"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        users: List[dict] = config.get("users", [])
        groups: List[str] = config.get("groups", [])

        for g in groups:
            executor.run(host, f"groupadd -f {g}", sudo=True, check=False)

        for u in users:
            name = u.get("name")
            if not name:
                continue
            shell = u.get("shell", "/bin/bash")
            home = u.get("home", f"/home/{name}")
            groups_list = u.get("groups", [])
            password = u.get("password")  # optional, prefer keys
            keys: List[str] = u.get("ssh_keys", [])
            sudo = u.get("sudo", False)

            # Create user if not exists
            executor.run(
                host,
                f"id {name} >/dev/null 2>&1 || useradd -m -s {shell} -d {home} {name}",
                sudo=True,
                check=False,
            )

            for g in groups_list:
                executor.run(host, f"usermod -aG {g} {name}", sudo=True, check=False)

            if sudo:
                executor.run(
                    host,
                    f"echo '{name} ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/{name} && chmod 440 /etc/sudoers.d/{name}",
                    sudo=True,
                    check=False,
                )

            if password:
                # Use chpasswd carefully
                executor.run(
                    host,
                    f"echo '{name}:{password}' | chpasswd",
                    sudo=True,
                    check=False,
                )

            if keys:
                ssh_dir = f"{home}/.ssh"
                executor.run(host, f"mkdir -p {ssh_dir} && chmod 700 {ssh_dir}", sudo=True, check=False)
                for key in keys:
                    executor.run(
                        host,
                        f"grep -qF '{key}' {ssh_dir}/authorized_keys 2>/dev/null || echo '{key}' >> {ssh_dir}/authorized_keys",
                        sudo=True,
                        check=False,
                    )
                executor.run(
                    host,
                    f"chmod 600 {ssh_dir}/authorized_keys && chown -R {name}:{name} {ssh_dir}",
                    sudo=True,
                    check=False,
                )

        return True
