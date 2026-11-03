"""Validation, rename, error, redirection and publication policy in Python."""

# ruff: noqa: S603, S607, SLF001

from __future__ import annotations

import json
from argparse import Namespace
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.commit_plan_check.commit_plan_check_support import (
    OPERATIONAL_STATUS,
    TREE_A,
    TREE_B,
    RepositoryState,
    initialize_repository,
    run_adapter,
    snapshot,
    stage_sample,
    valid_plan,
)
from tests.acceptance.commit_plan_check.repository_observations import (
    PLANS,
    declare_baseline,
    declare_index,
)
from tools import code_review_request as requestor
from tools import commit_plan_check
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path


@pytest.fixture
def validation_marker_results(
    tmp_path: Path,
    commit_plan_repository_seed: Path,
) -> tuple[
    commit_plan_check.CommitPlanCheckResult,
    commit_plan_check.CommitPlanCheckResult,
]:
    """Declare the before/after validation bytes consumed by production policy."""
    initialize_repository(tmp_path, commit_plan_repository_seed)
    docs = tmp_path / "docs" / "v1.2.3"
    docs.mkdir(parents=True)
    relative = "docs/v1.2.3/plan.v1.2.3.release-ready.validation.md"
    validation = docs / "plan.v1.2.3.release-ready.validation.md"
    validation.write_text(
        "### Analysis of Step 1 implementation state\n\nNo. Missing.\n",
        encoding="utf-8",
    )
    declare_baseline(tmp_path, relative)
    validation.write_text(
        "### Analysis of Step 1 implementation state\n\nYes. Complete.\n",
        encoding="utf-8",
    )
    declare_index(tmp_path, relative)
    wrong = "docs(release-ready): update step 1 validation"
    expected = "docs(release-ready): record step 1 validation"
    (tmp_path / "a.commit").write_text(
        valid_plan(relative, subject=wrong),
        encoding="utf-8",
    )

    invalid = commit_plan_check.check_commit_plan(tmp_path)
    (tmp_path / "a.commit").write_text(
        valid_plan(relative, subject=expected),
        encoding="utf-8",
    )
    valid = commit_plan_check.check_commit_plan(tmp_path)
    return invalid, valid


def test_checker_rejects_update_for_newly_completed_validation_plan(
    validation_marker_results: tuple[
        commit_plan_check.CommitPlanCheckResult,
        commit_plan_check.CommitPlanCheckResult,
    ],
) -> None:
    """A staged No-to-Yes transition requires the exact pw marker."""
    invalid, valid = validation_marker_results
    relative = "docs/v1.2.3/plan.v1.2.3.release-ready.validation.md"
    expected = "docs(release-ready): record step 1 validation"

    assert invalid.state is commit_plan_check.CommitPlanCheckState.INVALID_PLAN
    assert invalid.diagnostics == (
        "group 1 containing completed validation plan "
        f"{relative} must use exact subject: {expected}",
    )
    assert valid.state is commit_plan_check.CommitPlanCheckState.VALID


@pytest.fixture
def rename_results(
    tmp_path: Path,
    commit_plan_repository_seed: Path,
) -> subprocess.CompletedProcess[str]:
    """Declare both sides of the rename and run the production checker."""
    initialize_repository(tmp_path, commit_plan_repository_seed)
    (tmp_path / "old.txt").write_text("renamed\n", encoding="utf-8")
    declare_baseline(tmp_path, "old.txt")
    (tmp_path / "old.txt").rename(tmp_path / "new.txt")
    declare_index(tmp_path, "old.txt", "new.txt")
    (tmp_path / "a.commit").write_text(
        valid_plan("old.txt", "new.txt"),
        encoding="utf-8",
    )
    return run_adapter(tmp_path, "json")


def test_rename_inventory_contains_source_and_destination(
    rename_results: subprocess.CompletedProcess[str],
) -> None:
    """No-renames inventory treats both sides as exact plan membership."""
    assert rename_results.returncode == 0
    assert set(json.loads(rename_results.stdout)["staged_paths"]) == {"old.txt", "new.txt"}


