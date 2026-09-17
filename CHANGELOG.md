# Changelog

All notable changes to Putty-ES are documented in this file.

## [0.3.0] – 2026-09-17

### Added
- **Modern GUI** with CustomTkinter (dark theme)
- **Animated splash screen** on every GUI start
- **ppiRuler** – Python Package Implementor Ruler (offline package builder)
- New smart modules: `nginx`, `users`, `files`, `cron`, `certbot`, `monitoring`
- GitHub Actions release pipeline (Linux / Windows / macOS + PyInstaller)
- Multiple example configurations
- Tests, docs, installers, CONTRIBUTING improvements

### Changed
- Version bump to 0.3.0
- Improved CLI help and entry points (`putty-es`, `putty-es-gui`)

## [0.2.0] – 2026-09-17

### Added
- ppiRuler core engine, builder, animator
- CLI commands `putty-es ppi build` / `ppi info`

## [0.1.0] – 2026-09-17

### Added
- Initial release
- Core server management (config, executor, modules)
- Modules: packages, pypi, docker, firewall, system, ssh
- YAML/TOML configuration support
- Beautiful Rich CLI banner
