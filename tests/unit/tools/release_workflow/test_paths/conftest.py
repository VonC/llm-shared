"""Share immutable real path boundaries and retain native rejection evidence.

The explicit outside-Git probe runs in setup and retains its real exception;
its assertion stays cheap while total setup/call cost remains observable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_test_support import copy_template
from tools.release_workflow.paths import ProjectPathError, validate_project

if TYPE_CHECKING:
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
        sandbox.git(["add", f"{name}.txt"], cwd=sandbox.home / name)
    return sandbox


@pytest.fixture
def explicit_outside_git(git_sandbox: GitSandbox) -> pytest.ExceptionInfo[ProjectPathError]:
    """Retain the actual failure from both native config and discovery probes."""
    with pytest.raises(ProjectPathError) as caught:
        validate_project(git_sandbox.home, git_sandbox.context())
    return caught


# eof
