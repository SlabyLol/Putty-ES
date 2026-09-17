"""
ppiRuler – Python Package Implementor Ruler

Downloads any PyPI package, transforms it into clean standalone
executables and supporting files (INI, launchers, HTML, etc.)
so the package can run completely offline without fetching from servers.
"""

from putty_es.ppi_ruler.core import PPIRuler
from putty_es.ppi_ruler.builder import PackageBuilder

__all__ = ["PPIRuler", "PackageBuilder"]
