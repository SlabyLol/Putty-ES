"""
Smart module discovery and loading system.
Supports built-in modules and user-provided plugins.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Optional, Type

from putty_es.modules.base import BaseModule

_MODULE_CACHE: Dict[str, Type[BaseModule]] = {}


def _load_builtin_modules() -> None:
    """Discover and register all built-in modules."""
    import putty_es.modules as modules_pkg

    package_path = Path(modules_pkg.__file__).parent
    for finder, name, ispkg in pkgutil.iter_modules([str(package_path)]):
        if name.startswith("_") or name == "base":
            continue
        try:
            mod = importlib.import_module(f"putty_es.modules.{name}")
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseModule)
                    and attr is not BaseModule
                    and hasattr(attr, "name")
                ):
                    _MODULE_CACHE[attr.name] = attr
        except Exception:
            # Skip broken modules gracefully
            pass


def _load_user_modules() -> None:
    """Load modules from ~/.putty-es/modules/"""
    user_dir = Path.home() / ".putty-es" / "modules"
    if not user_dir.exists():
        return

    import sys

    sys.path.insert(0, str(user_dir))
    for path in user_dir.glob("*.py"):
        if path.name.startswith("_"):
            continue
        try:
            mod_name = path.stem
            mod = importlib.import_module(mod_name)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseModule)
                    and attr is not BaseModule
                    and hasattr(attr, "name")
                ):
                    _MODULE_CACHE[attr.name] = attr
        except Exception:
            pass


def discover_modules() -> Dict[str, Type[BaseModule]]:
    """Return a mapping of module name → class."""
    if not _MODULE_CACHE:
        _load_builtin_modules()
        _load_user_modules()
    return dict(_MODULE_CACHE)


def get_module(name: str) -> Optional[Type[BaseModule]]:
    """Get a module class by name."""
    modules = discover_modules()
    return modules.get(name)
