"""prompt_workflow.py.

Generate the next-step LLM prompt for the current general topic and copy it to
the clipboard.

From the project root, the tool detects the relevant drafts on the current
branch, resolves the general topic (auto-selecting the one the memory locks to
the branch, unless ``--pick`` reopens the menu, Q53), derives the workflow state
from the documents on disk and the persisted step, offers an interactive menu to
repeat the current step or pick a next step, then builds the prompt, writes it to
``a.prompt.txt``, copies it to the clipboard (falling back to stdout), and
records the chosen step in ``a.prompt_memory``.

Fix (menu order): ``build_menu_options`` sorts its rows by step number,
descending and stable, so the next-step rows come above the repeat-current row
and the usual forward move is the pre-highlighted top row (Q54).

Fix (handoff): the ``handoff`` subcommand, ``pw handoff <task> <x>``, writes one
named step's prompt without the menu (Q56). ``run_handoff`` resolves the topic
from the single draft or the branch lock (Q63), validates the named step and
warns on a derived-step mismatch (Q59), maps the task to a cycle action (routing
``after-check`` from the Yes/No status the check wrote, Q58), and delivers and
records the prompt exactly as the interactive cycle does (Q60, Q61). ``--root``
and ``--debug`` move onto a shared parent parser so they parse on either side of
the subcommand (Q01).

See ``docs/design.v0.1.0.pw_handoff.md`` for the full specification and the design
decisions (Q01 to Q64) behind this tool.
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _bootstrap_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_bootstrap_root))

from tools import find_project_root
from tools import prompt_workflow_docs as docs
from tools import prompt_workflow_git as git
from tools import prompt_workflow_handoff as handoff
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_menu as menu
from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_steps as steps
from tools.prompt_workflow_models import MemoryRecord, PromptWorkflowError

if TYPE_CHECKING:
    from tools.prompt_workflow_models import StepAlternative, Topic, WorkflowState
    from tools.prompt_workflow_plan import CycleAction, CycleState

LOGGER = logging.getLogger("prompt_workflow")
# Name of the file the prompt is always written to, beside the clipboard (Q05).
PROMPT_FILENAME = "a.prompt.txt"
# Exit code used by the entry point for fatal errors.
EXIT_FATAL = 2


class ClipboardError(PromptWorkflowError):
    """Raised when the clipboard write fails."""


def _configure_logging(*, debug: bool) -> None:
    """Configure logging to stdout with message-only formatting."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def set_clipboard_text(text: str) -> None:
    """Set text content to the Windows clipboard via PowerShell (Q05).

    Args:
        text: The prompt text to place on the clipboard.

    Raises:
        ClipboardError: When the PowerShell clipboard command fails.
    """
    pwsh = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
    try:
        subprocess.run(  # noqa: S603
            [
                pwsh,
                "-noprofile",
                "-ExecutionPolicy",
                "Bypass",
                "-command",
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                "$Input | Set-Clipboard",
            ],
            input=text,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except subprocess.SubprocessError as err:
        msg = f"Failed to write clipboard: {err}"
        raise ClipboardError(msg) from err


def deliver_prompt(root: Path, prompt: str) -> None:
    """Write the prompt to ``a.prompt.txt`` and copy it, falling back to stdout."""
    (root / PROMPT_FILENAME).write_text(prompt, encoding="utf-8")
    try:
        set_clipboard_text(prompt)
    except ClipboardError as err:
        LOGGER.warning("Clipboard unavailable (%s); prompt follows.", err)
        LOGGER.info(prompt)


def _memory_matches(record: MemoryRecord | None, topic: Topic, branch: str) -> bool:
    """Return whether the memory record still applies to this topic and branch."""
    return (
        record is not None
        and record.branch == branch
        and record.version == topic.version
        and record.topic == topic.slug
    )


def _order_topics(
    topics: list[Topic],
    record: MemoryRecord | None,
    branch: str,
) -> list[Topic]:
    """Return the topics with the memorized one first when it is still valid."""
    preferred = [topic for topic in topics if _memory_matches(record, topic, branch)]
    others = [topic for topic in topics if not _memory_matches(record, topic, branch)]
    return preferred + others


def _locked_topic(
    topics: list[Topic],
    record: MemoryRecord | None,
    branch: str,
) -> Topic | None:
    """Return the topic the memory still locks to on this branch, or None (Q53).

    Topics are unique by version and slug, so at most one matches the record.
    """
    matches = [topic for topic in topics if _memory_matches(record, topic, branch)]
    return matches[0] if matches else None


def choose_topic(
    topics: list[Topic],
    record: MemoryRecord | None,
    branch: str,
    *,
    pick: bool = False,
) -> Topic | None:
    """Return the chosen topic: the only one, the branch-locked one, or a menu pick.

    A single detected topic is used directly. Otherwise, when ``pick`` is False and
    the memory still matches one detected topic on this branch, that topic is
    auto-selected and the menu is skipped (the branch lock, Q53); a one-line notice
    names it and points at ``pw --pick`` to choose another. With ``pick`` True, or
    when no memory matches, the menu is shown with the matching topic listed first.
    """
    if len(topics) == 1:
        return topics[0]
    if not pick:
        locked = _locked_topic(topics, record, branch)
        if locked is not None:
            LOGGER.info(
                "Topic %s %s locked to branch %s; run pw --pick to choose another.",
                locked.version,
                locked.slug,
                branch,
            )
            return locked
    ordered = _order_topics(topics, record, branch)
    options = [(f"{topic.version} {topic.slug}", topic) for topic in ordered]
    return menu.select("Choose the general topic:", options)


def build_menu_options(
    current: StepAlternative | None,
    next_alternatives: list[StepAlternative],
) -> list[tuple[str, StepAlternative]]:
    """Build the (label, alternative) menu options, higher step number first (Q54).

    The repeat-current row and the next-step rows are sorted by step number,
    descending and stable, so the usual forward move is the pre-highlighted top
    row and repeating the current step stays one arrow press away.
    """
    options: list[tuple[str, StepAlternative]] = []
    if current is not None:
        label = f"Repeat current step {current.number}: {current.instruction}"
        options.append((label, current))
    options.extend(
        (f"Step {alternative.number}: {alternative.instruction}", alternative)
        for alternative in next_alternatives
    )
    options.sort(key=lambda option: option[1].number, reverse=True)
    return options


def _ready_line(alternative: StepAlternative) -> str:
    """Return the single line shown after the prompt is delivered."""
    return (
        f"Prompt for step {alternative.number} ({alternative.instruction}) ready: "
        f"on the clipboard and in {PROMPT_FILENAME}."
    )


def _cycle_ready_line(cycle: CycleState, action: CycleAction) -> str:
    """Return the single line shown after a cycle prompt is delivered."""
    label = (
        "release notes" if action.kind == "release" else f"step {cycle.x} ({action.kind})"
    )
    return f"Prompt for {label} ready: on the clipboard and in {PROMPT_FILENAME}."


def _run_implement_cycle(
    root: Path,
    topic: Topic,
    branch: str,
    state: WorkflowState,
    config: dict[int, list[StepAlternative]],
) -> int:
    """Drive the implement, check and commit cycle for the current plan step (Q15-Q21)."""
    branch_start = git.fork_point(root)
    cycle = plan.compute_cycle(root, state, branch_start)
    if cycle is None:
        LOGGER.info("No plan steps found in the validation plan; nothing to do.")
        return 0

    if not cycle.terminal:
        LOGGER.info(plan.cycle_intro(root, state, cycle))
    action = menu.select(
        f"Choose the prompt for step {cycle.x}:",
        plan.build_cycle_options(cycle),
    )
    if action is None:
        LOGGER.info("No action selected; exiting.")
        return 0

    if action.stage_all:
        git.stage_all(root)
    prompt, workflow_step, instruction = plan.build_cycle_prompt(
        steps.instruction_prefix(root),
        config,
        root,
        topic,
        state,
        cycle,
        action,
    )
    deliver_prompt(root, prompt)
    memory.write_memory(
        root,
        MemoryRecord(
            branch=branch,
            version=topic.version,
            topic=topic.slug,
            step=workflow_step,
            instruction=instruction,
            plan_step=cycle.x,
        ),
    )
    LOGGER.info(_cycle_ready_line(cycle, action))
    return 0


def run(root: Path, *, pick: bool = False) -> int:
    """Drive one interactive run: resolve topic, pick a step, deliver the prompt.

    With ``pick`` True the topic menu is always shown, even when the memory locks a
    topic to this branch, so a different topic can be chosen (Q53).
    """
    branch = git.current_branch(root)
    topics = docs.relevant_drafts(root, root)
    if not topics:
        LOGGER.info("No relevant draft or general topic detected.")
        return 0

    record = memory.read_memory(root)
    topic = choose_topic(topics, record, branch, pick=pick)
    if topic is None:
        LOGGER.info("No general topic selected; exiting.")
        return 0

    matches = _memory_matches(record, topic, branch)
    memory_step = record.step if matches and record is not None else None
    instruction = record.instruction if matches and record is not None else None

    config = steps.load_steps()
    state = steps.compute_state(root, topic, memory_step)
    if state.plan is not None:
        return _run_implement_cycle(root, topic, branch, state, config)

    current = steps.current_alternative(config, memory_step, instruction)
    next_alternatives = steps.alternatives_for(config, steps.next_step_numbers(state))

    chosen = menu.select(
        "Choose the prompt to generate:",
        build_menu_options(current, next_alternatives),
    )
    if chosen is None:
        LOGGER.info("No step selected; exiting.")
        return 0

    prompt = steps.build_prompt(steps.instruction_prefix(root), chosen, root, topic, state)
    deliver_prompt(root, prompt)
    memory.write_memory(
        root,
        MemoryRecord(
            branch=branch,
            version=topic.version,
            topic=topic.slug,
            step=chosen.number,
            instruction=chosen.instruction,
        ),
    )
    LOGGER.info(_ready_line(chosen))
    return 0


def run_handoff(root: Path, task: str, step: str) -> int:
    """Write one named step's prompt without the menu (the handoff subcommand).

    Resolve the topic from the single draft or the branch lock (Q63), build the
    cycle state for the named ``step`` after checking it is a real
    ``Analysis of Step <id>`` section (Q59), warn when it differs from the
    git-derived ``x``, map ``task`` to its cycle action (routing ``after-check``
    from the Yes/No status the check wrote, Q58), stage everything for a commit
    action, then deliver and record the prompt exactly as the interactive cycle
    does (Q60, Q61).

    Args:
        root: The resolved project root.
        task: One of ``prompt_workflow_handoff.TASK_TOKENS``.
        step: The plan step id the handoff names, such as ``2`` or ``4A``.

    Returns:
        0 on success.

    Raises:
        PromptWorkflowError: On any refusal -- no resolvable topic (Q63), an
            unknown step (Q59) or task, or an ``after-check`` with no Yes/No
            status -- turned into ``EXIT_FATAL`` (2) by ``__main__`` (Q03).
    """
    branch = git.current_branch(root)
    topics = docs.relevant_drafts(root, root)
    record = memory.read_memory(root)
    topic = handoff.resolve_topic(topics, record, branch)
    if topic is None:
        msg = (
            "Cannot resolve a topic for the handoff without a menu "
            "(no single draft and no branch lock). Run pw --pick to lock one first."
        )
        raise PromptWorkflowError(msg)

    # The cycle re-derives its plan step from git and the validation plan, so the
    # persisted workflow step is not needed to build the handoff state (Q21).
    config = steps.load_steps()
    state = steps.compute_state(root, topic, None)
    branch_start = git.fork_point(root)

    plan_step = handoff.find_plan_step(state, step)
    derived = handoff.derived_mismatch(root, state, branch_start, step)
    if derived is not None:
        LOGGER.warning(
            "Handed step %s differs from the derived step %s; using the handed step.",
            step,
            derived,
        )
    action = handoff.action_for_task(task, plan_step)
    cycle = handoff.cycle_state_for_step(plan_step)

    if action.stage_all:
        git.stage_all(root)
    prompt, workflow_step, instruction = plan.build_cycle_prompt(
        steps.instruction_prefix(root),
        config,
        root,
        topic,
        state,
        cycle,
        action,
    )
    deliver_prompt(root, prompt)
    memory.write_memory(
        root,
        MemoryRecord(
            branch=branch,
            version=topic.version,
            topic=topic.slug,
            step=workflow_step,
            instruction=instruction,
            plan_step=cycle.x,
        ),
    )
    LOGGER.info(_cycle_ready_line(cycle, action))
    return 0


def _get_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser.

    ``--root`` and ``--debug`` live on a shared parent parser passed to both the
    top-level parser and the ``handoff`` subparser, so they parse on either side
    of the subcommand (Q01); ``--pick`` stays top-level only. The ``handoff``
    subcommand carries a ``task`` word and a plain-string ``step`` positional, so
    a sub-step id such as ``4A`` is accepted and validated by the resolver, not
    the parser (Q04, Q56).
    """
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        default=None,
        help="Project root override. If not provided, scan upward for the root.",
    )
    common.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    parser = argparse.ArgumentParser(
        parents=[common],
        description="Generate and copy the next-step LLM prompt for the current topic.",
    )
    parser.add_argument(
        "--pick",
        action="store_true",
        help="Reopen the topic menu even when a topic is locked to the branch.",
    )
    subparsers = parser.add_subparsers(dest="command")
    handoff_parser = subparsers.add_parser(
        "handoff",
        parents=[common],
        help="Write the prompt for one named step without the menu.",
    )
    handoff_parser.add_argument(
        "task",
        help=f"The handoff task, one of: {', '.join(handoff.TASK_TOKENS)}.",
    )
    handoff_parser.add_argument(
        "step",
        help="The plan step id the prompt is for, such as 2 or 4A.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Dispatch to ``run_handoff`` when the ``handoff`` subcommand is selected
    (Q56), otherwise to the interactive ``run``.
    """
    parser = _get_arg_parser()
    args = parser.parse_args(argv)
    _configure_logging(debug=args.debug)
    root = Path(args.root).resolve() if args.root else find_project_root(Path.cwd())
    if args.command == "handoff":
        return run_handoff(root, args.task, args.step)
    return run(root, pick=args.pick)


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with EXIT_FATAL."""
    _configure_logging(debug=False)
    LOGGER.error("ERROR: %s", err)
    raise SystemExit(EXIT_FATAL) from err


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PromptWorkflowError, OSError) as err:
        _log_fatal(err)


# eof
