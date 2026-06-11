"""Shared workflow-state builder of the prompt_workflow plan-cycle tests.

Split out of ``test_prompt_workflow_plan.py`` for the repo line budget:
both plan-cycle files (the parsing, derivation and menu scenarios, and
the per-step prompt scenarios) build the same workflow state through
this helper, so the real plan parsing, cycle derivation and prompt
building stays under test.
"""

from __future__ import annotations

from pathlib import Path

from tools.prompt_workflow_models import WorkflowState


def make_state(**overrides: object) -> WorkflowState:
    """Build a workflow state with every plan document resolved.

    Args:
        **overrides: The WorkflowState fields to replace.

    Returns:
        The workflow state.
    """
    base: dict[str, object] = {
        "requirement": Path("docs/feature-request.v9.8.0.iso.md"),
        "design": Path("docs/design.v9.8.0.iso.md"),
        "plan": Path("docs/plan.v9.8.0.iso.md"),
        "validation_plan": Path("docs/plan.v9.8.0.iso.validation.md"),
        "requirement_has_open_questions": False,
        "design_has_open_questions": False,
        "memory_step": None,
    }
    base.update(overrides)
    return WorkflowState(**base)  # type: ignore[arg-type]


# eof
