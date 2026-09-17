"""Tests for module discovery."""

from putty_es.core.module_loader import discover_modules, get_module


def test_discover_builtin_modules() -> None:
    mods = discover_modules()
    assert "packages" in mods
    assert "pypi" in mods
    assert "firewall" in mods
    assert "docker" in mods
    assert "system" in mods
    assert "ssh" in mods
    # newly added
    assert "nginx" in mods
    assert "users" in mods
    assert "files" in mods
    assert "cron" in mods
    assert "certbot" in mods
    assert "monitoring" in mods


def test_get_module() -> None:
    cls = get_module("packages")
    assert cls is not None
    assert cls.name == "packages"

    assert get_module("does-not-exist") is None
