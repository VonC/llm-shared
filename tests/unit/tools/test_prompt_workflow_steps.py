"""Tests for the workflow logic and prompt building of prompt_workflow.

Fix: Cover config loading, the header prefix in all three layouts, state
computation, the next-step precondition rules and the document-less tail, the
alternative lookups, and the Context resolution and prompt assembly with the
do-the-following colon (Q28).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_steps as steps
from tools.prompt_workflow_models import StepAlternative, Topic, WorkflowState

if TYPE_CHECKING:
    import pytest

# pyright: reportPrivateUsage=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false
# ruff: noqa: SLF001

_TOPIC = Topic(version="v9.8.0", slug="iso", draft_path=Path("docs/draft.v9.8.0.iso.md"))


def _state(**overrides: object) -> WorkflowState:
    base: dict[str, object] = {
        "requirement": None,
        "design": None,
        "plan": None,
        "validation_plan": None,
        "requirement_has_open_questions": False,
        "design_has_open_questions": False,
        "plan_has_open_questions": False,
        "memory_step": None,
    }
    base.update(overrides)
    return WorkflowState(**base)  # type: ignore[arg-type]


def test_load_steps_default_and_override(tmp_path: Path) -> None:
    """The shipped config loads all 13 steps; a custom path also loads."""
    alternatives_with_choice = 2
    config = steps.load_steps()
    assert sorted(config) == list(range(1, 14))
    assert len(config[1]) == alternatives_with_choice
    assert len(config[13]) == alternatives_with_choice

    custom = tmp_path / "steps.json"
    custom.write_text(
        json.dumps(
            {"steps": [{"number": 1, "alternatives": [
                {"instruction": "x.md", "body": "b", "context": ["draft"]},
            ]}]},
        ),
        encoding="utf-8",
    )
    loaded = steps.load_steps(custom)
    assert loaded[1][0].instruction == "x.md"
    assert loaded[1][0].context == ("draft",)


def test_instruction_prefix_layouts(tmp_path: Path) -> None:
    """The prefix adapts to root-is-shared, shared-under-root, and unrelated."""
    shared = steps.llm_shared_dir()

    assert steps.instruction_prefix(shared) == "instructions"
    assert steps.instruction_prefix(shared.parent) == f"{shared.name}/instructions"
    assert steps.instruction_prefix(tmp_path) == "llm-shared/instructions"


def test_compute_state_without_requirement(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """No documents on disk yields an all-empty state and no open-questions read."""
    monkeypatch.setattr(steps.docs, "select_document", lambda _r, _t, _role: None)

    state = steps.compute_state(tmp_path, _TOPIC, memory_step=None)

    assert state.requirement is None
    assert state.requirement_has_open_questions is False
    assert state.design_has_open_questions is False


def test_compute_state_with_documents(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Resolved documents drive the open-questions flags from their content."""
    resolved = {
        "requirement": Path("req.md"),
        "design": Path("design.md"),
        "plan": None,
        "validation_plan": None,
    }
    monkeypatch.setattr(
        steps.docs,
        "select_document",
        lambda _r, _t, role: resolved[role],
    )
    monkeypatch.setattr(
        steps.docs,
        "has_open_questions",
        lambda path: path == Path("req.md"),
    )

    expected_step = 4
    state = steps.compute_state(tmp_path, _TOPIC, memory_step=expected_step)

    assert state.requirement_has_open_questions is True
    assert state.design_has_open_questions is False
    assert state.memory_step == expected_step


def test_next_step_numbers_document_phase() -> None:
    """The requirement, design and plan gates pick the right review steps."""
    assert steps.next_step_numbers(_state()) == [1]
    assert steps.next_step_numbers(
        _state(requirement=Path("r"), requirement_has_open_questions=True),
    ) == [3]
    assert steps.next_step_numbers(_state(requirement=Path("r"))) == [2]
    assert steps.next_step_numbers(
        _state(requirement=Path("r"), memory_step=3),
    ) == [4]
    assert steps.next_step_numbers(
        _state(requirement=Path("r"), design=Path("d"), design_has_open_questions=True),
    ) == [6]
    assert steps.next_step_numbers(
        _state(requirement=Path("r"), design=Path("d")),
    ) == [5]
    assert steps.next_step_numbers(
        _state(requirement=Path("r"), design=Path("d"), memory_step=6),
    ) == [7]


