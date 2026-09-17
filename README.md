# Putty-ES

```
██████╗ ██╗   ██╗████████╗████████╗██╗   ██╗      ███████╗███████╗
██╔══██╗██║   ██║╚══██╔══╝╚══██╔══╝╚██╗ ██╔╝      ██╔════╝██╔════╝
██████╔╝██║   ██║   ██║      ██║    ╚████╔╝ █████╗█████╗  ███████╗
██╔═══╝ ██║   ██║   ██║      ██║     ╚██╔╝  ╚════╝██╔══╝  ╚════██║
██║     ╚██████╔╝   ██║      ██║      ██║         ███████╗███████║
╚═╝      ╚═════╝    ╚═╝      ╚═╝      ╚═╝         ╚══════╝╚══════╝
                    Elite Server Setup & Management
```

**Putty-ES** is a modern open-source framework for automated server provisioning, configuration management, offline PyPI packaging (**ppiRuler**) and a polished **GUI with animated startup**.

[![Release](https://img.shields.io/github/v/release/SlabyLol/Putty-ES)](https://github.com/SlabyLol/Putty-ES/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Features

### Server Management
- Configuration-driven (YAML / TOML)
- Smart modules (12+ built-in)
- SSH-first, idempotent operations
- Beautiful Rich CLI

### ppiRuler
- Download any PyPI package
- Build offline artifacts: Windows EXE, Linux binary, HTML, INI, DLL notes
- No runtime network calls to package servers

### GUI
- Animated splash screen on every start
- Dark modern UI (CustomTkinter)
- Tabs: Server Management · ppiRuler · About

### Release pipeline
- GitHub Actions builds Linux / Windows / macOS binaries with PyInstaller
- Wheels + sdists
- Automatic GitHub Releases on tags **and** manual `workflow_dispatch`

## Installation

```bash
pip install putty-es
```

From source:

```bash
git clone https://github.com/SlabyLol/Putty-ES.git
cd Putty-ES
pip install -e ".[full]"
# or
bash scripts/install.sh
```

Windows:

```powershell
.\scripts\install.ps1
```

## Quick Start

```bash
# GUI (animated startup)
putty-es --gui
putty-es gui
putty-es-gui

# CLI
putty-es init
putty-es apply configs/example-webserver.yaml
putty-es modules

# ppiRuler – offline package
putty-es ppi build requests
putty-es ppi build rich -t exe -t html -t ini -o ./offline-rich
```

## Smart Modules

| Module | Purpose |
|--------|---------|
| `packages` | apt / dnf / yum / apk / pacman |
| `pypi` | Python packages on remote hosts |
| `docker` | Docker Engine + images + containers |
| `firewall` | ufw / firewalld |
| `system` | hostname, timezone, services, sysctl |
| `ssh` | keys + hardening |
| `nginx` | sites & reverse proxies |
| `users` | users, groups, sudo, SSH keys |
| `files` | directories & file content |
| `cron` | idempotent cron jobs |
| `certbot` | Let's Encrypt SSL |
| `monitoring` | tools + health script |

See [docs/MODULES.md](docs/MODULES.md).

## Example Configs

- `configs/example-minimal.yaml`
- `configs/example-webserver.yaml`
- `configs/example-full-stack.yaml`
- `configs/example-database.yaml`
- `configs/example-docker-host.yaml`

## Create a Release

### Option A – Tag (recommended)

```bash
git tag v0.3.0
git push origin v0.3.0
```

### Option B – Manual workflow

1. Go to **Actions → Build & Release Putty-ES**
2. Click **Run workflow**
3. Optionally enter a version (e.g. `v0.3.0`)
4. The release job now runs on both tags **and** `workflow_dispatch` (no longer skipped)

Artifacts published:
- `putty-es-linux-x64`
- `putty-es-windows-x64.exe`
- `putty-es-macos-x64`
- GUI binaries (when available)
- Python wheel + sdist

## Project layout

```
Putty-ES/
├── .github/workflows/
│   ├── release.yml      # multi-OS build + GitHub Release
│   └── ci.yml
├── configs/             # example fleets
├── docs/                # MODULES, PPIRULER, GUI
├── scripts/             # install.sh, install.ps1, build_local.sh
├── src/putty_es/
│   ├── cli.py
│   ├── core/
│   ├── modules/         # 12 smart modules
│   ├── ppi_ruler/
│   └── gui/             # splash + main window
├── tests/
├── CHANGELOG.md
├── LICENSE
└── pyproject.toml
```

## License

MIT – free for personal and commercial use.

---

**Putty-ES** – servers, offline packages, GUI and real releases.
