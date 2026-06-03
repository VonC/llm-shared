"""Tests for the read-only git helpers of prompt_workflow.

Fix: Cover the git command wrapper (success and both error-message branches),
the current-branch query, the fork-point walk (found and not found), the
changed-files diff, and the porcelain path parsing including renames and short
lines.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_git as git
from tools.prompt_workflow_models import PromptWorkflowError

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# pyright: reportPrivateUsage=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false
# ruff: noqa: SLF001


def _which_git(_name: str) -> str:
    return "git"


def test_run_git_returns_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A successful git command returns its stdout and builds the right argv."""
    captured: dict[str, object] = {}

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="branch-text")

    monkeypatch.setattr(shutil, "which", _which_git)
    monkeypatch.setattr(git.subprocess, "run", fake_run)

    assert git.run_git(["rev-parse", "HEAD"], cwd=tmp_path) == "branch-text"
    assert captured["command"] == ["git", "rev-parse", "HEAD"]
    assert captured["cwd"] == tmp_path


def test_run_git_wraps_error_with_stderr(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A failing command surfaces the stderr text in the raised error."""

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.CalledProcessError(1, command, stderr="boom")

    monkeypatch.setattr(shutil, "which", _which_git)
    monkeypatch.setattr(git.subprocess, "run", fake_run)

    with pytest.raises(PromptWorkflowError, match="boom"):
        git.run_git(["status"], cwd=tmp_path)


def test_run_git_wraps_error_without_stderr(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A failing command with no stderr still reports which command failed."""

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.CalledProcessError(1, command, stderr="")

    monkeypatch.setattr(shutil, "which", _which_git)
    monkeypatch.setattr(git.subprocess, "run", fake_run)

    with pytest.raises(PromptWorkflowError, match="git status failed"):
        git.run_git(["status"], cwd=tmp_path)


def test_current_branch_strips_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The current branch is the trimmed rev-parse output."""
    monkeypatch.setattr(git, "run_git", lambda _args, **_kwargs: "  main\n")
    assert git.current_branch(tmp_path) == "main"


def _fake_git(*, branch: str, branches: str, revlist: str) -> Callable[..., str]:
    """Build a run_git stub that answers the three commands fork_point issues."""

    def fake(args: list[str], *, cwd: Path) -> str:
        del cwd
        if args[:2] == ["rev-parse", "--abbrev-ref"]:
            return branch
        if args[:1] == ["for-each-ref"]:
            return branches
        if args[:1] == ["rev-list"]:
            return revlist
        msg = f"Unexpected git args: {args}"
        raise AssertionError(msg)

    return fake


def test_fork_point_returns_boundary_commit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The fork point is the boundary commit shared with another branch."""
    monkeypatch.setattr(
        git,
        "run_git",
        _fake_git(branch="feature", branches="main\nfeature\n", revlist="c1\n-c0\n"),
    )
    assert git.fork_point(tmp_path) == "c0"


def test_fork_point_none_without_other_branches(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """With only the current branch there is no fork point (Q07 fallback)."""
    monkeypatch.setattr(
        git,
        "run_git",
        _fake_git(branch="main", branches="main\n", revlist=""),
    )
    assert git.fork_point(tmp_path) is None


def test_fork_point_none_without_boundary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """No boundary line means no shared commit, so no fork point."""
    monkeypatch.setattr(
        git,
        "run_git",
        _fake_git(branch="feature", branches="main\nfeature\n", revlist="c1\nc0\n"),
    )
    assert git.fork_point(tmp_path) is None


def test_changed_files_since_lists_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Changed files come from the name-only diff against the base commit."""
    monkeypatch.setattr(git, "run_git", lambda _args, **_kwargs: "docs/a.md\ndocs/b.md\n")
    assert git.changed_files_since(tmp_path, "base") == ["docs/a.md", "docs/b.md"]


def test_working_tree_changed_files_parses_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Porcelain parsing keeps target paths, handles renames, and drops blanks."""
    status = "\n M docs/one.md\nR  docs/old.md -> docs/new.md\nXY\n?? docs/two.md\n"
    monkeypatch.setattr(git, "run_git", lambda _args, **_kwargs: status)

    assert git.working_tree_changed_files(tmp_path) == [
        "docs/one.md",
        "docs/new.md",
        "docs/two.md",
    ]


def test_status_entries_pairs_status_and_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Each porcelain line becomes a (status, path) pair; short lines drop."""
    status = "M  tools/a.py\n D docs/x.md\n?? new.py\nXY\n\nR  old.py -> new2.py\n"
    monkeypatch.setattr(git, "run_git", lambda _args, **_kwargs: status)

    assert git.status_entries(tmp_path) == [
        ("M ", "tools/a.py"),
        (" D", "docs/x.md"),
        ("??", "new.py"),
        ("R ", "new2.py"),
    ]


def test_staged_files_lists_cached_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Staged files come from the cached name-only diff."""
    monkeypatch.setattr(git, "run_git", lambda _args, **_kwargs: "docs/a.md\ntools/b.py\n")
    assert git.staged_files(tmp_path) == ["docs/a.md", "tools/b.py"]


def test_has_step_commit_with_and_without_base(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The grep range is base..HEAD when known, otherwise the whole history."""
    calls: list[list[str]] = []

    def fake(args: list[str], **_kwargs: object) -> str:
        calls.append(args)
        return "abc123\n" if "base..HEAD" in args else ""

    monkeypatch.setattr(git, "run_git", fake)

    assert git.has_step_commit(tmp_path, 2, "base") is True
    assert git.has_step_commit(tmp_path, 3, None) is False
    assert calls[0] == ["log", "-i", "--grep=record step 2 validation", "--format=%H", "base..HEAD"]
    assert calls[1] == ["log", "-i", "--grep=record step 3 validation", "--format=%H", "HEAD"]


def test_stage_all_runs_git_add(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Staging everything runs ``git add -A``."""
    calls: list[list[str]] = []

    def fake(args: list[str], **_kwargs: object) -> str:
        calls.append(args)
        return ""

    monkeypatch.setattr(git, "run_git", fake)
    git.stage_all(tmp_path)
    assert calls == [["add", "-A"]]


# eof
