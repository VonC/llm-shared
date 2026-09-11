"""Bounded exact-path routing for live specification review exchanges.

Step 3 keeps review-mode detection and exchange observation outside the main
``pw skill`` router. It checks only the requirement, design, and plan already
resolved for one topic, never scans documentation folders, and never reads a
versioned transcript as routing context.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.prompt_workflow_models import PromptWorkflowError
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactState,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
)
from tools.review_exchange_paths import derive_artifact_paths, load_review_configuration
from tools.review_exchange_store import ReviewExchangeStore
from tools.spec_review_request import specification_context

if TYPE_CHECKING:
    from pathlib import Path

    from tools.prompt_workflow_models import Topic, WorkflowState

_UMBRELLA_PREFIX: Final[str] = "- Umbrella: "
_POLICY: Final[FamilyPolicy] = FamilyPolicy(
    "consolidation-ready",
    "Revise and review again",
    "Consolidate",
)


class SpecificationReviewRoutingError(PromptWorkflowError):
    """Raised when exact specification review routing is ambiguous or invalid."""


@dataclass(frozen=True)
class LiveSpecificationRoute:
    """One immutable specification context and its coherently observed state."""

    context: ReviewContext
    state: ArtifactState


def _umbrella_path(root: Path, topic: Topic) -> Path | None:
    """Read the child draft's one explicit umbrella marker, when present."""
    content = topic.draft_path.read_text(encoding="utf-8")
    matches = [
        line.removeprefix(_UMBRELLA_PREFIX).strip()
        for line in content.splitlines()
        if line.startswith(_UMBRELLA_PREFIX)
    ]
    if not matches:
        return None
    if len(matches) != 1 or not matches[0]:
        raise SpecificationReviewRoutingError("draft has an ambiguous umbrella marker")
    umbrella = (root / matches[0]).resolve()
    try:
        umbrella.relative_to(root.resolve())
    except ValueError as error:
        raise SpecificationReviewRoutingError("umbrella is outside the project root") from error
    if not umbrella.is_file():
        raise SpecificationReviewRoutingError(f"umbrella does not exist: {matches[0]}")
    return umbrella


def specification_contexts(
    root: Path,
    topic: Topic,
    state: WorkflowState,
) -> tuple[ReviewContext, ...]:
    """Return at most three exact contexts from the already resolved topic state."""
    umbrella = _umbrella_path(root, topic)
    candidates = (state.requirement, state.design, state.plan)
    contexts = tuple(
        specification_context(document, umbrella)
        for document in candidates
        if document is not None
    )
    for context in contexts:
        identity = context.identity
        if identity.version != topic.version or identity.slug != topic.slug:
            raise SpecificationReviewRoutingError(
                f"resolved document differs from topic: {identity.key}",
            )
    return contexts


def _classify_context(
    root: Path,
    context: ReviewContext,
    configuration: ReviewConfiguration,
) -> ArtifactState:
    """Classify one exact context through the shared read-only observer."""
    paths = derive_artifact_paths(root, context)
    core = ReviewExchangeCore(
        ReviewExchangeStore(paths),
        context,
        _POLICY,
        configuration,
    )
    return core.classify().state


def _describe(root: Path, route: LiveSpecificationRoute) -> str:
    """Render one complete identity and repository-relative document path."""
    document = route.context.document_path.relative_to(root.resolve()).as_posix()
    return f"{route.context.identity.key} document={document} state={route.state.value}"


def _live_routes(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    configuration: ReviewConfiguration,
) -> tuple[LiveSpecificationRoute, ...]:
    """Observe the constant candidate set and return every non-idle route."""
    return tuple(
        LiveSpecificationRoute(context, observed)
        for context in specification_contexts(root, topic, state)
        if (observed := _classify_context(root, context, configuration))
        is not ArtifactState.IDLE
    )


def _one_live_route(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    configuration: ReviewConfiguration,
) -> LiveSpecificationRoute | None:
    """Return the sole live route or fail closed with every exact identity."""
    routes = _live_routes(root, topic, state, configuration)
    if len(routes) > 1:
        detail = "; ".join(_describe(root, route) for route in routes)
        raise SpecificationReviewRoutingError(
            f"multiple live specification exchanges for one topic: {detail}",
        )
    return routes[0] if routes else None


def live_specification_route(
    root: Path,
    topic: Topic,
    state: WorkflowState,
) -> LiveSpecificationRoute | None:
    """Return one immutable live route from a single state observation."""
    configuration = load_review_configuration(root)
    if not configuration.enabled:
        return None
    return _one_live_route(root, topic, state, configuration)


def live_specification_document(
    root: Path,
    topic: Topic,
    state: WorkflowState,
) -> Path | None:
    """Return the sole live document for callers that do not select a role."""
    route = live_specification_route(root, topic, state)
    return route.context.document_path if route is not None else None


def specification_umbrella(root: Path, topic: Topic) -> Path | None:
    """Return the umbrella both review roles must carry, when the effort has one.

    Routing names this on the emitted command so a role does not have to
    rediscover it. A role whose exchange context omits an umbrella the
    published request carries is reported `inconsistent` by every operation.

    Args:
        root: The project root the documents live under.
        topic: The resolved topic, whose draft carries the umbrella marker.

    Returns:
        The umbrella path, or None when the effort has none.
    """
    return _umbrella_path(root, topic)


def forced_specification_document(
    root: Path,
    topic: Topic,
    state: WorkflowState,
) -> Path | None:
    """Return one live or newly questioned document for explicit delegation."""
    configuration = load_review_configuration(root)
    if not configuration.enabled:
        return None
    live = _one_live_route(root, topic, state, configuration)
    if live is not None:
        return live.context.document_path
    candidates = tuple(
        document
        for document, has_questions in (
            (state.requirement, state.requirement_has_open_questions),
            (state.design, state.design_has_open_questions),
            (state.plan, state.plan_has_open_questions),
        )
        if document is not None and has_questions
    )
    if len(candidates) > 1:
        detail = "; ".join(path.relative_to(root.resolve()).as_posix() for path in candidates)
        raise SpecificationReviewRoutingError(
            f"multiple open-question specifications for one topic: {detail}",
        )
    return candidates[0] if candidates else None


# eof
