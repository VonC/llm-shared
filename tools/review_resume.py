"""Pure role selection and continuation routing for interrupted reviews.

Step 5 keeps resume policy separate from filesystem discovery and LLM prompts.
The service receives typed live-exchange evidence, resolves only a defensible
role, and returns the next role-owned action without performing a mutation.
Intact lease expiry is recoverable evidence for both resume and global waiting.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from tools.llm_nature import LlmNature
from tools.review_exchange_models import ArtifactState, ReviewRole

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.review_exchange_ownership import OwnershipCapability


def can_resume_expired_leases(states: tuple[ArtifactState | None, ...]) -> bool:
    """Accept lease-only abandonment without masking damaged or repair states."""
    abandoned = {
        ArtifactState.ABANDONED_REQUEST, ArtifactState.ABANDONED_ANSWER,
        ArtifactState.ABANDONED_MID_ROUND,
    }
    intact = abandoned | {
        ArtifactState.IDLE, ArtifactState.ROUND_IN_PROGRESS,
        ArtifactState.REQUEST_PENDING, ArtifactState.ANSWER_PENDING,
        ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS,
        ArtifactState.CONVERGENCE_GATE, ArtifactState.OWNING_ACTION_PENDING,
    }
    return any(state in abandoned for state in states) and all(state in intact for state in states)


class ResumeAction(StrEnum):
    """Role-owned next actions returned to the canonical resume instruction."""

    REVIEW_REQUEST = "review-request"
    WAIT_ANY_REQUEST = "wait-any-request"
    WAIT_EXACT_ANSWER = "wait-exact-answer"
    CONTINUE_REQUESTOR = "continue-requestor"
    FOLLOW_WORKFLOW = "follow-workflow"


class ResumeDecisionOutcome(StrEnum):
    """Typed readiness and human-choice boundaries for one resume attempt."""

    READY = "ready"
    ROLE_SELECTION_REQUIRED = "role-selection-required"
    CONFIRMATION_REQUIRED = "confirmation-required"
    EXCHANGE_SELECTION_REQUIRED = "exchange-selection-required"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ResumeExchange:
    """Minimal trusted exchange facts needed for role routing."""

    state: ArtifactState
    requestor_nature: LlmNature | None
    reviewer_nature: LlmNature | None
    requestor_conflicting: bool = False
    reviewer_conflicting: bool = False

    def nature_for(self, role: ReviewRole) -> LlmNature | None:
        """Return the recorded LLM nature for one non-human review role."""
        return self.requestor_nature if role is ReviewRole.REQUESTOR else self.reviewer_nature


@dataclass(frozen=True)
class ResumeDecision:
    """One non-mutating resume-policy result for a session or human prompt."""

    outcome: ResumeDecisionOutcome
    role: ReviewRole | None = None
    action: ResumeAction | None = None


@dataclass(frozen=True)
class ResumeContext:
    """Human resume intent and the selected, freshly inspected exchange."""

    current_nature: LlmNature
    exchanges: tuple[ResumeExchange, ...]
    role: ReviewRole | None = None
    override: bool = False


@dataclass(frozen=True)
class ResumeRoleResolution:
    """Resolved continuation with an optional session-only capability."""

    decision: ResumeDecision
    capability: OwnershipCapability | None = None


class ReviewResumeService:
    """Gate identity and role before an injected automatic ownership claim."""

    def resume(
        self,
        context: ResumeContext,
        acquire: Callable[[ReviewRole], OwnershipCapability],
    ) -> ResumeRoleResolution:
        """Acquire only after all gates pass; an idle role creates no exchange."""
        decision = self.decide(
            context.current_nature, context.exchanges,
            forced_role=context.role, override=context.override,
        )
        capability = None
        if decision.outcome is ResumeDecisionOutcome.READY and context.exchanges and decision.role is not None:
            capability = acquire(decision.role)
        return ResumeRoleResolution(decision, capability)

    def decide(
        self,
        current_nature: LlmNature,
        exchanges: tuple[ResumeExchange, ...],
        *,
        forced_role: ReviewRole | None = None,
        override: bool = False,
    ) -> ResumeDecision:
        """Return one typed route without guessing a role or exchange ordering."""
        if len(exchanges) > 1:
            return ResumeDecision(ResumeDecisionOutcome.EXCHANGE_SELECTION_REQUIRED)
        exchange = exchanges[0] if exchanges else None
        if exchange is not None and exchange.state in {
            ArtifactState.ESCALATED, ArtifactState.INCONSISTENT,
            ArtifactState.INTERRUPTED_ANSWER_PUBLICATION,
            ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND,
            ArtifactState.TRANSCRIPT_REPAIR_PENDING,
            ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS,
        }:
            return ResumeDecision(ResumeDecisionOutcome.BLOCKED)
        if forced_role is not None:
            return self._forced_role(current_nature, exchange, forced_role, override=override)
        matching = () if exchange is None else self._matching_roles(current_nature, exchange)
        if len(matching) != 1:
            return ResumeDecision(ResumeDecisionOutcome.ROLE_SELECTION_REQUIRED)
        return self._ready(matching[0], exchange)

    def _forced_role(
        self, nature: LlmNature, exchange: ResumeExchange | None,
        role: ReviewRole, *, override: bool,
    ) -> ResumeDecision:
        """Apply the selected role's complete evidence gate independently of its counterpart."""
        conflicting = False
        if exchange is not None:
            recorded_conflict = exchange.requestor_conflicting if role is ReviewRole.REQUESTOR else exchange.reviewer_conflicting
            conflicting = recorded_conflict or self._conflicts(nature, exchange.nature_for(role))
        if conflicting and not override:
            return ResumeDecision(ResumeDecisionOutcome.CONFIRMATION_REQUIRED, role=role)
        return self._ready(role, exchange)

    @staticmethod
    def _matching_roles(
        current_nature: LlmNature,
        exchange: ResumeExchange,
    ) -> tuple[ReviewRole, ...]:
        """Return exactly the roles with known evidence matching this host."""
        if current_nature is LlmNature.UNKNOWN:
            return ()
        return tuple(
            role
            for role in (ReviewRole.REQUESTOR, ReviewRole.REVIEWER)
            if exchange.nature_for(role) is current_nature
        )

    @staticmethod
    def _conflicts(
        current_nature: LlmNature,
        recorded_nature: LlmNature | None,
    ) -> bool:
        """Return whether an explicit role contradicts strong recorded evidence."""
        return (
            current_nature is not LlmNature.UNKNOWN
            and recorded_nature not in {None, LlmNature.UNKNOWN, current_nature}
        )

    @staticmethod
    def _ready(
        role: ReviewRole,
        exchange: ResumeExchange | None,
    ) -> ResumeDecision:
        """Map one resolved role and optional exchange to its owned action."""
        if role is ReviewRole.REVIEWER:
            action = (
                ResumeAction.REVIEW_REQUEST
                if exchange is not None and exchange.state in {ArtifactState.REQUEST_PENDING, ArtifactState.ABANDONED_REQUEST}
                else ResumeAction.WAIT_ANY_REQUEST
            )
        elif exchange is None:
            action = ResumeAction.FOLLOW_WORKFLOW
        else:
            action = (
                ResumeAction.WAIT_EXACT_ANSWER
                if exchange.state in {ArtifactState.ANSWER_PENDING, ArtifactState.REQUEST_PENDING, ArtifactState.ABANDONED_REQUEST, ArtifactState.ABANDONED_ANSWER}
                else ResumeAction.CONTINUE_REQUESTOR
            )
        return ResumeDecision(ResumeDecisionOutcome.READY, role, action)


__all__ = [
    "ResumeAction",
    "ResumeContext",
    "ResumeDecision",
    "ResumeDecisionOutcome",
    "ResumeExchange",
    "ResumeRoleResolution",
    "ReviewResumeService",
    "can_resume_expired_leases",
]


# eof
