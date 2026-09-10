"""Forced workflow-skill routing for specification and code reviews.

This module keeps explicit review-role dispatch separate from the main workflow
step router while preserving the public ``forced_command`` contract.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_code_review as code_review
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_render as rendering
from tools import prompt_workflow_review as review
from tools import prompt_workflow_steps as steps
from tools.review_exchange_models import ArtifactState

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.prompt_workflow_models import Topic, WorkflowState

MD_SUFFIX = ".md"
SPEC_REVIEW_REQUESTOR = "spec-review-requestor"
SPEC_REVIEWER = "spec-reviewer"
CODE_REVIEW_REQUESTOR = "code-review-requestor"
CODE_REVIEWER = "code-reviewer"
FORCED_REVIEW_ROLES = frozenset(
    {
        SPEC_REVIEW_REQUESTOR,
        SPEC_REVIEWER,
        CODE_REVIEW_REQUESTOR,
        CODE_REVIEWER,
    },
)
# The document role a forced skill targets; the skill is emitted only when that
# document exists (Q04). Review and consolidate are not forceable here, since they
# read whichever document is current rather than a single owned one.
FORCED_ROLE = {
    "process-draft": "draft",
    "write-requirement": "requirement",
    "write-design": "design",
    "write-plans": "plan",
    "implement-step": "plan",
}


def _relpath(root: Path, path: Path) -> str:
    """Return ``path`` as a posix string relative to the project root."""
    return Path(os.path.relpath(Path(path).resolve(), root)).as_posix()


def _relpath_or_none(root: Path, path: Path | None) -> str | None:
    """Return ``_relpath`` for an optional path, keeping None for no umbrella."""
    return None if path is None else _relpath(root, path)


def forced_command(
    root: Path,
    topic: Topic,
    skill_name: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Route bare resume before discovery, or require the forced skill's document (Q04).

    Args:
        root: The project root, used to make the document path relative.
        topic: The resolved topic.
        skill_name: The forced skill name (a key of ``FORCED_ROLE``).
        env: The process environment, read for the host prefix.
        override: A host token forcing the prefix, or None to detect it.

    Returns:
        The host-prefixed command naming the skill's document when that document
        exists, or the bare resume entry without a document. Return None when
        another skill is unknown or its document is absent.
    """
    if skill_name in {"resume", "review-resume"}:
        return rendering.render_command(
            rendering.host_prefix(env, override), "review-resume.md", "",
        ).removesuffix(" on ")
    state = steps.compute_state(root, topic, None)
    if skill_name in FORCED_REVIEW_ROLES:
        return _forced_review_command(root, topic, state, skill_name, env, override)
    role = FORCED_ROLE.get(skill_name)
    if role is None:
        return None
    doc = (
        topic.draft_path
        if role == "draft"
        else {
            "requirement": state.requirement,
            "design": state.design,
            "plan": state.plan,
        }[role]
    )
    if doc is None:
        return None
    instruction = f"{skill_name}{MD_SUFFIX}"
    return rendering.render_command(
        rendering.host_prefix(env, override),
        instruction,
        _relpath(root, doc),
    )


def _forced_review_command(  # noqa: PLR0913
    root: Path,
    topic: Topic,
    state: WorkflowState,
    skill_name: str,
    env: Mapping[str, str],
    override: str | None,
) -> str | None:
    """Dispatch one explicit review role without burdening generic routing."""
    if skill_name == CODE_REVIEWER:
        return _forced_code_reviewer_command(root, topic, state, env, override)
    if skill_name == SPEC_REVIEWER:
        return _forced_spec_reviewer_command(root, topic, state, env, override)
    if skill_name == CODE_REVIEW_REQUESTOR:
        route = code_review.resolve_code_review_route(
            root,
            topic,
            state,
            memory.read_memory(root),
        )
        if route is None or route.actor is not code_review.CodeReviewActor.REQUESTOR:
            return None
        return code_review.command_for_route(
            root,
            route,
            rendering.host_prefix(env, override),
            rendering.render_step_command,
        )
    doc = review.forced_specification_document(root, topic, state)
    if doc is None:
        return None
    return rendering.render_umbrella_command(
        rendering.host_prefix(env, override),
        f"{SPEC_REVIEW_REQUESTOR}{MD_SUFFIX}",
        _relpath(root, doc),
        _relpath_or_none(root, review.specification_umbrella(root, topic)),
    )


def _forced_spec_reviewer_command(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    env: Mapping[str, str],
    override: str | None,
) -> str | None:
    """Render only an exact pending reviewer route and diagnose cold reclaim."""
    route = review.live_specification_route(root, topic, state)
    if route is None:
        return None
    if route.state is ArtifactState.ABANDONED_REQUEST:
        message = (
            "forced spec-reviewer cannot enter an abandoned request cold; "
            f"run {SPEC_REVIEW_REQUESTOR} reclaim for {route.context.identity.key}"
        )
        raise review.SpecificationReviewRoutingError(message)
    if route.state is not ArtifactState.REQUEST_PENDING:
        return None
    return rendering.render_umbrella_command(
        rendering.host_prefix(env, override),
        f"{SPEC_REVIEWER}{MD_SUFFIX}",
        _relpath(root, route.context.document_path),
        _relpath_or_none(root, route.context.umbrella_path),
    )


def _forced_code_reviewer_command(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    env: Mapping[str, str],
    override: str | None,
) -> str | None:
    """Render only an exact reviewer-owned code request route."""
    route = code_review.resolve_code_review_route(
        root,
        topic,
        state,
        memory.read_memory(root),
    )
    if route is None:
        return None
    if route.actor is not code_review.CodeReviewActor.REVIEWER:
        return None
    return code_review.command_for_route(
        root,
        route,
        rendering.host_prefix(env, override),
        rendering.render_step_command,
    )


__all__ = [
    "CODE_REVIEWER",
    "CODE_REVIEW_REQUESTOR",
    "FORCED_REVIEW_ROLES",
    "FORCED_ROLE",
    "SPEC_REVIEWER",
    "SPEC_REVIEW_REQUESTOR",
    "forced_command",
]


# eof
