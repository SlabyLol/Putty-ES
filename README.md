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

**Putty-ES** is a modern, intelligent, modular open-source framework for automated server provisioning, configuration management, and remote administration. Designed to be one of the most powerful and elegant tools in its class.

## Features

- **Smart Modular Architecture** – Plugin-based modules that can be extended infinitely
- **Configuration-Driven** – Define entire server fleets with YAML or TOML
- **PyPI Native** – First-class support for installing and managing Python packages on remote servers
- **Beautiful CLI** – Rich terminal UI with banners, progress bars, and colored output
- **SSH-First** – Secure remote execution powered by modern SSH libraries
- **Idempotent Operations** – Safe to run multiple times
- **Extensible** – Write your own modules in minutes
- **Production Ready** – Logging, dry-run mode, validation, and error handling

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

## Quick Start

```bash
# Show the banner and help
putty-es --help

# Initialize a new configuration
putty-es init

# Apply a configuration to a server
putty-es apply configs/webserver.yaml

# Run a specific module
putty-es module packages --host 192.168.1.10 --install nginx python3

# Interactive mode
putty-es shell --host example.com
```

## Configuration Example

```yaml
# configs/webserver.yaml
name: production-web
hosts:
  - hostname: web-01.example.com
    user: deploy
    port: 22
    key: ~/.ssh/id_ed25519

modules:
  - name: packages
    packages:
      - nginx
      - python3-pip
      - certbot
  - name: docker
    images:
      - nginx:latest
  - name: firewall
    allow:
      - 80/tcp
      - 443/tcp
  - name: pypi
    packages:
      - fastapi
      - uvicorn
      - gunicorn
```

## Architecture

```
putty_es/
├── cli.py              # Main CLI entrypoint with banner
├── core/
│   ├── config.py       # Configuration loading & validation
│   ├── executor.py     # Remote execution engine
│   ├── module_loader.py# Smart module discovery & loading
│   └── logging.py      # Structured logging
├── modules/
│   ├── base.py         # Abstract base module
│   ├── packages.py     # System package management
│   ├── pypi.py         # Python package (PyPI) management
│   ├── docker.py       # Docker & container management
│   ├── firewall.py     # Firewall (ufw/firewalld)
│   ├── ssh.py          # SSH hardening & key management
│   └── system.py       # Users, services, sysctl, etc.
└── configs/            # Example configurations
```

## Creating Custom Modules

```python
from putty_es.modules.base import BaseModule

class MySmartModule(BaseModule):
    name = "my-module"
    description = "Does something very smart"

    def apply(self, host, config):
        # Your logic here
        self.run(host, "echo 'Hello from Putty-ES'")
        return True
```

Place it in `~/.putty-es/modules/` or contribute upstream.

## License

MIT License – free for personal and commercial use.

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

**Putty-ES** – Because server setup should be elegant, intelligent, and enjoyable.
