"""Shell-free TUIOS transport of the human-launched bulk resume.

Production captures physical ANSI rows and confirms the live selector through
`list-agents --select ... --json`. Each ask uses the daemon's token for the
one expected, ready pane. The selector encodes spaces as wildcards, so both
the initial listing and the daemon's latest selection must be unambiguous.
The command follows `--` as one argument. A recovery Enter addresses the
TUIOS session and full pane UUID directly. The transport exit code is
diagnostic. Shared receipts and marked claims establish acceptance.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.resume_paused_evidence import observe_panes, parse_activity
from tools.resume_paused_input import TuiosDiscovery, parse_agents
from tools.resume_paused_models import ArtifactError
from tools.resume_paused_profiles import as_mapping, loads_strict

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
    refusal: str = ""


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

    def __init__(self, runner_for: Callable[[float], CommandRunner], *, physical: bool = False) -> None:
        """Keep the factory of argument-list runners bounded by a number of seconds."""
        self._runner_for = runner_for
        self._physical = physical

    def observe(self, timeout: float) -> PaneObservation | None:
        """List every live pane and its activity once, or ``None`` when discovery failed."""
        return observe_panes(self._runner_for(timeout))

    def select(self, panes: Sequence[PaneRecord], target: PaneRecord) -> Selection:
        """Return the wildcard selector that reaches only the target among the listed panes."""
        return resolve_selector(panes, target)

    def capture(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Capture the physical or unwrapped rows requested by this transport."""
        runner = self._runner_for(timeout)
        if self._physical:
            result = runner.run(("tuios", "capture-pane", "-s", pane.session, "-w", pane.pane_id, "--ansi", "--trim"))
            return tuple(result.stdout.splitlines()) if result.exit_code == 0 else None
        return TuiosDiscovery(runner).capture(pane)

    def _confirm(self, selector: str, pane_id: str, timeout: float) -> str | None:
        """Bind the selector to exactly the intended UUID using the daemon's confirmation token."""
        result = self._runner_for(timeout).run(("tuios", "list-agents", "--select", selector, "--json"))
        if result.exit_code:
            return None
        try:
            panes = parse_agents(result.stdout)
            activity = parse_activity(result.stdout).get(pane_id)
            token = as_mapping(loads_strict(result.stdout)).get("confirm")
        except (ArtifactError, ValueError, RecursionError):
            return None
        if not activity or not activity.resting:
            return None
        if len(panes) == 1 and panes[0].pane_id == pane_id and isinstance(token, str) and token:
            return token
        return None

    def ask(self, selector: str, command: str, timeout: float, pane_id: str = "") -> AskOutcome:
        """Type one command through the resolved selector and wait for the pane to settle."""
        args = ask_arguments(selector, command)
        if self._physical:
            confirm = self._confirm(selector, pane_id, min(5.0, timeout))
            if confirm is None:
                return AskOutcome(1, "selector-confirmation-unavailable")
            timeout = min(timeout, 65.0)
            args = (
                "tuios", "ask-agent", "--select", selector, "--confirm", confirm, "--ready-timeout", "1",
                "--stall-timeout", str(STALL_TIMEOUT_MS), "--timeout", "60000", "--lines", "1", "--json", "--", command,
            )
        return AskOutcome(self._runner_for(timeout).run(args).exit_code)

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
