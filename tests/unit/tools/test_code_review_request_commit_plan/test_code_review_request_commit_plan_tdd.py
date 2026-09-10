"""TDD coverage for Step 3 commit-plan request publication enforcement.

The tests bind rendered evidence to one stable index tree and prove that every
non-ready, operational, or drifting state is rejected before paired writes.
"""

from __future__ import annotations

import json
from argparse import Namespace
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools import code_review_request as requestor
from tools.code_review_validation import resolve_code_review_validation
from tools.commit_plan_check import CommitPlanCheckResult, CommitPlanCheckState
from tools.git_batch_commit_models import CommitPlanGroup
from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_models_envelope import parse_envelope_markdown

if TYPE_CHECKING:
    from pathlib import Path

_TREE_A = "a" * 40
_TREE_B = "b" * 40
_TIMESTAMP = "2026-08-27T08:00:00+02:00"
_DUNDER_PATH = "tests/unit/tools/test_x/__init__.py"


def _ready_result() -> CommitPlanCheckResult:
    """Return one realistic ready result with ordered group membership."""
    return CommitPlanCheckResult(
        state=CommitPlanCheckState.VALID,
        groups=(
            CommitPlanGroup(
                1,
                "feat(commit-plan-check): gate requests",
                ("tools/code_review_request.py", _DUNDER_PATH),
            ),
        ),
        staged_paths=("tools/code_review_request.py", _DUNDER_PATH),
    )


def _round_input(tmp_path: Path) -> requestor.CodeReviewRoundInput:
    """Build one direct public-renderer input with ready checker evidence."""
    plan = tmp_path / "plan.v0.11.0.commit-plan-check.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    return requestor.CodeReviewRoundInput(
        context=requestor.code_review_context(plan, "3"),
        round_number=1,
        created_at=_TIMESTAMP,
        assessment="Step 3 is complete.",
        implementation_report="The request gate is implemented.",
        change_summary="The Step 3 paths are staged.",
        writer_response="No earlier response exists.",
        request_index_tree=_TREE_A,
        resolved_validation_set=resolve_code_review_validation(("ghog day",)),
        commit_plan_result=_ready_result(),
    )


def _files(tmp_path: Path) -> dict[str, Path]:
    """Create ignored-style caller inputs and paired output paths."""
    home = tmp_path / ".reviews"
    home.mkdir(exist_ok=True)
    files = {
        "assessment": home / "a.assessment.md",
        "report": home / "a.report.md",
        "changes": home / "a.changes.md",
        "response": home / "a.response.md",
        "content": home / "a.request.md",
        "summary": home / "a.summary.md",
    }
    for key in ("assessment", "report", "changes", "response"):
        files[key].write_text(f"{key} evidence\n", encoding="utf-8")
    return files


def _arguments(tmp_path: Path, files: dict[str, Path]) -> Namespace:
    """Build the private command adapter input used by the focused gate tests."""
    plan = tmp_path / "plan.v0.11.0.commit-plan-check.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    return Namespace(
        plan=str(plan),
        implementation_step="3",
        umbrella=None,
        round_number=1,
        assessment_file=str(files["assessment"]),
        implementation_report_file=str(files["report"]),
        change_summary_file=str(files["changes"]),
        writer_response_file=str(files["response"]),
        guidance_file=None,
        plan_validation_command=[],
        request_validation_command=[],
        request_content_output=str(files["content"]),
        transcript_summary_output=str(files["summary"]),
    )


