"""Shared data models, role constants, and the error type for prompt_workflow.

This module holds the small, dependency-free pieces used across the
prompt_workflow tool: the base exception, the context-role vocabulary that maps
a role name (from the per-step JSON, see `tools/prompt_workflow.steps.json`) to
the document-type prefixes used on disk, and the frozen dataclasses that carry a
resolved topic, a step alternative, a workflow state, and the persisted memory
record.

Keeping these here avoids circular imports between the git, docs, memory, and
steps modules, the same way `tools/_models.py` does for the wider package.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pathlib import Path

# Suffix that distinguishes a validation plan from a plain plan document.
VALIDATION_SUFFIX: Final[str] = ".validation.md"

# File roles map to the document-type prefixes that can satisfy them on disk.
# A requirement is either a feature-request or an issue; a validation plan is a
# plan file ending with VALIDATION_SUFFIX (resolved in the docs module).
ROLE_DOC_TYPES: Final[dict[str, tuple[str, ...]]] = {
    "draft": ("draft",),
    "requirement": ("feature-request", "issue"),
    "design": ("design",),
    "plan": ("plan",),
    "validation_plan": ("plan",),
}

# Non-file roles render as a fixed phrase in the Context section instead of a
# resolved file path.
NON_FILE_ROLE_TEXT: Final[dict[str, str]] = {
    "git_status": "the current git status",
    "git_history": "the git history since the last tag",
}


class PromptWorkflowError(Exception):
    """Base exception for every fatal error raised by the prompt_workflow tool."""


@dataclass(frozen=True)
class StepAlternative:
    """One selectable action of a workflow step.

    Attributes:
        number: The step number (1 to 13) this alternative belongs to.
        instruction: The instruction file name, such as ``write-design.md``.
        body: The per-step body line that states the step intent.
        context: The ordered context roles resolved into the Context section.
    """

    number: int
    instruction: str
    body: str
    context: tuple[str, ...]


@dataclass(frozen=True)
class Topic:
    """A general topic resolved from a relevant draft file.

    Attributes:
        version: The version token parsed from the draft name (e.g. ``v9.8.0``).
        slug: The topic slug parsed from the draft name (e.g. ``resources_isolation``).
        draft_path: The absolute path to the draft file naming this topic.
    """

    version: str
    slug: str
    draft_path: Path


@dataclass(frozen=True)
class WorkflowState:
    """The document and memory state used to evaluate step preconditions.

    Attributes:
        requirement: Most recent requirement document for the topic, or None.
        design: Most recent design document for the topic, or None.
        plan: Most recent plain plan document for the topic, or None.
        validation_plan: Most recent validation plan document, or None.
        requirement_has_open_questions: Whether the requirement still has a
            ``## Open questions`` section.
        design_has_open_questions: Whether the design still has a
            ``## Open questions`` section.
        plan_has_open_questions: Whether the plain plan still has a
            ``## Open questions`` section, driving its own review-and-consolidate
            round (steps 8 and 9) before the implement cycle. The validation plan
            has no such flag: it is never put through the review loop.
        memory_step: The step number persisted in the memory file, or None.
    """

    requirement: Path | None
    design: Path | None
    plan: Path | None
    validation_plan: Path | None
    requirement_has_open_questions: bool
    design_has_open_questions: bool
    plan_has_open_questions: bool
    memory_step: int | None


@dataclass(frozen=True)
class MemoryRecord:
    """The workflow context persisted in the ``a.prompt_memory`` file.

    Attributes:
        branch: The git branch the memory was written on.
        version: The resolved topic version (e.g. ``v9.8.0``).
        topic: The resolved topic slug.
        step: The current step number, or None when no step ran yet.
        instruction: The chosen instruction file for the current step, or None.
        plan_step: The plan step id ``x`` reached in the implement cycle, or None.
            It is a string because it may carry a letter suffix such as ``4A``
            for a sub-step (Q41); only the workflow ``step`` stays an int.
    """

    branch: str
    version: str
    topic: str
    step: int | None = None
    instruction: str | None = None
    plan_step: str | None = None


# eof
