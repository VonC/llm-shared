"""Tests for strict immutable review-status records and JSON projection."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from typing import cast

import pytest

from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ExchangeIdentity,
    ReviewFamily,
    ReviewRole,
)
from tools.review_status_models import (
    ArtifactApplicability,
    ArtifactKind,
    ArtifactStatus,
    DamagedCandidateStatus,
    ExchangeStatus,
    LeaseFreshness,
    LeaseStatus,
    MigrationStatus,
    NextAction,
    ReviewStatusModelError,
    ReviewStatusOutcome,
    ReviewStatusResult,
    RoleNatureStatus,
    RoleSpecialization,
)

_NOW = "2026-08-30T00:00:00+02:00"
_RENEWED = "2026-08-29T23:30:00+02:00"
_EXPIRES = "2026-08-30T00:30:00+02:00"
_UNTRUSTWORTHY_STATUS = 3
_OPERATIONAL_FAILURE_STATUS = 2


def _identity() -> ExchangeIdentity:
    """Return one valid specification-plan identity."""
    return ExchangeIdentity(
        ReviewFamily.SPECIFICATION,
        "plan",
        "v0.11.0",
        "review-status-command",
    )


def _artifact(kind: ArtifactKind) -> ArtifactStatus:
    """Return one canonical present artifact record."""
    return ArtifactStatus(
        path=f"a.{kind.value}.md",
        applicability=ArtifactApplicability.EXPECTED,
        present=True,
    )


def _artifacts() -> dict[ArtifactKind, ArtifactStatus]:
    """Return all six artifact kinds in deliberately reversed order."""
    return {kind: _artifact(kind) for kind in reversed(tuple(ArtifactKind))}


def _lease() -> LeaseStatus:
    """Return one internally consistent current lease."""
    return LeaseStatus(
        renewed_at=_RENEWED,
        expires_at=_EXPIRES,
        evaluated_at=_NOW,
        timeout_seconds=3600,
        freshness=LeaseFreshness.CURRENT,
    )


def _exchange() -> ExchangeStatus:
    """Return one complete healthy exchange status."""
    return ExchangeStatus(
        identity=_identity(),
        reviewed_document="docs/v0.11.0/plan.v0.11.0.review-status-command.md",
        umbrella="docs/v0.11.0/draft.v0.11.0.review-mode.md",
        implementation_step=None,
        round_number=2,
        occurrence=1,
        state=ArtifactState.REQUEST_PENDING,
        diagnostic="request awaits reviewer action",
        continuing_role=ReviewRole.REVIEWER,
        specialization=RoleSpecialization.SPECIFICATION_REVIEWER,
        owner=Actor.REQUESTOR,
        lease=_lease(),
        artifacts=_artifacts(),
        requestor_llm_nature=RoleNatureStatus.unrecorded(),
        reviewer_llm_nature=RoleNatureStatus.unrecorded(),
        next_action=NextAction.WAIT_FOR_COUNTERPART,
        next_action_text="Wait for the reviewer answer.",
    )


def test_closed_vocabularies_have_exact_wire_values() -> None:
    """Every status vocabulary stays closed and stable for machine consumers."""
    assert tuple(ReviewStatusOutcome) == (
        "trustworthy",
        "untrustworthy",
        "operational-failure",
    )
    assert tuple(LeaseFreshness) == ("current", "expired", "not-held", "missing")
    assert tuple(ArtifactApplicability) == ("expected", "not-applicable")
    assert tuple(NextAction) == (
        "wait-for-counterpart",
        "requestor-work",
        "reviewer-work",
        "human-confirmation",
        "authorized-owning-work",
        "reclaim",
        "repair",
        "resolve-escalation",
        "no-safe-action",
    )
    assert tuple(ArtifactKind) == (
        "request",
        "answer",
        "transcript",
        "coordination",
        "tombstone",
        "transition-lock",
    )


def test_artifact_status_projects_explicit_fields_and_is_immutable() -> None:
    """Artifact evidence keeps applicability separate from observed presence."""
    artifact = ArtifactStatus(
        path="a.review-answer.plan.v0.11.0.topic.md",
        applicability=ArtifactApplicability.NOT_APPLICABLE,
        present=True,
    )

    assert artifact.to_dict() == {
        "path": "a.review-answer.plan.v0.11.0.topic.md",
        "applicability": "not-applicable",
        "present": True,
    }
    with pytest.raises(FrozenInstanceError):
        artifact.present = False  # type: ignore[misc]  # ty: ignore[invalid-assignment]


@pytest.mark.parametrize("path", ["", "/absolute", "../escape", "a\\b", "./a", "a//b"])
def test_artifact_status_rejects_noncanonical_relative_paths(path: str) -> None:
    """Subordinate paths must use canonical repository-relative POSIX form."""
    with pytest.raises(ReviewStatusModelError):
        ArtifactStatus(
            path=path,
            applicability=ArtifactApplicability.EXPECTED,
            present=False,
        )


def test_artifact_status_rejects_untyped_fields() -> None:
    """Runtime construction rejects values that bypass static type checking."""
    with pytest.raises(ReviewStatusModelError, match="applicability"):
        ArtifactStatus(
            path="a.request.md",
            applicability=cast("ArtifactApplicability", "expected"),
            present=True,
        )
    with pytest.raises(ReviewStatusModelError, match="presence"):
        ArtifactStatus(
            path="a.request.md",
            applicability=ArtifactApplicability.EXPECTED,
            present=cast("bool", 1),
        )


def test_current_lease_projects_fixed_reproducible_evidence() -> None:
    """Lease output keeps renewal, expiry, evaluation, and timeout together."""
    assert _lease().to_dict() == {
        "renewed_at": _RENEWED,
        "expires_at": _EXPIRES,
        "evaluated_at": _NOW,
        "timeout_seconds": 3600,
        "freshness": "current",
    }


@pytest.mark.parametrize(
    "changes",
    [
        {"timeout_seconds": 0},
        {"renewed_at": None},
        {"expires_at": None},
        {"expires_at": "2026-08-30T00:29:59+02:00"},
        {"freshness": LeaseFreshness.EXPIRED},
    ],
)
def test_current_lease_rejects_inconsistent_evidence(changes: dict[str, object]) -> None:
    """A derived current lease cannot disagree with its fixed timestamps."""
    with pytest.raises(ReviewStatusModelError):
        replace(_lease(), **changes)


def test_lease_rejects_invalid_timestamp_category_and_cleared_shape() -> None:
    """Lease validation covers malformed time and values outside the typed API."""
    with pytest.raises(ReviewStatusModelError, match="invalid lease evaluation"):
        replace(_lease(), evaluated_at="not-a-timestamp")
    with pytest.raises(ReviewStatusModelError, match="freshness"):
        replace(_lease(), freshness=cast("LeaseFreshness", "current"))
    with pytest.raises(ReviewStatusModelError, match="must not carry"):
        LeaseStatus(
            renewed_at=_RENEWED,
            expires_at=None,
            evaluated_at=_NOW,
            timeout_seconds=3600,
            freshness=LeaseFreshness.NOT_HELD,
        )


@pytest.mark.parametrize("freshness", [LeaseFreshness.NOT_HELD, LeaseFreshness.MISSING])
def test_unheld_and_missing_leases_require_absent_lease_timestamps(
    freshness: LeaseFreshness,
) -> None:
    """States without lease evidence expose null renewal and expiry together."""
    lease = LeaseStatus(None, None, _NOW, 3600, freshness)

    assert lease.renewed_at is None
    assert lease.expires_at is None


def test_exchange_status_has_exact_tagged_projection_and_frozen_artifacts() -> None:
    """A healthy entry emits the complete stable schema in canonical key order."""
    exchange = _exchange()

    assert exchange.to_dict() == {
        "kind": "exchange",
        "identity": _identity().to_dict(),
        "reviewed_document": "docs/v0.11.0/plan.v0.11.0.review-status-command.md",
        "umbrella": "docs/v0.11.0/draft.v0.11.0.review-mode.md",
        "implementation_step": None,
        "round": 2,
        "occurrence": 1,
        "state": "request-pending",
        "diagnostic": "request awaits reviewer action",
        "continuing_role": "reviewer",
        "specialization": "specification-reviewer",
        "owner": "requestor",
        "lease": _lease().to_dict(),
        "artifacts": {kind.value: _artifact(kind).to_dict() for kind in ArtifactKind},
        "requestor_llm_nature": "unrecorded",
        "requestor_llm_nature_evidence": [],
        "reviewer_llm_nature": "unrecorded",
        "reviewer_llm_nature_evidence": [],
        "next_action": "wait-for-counterpart",
        "next_action_text": "Wait for the reviewer answer.",
    }
    with pytest.raises(TypeError):
        exchange.artifacts[ArtifactKind.REQUEST] = _artifact(  # type: ignore[index]  # ty: ignore[invalid-assignment]
            ArtifactKind.REQUEST,
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"round_number": 0},
        {"occurrence": 0},
        {"state": ArtifactState.IDLE},
        {"continuing_role": ReviewRole.HUMAN},
        {"specialization": RoleSpecialization.SPECIFICATION_REQUESTOR},
        {"implementation_step": "1"},
        {"reviewed_document": "C:/absolute.md"},
        {"artifacts": {ArtifactKind.REQUEST: _artifact(ArtifactKind.REQUEST)}},
    ],
)
def test_exchange_status_rejects_inconsistent_healthy_evidence(
    changes: dict[str, object],
) -> None:
    """Healthy entries reject missing, inactive, or identity-conflicting facts."""
    with pytest.raises(ReviewStatusModelError):
        replace(_exchange(), **changes)


def test_exchange_status_rejects_untyped_identity_action_and_human_owner() -> None:
    """Healthy entries reject values that evade their static field types."""
    with pytest.raises(ReviewStatusModelError, match="identity"):
        replace(_exchange(), identity=cast("ExchangeIdentity", object()))
    with pytest.raises(ReviewStatusModelError, match="next action"):
        replace(_exchange(), next_action=cast("NextAction", "wait-for-counterpart"))
    with pytest.raises(ReviewStatusModelError, match="owner"):
        replace(_exchange(), owner=Actor.HUMAN)
    with pytest.raises(ReviewStatusModelError, match="requestor"):
        replace(
            _exchange(),
            requestor_llm_nature=cast("RoleNatureStatus", "unrecorded"),
        )
    with pytest.raises(ReviewStatusModelError, match="reviewer"):
        replace(
            _exchange(),
            reviewer_llm_nature=cast("RoleNatureStatus", "unrecorded"),
        )


def test_code_exchange_requires_and_accepts_an_implementation_step() -> None:
    """Code-family entries exercise their family-specific step boundary."""
    code_identity = ExchangeIdentity(
        ReviewFamily.CODE,
        "code",
        "v0.11.0",
        "review-status-command",
    )

    with pytest.raises(ReviewStatusModelError, match="implementation step"):
        replace(
            _exchange(),
            identity=code_identity,
            specialization=RoleSpecialization.CODE_REVIEWER,
        )
    code_exchange = replace(
        _exchange(),
        identity=code_identity,
        implementation_step="1",
        specialization=RoleSpecialization.CODE_REVIEWER,
    )

    assert code_exchange.implementation_step == "1"


def test_damaged_candidate_keeps_only_candidate_evidence() -> None:
    """A damaged entry is separately tagged and may omit untrusted identity."""
    damaged = DamagedCandidateStatus(
        candidate_path="a.review-active.bad-name.md",
        diagnostic="candidate identity is malformed",
    )

    assert damaged.to_dict() == {
        "kind": "damaged-candidate",
        "candidate_path": "a.review-active.bad-name.md",
        "identity": None,
        "diagnostic": "candidate identity is malformed",
    }
    assert replace(damaged, candidate_identity=_identity()).to_dict()["identity"] == (
        _identity().to_dict()
    )


@pytest.mark.parametrize(
    "changes",
    [{"candidate_path": "../bad"}, {"diagnostic": ""}, {"candidate_identity": "guess"}],
)
def test_damaged_candidate_rejects_guessed_or_incomplete_evidence(
    changes: dict[str, object],
) -> None:
    """Damaged records never accept a free-form guessed exchange identity."""
    with pytest.raises(ReviewStatusModelError):
        replace(
            DamagedCandidateStatus("a.review-active.bad.md", "bad candidate"),
            **changes,
        )


def test_repository_result_projects_schema_and_process_status() -> None:
    """One result owns stable schema, counts, errors, entries, and exit status."""
    trustworthy = ReviewStatusResult(
        schema_version=2,
        repository_root="C:/work/project",
        outcome=ReviewStatusOutcome.TRUSTWORTHY,
        exchanges=(_exchange(),),
        active_count=1,
        has_errors=False,
        migration=MigrationStatus.unnecessary(".reviews"),
    )
    damaged = DamagedCandidateStatus("a.review-active.bad.md", "bad candidate")
    untrustworthy = ReviewStatusResult(
        schema_version=2,
        repository_root="C:/work/project",
        outcome=ReviewStatusOutcome.UNTRUSTWORTHY,
        exchanges=(_exchange(), damaged),
        active_count=2,
        has_errors=True,
        migration=MigrationStatus.unnecessary(".reviews"),
    )
    operational = ReviewStatusResult(
        schema_version=2,
        repository_root="C:/work/project",
        outcome=ReviewStatusOutcome.OPERATIONAL_FAILURE,
        exchanges=(),
        active_count=0,
        has_errors=True,
        migration=MigrationStatus.blocked(".reviews", ("unreadable",)),
    )

    assert trustworthy.process_status == 0
    assert untrustworthy.process_status == _UNTRUSTWORTHY_STATUS
    assert operational.process_status == _OPERATIONAL_FAILURE_STATUS
    assert trustworthy.to_dict() == {
        "schema_version": 2,
        "repository_root": "C:/work/project",
        "outcome": "trustworthy",
        "active_count": 1,
        "has_errors": False,
        "migration": {
            "state": "unnecessary",
            "artifact_home": ".reviews",
            "moved_count": 0,
            "diagnostics": [],
        },
        "exchanges": [_exchange().to_dict()],
    }


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": 3},
        {"repository_root": "relative/root"},
        {"active_count": 0},
        {"has_errors": True},
        {"outcome": ReviewStatusOutcome.UNTRUSTWORTHY, "has_errors": False},
        {"outcome": ReviewStatusOutcome.OPERATIONAL_FAILURE, "has_errors": True},
    ],
)
def test_repository_result_rejects_inconsistent_aggregate_evidence(
    changes: dict[str, object],
) -> None:
    """Aggregate flags and counts cannot contradict the ordered entries."""
    result = ReviewStatusResult(
        schema_version=2,
        repository_root="C:/work/project",
        outcome=ReviewStatusOutcome.TRUSTWORTHY,
        exchanges=(_exchange(),),
        active_count=1,
        has_errors=False,
        migration=MigrationStatus.unnecessary(".reviews"),
    )

    with pytest.raises(ReviewStatusModelError):
        replace(result, **changes)


def test_repository_result_rejects_values_outside_its_typed_boundary() -> None:
    """Aggregate construction checks runtime callers as well as typed callers."""
    result = ReviewStatusResult(
        schema_version=2,
        repository_root="C:/work/project",
        outcome=ReviewStatusOutcome.TRUSTWORTHY,
        exchanges=(_exchange(),),
        active_count=1,
        has_errors=False,
        migration=MigrationStatus.unnecessary(".reviews"),
    )

    with pytest.raises(ReviewStatusModelError, match="outcome"):
        replace(result, outcome=cast("ReviewStatusOutcome", "trustworthy"))
    with pytest.raises(ReviewStatusModelError, match="tuple"):
        replace(
            result,
            exchanges=cast("tuple[ExchangeStatus, ...]", [_exchange()]),
        )
    with pytest.raises(ReviewStatusModelError, match="boolean"):
        replace(result, has_errors=cast("bool", 0))
    with pytest.raises(ReviewStatusModelError, match="migration"):
        replace(result, migration=cast("MigrationStatus", "unnecessary"))
    with pytest.raises(ReviewStatusModelError, match="retained evidence"):
        ReviewStatusResult(
            schema_version=2,
            repository_root="C:/work/project",
            outcome=ReviewStatusOutcome.UNTRUSTWORTHY,
            exchanges=(),
            active_count=0,
            has_errors=True,
            migration=MigrationStatus.unnecessary(".reviews"),
        )


def test_trustworthy_result_rejects_a_damaged_candidate() -> None:
    """A trustworthy outcome cannot hide an untrusted candidate entry."""
    damaged = DamagedCandidateStatus("a.review-active.bad.md", "bad candidate")

    with pytest.raises(ReviewStatusModelError, match="damaged"):
        ReviewStatusResult(
            schema_version=2,
            repository_root="C:/work/project",
            outcome=ReviewStatusOutcome.TRUSTWORTHY,
            exchanges=(damaged,),
            active_count=1,
            has_errors=False,
            migration=MigrationStatus.unnecessary(".reviews"),
        )


# eof
