"""Test Step 5 role selection and continuation routing without file IO."""

from __future__ import annotations

from tools.llm_nature import LlmNature
from tools.review_exchange_models import ArtifactState, ReviewRole
from tools.review_resume import (
    ResumeAction,
    ResumeDecisionOutcome,
    ResumeExchange,
    ReviewResumeService,
)


class TestReviewResumeService:
    """Cover role inference, explicit choices, ambiguity, and continuation routes."""

    def test_matching_reviewer_is_inferred_for_a_request(self) -> None:
        """Known reviewer evidence routes a pending request to reviewer work."""
        exchange = ResumeExchange(
            ArtifactState.REQUEST_PENDING,
            LlmNature.CODEX,
            LlmNature.CLAUDE,
        )

        decision = ReviewResumeService().decide(LlmNature.CLAUDE, (exchange,))

        assert decision.outcome is ResumeDecisionOutcome.READY
        assert decision.role is ReviewRole.REVIEWER
        assert decision.action is ResumeAction.REVIEW_REQUEST

    def test_idle_reviewer_uses_global_wait(self) -> None:
        """An explicit reviewer role may wait before any exchange exists."""
        decision = ReviewResumeService().decide(
            LlmNature.UNKNOWN,
            (),
            forced_role=ReviewRole.REVIEWER,
        )

        assert decision.outcome is ResumeDecisionOutcome.READY
        assert decision.action is ResumeAction.WAIT_ANY_REQUEST

    def test_missing_role_evidence_requires_selection(self) -> None:
        """Legacy no-nature evidence does not guess the caller's protocol role."""
        exchange = ResumeExchange(ArtifactState.ANSWER_PENDING, None, None)

        decision = ReviewResumeService().decide(LlmNature.CODEX, (exchange,))

        assert decision.outcome is ResumeDecisionOutcome.ROLE_SELECTION_REQUIRED
        assert decision.role is None

    def test_two_matching_roles_require_selection(self) -> None:
        """One LLM traced in both roles does not receive a guessed continuation."""
        exchange = ResumeExchange(
            ArtifactState.ROUND_IN_PROGRESS,
            LlmNature.CODEX,
            LlmNature.CODEX,
        )

        decision = ReviewResumeService().decide(LlmNature.CODEX, (exchange,))

        assert decision.outcome is ResumeDecisionOutcome.ROLE_SELECTION_REQUIRED
        assert decision.action is None

    def test_forced_conflicting_role_requires_confirmation(self) -> None:
        """A forced role never silently overrides contrary known evidence."""
        exchange = ResumeExchange(
            ArtifactState.REQUEST_PENDING,
            LlmNature.CODEX,
            LlmNature.CLAUDE,
        )

        decision = ReviewResumeService().decide(
            LlmNature.CODEX,
            (exchange,),
            forced_role=ReviewRole.REVIEWER,
        )

        assert decision.outcome is ResumeDecisionOutcome.CONFIRMATION_REQUIRED
        assert decision.role is ReviewRole.REVIEWER

    def test_requestor_routes_to_exact_answer_wait(self) -> None:
        """A requestor waits only for the selected exchange's answer."""
        exchange = ResumeExchange(
            ArtifactState.REQUEST_PENDING,
            LlmNature.CODEX,
            LlmNature.CLAUDE,
        )

        decision = ReviewResumeService().decide(LlmNature.CODEX, (exchange,))

        assert decision.outcome is ResumeDecisionOutcome.READY
        assert decision.action is ResumeAction.WAIT_EXACT_ANSWER

    def test_requestor_owned_state_routes_to_owned_work(self) -> None:
        """A selected requestor keeps its continuation bound to its own exchange."""
        exchange = ResumeExchange(
            ArtifactState.OWNING_ACTION_PENDING,
            LlmNature.CODEX,
            LlmNature.CLAUDE,
        )

        decision = ReviewResumeService().decide(LlmNature.CODEX, (exchange,))

        assert decision.action is ResumeAction.CONTINUE_REQUESTOR

    def test_idle_requestor_follows_the_workflow_router(self) -> None:
        """A requestor without an exchange returns to the normal workflow router."""
        decision = ReviewResumeService().decide(
            LlmNature.UNKNOWN,
            (),
            forced_role=ReviewRole.REQUESTOR,
        )

        assert decision.action is ResumeAction.FOLLOW_WORKFLOW

    def test_multiple_exchanges_are_not_selected_by_order(self) -> None:
        """Several live exchanges return typed ambiguity rather than queueing."""
        exchange = ResumeExchange(ArtifactState.REQUEST_PENDING, None, None)

        decision = ReviewResumeService().decide(
            LlmNature.UNKNOWN,
            (exchange, exchange),
            forced_role=ReviewRole.REVIEWER,
        )

        assert decision.outcome is ResumeDecisionOutcome.EXCHANGE_SELECTION_REQUIRED

    def test_unknown_host_does_not_select_a_role_from_status(self) -> None:
        """Unavailable host evidence leaves role selection to the user."""
        exchange = ResumeExchange(
            ArtifactState.REQUEST_PENDING,
            LlmNature.CODEX,
            LlmNature.CLAUDE,
        )

        decision = ReviewResumeService().decide(LlmNature.UNKNOWN, (exchange,))

        assert decision.outcome is ResumeDecisionOutcome.ROLE_SELECTION_REQUIRED
