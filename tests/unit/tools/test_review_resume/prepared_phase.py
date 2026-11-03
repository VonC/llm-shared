"""Declare resume starting evidence without replaying the exchange protocol."""

from __future__ import annotations

from dataclasses import replace

from tests.unit.tools.review_exchange_test_support import review_summary
from tests.unit.tools.test_review_exchange_lifecycle import (
    test_review_exchange_lifecycle_tdd as lifecycle,
)
from tools.llm_nature import LlmNature
from tools.review_exchange_models import (
    Actor,
    ConfirmationOutcome,
    CoordinationStatus,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    Envelope,
    render_envelope_markdown,
    render_json_markdown,
)
from tools.review_exchange_ownership import OwnershipCapability, OwnershipService
from tools.review_exchange_store import TranscriptEntry
from tools.review_role_nature import RoleNatureSnapshot

_PHASE_ACTORS = {
    "started": (Actor.REQUESTOR, Actor.REVIEWER),
    "request": (Actor.REQUESTOR, Actor.REVIEWER),
    "answer": (Actor.REVIEWER, Actor.REQUESTOR),
    "convergence": (Actor.REVIEWER, Actor.HUMAN),
    "authorized": (Actor.REQUESTOR, Actor.HUMAN),
}

def _coordination(
    core: lifecycle.ReviewExchangeCore, context: lifecycle.ReviewContext,
    clock: lifecycle.FakeTime, phase: str,
) -> tuple[CoordinationRecord, OwnershipCapability]:
    """Declare ownership and coordination state independently of publication."""
    request = phase in {"started", "request"}
    convergence = phase in {"convergence", "authorized"}
    authorized = phase == "authorized"
    snapshot = RoleNatureSnapshot(LlmNature.CODEX, None if request else LlmNature.CODEX)
    timestamp = lifecycle._timestamp(clock)
    capability = OwnershipCapability(1 if request else 2, "scenario-ownership-token-000000000000")
    actor, next_actor = _PHASE_ACTORS[phase]
    record = CoordinationRecord(
        context, core.policy,
        CoordinationStatus.AWAITING_HUMAN_CONFIRMATION if convergence else CoordinationStatus.ACTIVE,
        actor, next_actor,
        1, None if convergence else timestamp,
        convergence_recommended=None if request else convergence,
        role_natures=snapshot,
        ownership_generation=capability.generation,
        ownership_token_digest=OwnershipService.digest(capability.token),
    )
    if authorized:
        record = replace(record, confirmation_label="Commit",
                         confirmed_outcome=ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW,
                         confirmation_timestamp=timestamp)
    return record, capability


def prepare_phase(
    core: lifecycle.ReviewExchangeCore, context: lifecycle.ReviewContext,
    clock: lifecycle.FakeTime, phase: str,
) -> None:
    """Materialize one declared phase; the test still performs its real continuation."""
    assert phase in _PHASE_ACTORS
    store = core.store
    family = "Code" if context.identity.family is ReviewFamily.CODE else "Specification"
    document = context.document_path.relative_to(store.paths.project_root).as_posix()
    # Template loading and atomic initialization have their own store tests.
    # These scenarios start with an existing transcript, still prepared inside
    # the measured lifecycle, without replaying those prerequisite operations.
    header = (
        f"# {family} review transcript for {context.identity.version}\n\n"
        f"- Exchange: {context.identity.key}\n"
        f"- Reviewed document: {document}\n\n"
        "This append-only transcript records completed review rounds. Review agents add\n"
        "new entries through the review-exchange core and do not reread earlier entries\n"
        "as working context.\n"
    )
    record, capability = _coordination(core, context, clock, phase)
    store.paths.coordination.write_text(
        render_json_markdown(f"Review exchange coordination for {context.identity.key}", record.to_dict(), ""),
        encoding="utf-8",
    )
    core.present_ownership(capability)
    if phase == "started":
        store.paths.transcript.write_text(header, encoding="utf-8")
        return
    request_record = replace(record, role_natures=RoleNatureSnapshot(LlmNature.CODEX, None))
    prefix = f"step-{context.implementation_step}-" if context.implementation_step is not None else ""
    envelope = Envelope(
        context.identity, context.umbrella_path, context.document_path,
        context.implementation_step, ReviewRole.REQUESTOR, 1,
        lifecycle._timestamp(clock), role_natures=request_record.role_natures,
    )
    entries = [store._render_transcript_entry(
        request_record, TranscriptEntry(f"request-{prefix}round-1", ReviewRole.REQUESTOR,
                                       "request", envelope.created_at, "Prepared request evidence.\n"),
    )]
    if phase == "request":
        store.paths.request.write_text(render_envelope_markdown(envelope, review_summary(context, 1)), encoding="utf-8")
    if phase != "request":
        convergence = phase in {"convergence", "authorized"}
        envelope = replace(
            envelope, role=ReviewRole.REVIEWER,
            disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED if convergence else ReviewDisposition.CHANGES_REQUESTED,
            role_natures=record.role_natures,
        )
        store.paths.answer.write_text(render_envelope_markdown(envelope, "Prepared reviewer feedback.\n"), encoding="utf-8")
        entries.append(store._render_transcript_entry(
            record, TranscriptEntry(f"answer-{prefix}round-1", ReviewRole.REVIEWER,
                                    "answer", envelope.created_at, "Prepared answer evidence.\n"),
        ))
    if phase == "authorized":
        entries.append(store._render_transcript_entry(
            record, TranscriptEntry("human-confirmation-round-1", ReviewRole.HUMAN,
                                    "human-confirmation", lifecycle._timestamp(clock),
                                    "Prepared human Commit authorization.\n"),
        ))
    store.paths.transcript.write_text(
        header + "".join(entries), encoding="utf-8",
    )


# eof
