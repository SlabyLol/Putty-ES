"""
Abstract base class for all Putty-ES smart modules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor


class BaseModule(ABC):
    """
    Base class for every Putty-ES module.

    Subclass this and implement `apply` to create a new smart module.
    """

    name: str = "base"
    description: str = "Base module – do not use directly"
    version: str = "1.0.0"

    @abstractmethod
    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        """
        Apply this module to the given host.

        Args:
            host: Target host information.
            config: Module-specific configuration dictionary.
            executor: Executor instance for running remote commands.

        Returns:
            True if successful, False otherwise.
        """
        ...

    def validate(self, config: dict[str, Any]) -> None:
        """Optional configuration validation. Raise ValueError on error."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
