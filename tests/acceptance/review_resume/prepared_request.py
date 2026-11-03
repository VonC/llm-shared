"""Write typed pending-request bytes without replaying publication transactions.

The actual operations tested by each scenario still use production persistence.
Prerequisite setup renders the same records and transcript entry directly.
A caller whose core registers its own family policy passes that policy, so the
declared record matches what the observer validates instead of classifying as
inconsistent; the default stays the acceptance family policy.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from tests.unit.tools.review_exchange_test_support import review_policy, review_summary
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
from tools.review_exchange_store import ReviewExchangeStore, TranscriptEntry
from tools.review_role_nature import RoleNatureSnapshot

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models import ArtifactPaths, FamilyPolicy, ReviewContext


class PreparedReview(Protocol):
    """The filesystem and identity required by typed review prerequisites."""

    @property
    def root(self) -> Path:
        """Return the consuming repository root."""
        ...

    @property
    def context(self) -> ReviewContext:
        """Return the exact review identity."""
        ...

    @property
    def paths(self) -> ArtifactPaths:
        """Return the prepared artifact locations."""
        ...


@dataclass(frozen=True)
class ReviewInputs:
    """Adapt an existing fixture without constructing another repository."""

    root: Path
    context: ReviewContext
    paths: ArtifactPaths


def prepare_request(
    repo: PreparedReview, nature: str | None, *,
    owner: Actor = Actor.REQUESTOR, reviewer_nature: str | None = None,
    round_number: int = 1,
) -> dict[str, Any]:
    """Write independent domain records; subsequent CLI transitions remain real."""
    record, envelope, capability = _pending_records(repo, nature, owner, reviewer_nature, round_number)
    store = ReviewExchangeStore(repo.paths)
    title = f"Review exchange coordination for {repo.context.identity.key}"
    repo.paths.coordination.write_text(render_json_markdown(title, record.to_dict(), ""), encoding="utf-8")
    repo.paths.request.write_text(
        render_envelope_markdown(envelope, review_summary(repo.context, round_number)), encoding="utf-8",
    )
    repo.paths.transcript.write_text(
        transcript_header(repo) + store._render_transcript_entry(record, _request_entry(repo, envelope)), encoding="utf-8",
    )
    return capability


def _pending_records(
    repo: PreparedReview, nature: str | None, owner: Actor, reviewer_nature: str | None,
    round_number: int = 1,
) -> tuple[CoordinationRecord, Envelope, dict[str, Any]]:
    """Construct typed prerequisites without publishing intermediate file states."""
    token = "scenario-request-token-000000000000000"  # noqa: S105 - deterministic test capability
    snapshot = RoleNatureSnapshot(
        LlmNature(nature) if nature is not None else None,
        LlmNature(reviewer_nature) if reviewer_nature is not None else None,
    )
    generation = 2 if owner is Actor.REVIEWER else 1
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    record = CoordinationRecord(
        repo.context, review_policy(repo.context), CoordinationStatus.ACTIVE,
        owner, Actor.REVIEWER, round_number, timestamp, role_natures=snapshot,
        ownership_generation=generation, ownership_token_digest=OwnershipService.digest(token),
    )
    envelope = Envelope(
        repo.context.identity, repo.context.umbrella_path, repo.context.document_path,
        repo.context.implementation_step, ReviewRole.REQUESTOR, round_number,
        "2026-08-05T09:00:00+02:00", role_natures=snapshot,
    )
    return record, envelope, {"ownership_generation": generation, "ownership_token": token}


def _request_entry(repo: PreparedReview, envelope: Envelope) -> TranscriptEntry:
    """Declare the selected request's already-published transcript entry."""
    step = repo.context.implementation_step
    prefix = f"step-{step}-" if step is not None else ""
    return TranscriptEntry(f"request-{prefix}round-{envelope.round_number}", ReviewRole.REQUESTOR,
                           "request", envelope.created_at, "Acceptance evidence.\n")


def transcript_header(repo: PreparedReview) -> str:
    """Declare existing transcript bytes; store initialization tests cover templates."""
    family = "Code" if repo.context.identity.family is ReviewFamily.CODE else "Specification"
    document = repo.context.document_path.relative_to(repo.root).as_posix()
    return (
        f"# {family} review transcript for {repo.context.identity.version}\n\n"
        f"- Exchange: {repo.context.identity.key}\n"
        f"- Reviewed document: {document}\n\n"
        "This append-only transcript records completed review rounds. Review agents add\n"
        "new entries through the review-exchange core and do not reread earlier entries\n"
        "as working context.\n"
    )


