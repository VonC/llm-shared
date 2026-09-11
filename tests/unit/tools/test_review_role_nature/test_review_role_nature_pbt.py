"""Properties of stable role-nature reconciliation."""

from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.llm_nature import LlmNature
from tools.review_exchange_models import ReviewRole
from tools.review_role_nature import RoleNatureEvidence, RoleNatureReconciler


@given(
    st.lists(
        st.sampled_from([None, *LlmNature]),
        min_size=0,
        max_size=40,
    ),
)
@settings(max_examples=40)
def test_reconciliation_preserves_input_order_and_collects_every_conflict(
    natures: list[LlmNature | None],
) -> None:
    """One linear pass returns all conflicts in their original order."""
    evidence = [
        RoleNatureEvidence(Path(f"artifact-{index}.json"), ReviewRole.REQUESTOR, nature)
        for index, nature in enumerate(natures)
    ]

    result = RoleNatureReconciler().reconcile(
        evidence,
        ReviewRole.REQUESTOR,
        LlmNature.CODEX,
    )

    expected = [
        item
        for item in evidence
        if item.nature not in {None, LlmNature.CODEX, LlmNature.UNKNOWN}
    ]
    assert list(result.conflicts) == expected
