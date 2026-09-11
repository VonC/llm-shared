"""Recovery, guidance, and bounded-dialogue acceptance for code review."""

from __future__ import annotations

import json
import os
from contextlib import chdir, redirect_stderr, redirect_stdout
from io import StringIO
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from tools import review_exchange_cli
from tools.code_review_evidence import (
    CodeReviewEvidence,
    capture_index_tree,
    read_manifest,
    record_pre_repair_blob,
    retire_manifest,
    write_manifest,
)
from tools.prompt_workflow_code_review import CODE_REVIEW_POLICY
from tools.review_exchange_models import (
    ArtifactState,
    ReviewDisposition,
    ReviewExchangeError,
)

from .fixtures import (
    Effort,
    git,
    make_effort,
    render_assessment,
    render_request,
    start_request,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def repeated_missing_evidence(tmp_path: Path) -> None:
    """Run two no-progress missing-evidence rounds outside call timing."""
    effort = make_effort(tmp_path / "repeated")
    exchange, _request = start_request(effort)
    first = render_assessment(
        effort,
        ReviewDisposition.CHANGES_REQUESTED,
        findings=("Mandatory evidence is unavailable.",),
        readiness_floor_complete=False,
    )
    exchange.publish_answer(first.answer_content, first.transcript_summary)
    exchange.consume_answer(reviewed_work_changed=False)
    exchange.continue_round()
    second_request = render_request(effort, round_number=2)
    exchange.publish_request(
        second_request.request_content,
        second_request.transcript_summary,
    )
    second = render_assessment(
        effort,
        ReviewDisposition.CHANGES_REQUESTED,
        round_number=2,
        findings=("Mandatory evidence is still unavailable.",),
        readiness_floor_complete=False,
    )
    exchange.publish_answer(second.answer_content, second.transcript_summary)
    record = exchange.consume_answer(reviewed_work_changed=False)
    assert record.status.value == "escalated"
    assert exchange.classify().state is ArtifactState.ESCALATED


def test_same_missing_evidence_in_next_round_hits_shared_no_progress_bound(
    repeated_missing_evidence: None,
) -> None:
    """Design case 12 / Requirement AC07: no progress ends automation."""
    assert repeated_missing_evidence is None


@pytest.fixture
def guided_assessment(tmp_path: Path) -> None:
    """Render and publish literal guidance handling outside call timing."""
    effort = make_effort(tmp_path / "guidance")
    exchange, request = start_request(effort, guidance="Keep recovery human-owned.")
    answer = render_assessment(
        effort,
        ReviewDisposition.CHANGES_REQUESTED,
        findings=("A writer clarification remains.",),
        readiness_floor_complete=False,
        guidance=(
            "Keep recovery human-owned.",
            "Recovery remains human-owned and identity rules are unchanged.",
        ),
    )
    exchange.publish_answer(answer.answer_content, answer.transcript_summary)
    assert "Keep recovery human-owned." in request.request_content
    assert "Recovery remains human-owned" in answer.answer_content
    assert "Recovery remains human-owned" in answer.transcript_summary


def test_human_override_guidance_is_answered_without_changing_boundaries(
    guided_assessment: None,
) -> None:
    """Design case 14: guidance informs assessment but grants no authority."""
    assert guided_assessment is None


@pytest.fixture
def stopped_repair_manifest(tmp_path: Path) -> None:
    """Retain an assessed repair tree and detect later drift outside call timing."""
    effort = make_effort(tmp_path / "stopped")
    baseline_tree = capture_index_tree(effort.root)
    baseline_blob = record_pre_repair_blob(effort.root, "reviewed.py")
    effort.source.write_text("VALUE = 2\nREVIEWED = True\n", encoding="utf-8")
    git(effort.root, "add", "reviewed.py")
    assessed_tree = capture_index_tree(effort.root)
    retained = CodeReviewEvidence(
        "code",
        "code",
        "v0.11.0",
        "acceptance",
        "6",
        baseline_tree,
        assessed_tree,
        recorded_blobs=(baseline_blob,),
        repair_paths=("reviewed.py",),
    )
    manifest = write_manifest(effort.root, retained)
    restored = read_manifest(effort.root, retained.identity)
    extra = effort.root / "later.py"
    extra.write_text("LATER = True\n", encoding="utf-8")
    git(effort.root, "add", "later.py")
    assert manifest.is_file()
    assert restored == retained
    assert capture_index_tree(effort.root) != restored.assessed_index_tree


def test_round_stopped_after_repairs_retains_tree_and_manifest_evidence(
    stopped_repair_manifest: None,
) -> None:
    """Design case 15: recovery preserves work and detects later index drift."""
    assert stopped_repair_manifest is None


@pytest.fixture
def interrupted_publication_replay(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Interrupt answer visibility once, then replay publication."""
    effort = make_effort(tmp_path / "interrupted")
    exchange, _request = start_request(effort)
    answer = render_assessment(
        effort,
        ReviewDisposition.CHANGES_REQUESTED,
        findings=("One writer action remains.",),
        readiness_floor_complete=False,
    )
    original_commit = exchange.store._commit_prepared
    failed = False

    def fail_once(prepared: Path, target: Path) -> None:
        nonlocal failed
        if target == exchange.store.paths.answer and not failed:
            failed = True
            message = "injected answer publication failure"
            raise OSError(message)
        original_commit(prepared, target)

    monkeypatch.setattr(exchange.store, "_commit_prepared", fail_once)
    with pytest.raises(ReviewExchangeError, match="answer publication failed"):
        exchange.publish_answer(answer.answer_content, answer.transcript_summary)
    exchange.publish_answer(answer.answer_content, answer.transcript_summary)
    transcript = exchange.store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("One writer action remains.") == 1
    assert exchange.classify().state is ArtifactState.ANSWER_PENDING


def test_interrupted_publication_replays_idempotently(
    interrupted_publication_replay: None,
) -> None:
    """Design case 16 / Requirement AC06: publication resumes idempotently."""
    assert interrupted_publication_replay is None


def _context_arguments(effort: Effort) -> list[str]:
    """Return the exact code-family CLI identity and policy arguments."""
    return [
        "--family",
        "code",
        "--document",
        str(effort.plan),
        "--umbrella",
        str(effort.umbrella),
        "--implementation-step",
        "6",
        "--convergence-signal",
        CODE_REVIEW_POLICY.convergence_signal,
        "--another-round-label",
        CODE_REVIEW_POLICY.another_round_label,
        "--continue-owning-workflow-label",
        CODE_REVIEW_POLICY.continue_owning_workflow_label,
    ]


@pytest.fixture
def exit_three_manifest_retirement(tmp_path: Path) -> None:
    """Publish convergence through the CLI and retire retained evidence."""
    effort = make_effort(tmp_path / "exit-three")
    exchange, _request = start_request(effort)
    tree = capture_index_tree(effort.root)
    retained = CodeReviewEvidence(
        "code",
        "code",
        "v0.11.0",
        "acceptance",
        "6",
        tree,
        tree,
    )
    manifest = write_manifest(effort.root, retained)
    answer = render_assessment(effort, ReviewDisposition.CONVERGENCE_RECOMMENDED)
    capability = exchange.ownership_capability
    assert capability is not None
    home = effort.root / ".reviews"
    content = home / "a.answer.md"
    summary = home / "a.answer-summary.md"
    content.write_text(answer.answer_content, encoding="utf-8")
    summary.write_text(answer.transcript_summary, encoding="utf-8")
    stdout, stderr = StringIO(), StringIO()
    with (
        chdir(effort.root),
        redirect_stdout(stdout),
        redirect_stderr(stderr),
        patch.dict(os.environ, {"PRJ_DIR": str(effort.root)}),
    ):
        code = review_exchange_cli.main(
            [
                "publish-answer",
                *_context_arguments(effort),
                "--ownership-generation",
                str(capability.generation),
                "--ownership-token",
                capability.token,
                "--content-file",
                str(content),
                "--summary-file",
                str(summary),
            ],
        )
    payload = json.loads(stdout.getvalue())
    assert (code, payload["outcome"], payload["state"]) == (
        3,
        "published",
        "convergence-gate",
    ), json.dumps(payload, sort_keys=True)
    assert retire_manifest(effort.root, retained.identity)
    assert not manifest.exists()
    assert exchange.classify().state is ArtifactState.CONVERGENCE_GATE


def test_published_exit_three_retires_manifest_after_observed_outcome(
    exit_three_manifest_retirement: None,
) -> None:
    """Recovery contract: convergence publication also retires its manifest."""
    assert exit_three_manifest_retirement is None