@pytest.fixture
def operational_results(
    tmp_path: Path,
) -> subprocess.CompletedProcess[str]:
    """Run the checker with an unavailable repository inventory observation."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "a.commit").write_text(valid_plan("sample.txt"), encoding="utf-8")
    return run_adapter(tmp_path, "json")


def test_failed_git_inventory_has_stable_operational_diagnostic(
    operational_results: subprocess.CompletedProcess[str],
) -> None:
    """An untrustworthy inventory boundary maps to status two."""
    assert operational_results.returncode == OPERATIONAL_STATUS
    assert operational_results.stdout == ""
    assert operational_results.stderr.startswith("commit-plan-check: cannot inventory commit plan:")


@pytest.fixture
def redirected_evidence(
    tmp_path: Path,
    commit_plan_repository_seed: Path,
) -> tuple[RepositoryState, RepositoryState, subprocess.CompletedProcess[str], Path]:
    """Redirect production CLI output to the caller-owned stream."""
    initialize_repository(tmp_path, commit_plan_repository_seed)
    stage_sample(tmp_path)
    (tmp_path / "a.commit").write_text(valid_plan("sample.txt"), encoding="utf-8")
    evidence = tmp_path / "a.check-evidence.json"
    before = snapshot(tmp_path)
    with evidence.open("w", encoding="utf-8", newline="\n") as stream:
        result = run_adapter(tmp_path, "json", stdout=stream)
    return before, snapshot(tmp_path), result, evidence


def test_caller_owned_redirection_is_the_only_observable_change(
    redirected_evidence: tuple[
        RepositoryState,
        RepositoryState,
        subprocess.CompletedProcess[str],
        Path,
    ],
) -> None:
    """The checker owns no write when the caller redirects its stdout."""
    before, after, result, evidence = redirected_evidence
    assert result.returncode == 0
    assert result.stderr == ""
    assert before == replace(after, files=tuple(entry for entry in after.files if entry[0] != evidence.name))
    assert dict(after.files).keys() == dict(before.files).keys() | {evidence.name}
    assert json.loads(evidence.read_text(encoding="utf-8"))["ready"] is True


def _request_arguments(root: Path) -> Namespace:
    """Create ignored caller inputs and paired outputs for the request gate."""
    home = root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    for name in ("assessment", "report", "changes", "response"):
        (home / f"a.{name}.md").write_text(f"{name}\n", encoding="utf-8")
    plan = root / "docs/v0.11.0/plan.v0.11.0.commit-plan-check.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text("# Plan\n", encoding="utf-8")
    return Namespace(
        plan=str(plan),
        implementation_step="4",
        umbrella=None,
        round_number=1,
        assessment_file=str(home / "a.assessment.md"),
        implementation_report_file=str(home / "a.report.md"),
        change_summary_file=str(home / "a.changes.md"),
        writer_response_file=str(home / "a.response.md"),
        guidance_file=None,
        plan_validation_command=[],
        request_validation_command=[],
        request_content_output=str(home / "a.request.md"),
        transcript_summary_output=str(home / "a.summary.md"),
        scope_capture_output=str(home / "a.scope.json"),
        scope_change_file=None,
    )


@pytest.fixture
def requestor_rejections(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    commit_plan_repository_seed: Path,
) -> tuple[str, str, bool, bool]:
    """Exercise request rejection over declared stable and drifting indexes."""
    initialize_repository(tmp_path, commit_plan_repository_seed)
    stage_sample(tmp_path)
    (tmp_path / "a.commit").write_text(valid_plan("other.txt"), encoding="utf-8")
    arguments = _request_arguments(tmp_path)
    before = dict(PLANS[tmp_path.resolve()].index)

    with pytest.raises(ReviewExchangeError, match="commit plan is not ready") as invalid:
        requestor._render_from_arguments(arguments, tmp_path)

    (tmp_path / "a.commit").write_text(valid_plan("sample.txt"), encoding="utf-8")
    trees = iter((TREE_A, TREE_B))

    def capture_drifting_tree(_root: Path) -> str:
        return next(trees)

    monkeypatch.setattr(requestor, "capture_index_tree", capture_drifting_tree)
    with pytest.raises(ReviewExchangeError, match="index changed") as drift:
        requestor._render_from_arguments(arguments, tmp_path)

    assert PLANS[tmp_path.resolve()].index == before
    return (
        str(invalid.value),
        str(drift.value),
        (tmp_path / ".reviews" / "a.request.md").exists(),
        (tmp_path / ".reviews" / "a.summary.md").exists(),
    )


def test_requestor_rejects_invalid_plan_and_index_drift_without_outputs(
    requestor_rejections: tuple[str, str, bool, bool],
) -> None:
    """Both request-publication rejection paths preserve paired outputs."""
    invalid, drift, request_exists, summary_exists = requestor_rejections

    assert "commit plan is not ready" in invalid
    assert "index changed" in drift
    assert not request_exists
    assert not summary_exists


# eof