def test_next_step_numbers_plan_review_round() -> None:
    """The plain plan gets its own review (8) and consolidate (9) round."""
    base = {"requirement": Path("r"), "design": Path("d"), "plan": Path("p")}
    # Just wrote the plan (step 7): the first move is to review it (step 8).
    assert steps.next_step_numbers(_state(**base, memory_step=7)) == [8]
    # Open questions on the plan route to the consolidate step (9).
    assert steps.next_step_numbers(
        _state(**base, plan_has_open_questions=True, memory_step=8),
    ) == [9]
    # A reviewed plan with no open questions left advances to consolidate (9).
    assert steps.next_step_numbers(_state(**base, memory_step=8)) == [9]


def test_plan_review_pending_gates_the_cycle() -> None:
    """The plan review round blocks the implement cycle until consolidate ran."""
    base = {"requirement": Path("r"), "design": Path("d")}
    # No plain plan yet: nothing pending, the cycle gate is not relevant.
    assert steps.plan_review_pending(_state(**base)) is False
    # A freshly written plan (step 7) still owes its review round.
    assert steps.plan_review_pending(_state(**base, plan=Path("p"), memory_step=7)) is True
    # Open questions on the plan keep the round pending.
    assert steps.plan_review_pending(
        _state(**base, plan=Path("p"), plan_has_open_questions=True, memory_step=9),
    ) is True
    # Consolidated (step 9) with no open questions: the cycle may take over.
    assert steps.plan_review_pending(_state(**base, plan=Path("p"), memory_step=9)) is False


def test_alternatives_for_skips_unknown_numbers() -> None:
    """Flattening alternatives ignores numbers absent from the config."""
    config = steps.load_steps()
    alternatives = steps.alternatives_for(config, [1, 99])
    assert [alt.instruction for alt in alternatives] == [
        "split-and-define.md",
        "write-requirement.md",
    ]


def test_current_alternative_lookup() -> None:
    """Current-step lookup matches by instruction, falls back, or returns None."""
    config = steps.load_steps()

    assert steps.current_alternative(config, None, None) is None
    matched = steps.current_alternative(config, 13, "prepare-release-notes.md")
    assert matched is not None
    assert matched.instruction == "prepare-release-notes.md"
    fallback = steps.current_alternative(config, 13, "missing.md")
    assert fallback is not None
    assert fallback.instruction == "implement-step.md"
    assert steps.current_alternative(config, 99, "x") is None


def test_build_prompt_resolves_context(tmp_path: Path) -> None:
    """The prompt joins header, body and a Context line with resolved roles."""
    topic = Topic(
        version="v9.8.0",
        slug="iso",
        draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md",
    )
    state = _state(
        requirement=tmp_path / "docs" / "feature-request.v9.8.0.iso.md",
        design=tmp_path / "docs" / "design.v9.8.0.iso.md",
        validation_plan=tmp_path / "docs" / "plan.v9.8.0.iso.validation.md",
    )
    alternative = StepAlternative(
        number=11,
        instruction="implementation-check.md",
        body="Check the current step implementation.",
        context=(
            "draft",
            "requirement",
            "design",
            "plan",
            "validation_plan",
            "git_status",
            "git_history",
        ),
    )

    prompt = steps.build_prompt("llm-shared/instructions", alternative, tmp_path, topic, state)

    assert prompt.startswith(
        "Follow the instructions from llm-shared/instructions/implementation-check.md "
        "and do the following:\n\nCheck the current step implementation.\n\nContext:",
    )
    assert "this is about v9.8.0 iso." in prompt
    assert "docs/draft.v9.8.0.iso.md" in prompt
    assert "the plan (not found yet)" in prompt
    assert "the current git status" in prompt
    assert "the git history since the last tag" in prompt


# eof
