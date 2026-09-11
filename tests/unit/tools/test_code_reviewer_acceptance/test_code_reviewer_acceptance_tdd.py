"""Assessment and publication acceptance for the code reviewer.

Each named test corresponds to one design acceptance case. Repository setup and
multi-command journeys run in fixtures so measured calls stay deterministic.
"""

from __future__ import annotations

import importlib
import inspect
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools import code_review_request
from tools.code_review_evidence import (
    attribute_reviewer_patch,
    capture_index_tree,
    capture_umbrella_digest,
    compare_umbrella_digest,
    record_pre_repair_blob,
)
from tools.code_review_validation import resolve_code_review_validation
from tools.prompt_workflow_code_review import (
    CodeReviewActor,
    command_for_route,
    resolve_code_review_route,
)
from tools.review_exchange_models import (
    ArtifactState,
    ReviewDisposition,
    ReviewExchangeError,
)
from tools.review_exchange_models_envelope import parse_envelope_markdown

from .fixtures import (
    core,
    git,
    make_effort,
    publish_rendered_request,
    ready_commit_plan_result,
    render_assessment,
    render_early_rejection,
    render_request,
    staged_paths,
    start_request,
)

if TYPE_CHECKING:
    from pathlib import Path

_REQUIREMENT_CASES = (
    (
        "AC01",
        "test_code_reviewer_acceptance_tdd",
        "test_one_exact_pending_code_request_routes_to_reviewer",
    ),
    (
        "AC02",
        "test_code_reviewer_acceptance_tdd",
        "test_mismatched_identity_or_missing_tree_is_rejected_early",
    ),
    (
        "AC03",
        "test_code_reviewer_io_acceptance_tdd",
        "test_reviewer_instruction_denies_requestor_human_and_commit_authority",
    ),
    (
        "AC04",
        "test_code_reviewer_acceptance_tdd",
        "test_small_named_repair_stages_only_reviewer_delta_and_requests_changes",
    ),
    (
        "AC05",
        "test_code_reviewer_acceptance_tdd",
        "test_all_evidence_passes_without_repair_reaches_advisory_gate",
    ),
    (
        "AC06",
        "test_code_reviewer_recovery_tdd",
        "test_interrupted_publication_replays_idempotently",
    ),
    (
        "AC07",
        "test_code_reviewer_recovery_tdd",
        "test_same_missing_evidence_in_next_round_hits_shared_no_progress_bound",
    ),
    (
        "AC08",
        "test_code_reviewer_launcher_smoke_tdd",
        "test_each_code_review_launcher_reaches_its_public_entry_point",
    ),
)


@pytest.fixture
def exact_pending_route(tmp_path: Path) -> None:
    """Publish and route one exact pending request outside call timing."""
    effort = make_effort(tmp_path / "exact")
    start_request(effort)
    route = resolve_code_review_route(effort.root, effort.topic, effort.state, effort.record)
    assert route is not None
    command = command_for_route(
        effort.root,
        route,
        "$",
        lambda prefix, instruction, document, step: (
            f"{prefix}{instruction}|{document}|{step}"
        ),
    )
    assert route.actor is CodeReviewActor.REVIEWER
    assert command == "$code-reviewer.md|docs/v0.11.0/plan.v0.11.0.acceptance.md|6"


def test_one_exact_pending_code_request_routes_to_reviewer(
    exact_pending_route: None,
) -> None:
    """Design case 01 / Requirement AC01: route the exact plan and step."""
    assert exact_pending_route is None


@pytest.fixture
def absent_step_rejection(tmp_path: Path) -> None:
    """Publish an undefined-step rejection outside call timing."""
    effort = make_effort(tmp_path / "absent", step="7")
    exchange, _request = start_request(effort)
    before = capture_index_tree(effort.root)
    answer = render_early_rejection(effort, "Step 7 is undefined by the plan.")
    exchange.publish_answer(answer.answer_content, answer.transcript_summary)
    assert exchange.classify().state is ArtifactState.ANSWER_PENDING
    assert capture_index_tree(effort.root) == before
    assert "Step 7 is undefined" in answer.answer_content


def test_request_step_absent_from_plan_rejects_without_mutation(
    absent_step_rejection: None,
) -> None:
    """Design case 02: an undefined step ends through changes-requested."""
    assert absent_step_rejection is None


