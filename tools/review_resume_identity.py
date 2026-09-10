"""Locked selected-occurrence backfill and lease-independent resume claims.

This adapter reuses the strict artifact parsers, atomic backfill service, and
ownership store. A stale selection or unresolved role conflict cannot claim.
"""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING

from tools.llm_nature import LlmNature
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    parse_envelope_markdown,
    parse_json_markdown,
    render_json_markdown,
)
from tools.review_exchange_ownership import OwnershipService
from tools.review_exchange_transcript_identity import current_request_occurrence
from tools.review_resume import (
    ResumeDecisionOutcome,
    ResumeExchange,
    ReviewResumeService,
)
from tools.review_role_nature import (
    MutableRoleNatureArtifact,
    RoleNatureBackfill,
    RoleNatureBackfillContext,
    RoleNatureEvidence,
    RoleNatureReconciler,
    RoleNatureSnapshot,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Any

    from tools.review_exchange_core import ReviewExchangeCore
    from tools.review_exchange_ownership import OwnershipCapability


def _render_snapshot(
    title: str, data: Mapping[str, Any], body: str, snapshot: RoleNatureSnapshot,
) -> str:
    """Preserve all authored content while upgrading only identity metadata."""
    return render_json_markdown(title, {**data, "role_natures": snapshot.to_dict()}, body)


def _validate_record(content: str) -> None:
    """Validate a complete rendered coordination replacement."""
    data, _body = parse_json_markdown(content)
    CoordinationRecord.from_dict(data)


def _validate_envelope(content: str) -> None:
    """Validate a complete rendered request, answer, or tombstone."""
    parse_envelope_markdown(content)


def _artifact(path: Path, role: ReviewRole, *, coordination: bool) -> MutableRoleNatureArtifact:
    """Read each selected runtime artifact once for reconciliation and rendering."""
    text = path.read_text(encoding="utf-8")
    data, body = parse_json_markdown(text)
    snapshot = (
        CoordinationRecord.from_dict(data).role_natures
        if coordination else parse_envelope_markdown(text)[0].role_natures
    )
    return MutableRoleNatureArtifact(
        RoleNatureEvidence(path, role, snapshot.for_role(role)), snapshot,
        partial(_render_snapshot, text.splitlines()[0][2:], data, body),
        _validate_record if coordination else _validate_envelope,
    )


def claim_selected(  # noqa: PLR0913 - exact selected occurrence and explicit conflict authority
    core: ReviewExchangeCore,
    role: ReviewRole,
    nature: LlmNature,
    *,
    round_number: int,
    occurrence: int,
    override: bool,
) -> OwnershipCapability:
    """Recheck, backfill, and claim under the normal exact transition lock."""
    store = core.store
    with store.transition_lock():
        observation = core.classify()
        record = observation.record
        if record is None or record.round_number != round_number or current_request_occurrence(store, core.context, round_number) != occurrence:
            raise ReviewExchangeError("resume selection changed; inspect again")
        decision = ReviewResumeService().decide(
            nature, (ResumeExchange(observation.state, None, None),), forced_role=role,
        )
        if decision.outcome is not ResumeDecisionOutcome.READY:
            raise ReviewExchangeError("resume state no longer permits continuation")
        service = OwnershipService()
        presented = core.ownership_capability
        if service.failure_for(record, presented) is not None:
            presented = None
        if presented is not None and record.owner.value != role.value:
            presented = None
        updated = _backfill_selected(core, record, role, nature, occurrence=occurrence, override=override)
        claim = store.claim_ownership(
            updated, service, Actor(role.value), presented=presented, force=presented is None,
        )
        return claim.capability


def _backfill_selected(  # noqa: PLR0913 - explicit selected identity transaction inputs
    core: ReviewExchangeCore, record: CoordinationRecord, role: ReviewRole,
    nature: LlmNature, *, occurrence: int, override: bool,
) -> CoordinationRecord:
    """Read and validate only the selected occurrence before missing-only identity completion."""
    store = core.store
    artifacts = [_artifact(store.paths.coordination, role, coordination=True)]
    artifacts.extend(
        _artifact(path, role, coordination=False)
        for path in (store.paths.request, store.paths.answer, store.paths.tombstone)
        if path.is_file()
    )
    reconciliation = RoleNatureReconciler().reconcile(
        [item.evidence for item in artifacts], role, nature,
    )
    if reconciliation.conflicts and not override:
        raise ReviewExchangeError("selected role conflicts require Override")
    RoleNatureBackfill().apply(
        artifacts,
        RoleNatureBackfillContext(role, nature, store.paths.transcript, occurrence, override),
    )
    return replace(record, role_natures=record.role_natures.record(role, nature)) if (
        nature is not LlmNature.UNKNOWN and record.role_natures.for_role(role) is None
    ) else record


def claim_discovered_request(core: ReviewExchangeCore, round_number: int, occurrence: int) -> OwnershipCapability | None:
    """Let exactly one waiting reviewer claim the still-current request."""
    with core.store.transition_lock():
        observation = core.classify()
        record = observation.record
        if (
            observation.state not in {ArtifactState.REQUEST_PENDING, ArtifactState.ABANDONED_REQUEST}
            or record is None or record.round_number != round_number
            or record.expected_next_actor is not Actor.REVIEWER
            or current_request_occurrence(core.store, core.context, round_number) != occurrence
        ):
            return None
        claim = core.store.claim_ownership(record, OwnershipService(), Actor.REVIEWER)
        return claim.capability


# eof
