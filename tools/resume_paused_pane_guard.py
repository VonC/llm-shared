"""Design Q27=B all-pane idle guard of a Claude reviewer activation.

Step 7 of v0.15.0 resume-paused. Claude 2.1.325 runs a local shell command
before it records the command's input, so a running local command can sit
behind a transcript that looks closed. Before every Claude reviewer send,
initial activation or later continuation, ``AllPaneIdleGuard`` therefore
requires fresh validated idle evidence from every live Claude pane that TUIOS
lists for the checkout, the proved requestor and the target reviewer
included; the Q23=A binding and the Q24=A requestor exception grant no pane
an exemption.

It is a ``PreSendCheck`` passed to ``PairDelivery.deliver``, so Step 6 runs
it under the held checkout guard on the fresh listing taken immediately
before the send: a pane whose state changed since an earlier check stops the
send without input. A pane belongs to the checkout when its recorded working
directory is the checkout or lies inside it; a Claude pane whose directory
cannot be read cannot be excluded and keeps activation pending.

Each pane must rest in TUIOS (idle or done, ready, no question, no draft) and
its fresh capture must show the recognized Claude empty editor through
``ClaudeScreens``. A
busy, unreadable or unknown-layout pane keeps activation pending. The guard
has its own fixed budget: each capture is bounded by the time left in it, and
none starts, nor is a capture acted on, once it is spent.
Other phases and Codex reviewers pass unchanged; reporting the fifth limit in
``limits=claude-wait-scope`` never replaces this guard.

Fix (Step 7 code review round 1): a question a pane reports is refused on its
own (``claude-pane-question``), whatever its blocking reason and state; the
budget is checked again after each screen reading, so a reading of the last
pane that spends it never authorizes the send; and the checkout's panes keep
their discovery order, one linear scan per refresh with no sort.

Fix (Step 7 code review round 2): the time left is sampled once, immediately
before each capture, and that same positive value bounds the capture, so a
budget spent between the pane's TUIOS check and its capture starts no capture
with a nonpositive timeout.
"""

from __future__ import annotations

from datetime import timedelta
from enum import StrEnum
from typing import TYPE_CHECKING, Final, Protocol

from tools.resume_paused_delivery_model import CALL_BOUND_SECONDS, Phase, Refusal
from tools.resume_paused_input import pane_host
from tools.resume_paused_models import ArtifactError, CanonicalRoot
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from datetime import datetime

    from tools.resume_paused_delivery_model import SendStep
    from tools.resume_paused_evidence import PaneActivity, PaneObservation
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_profiles import Clock

GUARD_BUDGET: Final = timedelta(seconds=CALL_BOUND_SECONDS)
_IDLE_STATES: Final = frozenset({"idle", "done"})
_DEADLINE: Final = Refusal("idle-guard-deadline")


class ClaudeScreen(StrEnum):
    """One Claude pane capture's reading under the pinned screen profile."""

    IDLE = "idle"
    BUSY = "busy"
    UNKNOWN = "unknown"


class ClaudeScreens(Protocol):
    """Injected pinned Claude screen profile: reads one capture of one pane."""

    def read(self, pane: PaneRecord, lines: tuple[str, ...]) -> ClaudeScreen:
        """Return the capture's reading; ``UNKNOWN`` for any layout the pinned profile does not rebuild."""
        ...


class UnpinnedClaudeScreens:
    """``ClaudeScreens`` while no Claude screen profile is pinned: every capture is unknown."""

    def read(self, pane: PaneRecord, lines: tuple[str, ...]) -> ClaudeScreen:
        """Read the capture as unknown."""
        del pane, lines
        return ClaudeScreen.UNKNOWN


