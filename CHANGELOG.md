# Changelog

## [0.3.1] – 2026-09-18

### Added – Putty-Fire
- Full **putty-fire** module: firewall, SSH harden, fail2ban, sysctl, status banner
- CLI: `putty-es fire activate` / `putty-es fire status`
- On activation: **Protected by Putty-Fire** (MOTD, `/etc/putty-fire/STATUS`, `putty-fire-status`)

### Added – Many modules
backup, swap, timezone, motd, logrotate, systemd, nodejs, redis, postgres, mysql,
ufw-profiles, audit, wireguard, fail2ban-extra, unattended-upgrades, hostname,
caddy, git-deploy, python-env, healthcheck, cleanup, sshd-banner, docker-compose,
limits, kernel-modules, ssh-keys-sync, report, and more

### Fixed
- GitHub Release uploads split (wheels first, binaries second) to reduce Unicorn timeouts
- PyPI Trusted Publishing job retained

## [0.3.0] – 2026-09-17
- GUI + animated splash, ppiRuler, initial release pipeline

## [0.2.0] – 2026-09-17
- ppiRuler core

## [0.1.0] – 2026-09-17
- Initial core modules
