"""Security audit snapshot."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from putty_es.modules.base import BaseModule
if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

class AuditModule(BaseModule):
    name = "audit"
    description = "Collect a security/health audit report on the host"

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        out = config.get("output", "/var/log/putty-es-audit.txt")
        script = f"""
echo "=== Putty-ES Audit $(date) ===" > {out}
echo "Hostname: $(hostname)" >> {out}
echo "Uptime: $(uptime)" >> {out}
echo "--- Listening ports ---" >> {out}
ss -tulpn 2>/dev/null >> {out} || netstat -tulpn >> {out} 2>/dev/null
echo "--- Failed SSH (last) ---" >> {out}
grep -i "failed password" /var/log/auth.log 2>/dev/null | tail -20 >> {out} || true
echo "--- Disk ---" >> {out}
df -h >> {out}
echo "--- Memory ---" >> {out}
free -h >> {out}
echo "--- Putty-Fire ---" >> {out}
cat /etc/putty-fire/STATUS 2>/dev/null >> {out} || echo "not active" >> {out}
echo "Audit written to {out}"
"""
        executor.run(host, script, sudo=True, check=False)
        return True
