"""Workflow logic for prompt_workflow: config, state, next steps, prompt text.

This module loads the static per-step configuration (Q13/Q14), computes the
header path prefix (Q10), derives the workflow state from the documents on disk
and the persisted step (Q04/Q11), decides the available next steps from the
precondition rules of the spec, and assembles the three-part prompt: a header
ending with a colon, the per-step body, and the Context section, the three
separated by a blank line (Q09, Q28).
"""

from __future__ import annotations

import json
import operator
import os
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_docs as docs
from tools.prompt_workflow_models import (
    NON_FILE_ROLE_TEXT,
    StepAlternative,
    WorkflowState,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.prompt_workflow_models import Topic

# Name of the per-step configuration file shipped next to this tool.
STEPS_CONFIG_NAME = "prompt_workflow.steps.json"
# Folder name of the instructions directory inside llm-shared.
INSTRUCTIONS_DIR = "instructions"
# Default llm-shared sub-folder name when it is not under the project root (Q10).
DEFAULT_SHARED_PREFIX = "llm-shared"
# Header template ending with a colon (Q28); the prefix already ends with the
# instructions directory.
HEADER_TEMPLATE = "Follow the instructions from {prefix}/{instruction} and do the following:"

# Map a file role to the WorkflowState attribute that holds its resolved path.
_ROLE_ATTRGETTER: dict[str, Callable[[WorkflowState], Path | None]] = {
    "requirement": operator.attrgetter("requirement"),
    "design": operator.attrgetter("design"),
    "plan": operator.attrgetter("plan"),
    "validation_plan": operator.attrgetter("validation_plan"),
}


def config_path() -> Path:
    """Return the path to the per-step JSON configuration next to this module."""
    return Path(__file__).resolve().parent / STEPS_CONFIG_NAME


def load_steps(path: Path | None = None) -> dict[int, list[StepAlternative]]:
    """Load the per-step configuration into a step-number to alternatives map.

    Args:
        path: Optional override of the configuration file; defaults to the file
            shipped next to this module.

    Returns:
        A mapping from step number to its list of selectable alternatives.
    """
    config_file = path if path is not None else config_path()
    data = json.loads(config_file.read_text(encoding="utf-8"))
    steps: dict[int, list[StepAlternative]] = {}
    for entry in data["steps"]:
        number = int(entry["number"])
        steps[number] = [
            StepAlternative(
                number=number,
                instruction=alternative["instruction"],
                body=alternative["body"],
                context=tuple(alternative["context"]),
            )
            for alternative in entry["alternatives"]
        ]
    return steps


def llm_shared_dir() -> Path:
    """Return the llm-shared directory (the parent of this ``tools/`` folder)."""
    return Path(__file__).resolve().parent.parent


def instruction_prefix(root: Path) -> str:
    """Return the instructions path prefix relative to the project root (Q10).

    Args:
        root: The resolved project root.

    Returns:
        ``instructions`` when the root is llm-shared itself, ``<rel>/instructions``
        when llm-shared sits under the root, and ``llm-shared/instructions`` when
        it is not under the root at all.
    """
    shared = llm_shared_dir()
    try:
        rel = shared.relative_to(root)
    except ValueError:
        return f"{DEFAULT_SHARED_PREFIX}/{INSTRUCTIONS_DIR}"
    rel_posix = rel.as_posix()
    if rel_posix == ".":
        return INSTRUCTIONS_DIR
    return f"{rel_posix}/{INSTRUCTIONS_DIR}"


def compute_state(root: Path, topic: Topic, memory_step: int | None) -> WorkflowState:
    """Resolve the documents and open-questions flags into a WorkflowState."""
    requirement = docs.select_document(root, topic, "requirement")
    design = docs.select_document(root, topic, "design")
    plan = docs.select_document(root, topic, "plan")
    validation_plan = docs.select_document(root, topic, "validation_plan")
    return WorkflowState(
        requirement=requirement,
        design=design,
        plan=plan,
        validation_plan=validation_plan,
        requirement_has_open_questions=(
            requirement is not None and docs.has_open_questions(requirement)
        ),
        design_has_open_questions=(
            design is not None and docs.has_open_questions(design)
        ),
        plan_has_open_questions=(
            plan is not None and docs.has_open_questions(plan)
        ),
        memory_step=memory_step,
    )


def _step_below(step: int | None, threshold: int) -> bool:
    """Return whether the persisted step is unset or below the threshold."""
    return step is None or step < threshold


def next_step_numbers(state: WorkflowState) -> list[int]:
    """Return the document-phase step numbers (1 to 9).

    The plain plan gets the same review-and-consolidate round the requirement and
    design get: write-plans (7), then review-ask-questions (8) and
    consolidate-then-review-ask-questions (9), looping while the plan carries open
    questions. The implement, check and commit cycle (steps 10 to 12) is handled
    separately once the plan round is done (Q21, ``plan_review_pending``), so this
    only covers the path up to the plan review.
    """
    if state.requirement is None:
        return [1]
    if state.requirement_has_open_questions:
        return [3]
    if state.design is None:
        return [2] if _step_below(state.memory_step, 2) else [4]
    if state.design_has_open_questions:
        return [6]
    if state.plan is None:
        return [5] if _step_below(state.memory_step, 5) else [7]
    return _plan_round_steps(state)


def _plan_round_steps(state: WorkflowState) -> list[int]:
    """Return the plan's own review-round step: review (8) or consolidate (9).

    A plan with open questions routes to the consolidate step (9). Otherwise a
    plan not reviewed yet (the persisted step is below 8) routes to the review
    step (8), and a reviewed plan to consolidate (9), which clears the round and
    lets ``plan_review_pending`` hand off to the implement cycle.
    """
    if state.plan_has_open_questions:
        return [9]
    return [8] if _step_below(state.memory_step, 8) else [9]


def plan_review_pending(state: WorkflowState) -> bool:
    """Return whether the plain plan still owes its review-and-consolidate round.

    The plan is reviewed (step 8) and consolidated (step 9) before the implement
    cycle takes over, mirroring the requirement and design rounds. The round is
    pending while the plan carries open questions (consolidate is the next move)
    or while the consolidate step has not run yet (the persisted step is below 9),
    so a freshly written plan is always reviewed before any code is implemented.
    The validation plan is never considered here: only the plain plan is reviewed.
    """
    if state.plan is None:
        return False
    if state.plan_has_open_questions:
        return True
    return _step_below(state.memory_step, 9)


def alternatives_for(
    config: dict[int, list[StepAlternative]],
    numbers: list[int],
) -> list[StepAlternative]:
    """Return the flattened alternatives for the given ordered step numbers."""
    alternatives: list[StepAlternative] = []
    for number in numbers:
        alternatives.extend(config.get(number, []))
    return alternatives


def current_alternative(
    config: dict[int, list[StepAlternative]],
    step: int | None,
    instruction: str | None,
) -> StepAlternative | None:
    """Return the alternative for the persisted step and instruction, or None."""
    if step is None:
        return None
    alternatives = config.get(step, [])
    for alternative in alternatives:
        if alternative.instruction == instruction:
            return alternative
    return alternatives[0] if alternatives else None


def _relpath(root: Path, path: Path) -> str:
    """Return path as a posix string relative to the project root."""
    return Path(os.path.relpath(path.resolve(), root)).as_posix()


def _role_path(topic: Topic, state: WorkflowState, role: str) -> Path | None:
    """Return the resolved file path for a file role, or None when unresolved."""
    if role == "draft":
        return topic.draft_path
    return _ROLE_ATTRGETTER[role](state)


def _context_entry(root: Path, topic: Topic, state: WorkflowState, role: str) -> str:
    """Return the Context text for one role: a phrase or a relative file path."""
    if role in NON_FILE_ROLE_TEXT:
        return NON_FILE_ROLE_TEXT[role]
    path = _role_path(topic, state, role)
    if path is None:
        return f"the {role.replace('_', ' ')} (not found yet)"
    return _relpath(root, path)


def resolve_context(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    roles: tuple[str, ...],
) -> list[str]:
    """Return the resolved Context entries for the alternative's roles."""
    return [_context_entry(root, topic, state, role) for role in roles]


def build_prompt(
    prefix: str,
    alternative: StepAlternative,
    root: Path,
    topic: Topic,
    state: WorkflowState,
) -> str:
    """Assemble the three-part prompt: header, body, and Context section (Q09)."""
    header = HEADER_TEMPLATE.format(prefix=prefix, instruction=alternative.instruction)
    entries = resolve_context(root, topic, state, alternative.context)
    context = (
        f"Context: this is about {topic.version} {topic.slug}. "
        f"Read {', '.join(entries)}."
    )
    return f"{header}\n\n{alternative.body}\n\n{context}"


# eof
