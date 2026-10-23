"""Reusable prepared-runtime fixture for identity and readiness contracts."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.test_support import prepared_runtime

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture
def bootstrap_state() -> Iterator[None]:
    """Restore bytecode, import path and private helper state after each check."""
    bytecode = sys.dont_write_bytecode
    search_path = list(sys.path)
    private = {name: module for name, module in sys.modules.items() if name.startswith("_release_bootstrap_")}
    yield
    sys.dont_write_bytecode = bytecode
    sys.path[:] = search_path
    for name in list(sys.modules):
        if name.startswith("_release_bootstrap_"):
            del sys.modules[name]
    sys.modules.update(private)


@pytest.fixture
def runtime(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Provide a tooling root, measured executable and measured prefix."""
    executable, prefix = prepared_runtime(tmp_path)
    return tmp_path, executable, prefix

# eof
