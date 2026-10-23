"""Repository release metadata and one-read readiness remain explicit contracts."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from tests.unit.tools.release_workflow.test_support import ENV, metadata
from tools.release_workflow.markers import evaluate, satisfies
from tools.release_workflow.readiness import validate

if TYPE_CHECKING:
    from collections.abc import Iterator

    import pytest


def test_repository_release_declarations() -> None:
    """The stdlib-only release group is empty in both project and generated lock."""
    root = Path(__file__).resolve().parents[5]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    package = next(item for item in lock["package"] if item["source"] == {"virtual": "."})
    assert project["dependency-groups"]["release"] == package["metadata"]["requires-dev"]["release"] == []
    assert {"include-group": "release"} in project["dependency-groups"]["dev"]


def test_inputs_read_once_and_no_environment_scan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each readiness invocation reads each input once without enumerating venvs."""
    metadata(tmp_path)
    read_paths: list[str] = []
    original = Path.open

    def observed_open(path: Path, mode: str) -> object:
        read_paths.append(path.name)
        return original(path, mode)

    def forbidden_scan(_path: Path) -> Iterator[Path]:
        msg = "readiness must not scan directories"
        raise AssertionError(msg)

    monkeypatch.setattr(Path, "open", observed_open)
    monkeypatch.setattr(Path, "iterdir", forbidden_scan)
    installed: dict[str, str] = {}
    assert validate(tmp_path, ENV, installed.__getitem__, evaluate, satisfies) == ()
    assert read_paths == ["pyproject.toml", "uv.lock"]

# eof
