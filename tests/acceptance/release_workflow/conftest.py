"""Small lock records represent external uv observations without running uv."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.test_support import metadata

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def uv_empty_shape(tmp_path: Path, *, dev_edges: bool) -> Path:
    """Declare both supported lock shapes; readiness parsing remains real."""
    metadata(tmp_path)
    if dev_edges:
        project = tmp_path / "pyproject.toml"
        project.write_text(project.read_text(encoding="utf-8").replace(
            'dev = [{include-group = "release"}]', 'dev = [{include-group = "release"}, "local-only"]',
        ) + '\n[tool.uv.sources]\nlocal-only = {path="../local-only"}\n', encoding="utf-8")
        lock = tmp_path / "uv.lock"
        lock.write_text(lock.read_text(encoding="utf-8").replace(
            "[package.metadata.requires-dev]", '[package.dev-dependencies]\ndev = [{name="local-only"}]\n[package.metadata.requires-dev]',
        ) + '\n[[package]]\nname="local-only"\nversion="1.0"\nsource={directory="../local-only"}\n', encoding="utf-8")
    return tmp_path


# eof
