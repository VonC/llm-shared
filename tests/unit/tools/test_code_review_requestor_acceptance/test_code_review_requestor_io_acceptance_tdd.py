"""IO and failure acceptance for the implementation review requestor.

Step 4 keeps identity, scratch-boundary, exact-path, and replay failures apart
from lifecycle journeys. Instrumentation rejects documentation scans and
transcript reads while public render and exchange validation remain active.
Envelope-failure cases use one deterministic valid tree object because the
real Git capture boundary is covered in its focused temporary-repository leaf.
Active-exchange setup is prepared before measured duplicate and escalation checks.
"""

from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from tools import code_review_request as request_renderer
from tools import prompt_workflow_code_review as code_review
from tools.code_review_validation import resolve_code_review_validation
from tools.commit_plan_check import CommitPlanCheckResult, CommitPlanCheckState
from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactState,
    ReviewConfiguration,
    ReviewDisposition,
    ReviewExchangeError,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

from .code_answer_builder import build_code_answer

if TYPE_CHECKING:
    from collections.abc import Callable

# ruff: noqa: S603, S607

_FATAL = 2
_REQUEST_INDEX_TREE = "a" * 40


def _git(root: Path, *arguments: str) -> None:
    """Run one bounded Git command for repository-boundary acceptance."""
    subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )


def _inputs(root: Path) -> tuple[Topic, WorkflowState, MemoryRecord]:
    """Create one exact opted-in plan context for routing failures."""
    root.mkdir()
    _git(root, "init", "-q")
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (root / "a.review-mode").write_text("", encoding="utf-8")
    docs = root / "docs" / "v1.2.3"
    docs.mkdir(parents=True)
    draft = docs / "draft.v1.2.3.io.md"
    draft.write_text("# Draft\n", encoding="utf-8")
    plan = docs / "plan.v1.2.3.io.md"
    plan.write_text("# Plan\n\n### Step 4. acceptance\n", encoding="utf-8")
    validation = docs / "plan.v1.2.3.io.validation.md"
    validation.write_text(
        "# Validation\n\n### Analysis of Step 4 implementation state\n\nNot started.\n",
        encoding="utf-8",
    )
    topic = Topic("v1.2.3", "io", draft)
    state = WorkflowState(
        requirement=None,
        design=None,
        plan=plan,
        validation_plan=validation,
        requirement_has_open_questions=False,
        design_has_open_questions=False,
        plan_has_open_questions=False,
        memory_step=None,
    )
    record = MemoryRecord(
        branch="io",
        version="v1.2.3",
        topic="io",
        step=10,
        instruction="implement-step.md",
        plan_step="4",
    )
    return topic, state, record


@pytest.fixture
def opted_in_inputs(
    tmp_path: Path,
) -> tuple[Path, Topic, WorkflowState, MemoryRecord]:
    """Build the real Git-backed routing context outside measured calls."""
    root = tmp_path / "opted-in"
    topic, state, record = _inputs(root)
    return root, topic, state, record


def test_mismatched_plan_step_round_and_umbrella_fail_closed(
    opted_in_inputs: tuple[Path, Topic, WorkflowState, MemoryRecord],
) -> None:
    """Nearby code identities cannot publish into one exact active exchange."""
    root, topic, state, record = opted_in_inputs
    route = code_review.resolve_code_review_route(root, topic, state, record)
    assert route is not None
    context = route.context
    core = ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(root, context)),
        context,
        code_review.CODE_REVIEW_POLICY,
        ReviewConfiguration(enabled=True),
    )
    core.start()
    request = request_renderer.render_code_review_request(
        request_renderer.CodeReviewRoundInput(
            context=context,
            round_number=1,
            created_at="2026-08-13T20:00:00+02:00",
            assessment="Assess the exact implementation step.",
            implementation_report="Implemented the declared step.",
            change_summary="The staged diff and a.commit are ready.",
            writer_response="The writer requests review.",
            request_index_tree=_REQUEST_INDEX_TREE,
            resolved_validation_set=resolve_code_review_validation(("ghog day",)),
            commit_plan_result=CommitPlanCheckResult(CommitPlanCheckState.VALID),
        ),
    )
    core.publish_request(request.request_content, request.transcript_summary)
    wrong_step = replace(context, implementation_step="5")
    answer = build_code_answer(
        wrong_step,
        1,
        ReviewDisposition.CHANGES_REQUESTED,
        recommendation="Wrong step.",
    )
    with pytest.raises(ReviewExchangeError, match="envelope differs"):
        core.publish_answer(answer.content, answer.summary)
    wrong_round = build_code_answer(
        context,
        2,
        ReviewDisposition.CHANGES_REQUESTED,
        recommendation="Wrong round.",
    )
    with pytest.raises(ReviewExchangeError, match="round differs"):
        core.publish_answer(wrong_round.content, wrong_round.summary)
    umbrella = root / "docs/v1.2.3/draft.v1.2.3.other.md"
    umbrella.write_text("# Other\n", encoding="utf-8")
    wrong_umbrella = replace(context, umbrella_path=umbrella)
    answer = build_code_answer(
        wrong_umbrella,
        1,
        ReviewDisposition.CHANGES_REQUESTED,
        recommendation="Wrong umbrella.",
    )
    with pytest.raises(ReviewExchangeError, match="envelope differs"):
        core.publish_answer(answer.content, answer.summary)
    assert core.classify().state is ArtifactState.REQUEST_PENDING


