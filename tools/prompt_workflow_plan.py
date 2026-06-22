"""Implement-validate-group cycle for prompt_workflow (steps 10 to 12).

Once a plan and its validation plan exist, the implement, check and commit cycle
is driven by a plan step ``x`` re-derived from the validation plan and git, not
by the persisted workflow step (Q21). This module parses the validation plan's
``Analysis of Step N`` markers (Q15), derives ``x`` and whether it advanced past
a recorded commit (Q16, Q19), classifies the working tree (Q20), and builds the
menu options and the per-step prompts the cycle offers (Q17).

Fix: the group-commits prompt (step 12) is now completed with the count and the
porcelain ``XY path`` list of the staged files, read after the optional
``git add -A`` (Q22, Q23); its Context drops the ``git_status`` role since the
body carries the list (Q24); and ``a.commit`` is emptied before the prompt is
delivered so the grouping starts from a clean file (Q25), and its Context lists
the five check documents (Q40). The implement, check and commit prompts and a
menu introduction line inline the plan step title and the plan document, read
once from the plan's ``### Step N.`` heading, dropping a segment when the title
or the plan is missing (Q26, Q30-Q40).

Fix (sub-steps): a plan step id may carry a letter suffix, such as ``4A`` (Q41,
Q42). The id is parsed from the ``Analysis of Step`` heading and kept as a string
through ``PlanStep.number`` and ``CycleState.x`` (Q41), so ``derive_x`` keys each
status by the full id and a sub-step ``Not started`` no longer overwrites its
parent ``Yes`` (Q45). Steps run in document order (Q43) and each sub-step is
committed on its own (Q44).

Fix (implement-missing): when the validation plan marks step ``x`` ``No`` (the
status line starts with ``No``), the implement entry switches to the
implement-missing variant (Q46). ``parse_validation_steps`` records that ``No``
state on ``PlanStep`` and ``compute_cycle`` carries it on ``CycleState`` (Q46);
``build_cycle_options`` relabels the entry ``Implement missing for step <id>`` and
sets ``CycleAction.missing`` (Q47); and the prompt is built from the second step-10
alternative, ``implement-missing-step.md``, which points at the validation plan's
``Missing work for Step x`` section and carries a split-large-file line-budget
reminder interpolated with the header ``{prefix}`` (Q48-Q52).

Fix (menu order): ``build_cycle_options`` lists the cycle options higher
workflow step first — the commit variants (10), then the check (9), then the
implement entry (8) — so the usual follow-up of the step just done is the
pre-highlighted top row (Q54). The implement-missing entry is the exception:
when a ``No`` status offers it, it tops the menu, since the step moves forward
by filling its recorded gap first (Q55).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_git as git
from tools import prompt_workflow_steps as steps

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.prompt_workflow_models import StepAlternative, Topic, WorkflowState

# A heading naming a plan step's analysis, matched loosely and case-insensitively
# to cover both the validation template and implementation-check.md wordings. The
# captured id is the \d+[A-Za-z]* token, so a lettered sub-step such as 4A is kept
# whole and never read as the bare number 4 (Q42).
ANALYSIS_RE = re.compile(r"analysis of step\s+(\d+[A-Za-z]*)", re.IGNORECASE)
# A status line that marks the step implemented and verified.
STATUS_YES_RE = re.compile(r"^\s*yes", re.IGNORECASE)
# A status line that marks the step explicitly not implemented (Q46). The word
# boundary keeps "No, ..." apart from "Not started", which stays a placeholder.
STATUS_NO_RE = re.compile(r"^\s*no\b", re.IGNORECASE)
# The docs folder prefix; changes outside it count as code changes (Q20).
_DOCS_PREFIX = "docs/"
# Workflow step number per cycle action kind (kept internal, never shown, Q17).
# The cycle sits after the plain plan's own review-and-consolidate round (steps 8
# and 9), so it starts at step 10.
_WORKFLOW_STEP = {"implement": 10, "check": 11, "commit": 12, "release": 13}
# Name of the grouped-commit file the commit prompt resets at the project root (Q25).
A_COMMIT_FILENAME = "a.commit"
# Template for the introduction line printed above a non-terminal cycle menu (Q33).
INTRO_TEMPLATE = 'Regarding step {x} ("{title}") from {plan_doc}:'


@dataclass(frozen=True)
class PlanStep:
    """One plan step parsed from the validation plan.

    Attributes:
        number: The plan step id read from the ``Analysis of Step N`` heading. It
            is the digits-then-optional-letters token (``ANALYSIS_RE``), kept as a
            string so a lettered sub-step such as ``4A`` round-trips whole and
            never collapses to the bare number ``4`` (Q41, Q42).
        verified: Whether its status line starts with ``Yes``.
        not_implemented: Whether its status line starts with ``No`` (Q46), distinct
            from a placeholder status (neither ``Yes`` nor ``No``) that leaves both
            flags False and keeps the plain implement body.
    """

    number: str
    verified: bool
    not_implemented: bool = False


@dataclass(frozen=True)
class CycleState:
    """The derived state of the implement cycle for the current plan step.

    Attributes:
        x: The plan step id the cycle is on, a string that may carry a letter
            suffix such as ``4A`` for a sub-step (Q41).
        verified: Whether step ``x`` is marked implemented and verified.
        terminal: Whether every plan step is done (propose release notes).
        has_code_changes: Whether any changed path lies outside ``docs/``.
        cached: Whether any change is staged.
        non_cached: Whether any change is unstaged or untracked.
        not_implemented: Whether step ``x``'s status line starts with ``No`` (Q46),
            so the implement entry becomes the implement-missing variant.
    """

    x: str
    verified: bool
    terminal: bool
    has_code_changes: bool
    cached: bool
    non_cached: bool
    not_implemented: bool = False


@dataclass(frozen=True)
class CycleAction:
    """One selectable cycle action.

    Attributes:
        kind: ``implement``, ``check``, ``commit`` or ``release``.
        stage_all: Whether to run ``git add -A`` before building the prompt.
        missing: Whether an implement action is the implement-missing variant,
            built from the ``implement-missing-step.md`` alternative (Q47).
    """

    kind: str
    stage_all: bool
    missing: bool = False


def _first_status_line(lines: list[str], start: int) -> str | None:
    """Return the first non-empty line at or after ``start``, or None at the end."""
    cursor = start
    while cursor < len(lines) and not lines[cursor].strip():
        cursor += 1
    return lines[cursor] if cursor < len(lines) else None


def _status_is_yes(lines: list[str], start: int) -> bool:
    """Return whether the first non-empty line from ``start`` begins with Yes."""
    line = _first_status_line(lines, start)
    return line is not None and STATUS_YES_RE.match(line) is not None


def _status_is_no(lines: list[str], start: int) -> bool:
    """Return whether the first non-empty line from ``start`` begins with No (Q46).

    A leading ``No`` with a word boundary marks the step not implemented; a
    ``No``-prefixed word such as ``Not started`` does not, so it stays a
    placeholder that keeps the plain implement body.
    """
    line = _first_status_line(lines, start)
    return line is not None and STATUS_NO_RE.match(line) is not None


def parse_validation_steps(text: str) -> list[PlanStep]:
    """Return the plan steps parsed from the validation plan text (Q15).

    A plan step is a heading matching ``Analysis of Step <N>`` whose first
    following non-empty line starts with ``Yes`` (verified) or anything else.
    """
    lines = text.splitlines()
    found: list[PlanStep] = []
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("#"):
            continue
        match = ANALYSIS_RE.search(line)
        if match is None:
            continue
        found.append(
            PlanStep(
                number=match.group(1),
                verified=_status_is_yes(lines, index + 1),
                not_implemented=_status_is_no(lines, index + 1),
            ),
        )
    return found


def derive_x(
    plan_steps: list[PlanStep],
    has_commit: Callable[[str], bool],
) -> tuple[str, bool, bool]:
    """Return ``(x, verified, terminal)`` for the cycle from the plan steps.

    ``x`` is the id of the last verified step, or the first step when none is
    verified (Q19). When that step already has a ``record step x validation``
    commit it advances to the next step in document order (Q43), or marks the
    cycle terminal when it was the last step (Q16, Q19). The ``verified`` map is
    keyed by the full id, so a sub-step ``Not started`` never overwrites the
    ``Yes`` of its parent step (Q45).
    """
    numbers = [step.number for step in plan_steps]
    verified = {step.number: step.verified for step in plan_steps}
    yes = [step.number for step in plan_steps if step.verified]
    base = yes[-1] if yes else numbers[0]
    if has_commit(base):
        index = numbers.index(base)
        if index == len(numbers) - 1:
            return base, verified[base], True
        following = numbers[index + 1]
        return following, verified[following], False
    return base, verified[base], False


def _is_staged(status: str) -> bool:
    """Return whether the porcelain status marks a staged change."""
    return status[0] not in {" ", "?"}


def _is_unstaged(status: str) -> bool:
    """Return whether the porcelain status marks an unstaged or untracked change."""
    return status[1] != " "


def compute_cycle(
    root: Path,
    state: WorkflowState,
    branch_start: str | None,
) -> CycleState | None:
    """Derive the cycle state, or None when there is no validation plan or steps."""
    if state.validation_plan is None:
        return None
    plan_steps = parse_validation_steps(state.validation_plan.read_text(encoding="utf-8"))
    if not plan_steps:
        return None

    def _has_commit(number: str) -> bool:
        return git.has_step_commit(root, number, branch_start)

    x, verified, terminal = derive_x(plan_steps, _has_commit)
    not_implemented = {step.number: step.not_implemented for step in plan_steps}[x]
    entries = git.status_entries(root)
    return CycleState(
        x=x,
        verified=verified,
        terminal=terminal,
        has_code_changes=any(not path.startswith(_DOCS_PREFIX) for _, path in entries),
        cached=any(_is_staged(status) for status, _ in entries),
        non_cached=any(_is_unstaged(status) for status, _ in entries),
        not_implemented=not_implemented,
    )


def build_cycle_options(cycle: CycleState) -> list[tuple[str, CycleAction]]:
    """Return the menu options for the cycle, labelled by the plan step (Q17, Q20).

    The options are listed higher workflow step first — commit (10), then check
    (9), then implement (8) — so the usual follow-up of the step just done sits
    at the top of the menu, pre-highlighted (Q54). One exception: when a ``No``
    status offers the implement-missing entry, that entry tops the menu, since
    moving forward is best served by filling the recorded gap first (Q55).
    """
    if cycle.terminal:
        return [("Prepare release notes", CycleAction(kind="release", stage_all=False))]

    options: list[tuple[str, CycleAction]] = []
    if cycle.verified:
        if cycle.cached:
            options.append(
                (f"Commit step {cycle.x} (cached)", CycleAction(kind="commit", stage_all=False)),
            )
        if cycle.non_cached:
            options.append(
                (
                    f"Commit step {cycle.x} (git add -A)",
                    CycleAction(kind="commit", stage_all=True),
                ),
            )
    if cycle.has_code_changes:
        options.append((f"Check step {cycle.x}", CycleAction(kind="check", stage_all=False)))
    label = (
        f"Implement missing for step {cycle.x}"
        if cycle.not_implemented
        else f"Implement step {cycle.x}"
    )
    implement = (
        label,
        CycleAction(kind="implement", stage_all=False, missing=cycle.not_implemented),
    )
    if cycle.not_implemented:
        options.insert(0, implement)
    else:
        options.append(implement)
    return options


def _relpath(root: Path, path: Path) -> str:
    """Return path as a posix string relative to the project root."""
    return Path(os.path.relpath(path.resolve(), root)).as_posix()


def _cycle_alternative(
    config: dict[int, list[StepAlternative]],
    action: CycleAction,
) -> StepAlternative:
    """Return the step alternative backing a cycle action.

    The implement-missing action takes the second step-10 alternative, the
    ``implement-missing-step.md`` body, in place of the plain implement body (Q48).
    """
    if action.kind == "release":
        return config[_WORKFLOW_STEP["release"]][1]
    alternatives = config[_WORKFLOW_STEP[action.kind]]
    if action.kind == "implement" and action.missing:
        return alternatives[1]
    return alternatives[0]


def staged_listing(root: Path) -> tuple[int, str]:
    """Return the count and the porcelain ``XY path`` lines of the staged files.

    The status entries are filtered to the staged ones (the index column is
    set), read at this point so they reflect the optional ``git add -A`` the
    caller may have run (Q23). Every staged file is listed whatever its folder,
    ``docs/`` included, and each line keeps the two-character status code so the
    grouping sees what changed, matching ``git status --short`` (Q22).
    """
    staged = [(status, path) for status, path in git.status_entries(root) if _is_staged(status)]
    lines = "\n".join(f"{status} {path}" for status, path in staged)
    return len(staged), lines


def reset_a_commit(root: Path) -> None:
    """Empty ``a.commit`` at the project root, creating it when absent (Q25).

    The group-commits instruction rewrites ``a.commit``; clearing it first drops
    any stale groups from a previous run. The file is truncated to size 0, never
    deleted, the same write-empty step ``oqm --create`` uses for its companion.
    """
    (root / A_COMMIT_FILENAME).write_text("", encoding="utf-8")


def read_step_title(plan_path: Path | None, x: str) -> str | None:
    """Return the title of plan step ``x`` from the plan document, or None.

    The title is the trailing text of the first heading line that names
    ``Step <x>``, the ``### Step N. <step title>`` heading of the plan's numbered
    steps section (Q30). A ``.``, ``:`` or ``-`` separator between the number and
    the title is tolerated (Q32). None is returned when the plan is missing or
    carries no such heading, so the check body falls back to the number only (Q31).

    The id ``x`` is escaped before it joins the pattern and a word-boundary check
    follows it, so ``4`` matches ``### Step 4.`` but not ``### Step 4A.`` (there is
    no word boundary between a digit and a letter), keeping a parent step apart
    from its sub-steps (Q42).

    Args:
        plan_path: The plain plan document, or None when it is not resolved.
        x: The plan step id whose title is read, such as ``4`` or ``4A``.

    Returns:
        The step title text, or None when it cannot be read.
    """
    if plan_path is None or not plan_path.is_file():
        return None
    pattern = re.compile(
        rf"^#+\s*step\s+{re.escape(x)}\b[\s.:\-]*([^\s.:\-].*?)\s*$",
        re.IGNORECASE,
    )
    for line in plan_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        match = pattern.match(stripped)
        if match is not None:
            return match.group(1).strip()
    return None


def _fill_optional(text: str, value: str | None, placeholder: str, segment: str) -> str:
    """Interpolate ``placeholder`` with ``value``, or drop ``segment`` when None.

    Used for the optional ``{title}`` and ``{plan_doc}`` parts of the cycle
    prompts and the menu introduction: a missing value drops the whole segment,
    spacing included, instead of leaving an empty placeholder (Q31, Q34, Q35).
    """
    if value is None:
        return text.replace(segment, "")
    return text.replace(placeholder, value)


def _title_and_plan(
    root: Path,
    state: WorkflowState,
    x: str,
) -> tuple[str | None, str | None]:
    """Return the step ``x`` title and the repo-relative plan path, or None each.

    The title is read from the plan ``### Step N.`` heading (Q30, Q32); the plan
    path is the resolved plan document, or None when no plan is resolved (Q35).
    """
    plan_doc = _relpath(root, state.plan) if state.plan is not None else None
    return read_step_title(state.plan, x), plan_doc


def cycle_intro(root: Path, state: WorkflowState, cycle: CycleState) -> str:
    """Return the introduction line printed above a non-terminal cycle menu.

    It reads ``Regarding step {x} ("{title}") from {plan_doc}:`` and drops the
    title or the plan segment when either is missing (Q33, Q34, Q35).
    """
    title, plan_doc = _title_and_plan(root, state, cycle.x)
    line = INTRO_TEMPLATE.replace("{x}", str(cycle.x))
    line = _fill_optional(line, title, "{title}", ' ("{title}")')
    return _fill_optional(line, plan_doc, "{plan_doc}", " from {plan_doc}")


def build_cycle_prompt(  # noqa: PLR0913
    prefix: str,
    config: dict[int, list[StepAlternative]],
    root: Path,
    topic: Topic,
    state: WorkflowState,
    cycle: CycleState,
    action: CycleAction,
) -> tuple[str, int, str]:
    """Build the prompt for a cycle action; return it with its workflow step.

    The body interpolates the plan step ``x`` (Q17). For an implement or check
    action the body also inlines the step title ``{title}`` and the plan document
    ``{plan_doc}`` read from the plan, dropping a segment when either is missing
    (Q26, Q30-Q35). The implement-missing action uses the ``implement-missing-step.md``
    body, whose ``{prefix}`` placeholder is filled with the header prefix so its
    split-large-file line resolves to a real path (Q47, Q48, Q50). For a commit action the body also names the step title and
    plan (Q38) and is completed with the count ``{n}`` and the porcelain ``{files}`` list of
    the staged files read at this point (Q22, Q23), and ``a.commit`` is emptied so
    the grouping starts from a clean file (Q25). When the staged set includes the
    validation plan, the prompt is completed with the required
    ``docs(<topic>): record step x validation`` final commit (Q16).
    """
    alternative = _cycle_alternative(config, action)
    body = alternative.body.replace("{x}", str(cycle.x)).replace("{prefix}", prefix)
    if action.kind in ("implement", "check"):
        title, plan_doc = _title_and_plan(root, state, cycle.x)
        body = _fill_optional(body, title, "{title}", ' "{title}"')
        body = _fill_optional(body, plan_doc, "{plan_doc}", ' "{plan_doc}"')
    elif action.kind == "commit":
        title, plan_doc = _title_and_plan(root, state, cycle.x)
        body = _fill_optional(body, title, "{title}", ' ("{title}")')
        body = _fill_optional(body, plan_doc, "{plan_doc}", ' of the implementation plan "{plan_doc}"')
        count, files = staged_listing(root)
        body = body.replace("{n}", str(count)).replace("{files}", files)
        reset_a_commit(root)
    rendered = replace(alternative, body=body)
    prompt = steps.build_prompt(prefix, rendered, root, topic, state)
    if (
        action.kind == "commit"
        and state.validation_plan is not None
        and _relpath(root, state.validation_plan) in git.staged_files(root)
    ):
        prompt += (
            f"\n\nAdditionally, the final commit must be "
            f"`docs({topic.slug}): record step {cycle.x} validation`."
        )
    return prompt, _WORKFLOW_STEP[action.kind], alternative.instruction


# eof
