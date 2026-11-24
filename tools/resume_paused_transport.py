"""Shell-free TUIOS transport of the human-launched bulk resume.

Step 6 of v0.15.0 resume-paused types into panes only through two argument
lists, run directly without a shell, so no shell or MSYS layer can rewrite a
leading ``/`` or interpret a metacharacter of the marked command:

- ``ask_arguments``: ``tuios ask-agent --select 'session:S name:N' --yes
  --stall-timeout 60000 --timeout 100000 --lines 1 --json -- <command>``, the
  selector form the requirement proved from any pane. ``--`` ends the options,
  so the command is one inert argument whatever it contains;
- ``enter_arguments``: ``tuios send-keys -s S -w <full pane id> Enter``, the
  single Codex recovery Enter, targeted by the full pane UUID.

TUIOS splits selector terms on spaces and matches each value as a glob, so a
space in a live session or pane name becomes the documented ``*`` wildcard. A
name holding another glob character or a non-printing one has no exact glob
and is refused. ``resolve_selector`` then requires that the selector, read
more broadly than TUIOS reads it (case-insensitive, a wildcard crossing any
character), matches exactly one listed pane, the validated full UUID; any
collision is an error before input.

``TuiosTransport`` adapts the delivery's transport port, so the selector
syntax stays here: ``select`` resolves the selector, and fresh discovery,
captures, the ask and the Enter each run on a runner bounded by the seconds
the delivery grants, the remaining budget of the send in progress. Every send
starts with its ask, so the ask's process bound and its ``--timeout`` are the
same 100 seconds. The caller's environment, ``TUIOS_*`` variables included,
is inherited unchanged. An ask's exit code is report-only: it never proves
that a command was taken.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.resume_paused_evidence import observe_panes
from tools.resume_paused_input import TuiosDiscovery

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tools.resume_paused_evidence import PaneObservation
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_profiles import CommandRunner

STALL_TIMEOUT_MS: Final = 60_000
ASK_TIMEOUT_MS: Final = 100_000
_GLOB_CHARACTERS: Final = frozenset("*?[]\\")
_WILDCARD: Final = "*"


@dataclass(frozen=True)
class Selection:
    """The resolved selector of one target, or the reason none is safe."""

    selector: str | None
    reason: str = ""


@dataclass(frozen=True)
class AskOutcome:
    """Exit code of one ask; report-only, never acceptance evidence."""

    exit_code: int


def selector_value(text: str) -> str | None:
    """Return the glob of one live session or pane name, ``None`` when no exact glob exists."""
    plain = all(character == " " or (character.isprintable() and not character.isspace()) for character in text)
    if not text or not plain or not _GLOB_CHARACTERS.isdisjoint(text):
        return None
    return text.replace(" ", _WILDCARD)


def _broad(glob: str) -> re.Pattern[str]:
    """Match a glob at least as broadly as TUIOS: any text for a wildcard, any letter case."""
    return re.compile(".*".join(re.escape(part) for part in glob.split(_WILDCARD)), re.IGNORECASE | re.DOTALL)


def resolve_selector(panes: Sequence[PaneRecord], target: PaneRecord) -> Selection:
    """Build the target's selector from its live session and name; it must match only the target."""
    session, name = selector_value(target.session), selector_value(target.name)
    if session is None or name is None:
        return Selection(None, "selector-unsupported")
    by_session, by_name = _broad(session), _broad(name)
    matches = [pane.pane_id for pane in panes if by_session.fullmatch(pane.session) and by_name.fullmatch(pane.name)]
    if matches != [target.pane_id]:
        return Selection(None, "selector-ambiguous" if len(matches) > 1 else "selector-unresolved")
    return Selection(f"session:{session} name:{name}")


def ask_arguments(selector: str, command: str) -> tuple[str, ...]:
    """Return the ask argument list; the command follows ``--`` as one argument."""
    return (
        "tuios", "ask-agent", "--select", selector, "--yes",
        "--stall-timeout", str(STALL_TIMEOUT_MS), "--timeout", str(ASK_TIMEOUT_MS),
        "--lines", "1", "--json", "--", command,
    )


def enter_arguments(session: str, pane_id: str) -> tuple[str, ...]:
    """Return the single recovery Enter, targeted by session and full pane UUID."""
    return ("tuios", "send-keys", "-s", session, "-w", pane_id, "Enter")


class TuiosTransport:
    """The delivery's pane transport over the TUIOS command line.

    Fix (code review round 1): every call takes the bound its caller grants,
    the remaining budget of the send in progress, and runs on a runner built
    for that bound, so no blocking call outlives its send's deadline.
    """

    def __init__(self, runner_for: Callable[[float], CommandRunner]) -> None:
        """Keep the factory of argument-list runners bounded by a number of seconds."""
        self._runner_for = runner_for

    def observe(self, timeout: float) -> PaneObservation | None:
        """List every live pane and its activity once, or ``None`` when discovery failed."""
        return observe_panes(self._runner_for(timeout))

    def select(self, panes: Sequence[PaneRecord], target: PaneRecord) -> Selection:
        """Return the wildcard selector that reaches only the target among the listed panes."""
        return resolve_selector(panes, target)

    def capture(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Capture the pane's unwrapped lines by session and full UUID."""
        return TuiosDiscovery(self._runner_for(timeout)).capture(pane)

    def ask(self, selector: str, command: str, timeout: float) -> AskOutcome:
        """Type one command through the resolved selector and wait for the pane to settle."""
        return AskOutcome(self._runner_for(timeout).run(ask_arguments(selector, command)).exit_code)

    def enter(self, session: str, pane_id: str, timeout: float) -> bool:
        """Press Enter once in the pane with this full UUID; ``True`` when TUIOS sent it."""
        return self._runner_for(timeout).run(enter_arguments(session, pane_id)).exit_code == 0


__all__ = [
    "ASK_TIMEOUT_MS",
    "STALL_TIMEOUT_MS",
    "AskOutcome",
    "Selection",
    "TuiosTransport",
    "ask_arguments",
    "enter_arguments",
    "resolve_selector",
    "selector_value",
]


# eof
