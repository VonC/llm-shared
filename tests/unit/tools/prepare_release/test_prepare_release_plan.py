"""CLI and rendering tests for the release planner script.

Fix: cover `prepare_release_plan.py` end to end for the coverage gate: the
human-readable and JSON outputs against a real temporary repository, the
exit-2 planner-error path, every rendering branch (boundary evidence and
candidates, merge and rebase conflict previews), and the `__main__` guard
through `runpy`, following the pattern of the groundhog acceptance suite.
The error path uses a broken `.git` file so the test stays hermetic even
when an ancestor of the pytest temp directory is a real Git repository.
"""

from __future__ import annotations

import json
import runpy
import sys
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools.prepare_release import prepare_release_plan as plan_cli
from tools.prepare_release.prepare_release_plan import main, render_plan
from tools.prepare_release.prepare_release_plan_models import (
    BoundaryCandidate,
    CommitSummary,
    ConflictRecord,
    MergePreview,
    RebasePreview,
    ReleaseAction,
    ReleaseMode,
    ReleasePlan,
)

from .prepare_release_plan_test_support import commit_file, initialize_repository

if TYPE_CHECKING:
    from pathlib import Path

# The CLI contract: a planner error exits 2, leaving 0 for a produced plan.
_PLANNER_ERROR_EXIT = 2
# A minimal feature plan; each rendering test replaces only the fields it
# exercises, so the assertions stay focused on one block at a time.
_TEMPLATE = ReleasePlan(
    repository="repo",
    git_version="2.50.0",
    branch="feature",
    branch_oid="a" * 40,
    main_branch="main",
    integration_branch=None,
    mode=ReleaseMode.FEATURE,
    action=ReleaseAction.MERGE_NO_FF,
    scope="base..feature",
    commits=(),
    operations=(),
)


def test_main_renders_a_human_plan_for_a_repository(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A real on-main repository renders the header, commits, and notes."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    commit_file(repo, "main.txt", "main\n", "feat: release work")

    code = main(["--root", str(repo), "--no-conflict-preview"])

    out = capsys.readouterr().out
    assert code == 0
    assert "Release mode: on-main" in out
    assert "Action: prepare-in-place" in out
    assert "Selected commits:" in out
    assert "Proposed operations:" in out
    assert "Note: No rebase and no branch merge are required." in out


def test_main_emits_json_with_the_full_plan(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--json serializes the complete plan through `ReleasePlan.to_dict`."""
    repo = tmp_path / "repo"
    initialize_repository(repo)

    code = main(["--root", str(repo), "--json", "--no-conflict-preview"])

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["mode"] == "on-main"
    assert payload["main_branch"] == "main"
    assert payload["action"] == "prepare-in-place"


def test_main_reports_planner_errors_on_stderr(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A planner error exits 2 with an ERROR line, never a traceback."""
    # A .git file naming a missing gitdir fails `rev-parse` deterministically,
    # even when an ancestor of the temp directory is itself a Git repository.
    broken = tmp_path / "broken"
    broken.mkdir()
    (broken / ".git").write_text("gitdir: does-not-exist\n", encoding="utf-8")

    code = main(["--root", str(broken)])

    captured = capsys.readouterr()
    assert code == _PLANNER_ERROR_EXIT
    assert captured.err.startswith("ERROR: Unable to verify the repository")
    assert captured.out == ""


def test_render_plan_lists_boundary_evidence_and_candidates() -> None:
    """Boundary fields render the base, the evidence, and each candidate."""
    plan = replace(
        _TEMPLATE,
        feature_base="b" * 40,
        boundary_evidence="reflog: branch: Created from main",
        boundary_candidates=(
            BoundaryCandidate(
                base="c1",
                parent_refs=("develop",),
                evidence="merge-base",
                commit_count=1,
            ),
            BoundaryCandidate(
                base="c2",
                parent_refs=(),
                evidence="merge-base",
                commit_count=2,
            ),
        ),
        commits=(CommitSummary(oid="d" * 40, subject="feat: work"),),
        operations=("git merge --no-ff feature",),
        notes=("note one",),
    )

    text = render_plan(plan)

    assert f"Feature base: {'b' * 40}" in text
    assert "Boundary evidence: reflog: branch: Created from main" in text
    assert "c1 (1 commits; develop; merge-base)" in text
    assert "c2 (2 commits; unknown parent; merge-base)" in text
    assert f"  {'d' * 12} feat: work" in text
    assert "Proposed operations:" in text
    assert "Note: note one" in text


def test_render_plan_shows_merge_preview_conflicts() -> None:
    """A conflicting merge preview lists files, types, and messages."""
    conflict = ConflictRecord(
        conflict_type="CONFLICT (contents)",
        paths=("shared.txt",),
        message="content conflict",
    )
    preview = MergePreview(
        clean=False,
        tree_oid="t",
        conflicted_files=("shared.txt",),
        conflicts=(conflict,),
    )

    text = render_plan(replace(_TEMPLATE, merge_preview=preview))

    assert "Merge conflict preview: conflicts likely" in text
    assert "  file: shared.txt" in text
    assert "  CONFLICT (contents): shared.txt" in text
    assert "    content conflict" in text


def test_render_plan_shows_a_clean_merge_preview() -> None:
    """A clean merge preview renders one clean line."""
    preview = MergePreview(clean=True, tree_oid="t", conflicted_files=(), conflicts=())

    text = render_plan(replace(_TEMPLATE, merge_preview=preview))

    assert "Merge conflict preview: clean" in text


def test_render_plan_shows_rebase_preview_outcomes() -> None:
    """The rebase preview renders clean, stopped, and anonymous outcomes."""
    clean = RebasePreview(
        clean=True,
        checked_commits=3,
        conflict_commit=None,
        conflict_subject=None,
        merge=None,
    )
    assert "Rebase conflict preview: clean through 3 commits" in render_plan(
        replace(_TEMPLATE, rebase_preview=clean),
    )

    merge = MergePreview(clean=False, tree_oid="t", conflicted_files=("f",), conflicts=())
    stopped = RebasePreview(
        clean=False,
        checked_commits=1,
        conflict_commit="e" * 40,
        conflict_subject="feat: stop",
        merge=merge,
    )
    text = render_plan(replace(_TEMPLATE, rebase_preview=stopped))
    assert f"Rebase conflict preview at {'e' * 12} feat: stop: conflicts likely" in text
    assert "  file: f" in text

    anonymous = RebasePreview(
        clean=False,
        checked_commits=1,
        conflict_commit=None,
        conflict_subject=None,
        merge=merge,
    )
    assert "Rebase conflict preview: conflicts likely" in render_plan(
        replace(_TEMPLATE, rebase_preview=anonymous),
    )


def test_render_plan_omits_the_preview_block_without_merge_data() -> None:
    """A stopped rebase preview carrying no merge details renders no block."""
    silent = RebasePreview(
        clean=False,
        checked_commits=1,
        conflict_commit=None,
        conflict_subject=None,
        merge=None,
    )

    text = render_plan(replace(_TEMPLATE, rebase_preview=silent))

    assert "conflict preview" not in text


def test_script_runs_through_its_main_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The planner script runs as __main__ and exits with the plan code."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    script_path = plan_cli.__file__
    argv = [script_path, "--root", str(repo), "--no-conflict-preview", "--json"]
    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(script_path, run_name="__main__")

    assert excinfo.value.code == 0


# eof
