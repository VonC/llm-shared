"""Bounded routing and clean commit continuation for implementation review.

The adapter derives one exact plan-step context from the current workflow,
checks only that identity's fixed exchange paths, and delegates authorized
batch commits. A durable phase marker separates the reviewed commit plan from
an optional residual plan, and completion requires a clean working tree.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Final, cast

from tools import prompt_workflow_git as git
from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_steps as steps
from tools.code_review_request import code_review_context
from tools.prompt_workflow_models import PromptWorkflowError
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ConfirmationOutcome,
    FamilyPolicy,
    ReviewContext,
)
from tools.review_exchange_paths import derive_artifact_paths, load_review_configuration
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState

CODE_REVIEW_POLICY: Final[FamilyPolicy] = FamilyPolicy(
    "commit-ready",
    "Rework and review again",
    "Commit",
)
CODE_REVIEW_REQUESTOR: Final[str] = "code-review-requestor.md"
CODE_REVIEWER: Final[str] = "code-reviewer.md"
RESIDUAL_GROUPING_REQUIRED: Final[int] = 3
_COMMIT_PHASE_MARKER: Final[str] = "a.code-review-commit-phase"
_PRIMARY_PHASE: Final[str] = "primary"
_RESIDUAL_PHASE: Final[str] = "residual"
LOGGER = logging.getLogger(__name__)


class CodeReviewRoutingError(PromptWorkflowError):
    """Raised when one exact code-review route is absent or inconsistent."""


class CodeReviewActor(Enum):
    """The only two workflow roles allowed to own a code-review route."""

    REVIEWER = "reviewer"
    REQUESTOR = "requestor"


def _actor_for_state(state: ArtifactState) -> CodeReviewActor:
    """Resolve the single owner from one already-classified exchange state."""
    if state in (ArtifactState.REQUEST_PENDING, ArtifactState.ABANDONED_REQUEST):
        return CodeReviewActor.REVIEWER
    return CodeReviewActor.REQUESTOR


@dataclass(frozen=True)
class CodeReviewRoute:
    """One exact implementation context, classified state, and single owner."""

    context: ReviewContext
    state: ArtifactState
    actor: CodeReviewActor

    def __post_init__(self) -> None:
        """Reject ownership that does not follow the exact state partition."""
        if self.actor is not _actor_for_state(self.state):
            raise CodeReviewRoutingError("code-review route actor disagrees with state")


def _umbrella_path(root: Path, topic: Topic) -> Path | None:
    """Resolve the child draft's sole explicit umbrella path, when present."""
    prefix = "- Umbrella: "
    matches = [
        line.removeprefix(prefix).strip()
        for line in topic.draft_path.read_text(encoding="utf-8").splitlines()
        if line.startswith(prefix)
    ]
    if not matches:
        return None
    if len(matches) != 1 or not matches[0]:
        raise CodeReviewRoutingError("draft has an ambiguous umbrella marker")
    umbrella = (root / matches[0]).resolve()
    try:
        umbrella.relative_to(root.resolve())
    except ValueError as error:
        raise CodeReviewRoutingError("umbrella is outside the project root") from error
    if not umbrella.is_file():
        raise CodeReviewRoutingError(f"umbrella does not exist: {matches[0]}")
    return umbrella


def _plan_steps(state: WorkflowState) -> tuple[str, ...]:
    """Return the exact declared validation-plan step identifiers."""
    if state.validation_plan is None:
        raise CodeReviewRoutingError("code review requires a validation plan")
    return tuple(
        item.number
        for item in plan.parse_validation_steps(
            state.validation_plan.read_text(encoding="utf-8"),
        )
    )


def _context(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    record: MemoryRecord | None,
) -> ReviewContext:
    """Build and validate the current plan-step context without searching."""
    if state.plan is None:
        raise CodeReviewRoutingError("code review requires an exact plan document")
    if record is None or record.plan_step is None:
        raise CodeReviewRoutingError("code review requires an implementation step")
    if record.plan_step not in _plan_steps(state):
        raise CodeReviewRoutingError(f"unknown plan step: {record.plan_step}")
    context = code_review_context(
        state.plan,
        record.plan_step,
        _umbrella_path(root, topic),
    )
    identity = context.identity
    if identity.version != topic.version or identity.slug != topic.slug:
        raise CodeReviewRoutingError("plan identity differs from the workflow topic")
    return context


