"""Fail closed on malformed Git metadata and physical filesystem failures."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import paths
from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.git_environment import controlled_environment
from tools.release_workflow.paths import (
    ProjectIdentity,
    ProjectPathError,
    authorize_path,
    validate_project,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


@pytest.mark.parametrize("output", ["", "relative\nrelative\nrelative\n", "missing"])
def test_malformed_metadata(output: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Malformed/truncated metadata is rejected instead of guessed."""
    git = GitExecutionContext(tmp_path / "git.exe", (2, 31, 0), controlled_environment({}, non_interactive=True), tmp_path, non_interactive=True)

    def run(args: Sequence[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(args, 0, b"" if "config" in args else output.encode("utf-8"), b"")

    monkeypatch.setattr(subprocess, "run", run)
    with pytest.raises(ProjectPathError, match="three absolute"):
        validate_project(tmp_path, git)


def test_root_resolution_error_keeps_supplied_value(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """OS failures retain the user's original root in a project diagnostic."""
    git = GitExecutionContext(tmp_path / "git.exe", (2, 31, 0), controlled_environment({}, non_interactive=True), tmp_path, non_interactive=True)

    def fail_resolve(_path: Path, *, strict: bool = False) -> Path:
        del strict
        raise PermissionError

    monkeypatch.setattr(Path, "resolve", fail_resolve)
    with pytest.raises(ProjectPathError, match=str(tmp_path.name)):
        validate_project(tmp_path, git)


def test_destination_resolution_error_keeps_supplied_value(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A link-resolution failure cannot authorize a future target."""
    identity = ProjectIdentity(tmp_path, tmp_path / ".git", tmp_path / ".git", str(tmp_path))

    def fail_resolve(_path: Path, *, strict: bool = False) -> Path:
        del strict
        raise OSError

    monkeypatch.setattr(Path, "resolve", fail_resolve)
    with pytest.raises(ProjectPathError, match="future-file"):
        authorize_path(identity, "future-file")


def test_managed_paths_never_scan_siblings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Authorization needs ancestor metadata only, regardless of worktree size."""
    identity = ProjectIdentity(tmp_path, tmp_path / ".git", tmp_path / ".git", str(tmp_path))

    def reject_scan(_path: Path) -> None:
        pytest.fail("whole-tree enumeration is forbidden")

    monkeypatch.setattr(Path, "iterdir", reject_scan)
    assert authorize_path(identity, "a/b/c/new") == tmp_path / "a" / "b" / "c" / "new"


def test_escape_without_another_repository_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Leaving the root fails even when no foreign Git marker is encountered."""
    root = tmp_path / "project"
    root.mkdir()
    identity = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    # A developer's home can itself be a repository. Isolate that ambient
    # metadata while retaining real filesystem traversal and root identity.
    def no_repository(_directory: Path) -> bool:
        return False

    monkeypatch.setattr(paths, "_foreign_boundary", no_repository)

    with pytest.raises(ProjectPathError, match="escapes physical project root"):
        authorize_path(identity, "../unmanaged/future-file")


# eof
