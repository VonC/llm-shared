"""Bounded process fixtures for setup and isolated readiness acceptance."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.acceptance.release_workflow.process_support import (
    empty_uv_lock,
    import_closure,
    process_scenario,
)

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path


@pytest.fixture
def processes(tmp_path: Path, scenario: str) -> dict[str, object]:
    """Measure each real Windows scenario with its own complete setup."""
    return process_scenario(tmp_path, scenario)


@pytest.fixture(scope="module")
def eager_closure(tmp_path_factory: pytest.TempPathFactory) -> subprocess.CompletedProcess[str]:
    """Measure the real eager import closure once in a site-free interpreter."""
    return import_closure(tmp_path_factory.mktemp("release_imports"))

@pytest.fixture
def uv_empty_shape(tmp_path: Path, *, dev_edges: bool) -> Path:
    """Measure each offline uv shape with its own complete setup."""
    return empty_uv_lock(tmp_path, dev_edges=dev_edges)

# eof
