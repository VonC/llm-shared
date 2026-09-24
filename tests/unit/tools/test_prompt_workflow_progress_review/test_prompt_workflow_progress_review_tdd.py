"""Contracts for the condensed review status line of `pw progress`.

Each active exchange condenses to its round, what it reviews, and whose move it
is with that role's LLM nature; an empty repository reads
`no review in progress`, and damaged or unavailable status points at `rwst`.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tools import prompt_workflow_progress_review as progress_review
from tools.llm_nature import LlmNature
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ExchangeIdentity,
    ReviewFamily,
    ReviewRole,
)
from tools.review_status_models import (
    SCHEMA_VERSION,
    ArtifactApplicability,
    ArtifactKind,
    ArtifactStatus,
    DamagedCandidateStatus,
    ExchangeStatus,
    LeaseFreshness,
    LeaseStatus,
    MigrationStatus,
    NextAction,
    ReviewStatusOutcome,
    ReviewStatusResult,
    RoleNatureEvidenceStatus,
    RoleNatureStatus,
    RoleSpecialization,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime
    from pathlib import Path

    import pytest

_ROOT = "C:/repositories/status"
_SLUG = "shared-wait-service"


def _artifacts() -> dict[ArtifactKind, ArtifactStatus]:
    """Return one complete artifact map."""
    return {
        kind: ArtifactStatus(
            path=f".reviews/{kind.value}.md",
            applicability=(
                ArtifactApplicability.NOT_APPLICABLE
                if kind in (ArtifactKind.TOMBSTONE, ArtifactKind.TRANSITION_LOCK)
                else ArtifactApplicability.EXPECTED
            ),
            present=kind not in (ArtifactKind.ANSWER, ArtifactKind.TRANSITION_LOCK),
        )
        for kind in ArtifactKind
    }


def _nature(nature: LlmNature) -> RoleNatureStatus:
    return RoleNatureStatus(nature, (RoleNatureEvidenceStatus(".reviews/coordination.md", nature),))


def _code_exchange() -> ExchangeStatus:
    """Return a code exchange waiting for the Codex reviewer."""
    return ExchangeStatus(
        identity=ExchangeIdentity(ReviewFamily.CODE, "code", "v0.13.0", _SLUG),
        reviewed_document=f"docs/v0.13.0/plan.v0.13.0.{_SLUG}.md",
        umbrella=None,
        implementation_step="6",
        round_number=2,
        occurrence=1,
        state=ArtifactState.REQUEST_PENDING,
        diagnostic="request awaits reviewer action",
        continuing_role=ReviewRole.REVIEWER,
        specialization=RoleSpecialization.CODE_REVIEWER,
        owner=Actor.REQUESTOR,
        lease=LeaseStatus(
            renewed_at="2026-09-24T09:00:00+02:00",
            expires_at="2026-09-24T10:00:00+02:00",
            evaluated_at="2026-09-24T09:30:00+02:00",
            timeout_seconds=3600,
            freshness=LeaseFreshness.CURRENT,
        ),
        artifacts=_artifacts(),
        requestor_llm_nature=_nature(LlmNature.CLAUDE),
        reviewer_llm_nature=_nature(LlmNature.CODEX),
        next_action=NextAction.WAIT_FOR_COUNTERPART,
        next_action_text="Wait for the code reviewer answer.",
    )


def _spec_exchange() -> ExchangeStatus:
    """Return a specification exchange of another topic, requestor to move."""
    return replace(
        _code_exchange(),
        identity=ExchangeIdentity(
            ReviewFamily.SPECIFICATION, "design-specification", "v0.13.0", "other",
        ),
        reviewed_document="docs/v0.13.0/design.v0.13.0.other.md",
        implementation_step=None,
        round_number=1,
        state=ArtifactState.ANSWER_PENDING,
        continuing_role=ReviewRole.REQUESTOR,
        specialization=RoleSpecialization.SPECIFICATION_REQUESTOR,
        owner=Actor.REVIEWER,
        reviewer_llm_nature=RoleNatureStatus.unrecorded(),
        next_action=NextAction.REQUESTOR_WORK,
    )


def _result(
    *entries: ExchangeStatus | DamagedCandidateStatus,
    outcome: ReviewStatusOutcome = ReviewStatusOutcome.TRUSTWORTHY,
    migration: MigrationStatus | None = None,
) -> ReviewStatusResult:
    return ReviewStatusResult(
        schema_version=SCHEMA_VERSION,
        repository_root=_ROOT,
        outcome=outcome,
        exchanges=entries,
        active_count=len(entries),
        has_errors=outcome is not ReviewStatusOutcome.TRUSTWORTHY,
        migration=migration or MigrationStatus.unnecessary(".reviews"),
    )


def test_an_empty_repository_has_no_review_in_progress() -> None:
    """No active exchange condenses to one explicit line."""
    assert progress_review.condense(_result(), _SLUG) == ["no review in progress"]


def test_exchanges_name_round_subject_role_and_nature() -> None:
    """The current topic's step review and another topic's design review."""
    lines = progress_review.condense(_result(_code_exchange(), _spec_exchange()), _SLUG)

    assert lines == [
        "round 2 for step 6: wait for code reviewer (codex) response",
        "round 1 for design-specification of other: wait for spec requestor (claude) update",
    ]


def test_gates_and_authorized_work_name_the_human_labels() -> None:
    """Convergence waits for the human choice; an authorized action for its requestor."""
    gate = replace(_code_exchange(), next_action=NextAction.HUMAN_CONFIRMATION)
    spec_gate = replace(_spec_exchange(), next_action=NextAction.HUMAN_CONFIRMATION)
    owning = replace(_code_exchange(), next_action=NextAction.AUTHORIZED_OWNING_WORK)
    stuck = replace(_code_exchange(), next_action=NextAction.RECLAIM, next_action_text="Reclaim it.")

    lines = progress_review.condense(_result(gate, spec_gate, owning, stuck), _SLUG)

    assert lines == [
        "round 2 for step 6: wait for the human choice: Commit, or Rework and review again",
        "round 1 for design-specification of other: wait for the human choice: "
        "Consolidate, "
        "or Revise and review again",
        "round 2 for step 6: wait for code requestor (claude) to finish the authorized Commit",
        "round 2 for step 6: reclaim: Reclaim it.",
    ]


def test_damaged_and_unavailable_status_point_at_rwst() -> None:
    """Damaged candidates are counted; a blocked migration shows its diagnostic."""
    damaged = DamagedCandidateStatus(candidate_path="a.review-active.broken.md", diagnostic="bad")
    blocked = MigrationStatus.blocked(".reviews", ("legacy artifact conflict",))

    assert progress_review.condense(
        _result(damaged, outcome=ReviewStatusOutcome.UNTRUSTWORTHY), None,
    ) == ["1 damaged review candidate(s), run rwst for details"]
    assert progress_review.condense(
        _result(outcome=ReviewStatusOutcome.OPERATIONAL_FAILURE, migration=blocked), None,
    ) == ["review status unavailable (run rwst): legacy artifact conflict"]


def test_review_lines_collect_the_status_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`review_lines` runs the `rwst` collection with a wall clock and condenses it."""
    calls: list[Path] = []

    def fake_collect(root: Path, wall_clock: Callable[[], datetime]) -> ReviewStatusResult:
        calls.append(root)
        assert callable(wall_clock)
        assert wall_clock().tzinfo is not None
        return _result(_code_exchange())

    monkeypatch.setattr(progress_review, "collect_review_status", fake_collect)

    assert progress_review.review_lines(tmp_path, _SLUG) == [
        "round 2 for step 6: wait for code reviewer (codex) response",
    ]
    assert calls == [tmp_path]


# eof
