"""
File & directory management module (create, copy content, permissions).
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class FilesModule(BaseModule):
    name = "files"
    description = "Create directories, write files, set permissions and ownership"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        directories: List[dict] = config.get("directories", [])
        files: List[dict] = config.get("files", [])

        for d in directories:
            path = d.get("path")
            if not path:
                continue
            mode = d.get("mode", "755")
            owner = d.get("owner")
            group = d.get("group")

            executor.run(host, f"mkdir -p {path}", sudo=True, check=False)
            executor.run(host, f"chmod {mode} {path}", sudo=True, check=False)
            if owner:
                chown = f"{owner}:{group}" if group else owner
                executor.run(host, f"chown {chown} {path}", sudo=True, check=False)

        for f in files:
            path = f.get("path")
            content = f.get("content", "")
            mode = f.get("mode", "644")
            owner = f.get("owner")
            group = f.get("group")

            if not path:
                continue

            # Write content safely
            # Use base64 to avoid quoting hell for arbitrary content
            import base64

            b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
            executor.run(
                host,
                f"echo '{b64}' | base64 -d > {path}",
                sudo=True,
                check=False,
            )
            executor.run(host, f"chmod {mode} {path}", sudo=True, check=False)
            if owner:
                chown = f"{owner}:{group}" if group else owner
                executor.run(host, f"chown {chown} {path}", sudo=True, check=False)

        return True