def _record_matches_topic(record: MemoryRecord, topic: Topic) -> bool:
    """Report whether a durable review record belongs to this workflow topic."""
    return record.version == topic.version and record.topic == topic.slug


def _record_plan_step(record: MemoryRecord | None, topic: Topic) -> str | None:
    """Return the plan step only when the record belongs to this topic."""
    if record is None or record.plan_step is None:
        return None
    if not _record_matches_topic(record, topic):
        return None
    return record.plan_step


def _core(root: Path, context: ReviewContext) -> ReviewExchangeCore:
    """Bind the shared observer to one code-review identity and policy."""
    return ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(root, context)),
        context,
        CODE_REVIEW_POLICY,
        load_review_configuration(root),
    )


def resolve_code_review_route(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    record: MemoryRecord | None,
) -> CodeReviewRoute | None:
    """Return the marker-enabled or already-live exact plan-step route.

    A cold route exists only while review mode is enabled. Once coordination is
    durable, its fixed paths win even if the marker is later removed. Any live
    evidence for the same code identity but another implementation step fails
    closed instead of being silently ignored.

    A record naming another topic or version is not evidence about this one, so
    it routes nowhere rather than failing. Every effort that ran a code review
    leaves its record behind, and the next effort would otherwise meet a fatal
    on its first call whose only remedy is deleting an ignored scratch file.
    Fail-closed is kept where it means something: an unknown step for this
    topic, or live evidence at another step, still raise.
    """
    if state.plan is None:
        return None
    record_plan_step = _record_plan_step(record, topic)
    if record_plan_step is None:
        return None
    probe_context = code_review_context(
        state.plan,
        record_plan_step,
        _umbrella_path(root, topic),
    )
    paths = derive_artifact_paths(root, probe_context)
    store = ReviewExchangeStore(paths)
    persisted = store.read_coordination()
    if (
        persisted is not None
        and persisted.context.implementation_step
        != probe_context.implementation_step
    ):
        raise CodeReviewRoutingError(
            "live code exchange uses another implementation step",
        )
    configuration = load_review_configuration(root)
    live_paths = (
        paths.request,
        paths.answer,
        paths.coordination,
        paths.tombstone,
        paths.transition_lock,
    )
    has_exact_evidence = any(path.exists() for path in live_paths)
    if not configuration.enabled and not has_exact_evidence:
        return None
    context = _context(root, topic, state, record)
    observation = ReviewExchangeCore(
        store,
        context,
        CODE_REVIEW_POLICY,
        configuration,
    ).classify()
    if observation.state is ArtifactState.INCONSISTENT:
        raise CodeReviewRoutingError(f"inconsistent code exchange: {observation.diagnostic}")
    return CodeReviewRoute(
        context,
        observation.state,
        _actor_for_state(observation.state),
    )


def command_for_route(
    root: Path,
    route: CodeReviewRoute,
    prefix: str,
    render_step: Callable[[str, str, str, str], str],
) -> str:
    """Render the specialized handoff from one immutable typed actor."""
    document = route.context.document_path.relative_to(root.resolve()).as_posix()
    implementation_step = cast("str", route.context.implementation_step)
    instruction = (
        CODE_REVIEWER
        if route.actor is CodeReviewActor.REVIEWER
        else CODE_REVIEW_REQUESTOR
    )
    return render_step(
        prefix,
        instruction,
        document,
        implementation_step,
    )