@pytest.fixture
def tracked_scratch_result(tmp_path: Path) -> tuple[int, bool, bool]:
    """Run tracked-input rejection outside the measured assertion call."""
    root = tmp_path / "tracked"
    _topic, state, _record = _inputs(root)
    plan = cast("Path", state.plan)
    home = root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    authored: list[Path] = []
    for name in ("assessment", "report", "changes", "response"):
        path = home / f"a.{name}.md"
        path.write_text(f"{name}.\n", encoding="utf-8")
        authored.append(path)
    _git(root, "add", "-f", ".reviews/a.assessment.md")
    request_output = home / "a.request.md"
    summary_output = home / "a.summary.md"
    code = request_renderer.main(
        [
            "--plan",
            str(plan),
            "--implementation-step",
            "4",
            "--round-number",
            "1",
            "--assessment-file",
            str(authored[0]),
            "--implementation-report-file",
            str(authored[1]),
            "--change-summary-file",
            str(authored[2]),
            "--writer-response-file",
            str(authored[3]),
            "--request-content-output",
            str(request_output),
            "--transcript-summary-output",
            str(summary_output),
        ],
        project_root=root,
    )
    return code, request_output.exists(), summary_output.exists()


def test_tracked_scratch_input_and_output_pair_are_rejected(
    tracked_scratch_result: tuple[int, bool, bool],
) -> None:
    """A tracked authored input cannot produce either request output."""
    code, request_exists, summary_exists = tracked_scratch_result
    assert code == _FATAL
    assert not request_exists
    assert not summary_exists


@pytest.fixture
def bounded_route_inputs(
    tmp_path: Path,
) -> tuple[Path, Topic, WorkflowState, MemoryRecord, Path]:
    """Create the repository and unrelated staged path outside the measured call."""
    root = tmp_path / "bounded"
    topic, state, record = _inputs(root)
    unrelated = root / "unrelated.txt"
    unrelated.write_text("staged but not review identity\n", encoding="utf-8")
    _git(root, "add", "unrelated.txt")
    return root, topic, state, record, unrelated


def test_exact_routing_rejects_scans_transcript_reads_and_unrelated_staging(
    bounded_route_inputs: tuple[Path, Topic, WorkflowState, MemoryRecord, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Routing uses fixed evidence and never treats another staged path as identity."""
    root, topic, state, record, unrelated = bounded_route_inputs
    original_read = Path.read_text
    reads: list[Path] = []

    def forbidden_scan(_path: Path, *_args: object, **_kwargs: object) -> object:
        pytest.fail("directory scan attempted")

    def guarded_read(path: Path, *args: object, **kwargs: object) -> str:
        reads.append(path)
        if path.name.startswith("review."):
            pytest.fail("transcript read attempted")
        reader = cast("Callable[..., str]", original_read)
        return reader(path, *args, **kwargs)

    monkeypatch.setattr(Path, "glob", forbidden_scan)
    monkeypatch.setattr(Path, "rglob", forbidden_scan)
    monkeypatch.setattr(Path, "iterdir", forbidden_scan)
    monkeypatch.setattr(Path, "read_text", guarded_read)
    route = code_review.resolve_code_review_route(root, topic, state, record)
    assert route is not None
    assert route.context.document_path == state.plan
    assert unrelated not in reads
    assert all(not path.name.startswith("review.") for path in reads)


@pytest.fixture
def active_duplicate_review(
    opted_in_inputs: tuple[Path, Topic, WorkflowState, MemoryRecord],
) -> ReviewExchangeCore:
    """Prepare the initial active exchange while leaving duplicate and escalation checks measured."""
    root, topic, state, record = opted_in_inputs
    route = code_review.resolve_code_review_route(root, topic, state, record)
    assert route is not None
    core = ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(root, route.context)),
        route.context,
        code_review.CODE_REVIEW_POLICY,
        ReviewConfiguration(enabled=True),
    )
    core.start()
    return core


def test_duplicate_live_exchange_and_escalation_stay_stopped(
    active_duplicate_review: ReviewExchangeCore,
) -> None:
    """Duplicate starts and escalated evidence cannot gain a second owner."""
    core = active_duplicate_review
    with pytest.raises(ReviewExchangeError, match="already active"):
        core.start()
    record_after = core.escalate("Conflicting live code review identity.")
    assert record_after.status.value == "escalated"
    assert core.classify().state is ArtifactState.ESCALATED
    with pytest.raises(ReviewExchangeError, match="reclaim requires"):
        core.reclaim()


# eof
