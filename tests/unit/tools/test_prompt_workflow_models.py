"""Tests for the shared dataclasses and role constants of prompt_workflow.

Fix: Instantiate each frozen dataclass and check the role vocabulary so the
models module is exercised directly. Also check that ``MemoryRecord.plan_step``
holds a lettered sub-step id as a string (Q41).
"""

from __future__ import annotations

from pathlib import Path

from tools.prompt_workflow_models import (
    NON_FILE_ROLE_TEXT,
    ROLE_DOC_TYPES,
    MemoryRecord,
    PromptWorkflowError,
    StepAlternative,
    Topic,
    WorkflowState,
)


def test_dataclasses_carry_their_fields() -> None:
    """Each dataclass keeps the values it was built with."""
    step_number = 4
    alternative = StepAlternative(
        number=step_number,
        instruction="write-design.md",
        body="Write the design.",
        context=("draft", "requirement"),
    )
    topic = Topic(version="v9.8.0", slug="resources_isolation", draft_path=Path("d.md"))
    state = WorkflowState(
        requirement=None,
        design=None,
        plan=None,
        validation_plan=None,
        requirement_has_open_questions=False,
        design_has_open_questions=False,
        memory_step=None,
    )
    record = MemoryRecord(branch="main", version="v9.8.0", topic="resources_isolation")
    sub_record = MemoryRecord(
        branch="main", version="v9.8.0", topic="resources_isolation", plan_step="4A",
    )

    assert alternative.number == step_number
    assert topic.slug == "resources_isolation"
    assert state.memory_step is None
    assert record.step is None
    assert record.instruction is None
    assert record.plan_step is None
    assert sub_record.plan_step == "4A"


def test_role_vocabulary_is_consistent() -> None:
    """The role maps cover the file roles and the two non-file roles."""
    assert ROLE_DOC_TYPES["requirement"] == ("feature-request", "issue")
    assert "git_status" in NON_FILE_ROLE_TEXT
    assert issubclass(PromptWorkflowError, Exception)


# eof