def _prepare_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep focused command tests on the gate rather than Git ignore setup."""
    monkeypatch.setattr(requestor, "_is_effectively_ignored", _always_ignored)
    monkeypatch.setattr(requestor, "format_local_timestamp", lambda: _TIMESTAMP)
    monkeypatch.setattr(
        requestor,
        "load_project_validation_commands",
        _project_validation_commands,
    )


def _always_ignored(_root: Path, _path: Path) -> bool:
    """Keep focused gate tests independent of Git ignore configuration."""
    return True


def _project_validation_commands(_root: Path) -> tuple[str, ...]:
    """Return the mandatory project command for focused rendering tests."""
    return ("ghog day",)


def test_direct_renderer_requires_one_typed_ready_result(tmp_path: Path) -> None:
    """The public typed boundary cannot represent unchecked request evidence."""
    source = _round_input(tmp_path)
    with pytest.raises(ReviewExchangeError, match="commit plan result must be typed"):
        replace(source, commit_plan_result=None)  # type: ignore[arg-type]
    with pytest.raises(ReviewExchangeError, match="commit plan result must be ready"):
        replace(
            source,
            commit_plan_result=CommitPlanCheckResult(
                CommitPlanCheckState.INVALID_PLAN,
                diagnostics=("membership mismatch",),
            ),
        )


def test_command_checks_once_between_matching_tree_captures_before_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One ready result is bound to one stable tree and both rendered outputs."""
    files = _files(tmp_path)
    events: list[str] = []
    _prepare_command(monkeypatch)

    def capture(_root: Path) -> str:
        events.append("capture")
        return _TREE_A

    def check(_root: Path) -> CommitPlanCheckResult:
        events.append("check")
        return _ready_result()

    monkeypatch.setattr(requestor, "capture_index_tree", capture)
    monkeypatch.setattr(requestor, "check_commit_plan", check)
    original_write = requestor._write_utf8

    def recording_write(path: Path, content: str, label: str) -> None:
        events.append("write")
        original_write(path, content, label)

    monkeypatch.setattr(requestor, "_write_utf8", recording_write)
    requestor._render_from_arguments(_arguments(tmp_path, files), tmp_path)

    assert events == ["capture", "check", "capture", "write", "write"]
    content = files["content"].read_text(encoding="utf-8")
    _envelope, authored = parse_envelope_markdown(content)
    evidence = authored.split("```json\n", 1)[1].split("\n```", 1)[0]
    assert (
        json.loads(evidence)["commit_plan_result"]
        == _ready_result().structured_payload()
    )
    summary = files["summary"].read_text(encoding="utf-8")
    assert "commit_plan_result:\n\n```text\nstate: valid\nready: true" in summary


def test_transcript_fences_dunder_paths_as_command_output(tmp_path: Path) -> None:
    """Dunder paths stay literal inside the human evidence code fence."""
    summary = requestor.render_code_review_request(_round_input(tmp_path)).transcript_summary
    human_evidence = summary.split("```text\n", 1)[1].split("\n```", 1)[0]

    assert _DUNDER_PATH in human_evidence


@pytest.mark.parametrize(
    ("result", "trees", "message"),
    [
        (
            CommitPlanCheckResult(
                CommitPlanCheckState.INVALID_PLAN,
                diagnostics=("membership mismatch",),
            ),
            (_TREE_A,),
            "commit plan is not ready",
        ),
        (
            CommitPlanCheckResult(
                CommitPlanCheckState.OPERATIONAL_FAILURE,
                diagnostics=("cannot inventory commit plan",),
            ),
            (_TREE_A,),
            "commit plan check failed operationally",
        ),
        (
            _ready_result(),
            (_TREE_A, _TREE_B),
            "index changed during commit plan check",
        ),
    ],
)
def test_rejected_gate_never_creates_or_changes_either_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    result: CommitPlanCheckResult,
    trees: tuple[str, ...],
    message: str,
) -> None:
    """Non-ready, operational, and tree-drift paths preserve both outputs."""
    files = _files(tmp_path)
    files["content"].write_text("old content\n", encoding="utf-8")
    files["summary"].write_text("old summary\n", encoding="utf-8")
    captures = iter(trees)
    _prepare_command(monkeypatch)

    def capture(_root: Path) -> str:
        return next(captures)

    def check(_root: Path) -> CommitPlanCheckResult:
        return result

    monkeypatch.setattr(requestor, "capture_index_tree", capture)
    monkeypatch.setattr(requestor, "check_commit_plan", check)

    with pytest.raises(ReviewExchangeError, match=message):
        requestor._render_from_arguments(_arguments(tmp_path, files), tmp_path)

    assert files["content"].read_text(encoding="utf-8") == "old content\n"
    assert files["summary"].read_text(encoding="utf-8") == "old summary\n"


# eof
