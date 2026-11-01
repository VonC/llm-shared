"""Share immutable real path boundaries and retain native rejection evidence.

Discovery and outside-Git probes run in setup and retain their real results;
assertions stay cheap while total setup/call cost remains observable.
Linked Git metadata rejection shares one real validated identity instead of
repeating identical Git subprocess probes for the pointer and its child.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_test_support import copy_template
from tools.release_workflow.paths import (
    ProjectPathError,
    discover_project,
    validate_project,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.paths import ProjectIdentity


@pytest.fixture(scope="module")
def boundary_matrix(
    git_template: GitSandbox, tmp_path_factory: pytest.TempPathFactory,
) -> tuple[GitSandbox, ProjectIdentity, ProjectIdentity]:
    """Validate A/B once, retaining actual junctions and nested Git metadata."""
    sandbox = copy_template(git_template, tmp_path_factory.mktemp("path-boundaries"))
    root_a, root_b = sandbox.home / "A", sandbox.home / "B"
    sandbox.junction("A/shortcut", root_a / "nested")
    sandbox.junction("B/internal", root_b / "sub")
    sandbox.junction("B/external", root_a)
    sandbox.junction("B/external-nested", root_a / "nested")
    git = sandbox.context()
    return sandbox, validate_project(root_a, git), validate_project(root_b, git)


@pytest.fixture(scope="module")
def indexed_sandbox(git_template: GitSandbox, tmp_path_factory: pytest.TempPathFactory) -> GitSandbox:
    """Build distinct real indexes once before testing caller index isolation."""
    sandbox = copy_template(git_template, tmp_path_factory.mktemp("indexed-boundaries"))
    for name in ("A", "B"):
        sandbox.stage(sandbox.home / name, f"{name}.txt")
    return sandbox


@pytest.fixture
def explicit_outside_git(git_sandbox: GitSandbox) -> pytest.ExceptionInfo[ProjectPathError]:
    """Retain the actual failure from both native config and discovery probes."""
    with pytest.raises(ProjectPathError) as caught:
        validate_project(git_sandbox.home, git_sandbox.context())
    return caught


@pytest.fixture(scope="module")
def discovered_project(git_template: GitSandbox) -> ProjectIdentity:
    """Reuse immutable native subfolder discovery without copying another repo."""
    return discover_project(git_template.home / "B/sub", git_template.context())


@pytest.fixture(scope="module")
def linked_identity(linked_sandbox: GitSandbox) -> ProjectIdentity:
    """Validate the immutable real linked worktree once before metadata rejection."""
    return validate_project(linked_sandbox.home / "linked", linked_sandbox.context())


@pytest.fixture
def equivalent_alias(git_sandbox: GitSandbox) -> Path:
    """Construct the real junction before timing physical-root validation."""
    return git_sandbox.junction("alias", git_sandbox.home / "B")


# eof
