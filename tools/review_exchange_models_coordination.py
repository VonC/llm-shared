"""Durable coordination model for the v0.11.0 review-exchange core.

Step 3 adds a monotonic ownership generation and token digest while retaining
legacy parsing for records that predate role-nature or ownership evidence. A
plaintext ownership token is never represented by this durable model.

Fix (v0.14.0 resume-paused, Step 4): an optional ``marked_claim`` records the
non-secret evidence of a marked resume claim, launch id, receiving pane, host,
assignment binding, round and occurrence, with the generation it was issued
with. It must equal the record's ownership generation, so it rides through
current-owner transitions and a newly issued claim clears or replaces it.
Records without the key parse as before.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

from tools.review_exchange_models import (
    Actor,
    ConfirmationOutcome,
    CoordinationStatus,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewContext,
    ReviewExchangeError,
    enum_value,
    mapping_value,
    non_negative_integer,
    optional_boolean,
    optional_string,
    positive_integer,
    strict_fields,
    validate_local_timestamp,
)
from tools.review_role_nature import RoleNatureSnapshot

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


def _validate_coordination_status(record: CoordinationRecord) -> None:
    """Validate lease and expected-actor rules for the durable status."""
    if record.status is CoordinationStatus.ACTIVE and record.lease_renewed_at is None:
        raise ReviewExchangeError("active coordination requires a lease timestamp")
    if (
        record.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
        and record.expected_next_actor is not Actor.HUMAN
    ):
        raise ReviewExchangeError("confirmation status requires human as next actor")
    if record.status is not CoordinationStatus.ESCALATED:
        return
    if not record.escalation_reason:
        raise ReviewExchangeError("escalated coordination requires a reason")
    if record.lease_renewed_at is not None:
        raise ReviewExchangeError("escalated coordination cannot carry an active lease")


def _validate_incomplete_transition(record: CoordinationRecord) -> None:
    """Validate the all-or-none transcript repair marker fields."""
    fields = (
        record.incomplete_transition,
        record.transcript_entry_id,
        record.transcript_offset,
    )
    if not any(value is not None for value in fields):
        return
    if not all(value is not None for value in fields):
        raise ReviewExchangeError(
            "incomplete transition fields must be recorded together",
        )
    offset = cast("int", record.transcript_offset)
    non_negative_integer(offset, "transcript offset")


def _validate_confirmation(record: CoordinationRecord) -> None:
    """Validate the all-or-none human confirmation fields."""
    fields = (
        record.confirmation_label,
        record.confirmed_outcome,
        record.confirmation_timestamp,
    )
    if not any(value is not None for value in fields):
        return
    if not all(value is not None for value in fields):
        raise ReviewExchangeError("confirmation fields must be recorded together")
    timestamp = cast("str", record.confirmation_timestamp)
    validate_local_timestamp(timestamp)


_OWNERSHIP_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def _validate_ownership(record: CoordinationRecord) -> None:
    """Validate the all-or-none ownership generation and digest pair."""
    generation = record.ownership_generation
    digest = record.ownership_token_digest
    non_negative_integer(generation, "ownership generation")
    if generation == 0 and digest is None:
        return
    if generation == 0 or digest is None:
        raise ReviewExchangeError("ownership fields must be recorded together")
    if _OWNERSHIP_DIGEST_RE.fullmatch(digest) is None:
        raise ReviewExchangeError("invalid ownership token digest")


def _ownership_from_mapping(
    data: Mapping[str, Any],
    expected: set[str],
) -> tuple[int, str | None]:
    """Parse the optional legacy ownership pair outside the main constructor."""
    has_generation = "ownership_generation" in data
    has_digest = "ownership_token_digest" in data
    if has_generation != has_digest:
        raise ReviewExchangeError("ownership fields must be recorded together")
    if not has_generation:
        return 0, None
    expected.update({"ownership_generation", "ownership_token_digest"})
    return (
        non_negative_integer(data["ownership_generation"], "ownership generation"),
        optional_string(data["ownership_token_digest"], "ownership token digest"),
    )


_LAUNCH_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_PANE_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_HOST_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_MARKED_CLAIM_KEYS = frozenset({
    "launch_id", "pane_id", "host", "assignment_binding", "round", "occurrence", "issued_generation",
})


def _spelled(pattern: re.Pattern[str], value: object) -> bool:
    """Return whether one parsed value is a string in its strict spelling."""
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _marked_positive(value: object, label: str) -> int:
    """Return one positive JSON integer of a marked claim, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ReviewExchangeError(f"invalid marked claim {label}")
    return value


