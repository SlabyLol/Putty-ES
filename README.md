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

**Putty-ES** is a modern, intelligent, modular open-source framework for automated server provisioning, configuration management, remote administration, **ppiRuler** and a beautiful **GUI with animated startup**.

## Features

### Core Server Management
- Smart modular architecture (plugin-based)
- Configuration-driven (YAML / TOML)
- Native PyPI support on remote servers
- Beautiful CLI with banners & colors
- SSH-first, idempotent operations

### ppiRuler – Python Package Implementor Ruler
- Download any package from PyPI
- Transform into completely offline distribution
- Windows EXE / launcher, Linux binary, HTML page, INI configs, DLL notes
- Animated terminal startup sequence

### Modern GUI
- **Animated splash screen** on every program start
- Dark professional theme (CustomTkinter)
- Tabs for Server Management + ppiRuler + About
- One-click offline package building
- Live log output

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

## Launch the GUI (with animated startup)

```bash
putty-es --gui
# or
putty-es gui
# or
putty-es-gui
```

When you start the program a clean animated splash screen appears, then the main window opens.

## CLI Quick Start

```bash
putty-es --help
putty-es init
putty-es apply configs/example-webserver.yaml
putty-es ppi build requests
putty-es modules
```

## ppiRuler Examples

```bash
putty-es ppi build requests
putty-es ppi build rich --version 13.7.1 -t exe -t html -t ini -o ./offline-rich
putty-es ppi info
```

## Architecture

```
putty_es/
├── cli.py                 # CLI + --gui flag
├── core/                  # Config, Executor, Module loader
├── modules/               # Smart server modules
├── ppi_ruler/             # Offline package engine
│   ├── core.py
│   ├── builder.py
│   └── animator.py        # Terminal animations
└── gui/                   # Graphical interface
    ├── splash.py          # Animated startup splash
    └── app.py             # Main window (tabs)
```

## Auto Release

Tag a version → GitHub Actions builds wheels, sdists and PyInstaller executables for Linux / Windows / macOS and creates a Release.

```bash
git tag v0.3.0
git push origin v0.3.0
```

## License

MIT License – free for personal and commercial use.

---

**Putty-ES** – Server setup, offline packages and a polished GUI with real startup animation.
