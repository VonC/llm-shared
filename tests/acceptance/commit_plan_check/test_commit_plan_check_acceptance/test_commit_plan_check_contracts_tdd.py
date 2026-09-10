"""Acceptance evidence for the commit-plan checker's non-parity contracts.

Covers the validation-plan subject marker, rename inventory, operational Git
failure, caller-owned stdout redirection and the request publication gates.
Slow Git setup runs in fixtures so measured assertion calls remain bounded.

Fix: split out of ``test_commit_plan_check_acceptance_tdd`` so these scenarios
run on a different xdist worker from the readiness-state parity scenario. The
shared builders live in ``commit_plan_check_support``; no scenario changed.
"""

# ruff: noqa: S603, S607, SLF001

from __future__ import annotations

import json
import subprocess
from argparse import Namespace
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.commit_plan_check.commit_plan_check_support import (
    OPERATIONAL_STATUS,
    TREE_A,
    TREE_B,
    RepositoryState,
    adapter_arguments,
    commit,
    git,
    initialize_repository,
    module_environment,
    run_adapter,
    snapshot,
    stage_sample,
    valid_plan,
)
from tools import code_review_request as requestor
from tools import commit_plan_check
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def validation_marker_results(
    tmp_path: Path,
) -> tuple[
    commit_plan_check.CommitPlanCheckResult,
    commit_plan_check.CommitPlanCheckResult,
]:
    """Build real Git evidence outside the duration-measured assertion call."""
    initialize_repository(tmp_path)
    docs = tmp_path / "docs" / "v1.2.3"
    docs.mkdir(parents=True)
    relative = "docs/v1.2.3/plan.v1.2.3.release-ready.validation.md"
    validation = docs / "plan.v1.2.3.release-ready.validation.md"
    validation.write_text(
        "### Analysis of Step 1 implementation state\n\nNo. Missing.\n",
        encoding="utf-8",
    )
    git(tmp_path, "add", "--", relative)
    commit(tmp_path, "docs(release-ready): add validation plan")
    validation.write_text(
        "### Analysis of Step 1 implementation state\n\nYes. Complete.\n",
        encoding="utf-8",
    )
    git(tmp_path, "add", "--", relative)
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
    """A real staged No-to-Yes transition requires the exact pw marker."""
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
) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    """Run both adapters against a real staged rename during setup."""
    initialize_repository(tmp_path)
    (tmp_path / "old.txt").write_text("renamed\n", encoding="utf-8")
    git(tmp_path, "add", "--", "old.txt")
    commit(tmp_path, "test: add rename source")
    git(tmp_path, "mv", "old.txt", "new.txt")
    (tmp_path / "a.commit").write_text(
        valid_plan("old.txt", "new.txt"),
        encoding="utf-8",
    )
    return (
        run_adapter(tmp_path, "module", "json"),
        run_adapter(tmp_path, "launcher", "json"),
    )


def test_rename_inventory_contains_source_and_destination(
    rename_results: tuple[
        subprocess.CompletedProcess[str],
        subprocess.CompletedProcess[str],
    ],
) -> None:
    """No-renames inventory treats both sides as exact plan membership."""
    module, launcher = rename_results
    assert module.returncode == launcher.returncode == 0
    assert module.stdout == launcher.stdout
    assert set(json.loads(module.stdout)["staged_paths"]) == {"old.txt", "new.txt"}


@pytest.fixture
def operational_results(
    tmp_path: Path,
) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    """Run both adapters with a root whose Git inventory cannot be read."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "a.commit").write_text(valid_plan("sample.txt"), encoding="utf-8")
    return (
        run_adapter(tmp_path, "module", "json"),
        run_adapter(tmp_path, "launcher", "json"),
    )


def test_failed_git_inventory_has_stable_operational_diagnostic(
    operational_results: tuple[
        subprocess.CompletedProcess[str],
        subprocess.CompletedProcess[str],
    ],
) -> None:
    """An untrustworthy Git boundary maps to status two on both adapters."""
    module, launcher = operational_results
    assert module.returncode == launcher.returncode == OPERATIONAL_STATUS
    assert module.stdout == launcher.stdout == ""
    assert module.stderr == launcher.stderr
    assert module.stderr.startswith("commit-plan-check: cannot inventory commit plan:")


@pytest.fixture
def redirected_evidence(
    tmp_path: Path,
) -> tuple[RepositoryState, RepositoryState, subprocess.CompletedProcess[str], Path]:
    """Redirect launcher stdout as a caller-owned ignored file during setup."""
    initialize_repository(tmp_path)
    stage_sample(tmp_path)
    (tmp_path / "a.commit").write_text(valid_plan("sample.txt"), encoding="utf-8")
    evidence = tmp_path / "a.check-evidence.json"
    before = snapshot(tmp_path)
    with evidence.open("w", encoding="utf-8", newline="\n") as stream:
        result = subprocess.run(
            adapter_arguments(tmp_path, "launcher", "json"),
            cwd=tmp_path,
            env=module_environment(),
            check=False,
            stdout=stream,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
        )
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
    assert before == replace(after, ignored_root=before.ignored_root)
    assert set(after.ignored_root) == {*before.ignored_root, evidence.name}
    assert json.loads(evidence.read_text(encoding="utf-8"))["ready"] is True


def _request_arguments(root: Path) -> Namespace:
    """Create ignored caller inputs and paired outputs for the request gate."""
    home = root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    for name in ("assessment", "report", "changes", "response"):
        (home / f"a.{name}.md").write_text(f"{name}\n", encoding="utf-8")
    return Namespace(
        plan="docs/v0.11.0/plan.v0.11.0.commit-plan-check.md",
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
    )


@pytest.fixture
def requestor_rejections(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[str, str, bool, bool]:
    """Exercise both real-Git request rejections outside the measured call."""
    initialize_repository(tmp_path)
    stage_sample(tmp_path)
    (tmp_path / "a.commit").write_text(valid_plan("other.txt"), encoding="utf-8")
    arguments = _request_arguments(tmp_path)

    with pytest.raises(ReviewExchangeError, match="commit plan is not ready") as invalid:
        requestor._render_from_arguments(arguments, tmp_path)

    (tmp_path / "a.commit").write_text(valid_plan("sample.txt"), encoding="utf-8")
    trees = iter((TREE_A, TREE_B))

    def capture_drifting_tree(_root: Path) -> str:
        return next(trees)

    monkeypatch.setattr(requestor, "capture_index_tree", capture_drifting_tree)
    with pytest.raises(ReviewExchangeError, match="index changed") as drift:
        requestor._render_from_arguments(arguments, tmp_path)

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