def run_batch_commit(
    arguments: tuple[str, ...],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    """Invoke the existing strict batch-commit workflow at one external seam.

    The launcher ships with llm-shared, so it is located through
    ``llm_shared_dir`` rather than the project root; ``cwd`` stays the reviewed
    project because that is where `a.commit` and the staged work live.
    """
    command = steps.llm_shared_dir() / "bin" / "gcba.bat"
    return subprocess.run(  # noqa: S603
        [str(command), *arguments],
        cwd=cwd,
        check=False,
        text=True,
    )


def _phase_marker(root: Path) -> Path:
    """Return the ignored marker that makes authorized replay phase-safe."""
    return root.resolve() / _COMMIT_PHASE_MARKER


def _phase_content(context: ReviewContext, phase: str) -> str:
    """Render one exact review identity and commit phase."""
    return (
        f"{phase}\n{context.identity.key}\n"
        f"{cast('str', context.implementation_step)}\n"
    )


def _read_phase(root: Path, context: ReviewContext) -> str | None:
    """Read the current phase and reject a stale marker from another review."""
    marker = _phase_marker(root)
    if not marker.exists():
        return None
    content = marker.read_text(encoding="utf-8")
    for phase in (_PRIMARY_PHASE, _RESIDUAL_PHASE):
        if content == _phase_content(context, phase):
            return phase
    raise CodeReviewRoutingError("code-review commit phase marker is stale")


def _write_phase(root: Path, context: ReviewContext, phase: str) -> None:
    """Persist the current authorized commit phase before its mutation."""
    _phase_marker(root).write_text(
        _phase_content(context, phase),
        encoding="utf-8",
    )


def _announce_residual_grouping() -> None:
    """Log the single authorized next action for staged residual changes."""
    LOGGER.info(
        "Residual changes are staged. Run $llm-shared:group-commits-msg "
        "without a new menu, then run pw code-review-commit --residual.",
    )


def _require_clean_tree(root: Path) -> None:
    """Reject completion while any tracked or untracked change remains."""
    entries = git.status_entries(root.resolve())
    if entries:
        paths = ", ".join(path for _status, path in entries)
        raise CodeReviewRoutingError(
            f"authorized code-review commits left a dirty working tree: {paths}",
        )


def _continue_residual_commit(
    root: Path,
    context: ReviewContext,
    core: ReviewExchangeCore,
) -> int:
    """Execute the grouped residue and consume authority only when clean."""
    if _read_phase(root, context) != _RESIDUAL_PHASE:
        raise CodeReviewRoutingError("no staged residual commit is pending")
    result = run_batch_commit(
        ("--root-a-commit", "--non-interactive"),
        cwd=root.resolve(),
    )
    if result.returncode != 0:
        return result.returncode
    _require_clean_tree(root)
    _phase_marker(root).unlink()
    core.complete()
    return 0


def _continue_primary_commit(
    root: Path,
    context: ReviewContext,
    core: ReviewExchangeCore,
) -> int:
    """Execute the reviewed plan or resume its residual grouping handoff."""
    phase = _read_phase(root, context)
    if phase == _RESIDUAL_PHASE:
        git.stage_all(root.resolve())
        _announce_residual_grouping()
        return RESIDUAL_GROUPING_REQUIRED
    if phase is None:
        _write_phase(root, context, _PRIMARY_PHASE)
    result = run_batch_commit(
        ("--root-a-commit", "--non-interactive"),
        cwd=root.resolve(),
    )
    if result.returncode != 0:
        return result.returncode
    if not git.status_entries(root.resolve()):
        _phase_marker(root).unlink()
        core.complete()
        return 0
    _write_phase(root, context, _RESIDUAL_PHASE)
    git.stage_all(root.resolve())
    _announce_residual_grouping()
    return RESIDUAL_GROUPING_REQUIRED


def continue_authorized_commit(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    record: MemoryRecord | None,
    *,
    residual: bool = False,
) -> int:
    """Commit reviewed work, then one grouped residue, before completing."""
    route = resolve_code_review_route(root, topic, state, record)
    if route is None or route.state is not ArtifactState.OWNING_ACTION_PENDING:
        raise CodeReviewRoutingError("code-review commit is not authorized")
    core = _core(root, route.context)
    coordination = core.store.read_coordination(required=True)
    if (
        coordination is None
        or coordination.confirmed_outcome
        is not ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
    ):
        raise CodeReviewRoutingError("code-review commit is not durably authorized")
    core.pickup_ownership(Actor.REQUESTOR)

    if residual:
        return _continue_residual_commit(root, route.context, core)
    return _continue_primary_commit(root, route.context, core)


# eof
