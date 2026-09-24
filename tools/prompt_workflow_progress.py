"""Report where the current topic stands and how far along it is (`pw progress`).

`pw skill` prints only the next command. `pw progress` prints, above that same
command, the branch, the topic, its umbrella position (or that it is a
standalone topic), the document phase, and the plan step position.

Positions are counted, not read from ids: plan step ids come from the
validation plan in document order, so a step `3.2` that is the fourth of
eleven listed steps renders as `step 3.2 (4/11)`. An id equal to its position
renders compactly, as in `topic 3/4`.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools import prompt_workflow_docs as docs
from tools import prompt_workflow_git as git
from tools import prompt_workflow_handoff as handoff
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_skill as skill
from tools import prompt_workflow_steps as steps
from tools.prompt_workflow_post_commit import slug_key

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from pathlib import Path

    from tools.prompt_workflow_models import CollectionItem, Topic
    from tools.prompt_workflow_plan import PlanStep

# The ordered document phases of one topic, from the unprocessed draft to the
# implementation cycle.
PHASES: Final[tuple[str, ...]] = ("draft", "requirement", "design", "plan", "implementation")
_IMPLEMENTATION: Final[str] = "implementation"
_COMPLETED: Final[str] = "completed"
_UMBRELLA_PREFIX: Final[str] = "- Umbrella: "
_LABEL_WIDTH: Final[int] = 10


def format_position(label: str, index: int, total: int) -> str:
    """Return `index/total`, prefixed by the label when it differs from the index.

    Args:
        label: The id as written in the document, such as `3.2`, `A`, or `3`.
        index: The one-based position of that id in its ordered list.
        total: The number of ids in the list.

    Returns:
        `3/4` when the label is the position itself, otherwise `3.2 (4/11)`.
    """
    if label == str(index):
        return f"{index}/{total}"
    return f"{label} ({index}/{total})"


@dataclass(frozen=True)
class StepProgress:
    """The plan step position of a topic that has a validation plan.

    Attributes:
        current: The current step id, or None before the implementation cycle.
        index: The one-based position of the current step, or 0 when none.
        total: The number of steps listed in the validation plan.
        verified: How many steps the validation plan marks `Yes`.
        title: The current step title read from the plan, when available.
        terminal: True when every step is done and committed.
    """

    current: str | None
    index: int
    total: int
    verified: int
    title: str | None = None
    terminal: bool = False

    def render(self) -> str:
        """Return the one-line step report."""
        done = f"{self.verified}/{self.total} verified"
        if self.terminal:
            return f"all {self.total} steps done ({done})"
        if self.current is None:
            return f"{self.total} steps planned ({done})"
        position = format_position(self.current, self.index, self.total)
        title = f": {self.title}" if self.title else ""
        return f"{position}{title} ({done})"


def step_progress(
    plan_steps: list[PlanStep],
    has_commit: Callable[[str], bool],
    *,
    active: bool,
    title_for: Callable[[str], str | None] = lambda _step: None,
) -> StepProgress | None:
    """Return the step position from the validation plan steps.

    Args:
        plan_steps: The steps parsed from the validation plan, in document order.
        has_commit: Whether a step already has its record-step commit.
        active: True when the topic is in its implementation phase; otherwise
            only the planned and verified counts are reported.
        title_for: Reads the plan title of one step id.

    Returns:
        The step position, or None when the validation plan lists no step.
    """
    if not plan_steps:
        return None
    total = len(plan_steps)
    verified = sum(1 for step in plan_steps if step.verified)
    if not active:
        return StepProgress(current=None, index=0, total=total, verified=verified)
    current, _verified, terminal = plan.derive_x(plan_steps, has_commit)
    numbers = [step.number for step in plan_steps]
    return StepProgress(
        current=current,
        index=numbers.index(current) + 1,
        total=total,
        verified=verified,
        title=title_for(current),
        terminal=terminal,
    )


@dataclass(frozen=True)
class UmbrellaProgress:
    """The position of a topic, or of the next topic, in its umbrella.

    Attributes:
        slug: The umbrella slug.
        items: The ordered umbrella rows.
        index: The one-based row of the topic, or 0 when it is not listed.
    """

    slug: str
    items: tuple[CollectionItem, ...]
    index: int

    @property
    def completed(self) -> int:
        """Return how many umbrella rows are completed."""
        return sum(1 for item in self.items if item.status == _COMPLETED)

    def _done(self) -> str:
        return f"{self.completed}/{len(self.items)} topics completed"

    def render_child(self) -> str:
        """Return the umbrella line of a child topic."""
        if self.index == 0:
            return f"{self.slug}, topic not listed ({self._done()})"
        item = self.items[self.index - 1]
        position = format_position(str(self.index), self.index, len(self.items))
        return f"{self.slug}, topic {position}: {item.title} ({self._done()})"

    def render_own(self) -> str:
        """Return the umbrella line of the umbrella integration branch itself."""
        pending = [
            (index, item)
            for index, item in enumerate(self.items, start=1)
            if item.status != _COMPLETED
        ]
        if not pending:
            return f"{self._done()}, every topic done"
        index, item = pending[0]
        position = format_position(str(index), index, len(self.items))
        return f"{self._done()}, next topic {position}: {item.title} (`{item.slug}`)"


def phase_of(workflow_step: int, *, draft_pending: bool) -> str:
    """Return the document phase of a resolved workflow step.

    Args:
        workflow_step: The routed workflow step, 1 to 10.
        draft_pending: True when step 1 still has to process the draft.

    Returns:
        One of `PHASES`.
    """
    if workflow_step == 1 and draft_pending:
        return PHASES[0]
    if workflow_step == skill.IMPLEMENT_STEP:
        return _IMPLEMENTATION
    return skill.STEP_ROLE[workflow_step]


def render_phase(phase: str) -> str:
    """Return the phase with its position among `PHASES`."""
    index = PHASES.index(phase) + 1
    return f"{phase} ({index}/{len(PHASES)})"


def umbrella_path(root: Path, topic: Topic) -> Path | None:
    """Return the umbrella draft the topic belongs to, or None when standalone.

    The child draft's one `- Umbrella:` marker wins. A topic resolved through
    its umbrella draft (no own draft) uses that draft. Otherwise one
    same-version umbrella listing the slug is used, as `implementation-check`
    does; no match, or several, means a standalone topic.

    Args:
        root: The project root.
        topic: The resolved topic.

    Returns:
        The umbrella draft path, or None for a standalone topic.
    """
    draft = topic.draft_path
    if draft.is_file():
        marked = _marked_umbrella(root, draft)
        if marked is not None:
            return marked
        if _resolved_through_umbrella(draft, topic.slug):
            return draft
    candidates = [
        entry
        for directory in docs.docs_dirs_for_version(root, topic.version)
        for entry in sorted(directory.iterdir())
        if _is_other_listing_umbrella(entry, draft, topic.slug)
    ]
    return candidates[0].resolve() if len(candidates) == 1 else None


def _marked_umbrella(root: Path, draft: Path) -> Path | None:
    """Return the umbrella named by the draft's one existing `- Umbrella:` line."""
    markers = [
        line.removeprefix(_UMBRELLA_PREFIX).strip()
        for line in draft.read_text(encoding="utf-8").splitlines()
        if line.startswith(_UMBRELLA_PREFIX)
    ]
    if len(markers) == 1 and (root / markers[0]).is_file():
        return (root / markers[0]).resolve()
    return None


