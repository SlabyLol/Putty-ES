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

**Putty-ES** is a modern, intelligent, modular open-source framework for automated server provisioning, configuration management, remote administration **and** the powerful **ppiRuler** (Python Package Implementor Ruler).

## Features

### Core Server Management
- **Smart Modular Architecture** – Plugin-based modules that can be extended infinitely
- **Configuration-Driven** – Define entire server fleets with YAML or TOML
- **PyPI Native** – First-class support for installing Python packages on remote servers
- **Beautiful CLI** – Rich terminal UI with banners, progress bars and colored output
- **SSH-First** – Secure remote execution
- **Idempotent Operations** – Safe to run multiple times

### ppiRuler – Python Package Implementor Ruler
- Download **any** package from PyPI
- Transform it into a **completely offline** distribution
- Generate clean artifacts:
  - Windows EXE / portable launcher (PyInstaller)
  - Linux binary / shell launcher
  - HTML status & documentation page (with animation)
  - INI configuration files
  - DLL notes / stubs
  - `manifest.json`
- Beautiful animated startup sequence
- Clean installer-style progress
- Auto-release pipeline with GitHub Actions + PyInstaller

## Installation

```bash
pip install putty-es
```

Or from source:

```bash
git clone https://github.com/SlabyLol/Putty-ES.git
cd Putty-ES
pip install -e .
```

## Quick Start – Server Management

```bash
putty-es --help
putty-es init
putty-es apply configs/example-webserver.yaml
putty-es modules
```

## Quick Start – ppiRuler

```bash
# Build an offline package of "requests"
putty-es ppi build requests

# Specific version + selected targets
putty-es ppi build rich --version 13.7.1 -t exe -t html -t ini -o ./offline-rich

# Show info
putty-es ppi info
```

After running, you will find a clean folder structure:

```
ppi_output/
├── windows/          # .bat launcher or .exe + package/
├── linux/            # shell launcher + package/
├── html/             # beautiful index.html status page
├── config/           # .ini files
└── manifest.json
```

Everything is self-contained – no network calls to PyPI at runtime.

## Architecture

```
putty_es/
├── cli.py                 # Main CLI + ppi commands
├── core/                  # Config, Executor, Module loader
├── modules/               # Smart server modules
│   ├── packages.py
│   ├── pypi.py
│   ├── docker.py
│   ├── firewall.py
│   ├── system.py
│   └── ssh.py
└── ppi_ruler/             # Python Package Implementor Ruler
    ├── core.py            # Main engine
    ├── builder.py         # Multi-target builder
    └── animator.py        # Clean animations
```

## Creating Custom Modules

```python
from putty_es.modules.base import BaseModule

class MySmartModule(BaseModule):
    name = "my-module"
    description = "Does something very smart"

    def apply(self, host, config, executor):
        executor.run(host, "echo 'Hello from Putty-ES'")
        return True
```

## Auto Release (GitHub Actions)

Tag a version and the workflow automatically:

1. Builds wheels & sdists
2. Creates standalone executables with **PyInstaller** on Linux, Windows and macOS
3. Uploads everything as a GitHub Release

```bash
git tag v0.1.0
git push origin v0.1.0
```

## License

MIT License – free for personal and commercial use.

---

**Putty-ES** + **ppiRuler** – Because server setup and package distribution should be elegant, intelligent and completely offline-ready.
