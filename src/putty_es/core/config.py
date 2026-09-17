"""
Configuration loading and validation for Putty-ES.
Supports YAML and TOML formats with Pydantic models.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, field_validator

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


class Host(BaseModel):
    """Represents a single target host."""

    name: str = Field(..., description="Logical name of the host")
    hostname: str = Field(..., description="IP or DNS name")
    user: str = Field(default="root", description="SSH username")
    port: int = Field(default=22, ge=1, le=65535)
    key: Optional[str] = Field(default=None, description="Path to private key")
    password: Optional[str] = Field(default=None, description="Password (prefer keys)")
    tags: List[str] = Field(default_factory=list)

    @field_validator("key")
    @classmethod
    def expand_key_path(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return str(Path(v).expanduser())
        return v


class ModuleConfig(BaseModel):
    """Configuration for a single module invocation."""

    name: str
    # Extra fields are allowed and passed to the module
    model_config = {"extra": "allow"}


class Config(BaseModel):
    """Top-level Putty-ES configuration."""

    name: str = Field(default="unnamed-fleet")
    description: Optional[str] = None
    hosts: List[Host] = Field(default_factory=list)
    modules: List[ModuleConfig] = Field(default_factory=list)
    defaults: dict[str, Any] = Field(default_factory=dict)


def load_config(path: Union[str, Path]) -> Config:
    """Load and validate a configuration file (YAML or TOML)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    content = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(content) or {}
    elif suffix == ".toml":
        data = tomllib.loads(content)
    else:
        # Try YAML first, then TOML
        try:
            data = yaml.safe_load(content) or {}
        except Exception:
            data = tomllib.loads(content)

    return Config.model_validate(data)
