"""Tests for the non-interactive handoff resolution core (prompt_workflow_handoff).

These cover the task-to-action mapping and the ``after-check`` routing, the
named-step lookup against the validation plan and its missing-plan and not-found
errors, the derived-step mismatch report, and the menu-less topic resolution with
its branch-lock and refusal paths. The module owns no terminal IO, so the
validation-plan cases read a small file written under ``tmp_path`` and the git
lookup is monkeypatched.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import prompt_workflow_handoff as handoff
from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState
from tools.prompt_workflow_plan import CycleAction, PlanStep

_VALIDATION = """\
### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

### Analysis of Step 2 implementation state

No. Step 2 has NOT been fully implemented.

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented yet.
"""

_TOPIC = Topic(
    version="v0.1.0",
    slug="pw_handoff",
    draft_path=Path("docs/draft.v0.1.0.pw_handoff.md"),
)
_OTHER = Topic(
    version="v1.0.0",
    slug="other",
    draft_path=Path("docs/draft.v1.0.0.other.md"),
)


def _state(validation_plan: Path | None) -> WorkflowState:
    return WorkflowState(
        requirement=None,
        design=None,
        plan=None,
        validation_plan=validation_plan,
        requirement_has_open_questions=False,
        design_has_open_questions=False,
        memory_step=None,
    )


def _write_validation(tmp_path: Path, text: str = _VALIDATION) -> Path:
    path = tmp_path / "plan.v0.1.0.pw_handoff.validation.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_find_plan_step_returns_matching_step(tmp_path: Path) -> None:
    """A named step id is read from its Analysis of Step section."""
    state = _state(_write_validation(tmp_path))

    step = handoff.find_plan_step(state, "2")

    assert step.number == "2"
    assert step.not_implemented is True


def test_find_plan_step_without_validation_plan() -> None:
    """A missing validation plan is a fatal handoff error."""
    with pytest.raises(handoff.PromptWorkflowError, match="No validation plan"):
        handoff.find_plan_step(_state(None), "2")


def test_find_plan_step_unknown_id(tmp_path: Path) -> None:
    """An id with no Analysis of Step section is a fatal handoff error (Q59)."""
    state = _state(_write_validation(tmp_path))

    with pytest.raises(handoff.PromptWorkflowError, match="Analysis of Step 9"):
        handoff.find_plan_step(state, "9")


def test_action_for_task_direct_tokens() -> None:
    """The three direct task words map to their cycle actions (Q57, Q62)."""
    verified = PlanStep(number="2", verified=True)

    assert handoff.action_for_task("check", verified) == CycleAction(
        kind="check",
        stage_all=False,
    )
    assert handoff.action_for_task("implement-missing", verified) == CycleAction(
        kind="implement",
        stage_all=False,
        missing=True,
    )
    assert handoff.action_for_task("commit", verified) == CycleAction(
        kind="commit",
        stage_all=True,
    )


def test_action_for_task_after_check_routes_on_status() -> None:
    """after-check routes to implement-missing on No and commit on Yes (Q58)."""
    no_step = PlanStep(number="2", verified=False, not_implemented=True)
    yes_step = PlanStep(number="2", verified=True, not_implemented=False)

    assert handoff.action_for_task("after-check", no_step) == CycleAction(
        kind="implement",
        stage_all=False,
        missing=True,
    )
    assert handoff.action_for_task("after-check", yes_step) == CycleAction(
        kind="commit",
        stage_all=True,
    )


def test_action_for_task_after_check_placeholder_raises() -> None:
    """after-check on a step with no Yes/No status is a fatal handoff error."""
    placeholder = PlanStep(number="3", verified=False, not_implemented=False)

    with pytest.raises(handoff.PromptWorkflowError, match="no Yes/No status"):
        handoff.action_for_task("after-check", placeholder)


def test_action_for_task_unknown_token_raises() -> None:
    """An unknown task word is a fatal handoff error (Q62)."""
    with pytest.raises(handoff.PromptWorkflowError, match="Unknown handoff task"):
        handoff.action_for_task("publish", PlanStep(number="2", verified=True))


def test_cycle_state_for_step_carries_status() -> None:
    """The carrier state mirrors the step id and status; flags stay False (Q60)."""
    state = handoff.cycle_state_for_step(
        PlanStep(number="4A", verified=False, not_implemented=True),
    )

    assert state.x == "4A"
    assert state.verified is False
    assert state.not_implemented is True
    assert (state.has_code_changes, state.cached, state.non_cached) == (False, False, False)


def test_derived_mismatch_reports_difference(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The derived step is reported when it differs from the handed step (Q59)."""
    monkeypatch.setattr(handoff.git, "has_step_commit", lambda _root, _n, _base: False)
    state = _state(_write_validation(tmp_path))

    # derive_x picks the last Yes ("1"), so a handed "2" differs from it.
    assert handoff.derived_mismatch(tmp_path, state, None, "2") == "1"
    # A handed "1" matches the derived step, so there is no mismatch.
    assert handoff.derived_mismatch(tmp_path, state, None, "1") is None


def test_derived_mismatch_without_steps(tmp_path: Path) -> None:
    """A missing validation plan and an empty plan both report no mismatch."""
    assert handoff.derived_mismatch(tmp_path, _state(None), None, "2") is None

    empty = _state(_write_validation(tmp_path, "# no analysis sections here\n"))
    assert handoff.derived_mismatch(tmp_path, empty, None, "2") is None


def test_resolve_topic_single_and_lock() -> None:
    """A lone topic is used; with several, the branch-locked one wins (Q63)."""
    assert handoff.resolve_topic([_TOPIC], None, "main") == _TOPIC

    record = MemoryRecord(branch="main", version="v0.1.0", topic="pw_handoff")
    assert handoff.resolve_topic([_OTHER, _TOPIC], record, "main") == _TOPIC


def test_resolve_topic_refuses_without_lock() -> None:
    """Several drafts and no lock resolve to None, so the caller refuses (Q63)."""
    assert handoff.resolve_topic([_OTHER, _TOPIC], None, "main") is None

    mismatch = MemoryRecord(branch="main", version="v9.9.9", topic="pw_handoff")
    assert handoff.resolve_topic([_OTHER, _TOPIC], mismatch, "main") is None


# eof
