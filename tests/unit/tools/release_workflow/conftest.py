"""Reusable runtime and real Git templates for release identity contracts."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_test_support import (
    GitSandbox,
    copy_template,
    create_template,
)
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


@pytest.fixture(scope="session")
def git_template(tmp_path_factory: pytest.TempPathFactory) -> GitSandbox:
    """Initialize minimal real Git metadata and verify the executable once."""
    return create_template(tmp_path_factory.mktemp("release-git-template"))


@pytest.fixture
def git_sandbox(git_template: GitSandbox, tmp_path: Path) -> GitSandbox:
    """Give each case independent copies of the small empty repository."""
    return copy_template(git_template, tmp_path)


@pytest.fixture(scope="session")
def linked_sandbox(git_template: GitSandbox, tmp_path_factory: pytest.TempPathFactory) -> GitSandbox:
    """Share read-only real linked metadata between config and identity checks."""
    sandbox = copy_template(git_template, tmp_path_factory.mktemp("release-linked"))
    sandbox.linked_worktree()
    return sandbox

# eof
