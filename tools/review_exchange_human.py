"""Human-gated confirmation and escalation resolution transitions.

Step 3 separates the convergence-only human facet from automated round
orchestration while keeping it mixed into the public ``ReviewExchangeCore``
service. Choices remain role-neutral, durable, idempotent, and advisory until
the owning workflow explicitly completes.
"""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, cast

from tools.review_exchange_models import (
    Actor,
    ArchiveKind,
    ArtifactState,
    ConfirmationOutcome,
    CoordinationStatus,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewContext,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_store import TranscriptEntry

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime
    from pathlib import Path

    from tools.review_exchange_models_envelope import Envelope
    from tools.review_exchange_observer import ExchangeObservation
    from tools.review_exchange_ownership import OwnershipCapability, OwnershipClaim
    from tools.review_exchange_store import ReviewExchangeStore


@dataclass(frozen=True)
class ConfirmationDecision:
    """Durable human choice and whether it authorizes the owning action."""

    outcome: ConfirmationOutcome
    owning_action_authorized: bool
    record: CoordinationRecord


@dataclass(frozen=True)
class ResolutionResult:
    """Fresh active round plus exact evidence archives created by resolution."""

    record: CoordinationRecord
    archived_paths: tuple[Path, ...]


class ReviewExchangeHumanMixin(ABC):
    """Provide human transitions to the bound review-exchange core facade."""

    store: ReviewExchangeStore
    context: ReviewContext
    policy: FamilyPolicy
    _wall_clock: Callable[[], datetime]

    @abstractmethod
    def classify(self) -> ExchangeObservation:
        """Return the current exact-path observation."""

    @abstractmethod
    def escalate(self, reason: str, role: ReviewRole) -> CoordinationRecord:
        """Persist an escalation transition."""

    @abstractmethod
    def _require_record(self, observation: ExchangeObservation) -> CoordinationRecord:
        """Return the observation's coordination record or fail."""

    @abstractmethod
    def _restore_convergence_gate(
        self,
        record: CoordinationRecord,
        envelope: Envelope | None,
    ) -> CoordinationRecord:
        """Restore the durable convergence-gate fields."""

    @abstractmethod
    def _mark_transition(
        self,
        record: CoordinationRecord,
        transition: IncompleteTransitionKind,
        entry_id: str,
    ) -> CoordinationRecord:
        """Persist a marker before a transcript side effect."""

    @abstractmethod
    def _timestamp(self) -> str:
        """Return a local ISO-8601 timestamp."""

    @abstractmethod
    def _clear_marker(self, record: CoordinationRecord) -> CoordinationRecord:
        """Return a record with transition bookkeeping cleared."""

    @abstractmethod
    def _repeatable_entry(self, base: str) -> tuple[str, int]:
        """Return a unique transcript identity and attempt for a repeatable event."""

    @abstractmethod
    def _claim_locked(
        self,
        record: CoordinationRecord,
        actor: Actor,
        *,
        presented: OwnershipCapability | None = None,
        force: bool = False,
    ) -> OwnershipClaim:
        """Persist one ownership claim while the caller holds the transition lock."""

    def confirm(
        self,
        label: str,
        *,
        guidance: str | None = None,
    ) -> ConfirmationDecision:
        """Persist one registered human choice and finish its durable transition."""
        outcome = self.policy.outcome_for(label)
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            if (
                record.confirmed_outcome is ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
                and record.incomplete_transition is None
            ):
                if record.confirmation_label != label:
                    raise ReviewExchangeError("persisted confirmation uses another label")
                return ConfirmationDecision(
                    outcome=outcome,
                    owning_action_authorized=True,
                    record=record,
                )
            repairing = record.incomplete_transition is (
                IncompleteTransitionKind.HUMAN_CONFIRMATION
            )
            if not repairing:
                if observation.state is not ArtifactState.CONVERGENCE_GATE:
                    raise ReviewExchangeError("confirmation requires the convergence gate")
                record = self._restore_convergence_gate(record, observation.answer_envelope)
                entry_id = f"human-confirmation-round-{record.round_number}"
                record = self._mark_transition(
                    record,
                    IncompleteTransitionKind.HUMAN_CONFIRMATION,
                    entry_id,
                )
                record = replace(
                    record,
                    confirmation_label=label,
                    confirmed_outcome=outcome,
                    confirmation_timestamp=self._timestamp(),
                    human_guidance=guidance,
                )
                self.store.write_coordination(record)
            else:
                self._validate_confirmation_replay(record, label, outcome, guidance)
            entry = TranscriptEntry(
                f"human-confirmation-round-{record.round_number}",
                ReviewRole.HUMAN,
                "human-confirmation",
                record.confirmation_timestamp or self._timestamp(),
                self._confirmation_content(label, outcome, guidance),
            )
            marked = self.store.append_transcript_once(
                record,
                transition=IncompleteTransitionKind.HUMAN_CONFIRMATION,
                entry=entry,
                clear_marker=False,
            )
            if outcome is ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW:
                final = self._clear_marker(marked)
                self.store.write_coordination(final)
                return ConfirmationDecision(
                    outcome=outcome,
                    owning_action_authorized=True,
                    record=final,
                )
            self.store.remove_exact(self.store.paths.answer)
            final = replace(
                marked,
                status=CoordinationStatus.ACTIVE,
                owner=Actor.REQUESTOR,
                expected_next_actor=Actor.REVIEWER,
                round_number=marked.round_number + 1,
                lease_renewed_at=self._timestamp(),
                reviewed_work_changed=None,
                convergence_recommended=None,
                no_progress_streak=0,
                clarification_used=False,
                incomplete_transition=None,
                transcript_entry_id=None,
                transcript_offset=None,
                confirmation_label=None,
                confirmed_outcome=None,
                confirmation_timestamp=None,
                human_guidance=guidance,
            )
            self.store.write_coordination(final)
            return ConfirmationDecision(
                outcome=outcome,
                owning_action_authorized=False,
                record=final,
            )

    def cancel(self, reason: str) -> CoordinationRecord:
        """Route a human convergence cancellation through escalation."""
        if self.classify().state not in {
            ArtifactState.CONVERGENCE_GATE,
            ArtifactState.ESCALATED,
        }:
            raise ReviewExchangeError("cancellation requires a convergence gate")
        return self.escalate(reason, ReviewRole.HUMAN)

    def complete(self) -> bool:
        """Remove retained evidence only after the authorized owning action succeeds."""
        with self.store.transition_lock():
            observation = self.classify()
            if observation.record is None:
                return False
            record = self._require_record(observation)
            if (
                record.status is not CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
                or record.confirmed_outcome
                is not ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
                or record.incomplete_transition is not None
            ):
                raise ReviewExchangeError("owning action is not durably authorized")
            self.store.remove_exact(self.store.paths.answer)
            self.store.remove_exact(self.store.paths.coordination)
            return True


    def force_reclaim(self, summary: str) -> CoordinationRecord:
        """Resume one escalated round in place for an authorized manual handoff.

        Automated `reclaim` never crosses an escalation. A human who owns the
        stopped exchange may instead resume the same round without renumbering
        it, leaving the published request, answer, and transcript untouched and
        recording the decision as durable transcript evidence.

        Ownership is re-minted here rather than fenced. An exchange escalates
        precisely because the actor session stopped, so its capability is
        normally gone with that process. Requiring the lost capability to run
        the recovery built for that loss would make this operation unreachable
        in the only case it exists for, and no other transition can leave the
        escalated state. The stopped round has no live actor to displace, so the
        forced resume claims ownership for the actor the artifact shape names
        and returns the replacement capability to the resuming session.
        """
        if not summary.strip():
            raise ReviewExchangeError("forced reclaim summary must be non-empty")
        with self.store.transition_lock():
            observation = self.classify()
            if observation.record is None:
                raise ReviewExchangeError("operation requires durable coordination")
            record = observation.record
            if record.status is not CoordinationStatus.ESCALATED:
                raise ReviewExchangeError("forced reclaim requires an escalated exchange")
            if record.incomplete_transition not in (
                None,
                IncompleteTransitionKind.HUMAN_RECLAIM,
            ):
                raise ReviewExchangeError("repair the pending transition before forced reclaim")
            actor = self._resumed_actor()
            record = self._claim_locked(record, actor, force=True).record
            entry_id, occurrence = self._repeatable_entry(
                f"human-reclaim-round-{record.round_number}",
            )
            entry = TranscriptEntry(
                entry_id,
                ReviewRole.HUMAN,
                "human-reclaim",
                self._timestamp(),
                summary,
                occurrence,
            )
            marked = self._mark_transition(
                record,
                IncompleteTransitionKind.HUMAN_RECLAIM,
                entry.entry_id,
            )
            marked = self.store.append_transcript_once(
                marked,
                transition=IncompleteTransitionKind.HUMAN_RECLAIM,
                entry=entry,
                clear_marker=False,
            )
            resumed = replace(
                self._clear_marker(marked),
                status=CoordinationStatus.ACTIVE,
                expected_next_actor=actor,
                lease_renewed_at=self._timestamp(),
                escalation_reason=None,
                human_guidance=summary,
            )
            self.store.write_coordination(resumed)
            return resumed

    def _resumed_actor(self) -> Actor:
        """Return the actor one intact escalated round is handed back to."""
        shape = (
            self.store.paths.request.is_file(),
            self.store.paths.answer.is_file(),
            self.store.paths.tombstone.is_file(),
        )
        if shape == (False, True, False):
            return Actor.REQUESTOR
        if shape not in {(True, False, False), (False, False, False)}:
            raise ReviewExchangeError("forced reclaim requires one intact escalated round")
        return Actor.REVIEWER

    def resolve_escalation(
        self,
        summary: str,
        *,
        archive: bool,
    ) -> ResolutionResult:
        """Record human resolution, clear or archive evidence, and start fresh."""
        if not summary.strip():
            raise ReviewExchangeError("human resolution summary must be non-empty")
        with self.store.transition_lock():
            record = self._require_record(self.classify())
            if record.status is not CoordinationStatus.ESCALATED:
                raise ReviewExchangeError("resolution requires an escalated exchange")
            if record.incomplete_transition is not None:
                raise ReviewExchangeError("repair the pending transition before resolution")
            resolved_round = record.round_number + 1
            staged = replace(
                record,
                round_number=resolved_round,
                human_guidance=summary,
            )
            self.store.write_coordination(staged)
            entry = TranscriptEntry(
                f"human-resolution-round-{resolved_round}",
                ReviewRole.HUMAN,
                "human-resolution",
                self._timestamp(),
                summary,
            )
            marked = self._mark_transition(
                staged,
                IncompleteTransitionKind.HUMAN_RESOLUTION,
                entry.entry_id,
            )
            marked = self.store.append_transcript_once(
                marked,
                transition=IncompleteTransitionKind.HUMAN_RESOLUTION,
                entry=entry,
                clear_marker=False,
            )
            self.store.write_coordination(self._clear_marker(marked))
            archived = self._resolve_live_evidence(archive=archive)
            fresh = CoordinationRecord(
                self.context,
                self.policy,
                CoordinationStatus.ACTIVE,
                Actor.REQUESTOR,
                Actor.REVIEWER,
                resolved_round,
                self._timestamp(),
            )
            self.store.write_coordination(fresh)
            return ResolutionResult(fresh, archived)

    @staticmethod
    def _confirmation_content(
        label: str,
        outcome: ConfirmationOutcome,
        guidance: str | None,
    ) -> str:
        """Render role-neutral human confirmation transcript content."""
        content = f"Human choice: {label}\nOutcome: {outcome.value}"
        if guidance is not None:
            content += f"\nGuidance: {guidance}"
        return content

    @staticmethod
    def _validate_confirmation_replay(
        record: CoordinationRecord,
        label: str,
        outcome: ConfirmationOutcome,
        guidance: str | None,
    ) -> None:
        """Reject a retry that differs from its durable human decision."""
        if (
            record.confirmation_label != label
            or record.confirmed_outcome is not outcome
            or record.human_guidance != guidance
        ):
            raise ReviewExchangeError("confirmation retry differs from durable choice")

    def _resolve_live_evidence(self, *, archive: bool) -> tuple[Path, ...]:
        """Archive or clear only the fixed live transient evidence paths."""
        archived: list[Path] = []
        compact = self._wall_clock().astimezone().strftime("%Y%m%d-%H%M%S")
        ordered = (
            (ArchiveKind.REQUEST, self.store.paths.request),
            (ArchiveKind.ANSWER, self.store.paths.answer),
            (ArchiveKind.CONSUMED, self.store.paths.tombstone),
            (ArchiveKind.COORDINATION, self.store.paths.coordination),
        )
        for kind, path in ordered:
            if not path.exists():
                continue
            if archive:
                archived.append(self.store.archive_evidence(kind, compact))
            else:
                self.store.remove_exact(path)
        return tuple(archived)


    def force_complete(self, summary: str) -> bool:
        """Close one abandoned mid-round after an explicit human decision.

        This recovery is intentionally narrower than ordinary completion. It
        cannot manufacture convergence or authorize an owning action: it only
        retires an intact, artifact-free round whose lease already expired,
        after preserving the human's reason in the append-only transcript.
        """
        if not summary.strip():
            raise ReviewExchangeError("forced completion summary must be non-empty")
        with self.store.transition_lock():
            record = self._require_record(self.classify())
            repairing = record.incomplete_transition is (
                IncompleteTransitionKind.HUMAN_COMPLETION
            )
            if repairing:
                if record.human_guidance != summary:
                    raise ReviewExchangeError(
                        "forced completion retry differs from durable decision",
                    )
            else:
                if record.incomplete_transition is not None:
                    raise ReviewExchangeError(
                        "repair the pending transition before forced completion",
                    )
                if self.classify().state is not ArtifactState.ABANDONED_MID_ROUND:
                    raise ReviewExchangeError(
                        "forced completion requires an abandoned mid-round exchange",
                    )
                entry_id = f"human-completion-round-{record.round_number}"
                record = self._mark_transition(
                    record,
                    IncompleteTransitionKind.HUMAN_COMPLETION,
                    entry_id,
                )
                record = replace(
                    record,
                    lease_renewed_at=self._timestamp(),
                    human_guidance=summary,
                )
                self.store.write_coordination(record)
            decision_timestamp = cast("str", record.lease_renewed_at)
            entry = TranscriptEntry(
                f"human-completion-round-{record.round_number}",
                ReviewRole.HUMAN,
                "human-completion",
                decision_timestamp,
                summary,
            )
            self.store.append_transcript_once(
                record,
                transition=IncompleteTransitionKind.HUMAN_COMPLETION,
                entry=entry,
                clear_marker=False,
            )
            self.store.remove_exact(self.store.paths.coordination)
            return True


# eof
