"""Prepare real index mutations before artifact rejection assertions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.release_workflow.artifacts import resolve_artifacts
from tools.release_workflow.paths import ProjectIdentity

if TYPE_CHECKING:
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.artifacts import ArtifactDeclaration


@pytest.fixture
def tracked_artifact_sandbox(git_sandbox: GitSandbox) -> GitSandbox:
    """Prepare a genuine tracked subfolder for preflight rejection."""
    root = git_sandbox.home / "B"
    (root / "sub/tracked").write_bytes(b"tracked")
    git_sandbox.stage(root, "sub/tracked")
    return git_sandbox


@pytest.fixture
def newly_tracked_artifacts(git_sandbox: GitSandbox) -> ArtifactDeclaration:
    """Resolve while untracked, then mutate the actual index before preparation."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    declaration = resolve_artifacts(project, git_sandbox.context())
    declaration.home.mkdir()
    (declaration.home / "tracked").write_bytes(b"keep")
    git_sandbox.stage(root, ".reviews/tracked")
    return declaration


# eof
