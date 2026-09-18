# Putty-ES Smart Modules Catalog

## Core infrastructure
| Module | Description |
|--------|-------------|
| packages | apt/dnf/yum/apk/pacman |
| pypi | pip packages on remote |
| docker | Engine, images, containers |
| docker-compose | compose up -d |
| firewall | ufw/firewalld |
| ufw-profiles | Named profiles: web, db, mail, vpn, locked |
| system | hostname, timezone, services, sysctl |
| hostname | Clean hostname set |
| timezone | Timezone + NTP |
| swap | Swap file |
| users | Users, groups, sudo, keys |
| ssh | Keys + hardening |
| ssh-keys-sync | Sync many public keys |
| sshd-banner | SSH legal banner |
| files | Dirs/files content + perms |
| cron | Cron jobs |
| systemd | Custom service units |
| limits | nofile/nproc limits |
| kernel-modules | Load/blacklist modules |
| unattended-upgrades | Auto security updates |
| cleanup | Disk/cache cleanup |
| logrotate | Log rotation rules |
| motd | Login message |
| backup | Tar backups + schedule |
| audit | Security audit report |
| report | Inventory report |
| healthcheck | HTTP/TCP checks |
| monitoring | Tools + health script |
| certbot | Let's Encrypt |
| nginx | Sites / reverse proxy |
| caddy | Caddy server |
| wireguard | VPN tools + forwarding |
| redis | Redis server |
| postgres | PostgreSQL DBs |
| mysql | MariaDB/MySQL |
| nodejs | Node + global npm |
| python-env | venv + requirements |
| git-deploy | Clone/pull repos |
| fail2ban-extra | Extra jails |
| **putty-fire** | **Full protection – Protected by Putty-Fire** |

## Putty-Fire
See [PUTTY_FIRE.md](PUTTY_FIRE.md).