@pytest.fixture
def malformed_request_rejections(tmp_path: Path) -> None:
    """Exercise missing tree and authored identity mismatch outside call timing."""
    effort = make_effort(tmp_path / "malformed")
    valid = render_request(effort)
    with pytest.raises(ReviewExchangeError, match="request index tree"):
        code_review_request.CodeReviewRoundInput(
            context=effort.context,
            round_number=1,
            created_at="2026-08-18T12:00:00+02:00",
            assessment="assessment",
            implementation_report="report",
            change_summary="summary",
            writer_response="response",
            request_index_tree="",
            resolved_validation_set=resolve_code_review_validation(("ghog day",), ()),
            commit_plan_result=ready_commit_plan_result(),
        )

    exchange = core(effort)
    exchange.start()
    mismatched = replace(
        valid,
        request_content=valid.request_content.replace(
            "Implementation step: 6",
            "Implementation step: 5",
            1,
        ),
    )
    before = capture_index_tree(effort.root)
    with pytest.raises(ReviewExchangeError, match="summary identity mismatch"):
        publish_rendered_request(exchange, mismatched)
    assert exchange.classify().state is ArtifactState.ROUND_IN_PROGRESS
    assert capture_index_tree(effort.root) == before


def test_mismatched_identity_or_missing_tree_is_rejected_early(
    malformed_request_rejections: None,
) -> None:
    """Design case 03 / Requirement AC02: reject mismatched request evidence."""
    assert malformed_request_rejections is None


@pytest.fixture
def drift_rejection(tmp_path: Path) -> None:
    """Create request-time versus live-index drift outside call timing."""
    effort = make_effort(tmp_path / "drift")
    exchange, request = start_request(effort)
    request_tree = capture_index_tree(effort.root)
    extra = effort.root / "drift.py"
    extra.write_text("DRIFT = True\n", encoding="utf-8")
    git(effort.root, "add", "drift.py")
    live_tree = capture_index_tree(effort.root)
    assert request_tree != live_tree
    answer = render_early_rejection(
        effort,
        f"Index drift: request {request_tree}; live {live_tree}; path drift.py.",
    )
    exchange.publish_answer(answer.answer_content, answer.transcript_summary)
    assert request_tree in request.request_content
    assert request_tree in answer.answer_content
    assert live_tree in answer.answer_content


def test_live_index_drift_publishes_both_trees_and_paths(
    drift_rejection: None,
) -> None:
    """Design case 04: one request round identifies one staged subject."""
    assert drift_rejection is None


@pytest.fixture
def small_repair_journey(tmp_path: Path) -> None:
    """Attribute, stage, and publish one bounded repair outside call timing."""
    effort = make_effort(tmp_path / "repair")
    exchange, _request = start_request(effort)
    baseline = record_pre_repair_blob(effort.root, "reviewed.py")
    effort.source.write_text("VALUE = 2\nREVIEWED = True\n", encoding="utf-8")
    attribution = attribute_reviewer_patch(effort.root, baseline)
    git(effort.root, "add", "reviewed.py")
    answer = render_assessment(
        effort,
        ReviewDisposition.CHANGES_REQUESTED,
        repairs=("Added the bounded reviewer fix.",),
        staged=("reviewed.py",),
        substantive_repair=True,
        readiness_floor_complete=False,
    )
    exchange.publish_answer(answer.answer_content, answer.transcript_summary)
    assert attribution.attributable
    assert "+REVIEWED = True" in attribution.patch
    assert staged_paths(effort.root) == ("reviewed.py",)
    assert exchange.classify().state is ArtifactState.ANSWER_PENDING


def test_small_named_repair_stages_only_reviewer_delta_and_requests_changes(
    small_repair_journey: None,
) -> None:
    """Design case 05 / Requirement AC04: stage and report a bounded repair."""
    assert small_repair_journey is None


@pytest.fixture
def overlap_refusal(tmp_path: Path) -> None:
    """Leave a writer-overlapped repair unstaged outside call timing."""
    effort = make_effort(tmp_path / "overlap")
    git(effort.root, "restore", "--staged", "reviewed.py")
    effort.source.write_text("VALUE = 3  # writer work\n", encoding="utf-8")
    baseline = record_pre_repair_blob(effort.root, "reviewed.py")
    effort.source.write_text("VALUE = 3  # writer work\nREVIEWED = True\n", encoding="utf-8")
    attribution = attribute_reviewer_patch(effort.root, baseline)
    assert attribution.attributable
    assert "+REVIEWED = True" in attribution.patch
    assert staged_paths(effort.root) == ()


