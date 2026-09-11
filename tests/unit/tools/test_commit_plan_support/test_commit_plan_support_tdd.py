"""Tests for the exact shared staged-path inventory boundary.

Step 1 proves that checking and committing can consume one ordered Git index
inventory without path filtering, filesystem probes, or rename interpretation.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import commit_plan_support
from tools.git_command import GitCommandOptions

if TYPE_CHECKING:
    from pathlib import Path


def _return_stdout(
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
) -> None:
    """Replace the Git seam with one completed command carrying stdout."""

    def completed(
        arguments: tuple[str, ...],
        *,
        cwd: Path,
        options: GitCommandOptions,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        return subprocess.CompletedProcess(
            ["git", *arguments],
            0,
            stdout,
            "",
        )

    monkeypatch.setattr(
        commit_plan_support,
        "run_cross_platform_git_command",
        completed,
    )


def test_staged_paths_runs_the_exact_index_inventory_once(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The public boundary owns one exact cross-platform Git invocation."""
    calls: list[tuple[tuple[str, ...], Path, GitCommandOptions]] = []

    def completed(
        arguments: tuple[str, ...],
        *,
        cwd: Path,
        options: GitCommandOptions,
    ) -> subprocess.CompletedProcess[str]:
        calls.append((arguments, cwd, options))
        return subprocess.CompletedProcess(
            ["git", *arguments],
            0,
            "staged.txt\0",
            "",
        )

    monkeypatch.setattr(
        commit_plan_support,
        "run_cross_platform_git_command",
        completed,
    )

    assert commit_plan_support.staged_paths(tmp_path) == ("staged.txt",)
    assert calls == [
        (
            ("diff", "--cached", "--name-only", "--no-renames", "-z"),
            tmp_path,
            GitCommandOptions(capture_output=True, encoding="utf-8"),
        ),
    ]


def test_staged_paths_preserves_order_and_path_whitespace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """NUL decoding keeps Git order and every non-delimiter character."""
    _return_stdout(
        monkeypatch,
        " leading.txt\0trailing.txt \0line\nbreak.txt\0",
    )

    assert commit_plan_support.staged_paths(tmp_path) == (
        " leading.txt",
        "trailing.txt ",
        "line\nbreak.txt",
    )


def test_staged_paths_keeps_a_deleted_path_in_membership(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Inventory decoding does not probe or discard a deleted worktree path."""
    _return_stdout(monkeypatch, "removed/file.txt\0")

    assert commit_plan_support.staged_paths(tmp_path) == ("removed/file.txt",)


def test_staged_paths_keeps_both_no_rename_sides(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The source and destination emitted by --no-renames remain separate."""
    _return_stdout(monkeypatch, "before.txt\0after.txt\0")

    assert commit_plan_support.staged_paths(tmp_path) == (
        "before.txt",
        "after.txt",
    )


def test_staged_paths_discards_only_empty_nul_segments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An empty index and repeated delimiters cannot create phantom paths."""
    _return_stdout(monkeypatch, "\0\0")

    assert commit_plan_support.staged_paths(tmp_path) == ()


def _return_git_outputs(
    monkeypatch: pytest.MonkeyPatch,
    outputs: dict[tuple[str, ...], str],
) -> list[tuple[str, ...]]:
    """Replace the Git seam with exact per-command text responses."""
    calls: list[tuple[str, ...]] = []

    def completed(
        arguments: tuple[str, ...],
        *,
        cwd: Path,
        options: GitCommandOptions,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        calls.append(arguments)
        return subprocess.CompletedProcess(
            ["git", *arguments],
            0,
            outputs[arguments],
            "",
        )

    monkeypatch.setattr(
        commit_plan_support,
        "run_cross_platform_git_command",
        completed,
    )
    return calls


def test_completed_validation_requires_exact_subject_for_new_yes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A status transition to Yes derives the canonical topic and step marker."""
    path = "docs/v1.2.3/plan.v1.2.3.release-ready.validation.md"
    staged = "### Analysis of Step 1 implementation state\n\nYes. Complete.\n"
    head = "### Analysis of Step 1 implementation state\n\nNo. Missing.\n"
    calls = _return_git_outputs(
        monkeypatch,
        {
            ("ls-files", "--stage", "--", path): "100644 hash 0\tpath\n",
            ("show", f":{path}"): staged,
            ("ls-tree", "--name-only", "HEAD", "--", path): f"{path}\n",
            ("show", f"HEAD:{path}"): head,
        },
    )

    requirements = commit_plan_support.completed_validation_subject_requirements(
        tmp_path,
        ("src/code.py", path),
    )

    assert [(item.path, item.subject) for item in requirements] == [
        (path, "docs(release-ready): record step 1 validation"),
    ]
    assert calls == [
        ("ls-files", "--stage", "--", path),
        ("show", f":{path}"),
        ("ls-tree", "--name-only", "HEAD", "--", path),
        ("show", f"HEAD:{path}"),
    ]


@pytest.mark.parametrize(
    ("staged", "head"),
    [
        (
            "### Analysis of Step 1 implementation state\n\nNo. Missing.\n",
            "### Analysis of Step 1 implementation state\n\nNo. Missing.\n",
        ),
        (
            "### Analysis of Step 1 implementation state\n\nYes. Complete.\n",
            "### Analysis of Step 1 implementation state\n\nYes. Complete.\n",
        ),
    ],
)
def test_validation_without_new_yes_has_no_subject_requirement(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    staged: str,
    head: str,
) -> None:
    """Incomplete and previously completed steps permit ordinary doc subjects."""
    path = "docs/plan.v1.0.topic.validation.md"
    _return_git_outputs(
        monkeypatch,
        {
            ("ls-files", "--stage", "--", path): "index entry\n",
            ("show", f":{path}"): staged,
            ("ls-tree", "--name-only", "HEAD", "--", path): f"{path}\n",
            ("show", f"HEAD:{path}"): head,
        },
    )

    assert commit_plan_support.completed_validation_subject_requirements(
        tmp_path,
        (path,),
    ) == ()


def test_deleted_validation_plan_has_no_completion_requirement(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A staged deletion has no staged content capable of completing a step."""
    path = "docs/plan.v1.0.topic.validation.md"
    calls = _return_git_outputs(
        monkeypatch,
        {("ls-files", "--stage", "--", path): ""},
    )

    assert commit_plan_support.completed_validation_subject_requirements(
        tmp_path,
        (path,),
    ) == ()
    assert calls == [("ls-files", "--stage", "--", path)]


# eof
