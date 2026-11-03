"""Readiness checks only the applicable locked release closure, failing closed."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.test_support import ENV, metadata, package
from tools.release_workflow.markers import evaluate, satisfies
from tools.release_workflow.readiness import validate

if TYPE_CHECKING:
    from pathlib import Path


def test_empty_uv_shapes(tmp_path: Path) -> None:
    """Both uv empty-group shapes mean no installed package lookups."""
    metadata(tmp_path)
    installed: dict[str, str] = {}
    for table in ("", "[package.dev-dependencies]\ndev = []\n"):
        lock = tmp_path / "uv.lock"
        text = lock.read_text(encoding="utf-8")
        lock.write_text(text.replace("[package.metadata", table + "[package.metadata"), encoding="utf-8")
        assert validate(tmp_path, ENV, installed.__getitem__, evaluate, satisfies) == ()


def test_transitive_cycle_and_dev_isolation(tmp_path: Path) -> None:
    """Cycles visit packages once; inactive dependencies and dev are excluded."""
    packages = package("alpha", edges='{name="beta"}, {name="absent", marker="os_name != \'nt\'"}')
    packages += package("beta", edges='{name="alpha"}') + package("dev-only")
    metadata(tmp_path, packages, '{name="alpha"}')
    visits: list[str] = []

    def installed(name: str) -> str:
        visits.append(name)
        return "1.0"

    assert validate(tmp_path, ENV, installed, evaluate, satisfies) == ("alpha", "beta")
    assert visits == ["alpha", "beta"]


@pytest.mark.parametrize("mutation", [
    ("version = 1", "version = 2"),
    ('release = ["alpha"]', 'other = ["alpha"]'),
    ('{name="alpha"}', '{name="missing"}'),
    ('{name="alpha"}', '{name="alpha", extra=["feature"]}'),
    ('{name="alpha"}', '{name="alpha", marker="extra == \'x\'"}'),
])
def test_invalid_lock_fails(tmp_path: Path, mutation: tuple[str, str]) -> None:
    """Malformed or unsupported graph metadata cannot pass readiness."""
    metadata(tmp_path, package("alpha"), '{name="alpha"}')
    lock = tmp_path / "uv.lock"
    lock.write_text(lock.read_text().replace(*mutation), encoding="utf-8")
    with pytest.raises(ValueError, match=r"release|lock|dependency|marker"):
        validate(tmp_path, ENV, {"alpha": "1.0"}.__getitem__, evaluate, satisfies)


def test_duplicate_resolution_and_registry_rewrite(tmp_path: Path) -> None:
    """Explicit versions disambiguate; registry location changes no identity."""
    packages = package("alpha") + package("alpha", version="2.0")
    metadata(tmp_path, packages, '{name="alpha", version="2.0", source={registry="https://mirror.example/simple"}}')
    assert validate(tmp_path, ENV, {"alpha": "2.0"}.__getitem__, evaluate, satisfies) == ("alpha",)
    metadata(tmp_path, packages, '{name="alpha"}')
    with pytest.raises(ValueError, match="ambiguous"):
        validate(tmp_path, ENV, {"alpha": "2.0"}.__getitem__, evaluate, satisfies)


# eof