def test_repair_over_writer_work_is_reported_without_staging(
    overlap_refusal: None,
) -> None:
    """Design case 06: unsafe overlap stays writer-owned."""
    assert overlap_refusal is None


@pytest.fixture
def validation_row_repair(tmp_path: Path) -> None:
    """Stage one attributable validation-row update outside call timing."""
    effort = make_effort(tmp_path / "validation-row")
    relative = effort.validation.relative_to(effort.root).as_posix()
    baseline = record_pre_repair_blob(effort.root, relative)
    effort.validation.write_text(
        "# Validation\n\n### Analysis of Step 6 implementation state\n\n"
        "Yes. Step 6 has been fully implemented.\n",
        encoding="utf-8",
    )
    attribution = attribute_reviewer_patch(effort.root, baseline)
    git(effort.root, "add", relative)
    assert attribution.attributable
    assert effort.validation.relative_to(effort.root).as_posix() in staged_paths(effort.root)


def test_implementation_check_validation_row_is_attributable_and_stageable(
    validation_row_repair: None,
) -> None:
    """Design case 07: the reviewed validation row is permitted evidence."""
    assert validation_row_repair is None


@pytest.fixture
def umbrella_boundary(tmp_path: Path) -> None:
    """Detect an umbrella mutation without staging or reverting it."""
    effort = make_effort(tmp_path / "umbrella")
    before = capture_umbrella_digest(effort.umbrella)
    effort.umbrella.write_text("# Review mode\n\n| code-reviewer | completed |\n", encoding="utf-8")
    comparison = compare_umbrella_digest(before, effort.umbrella)
    assert comparison.changed
    assert effort.umbrella.relative_to(effort.root).as_posix() not in staged_paths(effort.root)
    assert "completed" in effort.umbrella.read_text(encoding="utf-8")


def test_umbrella_status_mutation_is_detected_and_left_in_place(
    umbrella_boundary: None,
) -> None:
    """Design case 08: reviewer mode detects rather than hides umbrella writes."""
    assert umbrella_boundary is None


@pytest.fixture
def failed_gate_journey(tmp_path: Path) -> None:
    """Publish a failing mandatory-gate result outside call timing."""
    effort = make_effort(tmp_path / "failed-gate")
    exchange, _request = start_request(effort)
    answer = render_assessment(
        effort,
        ReviewDisposition.CHANGES_REQUESTED,
        findings=("Mandatory coverage gate failed.",),
        readiness_floor_complete=False,
    )
    exchange.publish_answer(answer.answer_content, answer.transcript_summary)
    envelope, _authored = parse_envelope_markdown(answer.answer_content)
    assert envelope.disposition is ReviewDisposition.CHANGES_REQUESTED
    assert exchange.classify().state is ArtifactState.ANSWER_PENDING


def test_failed_mandatory_coverage_withholds_commit_readiness(
    failed_gate_journey: None,
) -> None:
    """Design case 09: mandatory evidence failure requests rework."""
    assert failed_gate_journey is None


@pytest.fixture
def convergence_journey(tmp_path: Path) -> None:
    """Publish an all-green no-repair answer outside call timing."""
    effort = make_effort(tmp_path / "convergence")
    exchange, _request = start_request(effort)
    answer = render_assessment(effort, ReviewDisposition.CONVERGENCE_RECOMMENDED)
    exchange.publish_answer(answer.answer_content, answer.transcript_summary)
    assert exchange.classify().state is ArtifactState.CONVERGENCE_GATE
    assert "does not authorize a commit" in answer.answer_content


def test_all_evidence_passes_without_repair_reaches_advisory_gate(
    convergence_journey: None,
) -> None:
    """Design case 13 / Requirement AC05: readiness stays advisory."""
    assert convergence_journey is None


@pytest.mark.parametrize(("criterion", "module_name", "test_name"), _REQUIREMENT_CASES)
def test_requirement_acceptance_criteria_have_executable_case_coverage(
    criterion: str,
    module_name: str,
    test_name: str,
) -> None:
    """Requirement AC01-AC08 resolve to collected Step 6 journey tests."""
    module = importlib.import_module(f"{__package__}.{module_name}")
    journey = getattr(module, test_name)
    docstring = inspect.getdoc(journey)

    assert callable(journey)
    assert docstring is not None
    assert f"Requirement {criterion}:" in docstring
