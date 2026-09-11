"""CLI and rendering tests for the release planner script.

Fix: cover `prepare_release_plan.py` end to end for the coverage gate: the
human-readable and JSON outputs against a planner result, the
exit-2 planner-error path, every rendering branch (boundary evidence and
candidates, merge and rebase conflict previews), and the `__main__` guard
through `runpy`, following the pattern of the groundhog acceptance suite. The
guard test injects an already-tested plan so it measures dispatch rather than
repeating the real Git workflow covered by the CLI tests above.
The CLI tests replace the separately tested Git workflow at the imported seam,
so rendering and error dispatch do not repeatedly launch Git subprocesses.
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
    feature_target_branch="main",
    mode=ReleaseMode.FEATURE,
    action=ReleaseAction.MERGE_NO_FF,
    scope="base..feature",
    commits=(),
    operations=(),
)
_ON_MAIN_PLAN = replace(
    _TEMPLATE,
    branch="main",
    mode=ReleaseMode.ON_MAIN,
    action=ReleaseAction.PREPARE_IN_PLACE,
    commits=(CommitSummary(oid="b" * 40, subject="feat: release work"),),
    operations=("prepare release artifacts",),
    notes=("No rebase and no branch merge are required.",),
)


def _on_main_plan(*_args: object, **_kwargs: object) -> ReleasePlan:
    """Return the representative on-main plan at the CLI workflow seam."""
    return _ON_MAIN_PLAN


def test_parser_accepts_umbrella_and_defaults_feature_target_to_auto() -> None:
    """Feature planning carries the collection destination into the planner."""
    args = plan_cli._parser().parse_args(  # noqa: SLF001 - focused CLI contract
        ["--umbrella", "docs/v0.11.0/draft.v0.11.0.review-mode.md"],
    )

    assert args.umbrella.as_posix().endswith("draft.v0.11.0.review-mode.md")
    assert args.feature_target == "auto"


def test_main_renders_a_human_plan_for_a_repository(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An on-main planner result renders the header, commits, and notes."""
    monkeypatch.setattr(plan_cli, "build_release_plan", _on_main_plan)
    code = main(
        ["--root", str(tmp_path), "--no-conflict-preview"],
    )

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
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--json serializes the complete plan through `ReleasePlan.to_dict`."""
    monkeypatch.setattr(plan_cli, "build_release_plan", _on_main_plan)
    code = main(
        ["--root", str(tmp_path), "--json", "--no-conflict-preview"],
    )

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["mode"] == "on-main"
    assert payload["main_branch"] == "main"
    assert payload["action"] == "prepare-in-place"


def test_main_reports_planner_errors_on_stderr(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A planner error exits 2 with an ERROR line, never a traceback."""
    def fail_plan(*_args: object, **_kwargs: object) -> ReleasePlan:
        message = "Unable to verify the repository"
        raise plan_cli.ReleasePlanError(message)

    monkeypatch.setattr(plan_cli, "build_release_plan", fail_plan)
    code = main(["--root", str(tmp_path)])

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


def _main_guard_plan(  # noqa: PLR0913 - mirrors the production seam exactly
    _root: Path,
    *,
    main_branch: str,
    integration_branch: str | None,
    umbrella: Path | None,
    branch: str | None,
    feature_base: str | None,
    feature_parent: str | None,
    feature_target: str,
    preview_conflicts: bool,
) -> ReleasePlan:
    """Return an already-tested plan for the main-guard dispatch boundary."""
    del (
        main_branch,
        integration_branch,
        umbrella,
        branch,
        feature_base,
        feature_parent,
        feature_target,
        preview_conflicts,
    )
    return _TEMPLATE


def test_script_runs_through_its_main_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The planner script runs as __main__ and exits with the plan code."""
    monkeypatch.setattr(
        "tools.prepare_release.prepare_release_plan_workflow.build_release_plan",
        _main_guard_plan,
    )
    script_path = plan_cli.__file__
    argv = [
        script_path,
        "--root",
        str(tmp_path),
        "--no-conflict-preview",
        "--json",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(script_path, run_name="__main__")

    assert excinfo.value.code == 0


# eof