def _resolved_through_umbrella(draft: Path, slug: str) -> bool:
    """Return whether the topic draft is another slug's umbrella listing this slug."""
    parsed = docs.parse_draft_name(draft.name)
    return parsed is not None and slug_key(parsed[1]) != slug_key(slug) and _lists(draft, slug)


def _is_other_listing_umbrella(entry: Path, draft: Path, slug: str) -> bool:
    """Return whether a docs entry is another draft whose umbrella table lists the slug."""
    return (
        entry.is_file()
        and entry.resolve() != draft.resolve()
        and docs.parse_draft_name(entry.name) is not None
        and _lists(entry, slug)
    )


def _lists(umbrella: Path, slug: str) -> bool:
    """Return whether an umbrella draft carries a row for the slug."""
    key = slug_key(slug)
    return any(slug_key(item.slug) == key for item in docs.collection_items(umbrella))


def umbrella_progress(umbrella: Path, slug: str | None) -> UmbrellaProgress:
    """Return the umbrella rows and the one-based row of the slug (0 if absent)."""
    items = docs.collection_items(umbrella)
    index = 0
    if slug is not None:
        key = slug_key(slug)
        index = next(
            (position for position, item in enumerate(items, start=1) if slug_key(item.slug) == key),
            0,
        )
    parsed = docs.parse_draft_name(umbrella.name)
    return UmbrellaProgress(
        slug=parsed[1] if parsed is not None else umbrella.stem,
        items=items,
        index=index,
    )


