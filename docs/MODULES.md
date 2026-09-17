# Putty-ES Smart Modules

| Module        | Description                                              |
|---------------|----------------------------------------------------------|
| `packages`    | Install/remove system packages (apt, dnf, yum, apk, pacman) |
| `pypi`        | Install Python packages from PyPI on remote hosts        |
| `docker`      | Install Docker Engine, pull images, run containers       |
| `firewall`    | Configure ufw / firewalld / basic iptables               |
| `system`      | Hostname, timezone, services, sysctl                     |
| `ssh`         | Deploy authorized keys + optional hardening              |
| `nginx`       | Install Nginx, create sites / reverse proxies            |
| `users`       | Create users, groups, sudo, SSH keys                     |
| `files`       | Create directories & files with content/permissions     |
| `cron`        | Manage cron jobs idempotently                            |
| `certbot`     | Let's Encrypt certificates via Certbot                   |
| `monitoring`  | Install monitoring tools + health-check script           |

## Custom modules

Place a Python file in `~/.putty-es/modules/` that subclasses `BaseModule`.

```python
from putty_es.modules.base import BaseModule

class HelloModule(BaseModule):
    name = "hello"
    description = "Says hello"

    def apply(self, host, config, executor):
        executor.run(host, "echo Hello from Putty-ES")
        return True
```
