"""Request and answer publication transitions for review exchanges.

Step 2 merges the acting host into the durable two-role snapshot before request,
answer, coordination, and transcript publication.
"""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import replace
from typing import TYPE_CHECKING, cast

from tools.llm_nature import LlmNatureDetector
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    IncompleteTransitionKind,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_models_envelope import (
    render_envelope_markdown,
    validate_summary_identity,
)
from tools.review_exchange_store import TranscriptEntry
from tools.review_exchange_transcript_identity import (
    current_request_occurrence,
    transcript_entry_base,
)
from tools.review_markdown_headings import qualify_round_headings

if TYPE_CHECKING:
    from tools.review_exchange_models import ReviewContext
    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_models_envelope import Envelope
    from tools.review_exchange_observer import ExchangeObservation
    from tools.review_exchange_store import ReviewExchangeStore
    from tools.review_role_nature import RoleNatureSnapshot


class ReviewExchangePublicationMixin(ABC):
    """Publish exact artifacts and keep their transcript entries collision-free."""

    store: ReviewExchangeStore
    context: ReviewContext

    @staticmethod
    def _acting_snapshot(
        record: CoordinationRecord,
        envelope: Envelope,
        role: ReviewRole,
    ) -> RoleNatureSnapshot:
        """Merge persisted evidence and record the current non-secret host enum."""
        snapshot = record.role_natures.merge(envelope.role_natures)
        nature = LlmNatureDetector().detect(os.environ).nature
        return snapshot.record(role, nature)

    def _rendered_human_guidance(
        self,
        guidance: str,
        round_number: int,
    ) -> str:
        """Return guidance as request renderers nest it below their H2 section."""
        identity = self.context.identity
        step = self.context.implementation_step
        qualifier = (
            f"step {step} {identity.slug}"
            if step is not None
            else f"{identity.type_token} {identity.slug}"
        )
        return qualify_round_headings(
            guidance.rstrip(),
            minimum_level=3,
            qualifier=qualifier,
            round_number=round_number,
        )

    @abstractmethod
    def classify(self) -> ExchangeObservation:
        """Return the current exact-path observation."""

    @abstractmethod
    def _require_record(self, observation: ExchangeObservation) -> CoordinationRecord:
        """Return current coordination or fail."""

    @abstractmethod
    def _validate_envelope(
        self,
        markdown: str,
        role: ReviewRole,
        record: CoordinationRecord,
    ) -> tuple[Envelope, str]:
        """Validate exact context, role, and current round."""

    @abstractmethod
    def _mark_transition(
        self,
        record: CoordinationRecord,
        transition: IncompleteTransitionKind,
        entry_id: str,
    ) -> CoordinationRecord:
        """Persist a marker before the first publication side effect."""

    @abstractmethod
    def _publish_or_repair_answer(self, markdown: str) -> None:
        """Publish an answer or repair its interrupted publication."""

    @abstractmethod
    def _timestamp(self) -> str:
        """Return a local ISO-8601 timestamp."""

    @abstractmethod
    def _clear_marker(self, record: CoordinationRecord) -> CoordinationRecord:
        """Return coordination without transcript repair bookkeeping."""

    def publish_request(
        self,
        markdown: str,
        transcript_content: str,
    ) -> CoordinationRecord:
        """Publish and append one validated current-round request idempotently."""
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            repairing = record.incomplete_transition is (
                IncompleteTransitionKind.PUBLISH_REQUEST
            )
            if not repairing and observation.state is not ArtifactState.ROUND_IN_PROGRESS:
                raise ReviewExchangeError("request publication requires a round in progress")
            envelope, authored = self._validate_envelope(markdown, ReviewRole.REQUESTOR, record)
            snapshot = self._acting_snapshot(record, envelope, ReviewRole.REQUESTOR)
            envelope = replace(envelope, role_natures=snapshot)
            record = replace(record, role_natures=snapshot)
            markdown = render_envelope_markdown(envelope, authored)
            validate_summary_identity(authored, self.context, record.round_number)
            if record.human_guidance is not None:
                rendered_guidance = self._rendered_human_guidance(
                    record.human_guidance,
                    record.round_number,
                )
                expected_guidance = (
                    f"Human guidance:\n\n{rendered_guidance}",
                    # Compatibility for the first heading-aware renderer, which
                    # kept the label and nested Markdown on one line.
                    f"Human guidance: {rendered_guidance}",
                    # Compatibility for requests authored before guidance headings
                    # became renderer-owned. Keep the exact-content requirement.
                    f"Human guidance: {record.human_guidance}",
                )
                if not any(candidate in authored for candidate in expected_guidance):
                    raise ReviewExchangeError(
                        "replacement request summary omits confirmed human guidance",
                    )
            entry_id, occurrence = self._exchange_entry(
                self._entry_base(ReviewRole.REQUESTOR, record.round_number),
                before_offset=record.transcript_offset if repairing else None,
            )
            entry = TranscriptEntry(
                entry_id,
                ReviewRole.REQUESTOR,
                "request",
                envelope.created_at,
                transcript_content,
                occurrence,
            )
            marked = self._mark_transition(
                record,
                IncompleteTransitionKind.PUBLISH_REQUEST,
                entry.entry_id,
            )
            self.store.publish_request(markdown)
            marked = self.store.append_transcript_once(
                marked,
                transition=IncompleteTransitionKind.PUBLISH_REQUEST,
                entry=entry,
                clear_marker=False,
            )
            final = replace(
                marked,
                owner=Actor.REQUESTOR,
                expected_next_actor=Actor.REVIEWER,
                lease_renewed_at=self._timestamp(),
                incomplete_transition=None,
                transcript_entry_id=None,
                transcript_offset=None,
                human_guidance=None,
            )
            self.store.write_coordination(final)
            return final

    def publish_answer(
        self,
        markdown: str,
        transcript_content: str,
    ) -> CoordinationRecord:
        """Consume, publish, append, and route one reviewer answer safely."""
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            repairing = record.incomplete_transition is (
                IncompleteTransitionKind.PUBLISH_ANSWER
            )
            if not repairing and observation.state is not ArtifactState.REQUEST_PENDING:
                raise ReviewExchangeError("answer publication requires a request pending")
            envelope, authored = self._validate_envelope(
                markdown,
                ReviewRole.REVIEWER,
                record,
            )
            snapshot = self._acting_snapshot(record, envelope, ReviewRole.REVIEWER)
            envelope = replace(envelope, role_natures=snapshot)
            record = replace(record, role_natures=snapshot)
            markdown = render_envelope_markdown(envelope, authored)
            before_offset = record.transcript_offset if repairing else None
            occurrence = current_request_occurrence(
                self.store,
                self.context,
                record.round_number,
                before_offset=before_offset,
            )
            base = transcript_entry_base(
                self.context,
                ReviewRole.REVIEWER,
                record.round_number,
            )
            entry_id = base if occurrence == 1 else f"{base}-exchange-{occurrence}"
            entry = TranscriptEntry(
                entry_id,
                ReviewRole.REVIEWER,
                "answer",
                envelope.created_at,
                transcript_content,
                occurrence,
            )
            marked = self._mark_transition(
                record,
                IncompleteTransitionKind.PUBLISH_ANSWER,
                entry.entry_id,
            )
            self._publish_or_repair_answer(markdown)
            marked = self.store.append_transcript_once(
                marked,
                transition=IncompleteTransitionKind.PUBLISH_ANSWER,
                entry=entry,
                clear_marker=False,
            )
            self.store.remove_exact(self.store.paths.tombstone)
            convergence = envelope.disposition is ReviewDisposition.CONVERGENCE_RECOMMENDED
            final = replace(
                marked,
                status=(
                    CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
                    if convergence
                    else CoordinationStatus.ACTIVE
                ),
                owner=Actor.REVIEWER,
                expected_next_actor=Actor.HUMAN if convergence else Actor.REQUESTOR,
                lease_renewed_at=None if convergence else self._timestamp(),
                convergence_recommended=convergence,
                incomplete_transition=None,
                transcript_entry_id=None,
                transcript_offset=None,
            )
            self.store.write_coordination(final)
            return final

    def repair_current_request_transcript(
        self,
        transcript_content: str,
    ) -> CoordinationRecord:
        """Re-render one final pending legacy request with exchange identity."""
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            repairing = record.incomplete_transition is (
                IncompleteTransitionKind.PUBLISH_REQUEST
            )
            if not repairing and observation.state is not ArtifactState.REQUEST_PENDING:
                raise ReviewExchangeError(
                    "request transcript repair requires a pending request",
                )
            markdown = self.store.read_artifact(self.store.paths.request)
            envelope, authored = self._validate_envelope(
                markdown,
                ReviewRole.REQUESTOR,
                record,
            )
            validate_summary_identity(authored, self.context, record.round_number)
            base = self._entry_base(ReviewRole.REQUESTOR, record.round_number)
            offset = self._request_repair_offset(
                record,
                base,
                repairing=repairing,
            )
            occurrence = self.store.entry_occurrence(
                base,
                discriminator="exchange",
                before_offset=offset,
            )
            if occurrence <= 1:
                raise ReviewExchangeError("request transcript entry has no exchange collision")
            entry_id = f"{base}-exchange-{occurrence}"
            marked = self._request_repair_marker(
                record,
                entry_id,
                offset,
                repairing=repairing,
            )
            entry = TranscriptEntry(
                entry_id,
                ReviewRole.REQUESTOR,
                "request",
                envelope.created_at,
                transcript_content,
                occurrence,
            )
            marked = self.store.append_transcript_once(
                marked,
                transition=IncompleteTransitionKind.PUBLISH_REQUEST,
                entry=entry,
                clear_marker=False,
            )
            final = self._clear_marker(marked)
            self.store.write_coordination(final)
            return final

    def _request_repair_offset(
        self,
        record: CoordinationRecord,
        base: str,
        *,
        repairing: bool,
    ) -> int:
        """Return the durable or newly located final-entry byte offset."""
        if not repairing:
            return self.store.current_entry_offset(base)
        # CoordinationRecord validates marker identity and byte offset together.
        return cast("int", record.transcript_offset)

    def _request_repair_marker(
        self,
        record: CoordinationRecord,
        entry_id: str,
        offset: int,
        *,
        repairing: bool,
    ) -> CoordinationRecord:
        """Persist or validate the marker for one legacy entry replacement."""
        if repairing:
            if record.transcript_entry_id != entry_id:
                raise ReviewExchangeError("pending request transcript repair identity differs")
            return record
        marked = replace(
            record,
            incomplete_transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            transcript_entry_id=entry_id,
            transcript_offset=offset,
        )
        self.store.write_coordination(marked)
        return marked

    def _exchange_entry(
        self,
        base: str,
        *,
        before_offset: int | None = None,
    ) -> tuple[str, int]:
        """Return a unique request or answer identity across restarted exchanges."""
        occurrence = self.store.entry_occurrence(
            base,
            discriminator="exchange",
            before_offset=before_offset,
        )
        entry_id = base if occurrence == 1 else f"{base}-exchange-{occurrence}"
        return entry_id, occurrence

    def _entry_base(self, role: ReviewRole, round_number: int) -> str:
        """Return a round identity scoped by step for code reviews."""
        return transcript_entry_base(self.context, role, round_number)


# eof
