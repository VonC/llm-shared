"""Non-interactive handoff resolution for prompt_workflow (the pw handoff subcommand).

The interactive cycle of ``prompt_workflow_plan`` resolves its action from a
``questionary`` menu. This module is the menu-less counterpart used by the
``pw handoff <task> <x>`` subcommand: it reads the named plan step from the
validation plan, maps a task word to a cycle action, routes the ``after-check``
task from the Yes/No status the check wrote, builds the carrier cycle state for
the named step, reports a derived-step mismatch, and resolves the topic without a
menu. It reuses the parsing, derivation and dataclasses of
``prompt_workflow_plan`` and the read-only git helpers; it owns no terminal IO
and writes no files, so every function is unit testable on its own (Q56 to Q63 of
``docs/design.v0.1.0.pw_handoff.md``).

The carrier cycle state of ``cycle_state_for_step`` populates only the fields the
handoff path reads: ``x`` (used by ``build_cycle_prompt``) and ``verified`` /
``not_implemented`` (mirrored from the plan step). The working-tree flags are
left False on purpose, because the handoff never goes through
``build_cycle_options`` and the commit handoff is always the ``git add -A``
variant (Q60), so the cached-versus-non-cached split the menu uses does not apply.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import prompt_workflow_git as git
from tools import prompt_workflow_plan as plan
from tools.prompt_workflow_models import PromptWorkflowError

if TYPE_CHECKING:
    from pathlib import Path

    from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState
    from tools.prompt_workflow_plan import CycleAction, CycleState, PlanStep

# The four task words the handoff subcommand accepts (Q57, Q62). ``check`` and
# ``after-check`` drive the automatic chain; ``implement-missing`` and ``commit``
# are kept for a manual call from the terminal.
CHECK = "check"
AFTER_CHECK = "after-check"
IMPLEMENT_MISSING = "implement-missing"
COMMIT = "commit"
TASK_TOKENS: tuple[str, ...] = (CHECK, AFTER_CHECK, IMPLEMENT_MISSING, COMMIT)


def find_plan_step(state: WorkflowState, step: str) -> PlanStep:
    """Return the plan step whose id is ``step``, read from the validation plan.

    Args:
        state: The workflow state holding the resolved validation-plan path.
        step: The plan step id named on the command line, such as ``2`` or ``4A``.

    Returns:
        The parsed ``PlanStep`` for that id.

    Raises:
        PromptWorkflowError: When no validation plan is resolved, or when no
            ``Analysis of Step <id>`` section carries that id (Q59).
    """
    if state.validation_plan is None:
        msg = "No validation plan resolved; run write-plans before a handoff."
        raise PromptWorkflowError(msg)
    plan_steps = plan.parse_validation_steps(
        state.validation_plan.read_text(encoding="utf-8"),
    )
    for plan_step in plan_steps:
        if plan_step.number == step:
            return plan_step
    msg = f"No 'Analysis of Step {step}' section found in the validation plan."
    raise PromptWorkflowError(msg)


def action_for_task(task: str, plan_step: PlanStep) -> CycleAction:
    """Return the cycle action a handoff task maps to (Q57, Q58, Q62).

    ``check`` builds the check action, ``implement-missing`` the implement-missing
    variant, and ``commit`` the ``git add -A`` commit. ``after-check`` is routed
    from the step status the check wrote: a ``No`` step (``not_implemented``) goes
    to implement-missing, a ``Yes`` step (``verified``) to commit (Q58).

    Args:
        task: One of ``TASK_TOKENS``.
        plan_step: The plan step the handoff names, carrying its Yes/No status.

    Returns:
        The ``CycleAction`` to build the prompt for.

    Raises:
        PromptWorkflowError: When ``task`` is not a known token, or when
            ``after-check`` finds a step that is neither verified nor
            not-implemented (the check left a placeholder status).
    """
    if task == CHECK:
        return plan.CycleAction(kind="check", stage_all=False)
    if task == IMPLEMENT_MISSING:
        return plan.CycleAction(kind="implement", stage_all=False, missing=True)
    if task == COMMIT:
        return plan.CycleAction(kind="commit", stage_all=True)
    if task == AFTER_CHECK:
        if plan_step.not_implemented:
            return plan.CycleAction(kind="implement", stage_all=False, missing=True)
        if plan_step.verified:
            return plan.CycleAction(kind="commit", stage_all=True)
        msg = f"Step {plan_step.number} has no Yes/No status yet; run the check first."
        raise PromptWorkflowError(msg)
    msg = f"Unknown handoff task {task!r}; expected one of {', '.join(TASK_TOKENS)}."
    raise PromptWorkflowError(msg)


def cycle_state_for_step(plan_step: PlanStep) -> CycleState:
    """Return the carrier cycle state for a named plan step.

    ``build_cycle_prompt`` reads only ``x`` from the cycle state; ``verified`` and
    ``not_implemented`` mirror the plan step for completeness. The working-tree
    flags are left False on purpose: the handoff never lists menu options and the
    commit handoff is always the ``git add -A`` variant (Q60).

    Args:
        plan_step: The plan step the handoff names.

    Returns:
        A ``CycleState`` carrying the step id and its status.
    """
    return plan.CycleState(
        x=plan_step.number,
        verified=plan_step.verified,
        terminal=False,
        has_code_changes=False,
        cached=False,
        non_cached=False,
        not_implemented=plan_step.not_implemented,
    )


def derived_mismatch(
    root: Path,
    state: WorkflowState,
    branch_start: str | None,
    step: str,
) -> str | None:
    """Return the git-derived plan step when it differs from ``step``, else None.

    The handed step is authoritative for the handoff (Q59); this only reports the
    cycle step ``derive_x`` would pick, so the caller can warn on a mismatch
    without overriding the explicit request.

    Args:
        root: The project root, for the per-step validation-commit lookup.
        state: The workflow state holding the validation-plan path.
        branch_start: The fork-point commit, or None on the default branch.
        step: The plan step id the handoff names.

    Returns:
        The derived step id when it differs from ``step``; None when they match,
        when no validation plan is resolved, or when it has no plan steps.
    """
    if state.validation_plan is None:
        return None
    plan_steps = plan.parse_validation_steps(
        state.validation_plan.read_text(encoding="utf-8"),
    )
    if not plan_steps:
        return None

    def _has_commit(number: str) -> bool:
        return git.has_step_commit(root, number, branch_start)

    derived, _verified, _terminal = plan.derive_x(plan_steps, _has_commit)
    return derived if derived != step else None


def _topic_matches(record: MemoryRecord | None, topic: Topic, branch: str) -> bool:
    """Return whether the memory record still locks this topic on this branch.

    Mirrors ``prompt_workflow._memory_matches`` for the non-interactive resolver,
    kept here so this module never imports the interactive entry point (Q53).
    """
    return (
        record is not None
        and record.branch == branch
        and record.version == topic.version
        and record.topic == topic.slug
    )


def resolve_topic(
    topics: list[Topic],
    record: MemoryRecord | None,
    branch: str,
) -> Topic | None:
    """Return the topic a non-interactive handoff resolves to, or None (Q63).

    A single detected draft is used directly. Otherwise the branch-locked topic is
    used when the memory still matches one on this branch. When several drafts
    exist and none is locked, None is returned and the caller refuses with a
    ``pw --pick`` message, since a non-interactive handoff cannot show the menu.

    Args:
        topics: The relevant draft topics on the current branch.
        record: The persisted memory record, or None.
        branch: The current branch name.

    Returns:
        The resolved topic, or None when it cannot be resolved without a menu.
    """
    if len(topics) == 1:
        return topics[0]
    for topic in topics:
        if _topic_matches(record, topic, branch):
            return topic
    return None


# eof
