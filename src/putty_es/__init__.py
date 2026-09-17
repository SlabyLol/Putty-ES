"""
Putty-ES – Elite Server Setup & Management Framework

Intelligent modular open-source tool for automated server provisioning,
configuration management, and the powerful ppiRuler
(Python Package Implementor Ruler).
"""

__version__ = "0.2.0"
__author__ = "DarkFox Co. / SlabyLol"
__license__ = "MIT"

from putty_es.core.config import Config, load_config
from putty_es.core.executor import Executor
from putty_es.modules.base import BaseModule

__all__ = [
    "__version__",
    "Config",
    "load_config",
    "Executor",
    "BaseModule",
]