@dataclass(frozen=True)
class MarkedClaimEvidence:
    """Non-secret evidence of one marked resume claim, before its generation is issued."""

    launch_id: str
    pane_id: str
    host: str
    assignment_binding: str
    round_number: int
    occurrence: int

    def __post_init__(self) -> None:
        """Refuse any field outside its strict spelling."""
        checks = (
            (_LAUNCH_ID_RE, self.launch_id, "launch id"),
            (_PANE_ID_RE, self.pane_id, "receiving pane"),
            (_HOST_RE, self.host, "host"),
            (_OWNERSHIP_DIGEST_RE, self.assignment_binding, "assignment binding"),
        )
        for pattern, value, label in checks:
            if not _spelled(pattern, value):
                raise ReviewExchangeError(f"invalid marked claim {label}")
        _marked_positive(self.round_number, "round")
        _marked_positive(self.occurrence, "occurrence")

    def issued(self, generation: int) -> MarkedClaimBinding:
        """Bind this evidence to the ownership generation just issued for it."""
        return MarkedClaimBinding(self, generation)


@dataclass(frozen=True)
class MarkedClaimBinding:
    """Marked claim evidence together with the ownership generation it was issued with."""

    evidence: MarkedClaimEvidence
    issued_generation: int

    def __post_init__(self) -> None:
        """Refuse a binding without a positive issued generation."""
        _marked_positive(self.issued_generation, "generation")

    def to_dict(self) -> dict[str, Any]:
        """Return the strict JSON-compatible binding."""
        evidence = self.evidence
        return {
            "launch_id": evidence.launch_id,
            "pane_id": evidence.pane_id,
            "host": evidence.host,
            "assignment_binding": evidence.assignment_binding,
            "round": evidence.round_number,
            "occurrence": evidence.occurrence,
            "issued_generation": self.issued_generation,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> MarkedClaimBinding:
        """Parse one strict binding mapping."""
        strict_fields(data, set(_MARKED_CLAIM_KEYS), "marked claim")
        evidence = MarkedClaimEvidence(
            data["launch_id"], data["pane_id"], data["host"], data["assignment_binding"],
            data["round"], data["occurrence"],
        )
        return cls(evidence, data["issued_generation"])


@dataclass(frozen=True)
class CoordinationRecord:
    """Durable state with digest-only ownership, an optional bound scope and marked claim."""

    context: ReviewContext
    policy: FamilyPolicy
    status: CoordinationStatus
    owner: Actor
    expected_next_actor: Actor
    round_number: int
    lease_renewed_at: str | None
    reviewed_work_changed: bool | None = None
    convergence_recommended: bool | None = None
    no_progress_streak: int = 0
    clarification_used: bool = False
    incomplete_transition: IncompleteTransitionKind | None = None
    transcript_entry_id: str | None = None
    transcript_offset: int | None = None
    escalation_reason: str | None = None
    confirmation_label: str | None = None
    confirmed_outcome: ConfirmationOutcome | None = None
    confirmation_timestamp: str | None = None
    human_guidance: str | None = None
    role_natures: RoleNatureSnapshot = field(default_factory=RoleNatureSnapshot)
    ownership_generation: int = 0
    ownership_token_digest: str | None = None
    bound_scope_fingerprint: str | None = None
    marked_claim: MarkedClaimBinding | None = None

    def __post_init__(self) -> None:
        """Validate status, marker, confirmation, ownership and marked claim invariants."""
        positive_integer(self.round_number, "coordination round")
        non_negative_integer(self.no_progress_streak, "no-progress streak")
        if self.lease_renewed_at is not None:
            validate_local_timestamp(self.lease_renewed_at)
        _validate_coordination_status(self)
        _validate_incomplete_transition(self)
        _validate_confirmation(self)
        _validate_ownership(self)
        if self.bound_scope_fingerprint is not None and (
            _OWNERSHIP_DIGEST_RE.fullmatch(self.bound_scope_fingerprint) is None
        ):
            raise ReviewExchangeError("invalid bound scope fingerprint")
        if self.marked_claim is not None and self.marked_claim.issued_generation != self.ownership_generation:
            raise ReviewExchangeError("marked claim generation must equal the ownership generation")

    def to_dict(self) -> dict[str, Any]:
        """Return strict JSON-compatible coordination data."""
        result = {
            "context": self.context.to_dict(),
            "policy": self.policy.to_dict(),
            "status": self.status.value,
            "owner": self.owner.value,
            "expected_next_actor": self.expected_next_actor.value,
            "round_number": self.round_number,
            "lease_renewed_at": self.lease_renewed_at,
            "reviewed_work_changed": self.reviewed_work_changed,
            "convergence_recommended": self.convergence_recommended,
            "no_progress_streak": self.no_progress_streak,
            "clarification_used": self.clarification_used,
            "incomplete_transition": (
                self.incomplete_transition.value
                if self.incomplete_transition is not None
                else None
            ),
            "transcript_entry_id": self.transcript_entry_id,
            "transcript_offset": self.transcript_offset,
            "escalation_reason": self.escalation_reason,
            "confirmation_label": self.confirmation_label,
            "confirmed_outcome": (
                self.confirmed_outcome.value if self.confirmed_outcome is not None else None
            ),
            "confirmation_timestamp": self.confirmation_timestamp,
            "human_guidance": self.human_guidance,
            "role_natures": self.role_natures.to_dict(),
        }
        if self.bound_scope_fingerprint is not None:
            result["bound_scope_fingerprint"] = self.bound_scope_fingerprint
        if self.ownership_generation > 0:
            result["ownership_generation"] = self.ownership_generation
            result["ownership_token_digest"] = self.ownership_token_digest
        if self.marked_claim is not None:
            result["marked_claim"] = self.marked_claim.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CoordinationRecord:
        """Construct coordination state from strict JSON-compatible data."""
        expected = {
            "context", "policy", "status", "owner", "expected_next_actor",
            "round_number", "lease_renewed_at", "reviewed_work_changed",
            "convergence_recommended", "no_progress_streak", "clarification_used",
            "incomplete_transition", "transcript_entry_id", "transcript_offset",
            "escalation_reason", "confirmation_label", "confirmed_outcome",
            "confirmation_timestamp", "human_guidance",
        }
        legacy = "role_natures" not in data
        if not legacy:
            expected.add("role_natures")
        ownership_generation, ownership_digest = _ownership_from_mapping(
            data,
            expected,
        )
        if "bound_scope_fingerprint" in data:
            expected.add("bound_scope_fingerprint")
        marked = None
        if "marked_claim" in data:
            expected.add("marked_claim")
            marked = MarkedClaimBinding.from_dict(mapping_value(data["marked_claim"], "marked claim"))
        strict_fields(data, expected, "coordination record")
        marker_value = data["incomplete_transition"]
        outcome_value = data["confirmed_outcome"]
        offset_value = data["transcript_offset"]
        offset = (
            None
            if offset_value is None
            else non_negative_integer(offset_value, "transcript offset")
        )
        clarification = data["clarification_used"]
        if not isinstance(clarification, bool):
            raise ReviewExchangeError("clarification-used flag must be boolean")
        return cls(
            context=ReviewContext.from_dict(
                mapping_value(data["context"], "coordination context"),
            ),
            policy=FamilyPolicy.from_dict(
                mapping_value(data["policy"], "coordination family policy"),
            ),
            status=enum_value(
                CoordinationStatus,
                data["status"],
                "coordination status",
            ),
            owner=enum_value(Actor, data["owner"], "owner"),
            expected_next_actor=enum_value(
                Actor,
                data["expected_next_actor"],
                "expected next actor",
            ),
            round_number=positive_integer(data["round_number"], "coordination round"),
            lease_renewed_at=optional_string(data["lease_renewed_at"], "lease timestamp"),
            reviewed_work_changed=optional_boolean(
                data["reviewed_work_changed"], "reviewed-work-changed",
            ),
            convergence_recommended=optional_boolean(
                data["convergence_recommended"], "convergence-recommended",
            ),
            no_progress_streak=non_negative_integer(
                data["no_progress_streak"], "no-progress streak",
            ),
            clarification_used=clarification,
            incomplete_transition=(
                None
                if marker_value is None
                else enum_value(
                    IncompleteTransitionKind,
                    marker_value,
                    "incomplete transition",
                )
            ),
            transcript_entry_id=optional_string(
                data["transcript_entry_id"], "transcript entry id",
            ),
            transcript_offset=offset,
            escalation_reason=optional_string(
                data["escalation_reason"], "escalation reason",
            ),
            confirmation_label=optional_string(
                data["confirmation_label"], "confirmation label",
            ),
            confirmed_outcome=(
                None
                if outcome_value is None
                else enum_value(
                    ConfirmationOutcome,
                    outcome_value,
                    "confirmation outcome",
                )
            ),
            confirmation_timestamp=optional_string(
                data["confirmation_timestamp"], "confirmation timestamp",
            ),
            human_guidance=optional_string(data["human_guidance"], "human guidance"),
            role_natures=RoleNatureSnapshot.from_optional_dict(
                None
                if legacy
                else mapping_value(
                    data["role_natures"],
                    "coordination role natures",
                ),
            ),
            ownership_generation=ownership_generation,
            ownership_token_digest=ownership_digest,
            bound_scope_fingerprint=optional_string(data.get("bound_scope_fingerprint"), "bound scope fingerprint"),
            marked_claim=marked,
        )


# eof