class PaneCapture(Protocol):
    """The capture call of the pane transport."""

    def capture(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Capture the pane's unwrapped lines, or ``None`` on failure."""
        ...


def _inside(pane_root: CanonicalRoot, root: CanonicalRoot) -> bool:
    """Return whether a pane directory is the checkout or lies inside it, by Windows rules."""
    return pane_root == root or pane_root.key.startswith(root.key.rstrip("\\") + "\\")


def _member(pane: PaneRecord, root: CanonicalRoot) -> bool | Refusal:
    """Return whether the pane is a Claude pane of the checkout, or why that cannot be decided."""
    try:
        inside: bool | None = _inside(CanonicalRoot.parse(pane.cwd, "pane checkout"), root)
    except ArtifactError:
        inside = None
    if inside is False:
        return False
    try:
        claude = pane_host(pane) is Host.CLAUDE
    except ArtifactError:
        return Refusal("pane-host-contradictory", failed=True)
    if not claude:
        return False
    return True if inside else Refusal("claude-pane-checkout-unknown")


def checkout_claude_panes(observation: PaneObservation, root: CanonicalRoot) -> tuple[PaneRecord, ...] | Refusal:
    """Return every live Claude pane of the checkout in discovery order, from one linear scan, or why one cannot be classified."""
    panes: list[PaneRecord] = []
    for pane in observation.panes:
        member = _member(pane, root)
        if isinstance(member, Refusal):
            return member
        if member:
            panes.append(pane)
    return tuple(panes)


def _resting(activity: PaneActivity | None) -> Refusal | None:
    """Require one Claude pane to rest in TUIOS: idle or done, ready, no question and no draft."""
    if activity is None:
        return Refusal("claude-pane-state-unknown")
    if activity.blocked:
        return Refusal("claude-pane-blocked")
    if activity.question:
        return Refusal("claude-pane-question")
    if activity.draft_held:
        return Refusal("claude-pane-draft")
    if activity.state not in _IDLE_STATES or activity.ready is not True:
        return Refusal("claude-pane-busy")
    return None


class AllPaneIdleGuard:
    """``PreSendCheck`` of every Claude reviewer send: all live Claude panes of the checkout read idle now."""

    def __init__(self, capture: PaneCapture, screens: ClaudeScreens, clock: Clock) -> None:
        """Keep the pane capture, the pinned Claude screen profile and the clock of the guard's budget."""
        self._capture = capture
        self._screens = screens
        self._clock = clock

    def check(self, step: SendStep) -> Refusal | None:
        """Refuse a Claude reviewer send unless every live Claude pane of the checkout reads idle."""
        if step.phase is not Phase.REVIEWER or step.action.host is not Host.CLAUDE:
            return None
        panes = checkout_claude_panes(step.observation, step.root)
        if isinstance(panes, Refusal):
            return panes
        deadline = self._clock.now() + GUARD_BUDGET
        for pane in panes:
            refusal = _resting(step.observation.activity.get(pane.pane_id)) or self._screen(pane, deadline)
            if refusal is not None:
                return refusal
        return None

    def _left(self, deadline: datetime) -> float:
        """Return the seconds left in the guard's budget."""
        return (deadline - self._clock.now()).total_seconds()

    def _screen(self, pane: PaneRecord, deadline: datetime) -> Refusal | None:
        """Capture one pane within the budget left and require the pinned idle reading, completed within it too.

        The time left is sampled once, immediately before the capture: a spent
        budget starts no capture, and the capture receives that same positive
        value, capped at the call bound. The budget is checked again after the
        capture and after the screen reading.
        """
        left = self._left(deadline)
        if left <= 0:
            return _DEADLINE
        lines = self._capture.capture(pane, min(CALL_BOUND_SECONDS, left))
        if self._left(deadline) <= 0:
            return _DEADLINE
        if lines is None:
            return Refusal("claude-pane-unreadable")
        reading = self._screens.read(pane, lines)
        if self._left(deadline) <= 0:
            return _DEADLINE
        if reading is ClaudeScreen.IDLE:
            return None
        return Refusal("claude-pane-busy" if reading is ClaudeScreen.BUSY else "claude-pane-unknown-layout")


__all__ = [
    "GUARD_BUDGET",
    "AllPaneIdleGuard",
    "ClaudeScreen",
    "ClaudeScreens",
    "PaneCapture",
    "UnpinnedClaudeScreens",
    "checkout_claude_panes",
]


# eof
