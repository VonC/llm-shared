"""Validate domain policies without a database or production host."""

from dataclasses import replace

import pytest

from tests.unit.tools.wait_service.test_store.test_store_tdd import (
    binding,
    intent,
    outcome,
)
from tools.wait_service.models import (
    MAX_TEXT,
    Capability,
    ConsumptionAttempt,
    DeadlinePolicy,
    Delivery,
    NormalEnd,
    WaitError,
)


class TestWaitModels:
    """Explicit policies and bounded records fail before persistence."""

    def test_equivalent_finite_deadlines_have_the_same_digest(self) -> None:
        """JSON number spelling cannot turn an exact intent retry into conflict."""
        original = intent()
        assert replace(original, deadline=DeadlinePolicy(20)).digest() == replace(original, deadline=DeadlinePolicy(20.0)).digest()

    @pytest.mark.parametrize("deadline", [None, float("inf"), float("nan"), True])
    def test_invalid_deadline_policy(self, deadline: float | None) -> None:
        """Missing or nonfinite deadlines cannot imply indefinite waiting."""
        with pytest.raises(WaitError, match="validation-error"):
            DeadlinePolicy(deadline)

    def test_conflicting_policy_is_invalid(self) -> None:
        """An explicit indefinite lifetime cannot also have a finite deadline."""
        with pytest.raises(WaitError, match="validation-error"):
            DeadlinePolicy(1.0, indefinite=True)

    def test_empty_identity_is_invalid(self) -> None:
        """Physical source and recipient identities cannot be display-only blanks."""
        original = intent()
        with pytest.raises(WaitError, match="identities"):
            replace(original, source=replace(original.source, worktree_id="")).digest()

    def test_binding_evidence_and_bounded_outcomes(self) -> None:
        """Unusable route and source evidence fail with typed validation errors."""
        binding().validate()
        outcome().validate()
        with pytest.raises(WaitError, match="route evidence"):
            replace(binding(), arming_evidence="").validate()
        with pytest.raises(WaitError, match="unknown outcome"):
            replace(outcome(), kind="pending").validate()
        with pytest.raises(WaitError, match="source data too large"):
            replace(outcome().observation, data="x" * (MAX_TEXT + 1)).validate()
        with pytest.raises(WaitError, match="unknown observation"):
            replace(outcome().observation, state="maybe").validate()

    def test_retry_state_and_consumption_evidence(self) -> None:
        """Delivery budgets and future settlement fields have separate meaning."""
        delivery = Delivery("event", "incarnation", "queued", 0, 0, None, "", "", "v1")
        delivery.validate()
        with pytest.raises(WaitError, match="negative retry"):
            replace(delivery, attempt_count=-1).validate()
        attempt = ConsumptionAttempt("attempt", "event", intent().recipient, "generation", "rejected")
        assert attempt.consumption_id is None
        assert not attempt.reconciliation_pending
        assert Capability.RETAINED != Capability.STRICT
        assert NormalEnd.UNAVAILABLE != NormalEnd.HOST_GATED

# eof
