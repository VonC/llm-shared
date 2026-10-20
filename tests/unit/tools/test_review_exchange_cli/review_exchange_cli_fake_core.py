"""Scripted lifecycle facade shared by review-exchange command tests."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tools.review_exchange_human import ConfirmationDecision, ResolutionResult
from tools.review_exchange_models import Actor, ArtifactState, ConfirmationOutcome
from tools.review_exchange_observer import ExchangeObservation
from tools.review_exchange_ownership import (
    OwnershipCapability,
    OwnershipClaim,
    OwnershipRejectedError,
)
from tools.review_exchange_wait import WaitOutcome, WaitProgress, WaitResult

if TYPE_CHECKING:
    from tools.review_exchange_models_coordination import CoordinationRecord


class FakeCore:
    """Record CLI delegation, optional scope capture and ownership capabilities."""

    def __init__(self, record: CoordinationRecord) -> None:
        """Start in a normal active round with an empty call log."""
        self.record = record
        self.state = ArtifactState.ROUND_IN_PROGRESS
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []
        self.wait_outcome = WaitOutcome.FOUND
        self.fail: Exception | None = None
        self.ownership_capability: OwnershipCapability | None = None
        self.ownership_capability_issued = False

    def present_ownership(self, capability: OwnershipCapability | None) -> None:
        """Record the parsed capability without adding a lifecycle call."""
        self.ownership_capability = capability
        self.ownership_capability_issued = False

    def _call(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Record a call or raise the injected failure."""
        if self.fail is not None:
            error = self.fail
            if isinstance(error, OwnershipRejectedError):
                self.fail = None
            raise error
        self.calls.append((name, args, kwargs))

    def classify(self) -> ExchangeObservation:
        """Return the scripted observable state."""
        if self.fail is not None:
            raise self.fail
        return ExchangeObservation(self.state, self.record, None, None, "scripted state")

    def start(self) -> CoordinationRecord:
        """Record round start."""
        self._call("start")
        return self.record

    def publish_request(
        self,
        markdown: str,
        transcript_content: str,
        scope_capture: str | None = None,
        *,
        amend_pending: bool = False,
    ) -> CoordinationRecord:
        """Record request publication inputs with the optional scope contract."""
        if amend_pending:
            self._call("amend_request", markdown, transcript_content, scope_capture)
        elif scope_capture is None:
            self._call("publish_request", markdown, transcript_content)
        else:
            self._call("publish_request", markdown, transcript_content, scope_capture)
        return self.record

    def publish_answer(
        self,
        markdown: str,
        transcript_content: str,
    ) -> CoordinationRecord:
        """Record answer publication inputs."""
        self._call("publish_answer", markdown, transcript_content)
        return self.record

    def repair_current_request_transcript(
        self,
        transcript_content: str,
    ) -> CoordinationRecord:
        """Record final legacy request transcript repair."""
        self._call("repair_current_request_transcript", transcript_content)
        return self.record

    def wait_for_exact(
        self,
        expected: ArtifactState,
        **kwargs: Any,
    ) -> WaitResult:
        """Emit one progress event and return the scripted wait outcome."""
        self._call("wait_for_exact", expected, **kwargs)
        callback = kwargs["progress_callback"]
        callback(WaitProgress(1.0, 4.0, ArtifactState.ROUND_IN_PROGRESS))
        observation = ExchangeObservation(
            expected,
            self.record,
            None,
            None,
            "wait finished",
        )
        return WaitResult(self.wait_outcome, observation)

    def consume_answer(self, **kwargs: Any) -> CoordinationRecord:
        """Record answer assessment flags."""
        self._call("consume_answer", **kwargs)
        return self.record

    def continue_round(self) -> CoordinationRecord:
        """Record automated continuation."""
        self._call("continue_round")
        return replace(self.record, round_number=self.record.round_number + 1)

    def reclaim(self) -> CoordinationRecord:
        """Record an abandoned-round lease renewal."""
        self._call("reclaim")
        return self.record

    def force_reclaim(self, summary: str) -> CoordinationRecord:
        """Record one authorized forced resume of an escalated round."""
        self._call("force_reclaim", summary)
        return self.record

    def pickup_ownership(self, actor: Actor) -> OwnershipClaim:
        """Record one lease-independent capability pickup."""
        self._call("pickup_ownership", actor)
        self.ownership_capability = OwnershipCapability(2, "t" * 32)
        self.ownership_capability_issued = True
        return OwnershipClaim(self.record, self.ownership_capability)

    def escalate(self, reason: str) -> CoordinationRecord:
        """Record an escalation reason."""
        self._call("escalate", reason)
        return self.record

    def confirm(
        self,
        label: str,
        *,
        guidance: str | None = None,
    ) -> ConfirmationDecision:
        """Record a human confirmation."""
        self._call("confirm", label, guidance=guidance)
        return ConfirmationDecision(
            outcome=ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW,
            owning_action_authorized=True,
            record=self.record,
        )

    def cancel(self, reason: str) -> CoordinationRecord:
        """Record convergence cancellation."""
        self._call("cancel", reason)
        return self.record

    def resolve_escalation(self, summary: str, *, archive: bool) -> ResolutionResult:
        """Record clear-or-archive recovery."""
        self._call("resolve_escalation", summary, archive=archive)
        archived = (Path("a.review-archive.test.md"),) if archive else ()
        return ResolutionResult(self.record, archived)

    def complete(self) -> bool:
        """Record owning-action completion."""
        self._call("complete")
        return True

    def force_complete(self, summary: str) -> bool:
        """Record one authorized forced completion."""
        self._call("force_complete", summary)
        return True
