"""Post-write and post-commit workflow continuation routing.

These transitions advance an already identified effort after its owning writer
or commit action, independently from the main state-based skill router.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_git as git
from tools import prompt_workflow_handoff as handoff
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_post_commit as post_commit
from tools import prompt_workflow_render as rendering
from tools import prompt_workflow_steps as steps

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.prompt_workflow_models import Topic, WorkflowState

PRODUCED_TYPE = {"requirement": "feature-request", "design": "design", "plan": "plan"}


def _relpath(root: Path, path: Path) -> str:
    """Return ``path`` as a posix string relative to the project root."""
    return Path(os.path.relpath(Path(path).resolve(), root)).as_posix()


def _document(root: Path, topic: Topic, role: str, state: WorkflowState) -> str:
    """Return an existing role document or the path it will use when written."""
    existing = {
        "requirement": state.requirement,
        "design": state.design,
        "plan": state.plan,
    }[role]
    if existing is not None:
        return _relpath(root, existing)
    effort_dir = _relpath(root, topic.draft_path.parent)
    filename = f"{PRODUCED_TYPE[role]}.{topic.version}.{topic.slug}.md"
    return (Path(effort_dir) / filename).as_posix()


def post_write_command(
    root: Path,
    topic: Topic,
    written_role: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return the review command for the artifact that was just written.

    This explicit handoff intentionally ignores decisions-table markers. A
    writer knows which artifact it produced, while bare ``pw skill`` remains the
    state-based router used after review and consolidation.

    Args:
        root: The project root.
        topic: The resolved topic.
        written_role: One of ``AFTER_WRITE_ROLES``.
        env: The process environment, read for the host prefix.
        override: A host token forcing the prefix, or None to detect it.

    Returns:
        A review command for the written artifact, or None when it is absent.
    """
    state = steps.compute_state(root, topic, None)
    document = {
        "requirement": state.requirement,
        "design": state.design,
        "plan": state.plan,
    }[written_role]
    if document is None:
        return None
    return rendering.render_command(
        rendering.host_prefix(env, override),
        "review-ask-questions.md",
        _relpath(root, document),
    )


def post_commit_command(
    root: Path,
    committed_step: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return the command to chain after committing ``committed_step`` (Step 7).

    Told the plan step the commit completes, this names the step after it for
    ``implement-step``; once that step was the last, ``prepare-release``; and when
    no validation plan is resolved (a standalone commit, no effort) or the step is
    not in the plan, None.

    Args:
        root: The project root.
        committed_step: The plan step id the commit just completed.
        env: The process environment, read for the host prefix.
        override: A host token forcing the prefix, or None to detect it.

    Returns:
        The host-prefixed command for the next action, or None when there is no
        plan in play or the committed step is not one of its steps.
    """
    branch = git.current_branch(root)
    record = memory.read_memory(root)
    topic = handoff.resolve_current_topic(root, branch, record)
    if topic is None:
        topic = post_commit.resolve_post_commit_topic(root, record, branch)
    if topic is None:
        return None
    state = steps.compute_state(root, topic, None)
    if state.validation_plan is None:
        return None
    numbers = [
        plan_step.number
        for plan_step in plan.parse_validation_steps(
            state.validation_plan.read_text(encoding="utf-8"),
        )
    ]
    if committed_step not in numbers:
        return None
    prefix = rendering.host_prefix(env, override)
    index = numbers.index(committed_step)
    if index + 1 < len(numbers):
        plan_doc = _document(root, topic, "plan", state)
        return f"{prefix}implement-step on {plan_doc} step {numbers[index + 1]}"
    return f"{prefix}prepare-release"


__all__ = ["post_commit_command", "post_write_command"]


# eof