def progress_lines(
    root: Path,
    topic: Topic,
    branch: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> list[tuple[str, str]]:
    """Return the labelled progress lines of a resolved topic.

    Args:
        root: The project root.
        topic: The resolved topic.
        branch: The current branch name.
        env: The process environment, read for the host prefix.
        override: An optional host token forcing the prefix.

    Returns:
        `(label, value)` pairs: branch, topic, umbrella, then phase and step
        for a topic (not for its umbrella integration branch), then next.
    """
    command, _note = skill.current_command(root, topic, branch, env, override)
    next_line = command or "none resolved"
    lines = [("branch", branch)]
    if skill.is_umbrella_branch(topic, branch):
        lines.append(("topic", f"{topic.version} {topic.slug} (umbrella)"))
        lines.append(("umbrella", umbrella_progress(topic.draft_path, None).render_own()))
        lines.append(("next", next_line))
        return lines
    lines.append(("topic", f"{topic.version} {topic.slug}"))
    umbrella = umbrella_path(root, topic)
    lines.append((
        "umbrella",
        "none, standalone topic"
        if umbrella is None
        else umbrella_progress(umbrella, topic.slug).render_child(),
    ))
    state = steps.compute_state(root, topic, None)
    phase = phase_of(
        skill.resolved_workflow_step(state),
        draft_pending=branch != topic.slug,
    )
    lines.append(("phase", render_phase(phase)))
    if state.validation_plan is not None:
        branch_start = git.fork_point(root)
        progress = step_progress(
            plan.parse_validation_steps(state.validation_plan.read_text(encoding="utf-8")),
            lambda number: git.has_step_commit(root, number, branch_start),
            active=phase == _IMPLEMENTATION,
            title_for=lambda number: plan.read_step_title(state.plan, number),
        )
        if progress is not None:
            lines.append(("step", progress.render()))
    lines.append(("next", next_line))
    return lines


def render_lines(lines: list[tuple[str, str]]) -> str:
    """Return the aligned `label value` report text."""
    return "".join(f"{label:<{_LABEL_WIDTH}}{value}\n" for label, value in lines)


def run_progress(root: Path, host_override: str | None = None) -> int:
    """Print where the current topic stands, then its next command.

    Args:
        root: The project root.
        host_override: A host token forcing the command prefix, or None.

    Returns:
        0 when a topic is resolved, `skill.EXIT_NOT_APPLICABLE` otherwise.
    """
    branch = git.current_branch(root)
    topic = handoff.resolve_current_topic(root, branch, memory.read_memory(root))
    if topic is None:
        sys.stdout.write(render_lines([("branch", branch), ("topic", "none resolved")]))
        return skill.EXIT_NOT_APPLICABLE
    sys.stdout.write(render_lines(progress_lines(root, topic, branch, os.environ, host_override)))
    return 0


# eof
