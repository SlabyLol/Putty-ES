"""Tests for configuration loading."""

from pathlib import Path

import pytest

from putty_es.core.config import load_config, Config, Host


def test_load_minimal_yaml(tmp_path: Path) -> None:
    cfg = tmp_path / "test.yaml"
    cfg.write_text(
        """
name: test-fleet
hosts:
  - name: h1
    hostname: 1.2.3.4
modules:
  - name: packages
    packages: [curl]
""",
        encoding="utf-8",
    )
    config = load_config(cfg)
    assert config.name == "test-fleet"
    assert len(config.hosts) == 1
    assert config.hosts[0].hostname == "1.2.3.4"
    assert len(config.modules) == 1
    assert config.modules[0].name == "packages"


def test_host_defaults() -> None:
    h = Host(name="x", hostname="example.com")
    assert h.user == "root"
    assert h.port == 22
    assert h.key is None
