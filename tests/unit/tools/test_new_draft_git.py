"""Tests for the new_draft git helpers: branch checks, creation, and relocation.

Cover the local/remote-tracking branch collision check, the mutating helpers
(`create_local_branch`, `add_worktree`), and the --from-draft relocation helpers
(`path_is_tracked`, `git_move`, `stage_path`), including the non-zero-exit error
path with and without captured stderr. `run_cross_platform_git_command` is
monkeypatched so no real repository is touched.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import new_draft_git as git
from tools.new_draft_models import NewDraftError

if TYPE_CHECKING:
    from pathlib import Path


def _completed(
    stdout: str = "",
    *,
    returncode: int = 0,
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    """Build a CompletedProcess stub with the given stdout/stderr/return code."""
    return subprocess.CompletedProcess(
        args=["git"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_branch_collision_local(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """branch_collision reports a local hit when `branch --list` is non-empty."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("  myslug\n")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.branch_collision("myslug", cwd=tmp_path) == git.COLLISION_LOCAL


def test_branch_collision_remote(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """branch_collision reports a remote hit when ls-remote finds the branch."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        if git_args[0] == "remote":
            return _completed("origin\n")
        if git_args[0] == "ls-remote":
            return _completed("abc123\trefs/heads/myslug\n")
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.branch_collision("myslug", cwd=tmp_path) == git.COLLISION_REMOTE


def test_branch_collision_none(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """branch_collision returns None when local is free and no remote is declared."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.branch_collision("myslug", cwd=tmp_path) is None


def test_list_remotes_returns_names(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """list_remotes returns one trimmed name per `git remote` line."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("origin\nupstream\n")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.list_remotes(tmp_path) == ["origin", "upstream"]


def test_remote_branch_exists_no_remotes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """remote_branch_exists is False (and queries nothing) without remotes."""
    calls: list[list[str]] = []

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        calls.append(list(git_args))
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.remote_branch_exists("myslug", cwd=tmp_path) is False
    assert not any(args[0] == "ls-remote" for args in calls)


def test_remote_branch_exists_checks_every_remote(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """remote_branch_exists finds a branch on a non-origin remote."""
    queried: list[str] = []

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        if git_args[0] == "remote":
            return _completed("origin\nupstream\n")
        queried.append(git_args[2])
        if git_args[2] == "upstream":
            return _completed("abc123\trefs/heads/myslug\n")
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.remote_branch_exists("myslug", cwd=tmp_path) is True
    assert queried == ["origin", "upstream"]


def test_remote_branch_exists_absent_on_all_remotes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """remote_branch_exists is False when no declared remote has the branch."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        if git_args[0] == "remote":
            return _completed("origin\n")
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.remote_branch_exists("myslug", cwd=tmp_path) is False


def test_current_head_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """current_head_branch returns the trimmed rev-parse output."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("main\n")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.current_head_branch(tmp_path) == "main"


def test_create_local_branch_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """create_local_branch runs `switch -c <slug>` and returns on success."""
    calls: list[list[str]] = []

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        calls.append(list(git_args))
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    git.create_local_branch("myslug", cwd=tmp_path)

    assert ["switch", "-c", "myslug"] in calls


def test_create_local_branch_failure_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """create_local_branch raises NewDraftError with the captured stderr detail."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("", returncode=1, stderr="fatal: already exists")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    with pytest.raises(
        NewDraftError,
        match="switch -c myslug failed: fatal: already exists",
    ):
        git.create_local_branch("myslug", cwd=tmp_path)


def test_add_worktree_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """add_worktree runs `worktree add -b <slug> <path>` on success."""
    calls: list[list[str]] = []

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        calls.append(list(git_args))
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)
    worktree_path = tmp_path / "wt"

    git.add_worktree(worktree_path, "myslug", cwd=tmp_path)

    assert ["worktree", "add", "-b", "myslug", str(worktree_path)] in calls


def test_add_worktree_failure_without_stderr_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """add_worktree raises a detail-free message when git fails with no stderr."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("", returncode=1, stderr="")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    with pytest.raises(NewDraftError, match=r"worktree add .* failed\.$"):
        git.add_worktree(tmp_path / "wt", "myslug", cwd=tmp_path)


def test_path_is_tracked_true(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """path_is_tracked is True when `ls-files --error-unmatch` exits zero."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("docs/draft.md\n")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.path_is_tracked(tmp_path / "docs" / "draft.md", cwd=tmp_path) is True


def test_path_is_tracked_false(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """path_is_tracked is False when `ls-files --error-unmatch` exits non-zero."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("", returncode=1, stderr="did not match any file(s)")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    assert git.path_is_tracked(tmp_path / "docs" / "draft.md", cwd=tmp_path) is False


def test_git_move_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """git_move runs `mv <source> <target>` on success."""
    calls: list[list[str]] = []

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        calls.append(list(git_args))
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)
    source = tmp_path / "docs" / "old.md"
    target = tmp_path / "docs" / "new.md"

    git.git_move(source, target, cwd=tmp_path)

    assert ["mv", str(source), str(target)] in calls


def test_git_move_failure_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """git_move raises NewDraftError with the captured stderr detail."""

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del git_args, cwd, options
        return _completed("", returncode=1, stderr="fatal: not under version control")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)

    with pytest.raises(
        NewDraftError,
        match=r"mv .* failed: fatal: not under version control",
    ):
        git.git_move(tmp_path / "a.md", tmp_path / "b.md", cwd=tmp_path)


def test_stage_path_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """stage_path runs `add -- <path>` on success."""
    calls: list[list[str]] = []

    def fake_run(
        git_args: list[str],
        *,
        cwd: Path | None = None,
        options: object = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        calls.append(list(git_args))
        return _completed("")

    monkeypatch.setattr(git, "run_cross_platform_git_command", fake_run)
    path = tmp_path / "docs" / "draft.md"

    git.stage_path(path, cwd=tmp_path)

    assert ["add", "--", str(path)] in calls


# eof
