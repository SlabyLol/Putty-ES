"""Basic tests for ppiRuler components."""

from putty_es.ppi_ruler.builder import PackageBuilder
from putty_es.ppi_ruler.core import PPIRuler


def test_ppi_ruler_init() -> None:
    ruler = PPIRuler(package="requests", output_dir="./tmp_ppi")
    assert ruler.package == "requests"
    assert "exe" in ruler.targets or "linux" in ruler.targets


def test_builder_init(tmp_path) -> None:
    b = PackageBuilder(
        package="demo",
        version="1.0.0",
        source_dir=tmp_path,
        output_dir=tmp_path / "out",
        meta={"name": "demo", "version": "1.0.0"},
    )
    assert b.package == "demo"