def prepare_convergence(
    repo: PreparedReview, *, authorized: bool = False, round_number: int = 1,
    include_transcript: bool = True, policy: FamilyPolicy | None = None,
) -> dict[str, Any]:
    """Declare a completed review prerequisite without replaying its CLI journey.

    Args:
        repo: The prepared repository, identity and artifact paths.
        authorized: Whether the human already confirmed the owning workflow.
        round_number: The round whose convergence answer is retained.
        include_transcript: ``False`` skips historical transcript rendering for
            completion-only contracts that never read it.
        policy: The family policy registered by the core under test. A unit
            harness with its own labels must pass it: the observer rejects a
            record whose policy differs, and confirmation then refuses the gate.

    Returns:
        The ownership capability fields matching the declared record.
    """
    record, request, capability = _pending_records(repo, "codex", Actor.REQUESTOR, None, round_number)
    if policy is not None:
        record = replace(record, policy=policy)
    store = ReviewExchangeStore(repo.paths)
    request_entry = store._render_transcript_entry(record, _request_entry(repo, request)) if include_transcript else ""
    snapshot = RoleNatureSnapshot(LlmNature.CODEX, LlmNature.CLAUDE)
    record = replace(
        record, status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
        owner=Actor.REQUESTOR if authorized else Actor.REVIEWER,
        expected_next_actor=Actor.HUMAN, lease_renewed_at=None,
        convergence_recommended=True, role_natures=snapshot,
    )
    timestamp = "2026-08-05T09:00:00+02:00"
    envelope = Envelope(
        repo.context.identity, repo.context.umbrella_path, repo.context.document_path,
        repo.context.implementation_step, ReviewRole.REVIEWER, round_number, timestamp,
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED, role_natures=snapshot,
    )
    repo.paths.answer.write_text(render_envelope_markdown(envelope, "Ready for human confirmation.\n"), encoding="utf-8")
    step = repo.context.implementation_step
    prefix = f"step-{step}-" if step is not None else ""
    entries = [TranscriptEntry(f"answer-{prefix}round-{round_number}", ReviewRole.REVIEWER, "answer", timestamp, "Reviewer evidence.\n")]
    if authorized:
        record = replace(record, confirmation_label=record.policy.continue_owning_workflow_label,
                         confirmed_outcome=ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW,
                         confirmation_timestamp=timestamp)
        entries.append(TranscriptEntry(f"human-confirmation-round-{round_number}", ReviewRole.HUMAN,
                                       "human-confirmation", timestamp, "Human authorization.\n"))
    repo.paths.coordination.write_text(
        render_json_markdown(f"Review exchange coordination for {repo.context.identity.key}", record.to_dict(), ""),
        encoding="utf-8",
    )
    if include_transcript:
        repo.paths.transcript.write_text(
            transcript_header(repo) + request_entry + "".join(store._render_transcript_entry(record, entry) for entry in entries),
            encoding="utf-8",
        )
    return capability


def prepare_assessed_round(repo: PreparedReview) -> OwnershipCapability:
    """Declare the producer's completed assessment before real next-round publication.

    Wait tests assert competing claims and the later request, not answer
    consumption. Its publication and consumption contracts have independent
    tests; retain their final typed record and transcript prerequisite here.
    """
    store = ReviewExchangeStore(repo.paths)
    record = store.read_coordination(required=True)
    assert record is not None
    token = "scenario-assessment-token-000000000000"  # noqa: S105 - fixture capability
    capability = OwnershipCapability(record.ownership_generation + 1, token)
    record = replace(record, owner=Actor.REQUESTOR, expected_next_actor=Actor.REQUESTOR,
                     reviewed_work_changed=True, convergence_recommended=False,
                     ownership_generation=capability.generation,
                     ownership_token_digest=OwnershipService.digest(token))
    repo.paths.request.unlink()
    repo.paths.coordination.write_text(
        render_json_markdown(f"Review exchange coordination for {repo.context.identity.key}", record.to_dict(), ""),
        encoding="utf-8",
    )
    step = repo.context.implementation_step
    prefix = f"step-{step}-" if step is not None else ""
    entry = TranscriptEntry(f"answer-{prefix}round-1", ReviewRole.REVIEWER, "answer",
                            "2026-08-05T09:00:00+02:00", "Reviewer evidence.\n")
    with repo.paths.transcript.open("a", encoding="utf-8") as stream:
        stream.write(store._render_transcript_entry(record, entry))
    return capability


# eof
