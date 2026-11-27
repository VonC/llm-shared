"""Reviewer-wait classification before a counterpart activation of the bulk resume.

Step 7 of v0.15.0 resume-paused decides, read-only and from fresh evidence,
whether a missing reviewer may receive its marked ``review-resume``:

- ``reviewer_active``: the exact active-reviewer leave-alone check, applied
  before any takeover proof. The exchange's current claim generation is owned
  by the reviewer, and the reviewer pane agrees: the current marked claim
  names it, or, without a marked claim, its latest typed command (histories
  list commands oldest first) is a ``review-resume`` selecting the reviewer.
- ``prior_delivery``: a marked reviewer ``review-resume`` already typed into
  the reviewer pane since the receipt, or undated, is an uncertain earlier
  delivery; it is diagnosed and never resent.
- ``ReviewerWait``: positive no-wait evidence (design Q16, Q17). The pane must
  be idle and ready with no draft or question. A Codex reviewer needs a fresh
  supported idle, empty-input capture: an active turn, such as an attached
  global wait, already reads as busy. A Claude reviewer needs the injected
  lifecycle ledger to prove absence (``WaitAbsence``) over a ``WaitScope`` that
  binds the proved requestor's pane and rebuilt marked input (the Q23=A file
  binding and the Q24=A requestor-operation exception) on initial activation
  and later continuation alike. No channel proves current Claude watcher
  liveness, so every potential Claude wait, an unavailable ledger included,
  stays pending. ``UnprovedAbsence`` answers while no Claude ledger profile is
  pinned (plan Q05).

Every refusal is an expected pending skip: no input is sent, nothing fails.
The ledger's counted reasons become ``ledger-<code>`` notes; no conversation
content is read here.

Fix (Step 7 code review round 1): a question the pane reports is refused on
its own (``reviewer-question``), even when TUIOS names no blocking reason and
the pane reads idle and ready.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Protocol

from tools.resume_paused_claude_ledger import Absence
from tools.resume_paused_delivery_model import Refusal
from tools.resume_paused_evidence import CommandKind, ScreenVerdict, classify_command
from tools.resume_paused_marker import MARKER_FLAG, marker_in_command
from tools.resume_paused_models import ArtifactError, SessionRole
from tools.resume_paused_profiles import Host
from tools.review_exchange_models import Actor

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from datetime import datetime

    from tools.resume_paused_claude_ledger import LedgerDecision
    from tools.resume_paused_evidence import (
        CommandHistory,
        ObservedCommand,
        PaneActivity,
        ScreenProbe,
    )
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_models import CanonicalRoot
    from tools.resume_paused_review import ExchangeSnapshot

_IDLE_STATES: Final = frozenset({"idle", "done"})


@dataclass(frozen=True)
class WaitScope:
    """What one reviewer-wait decision covers: the checkout, the reviewer, the receipt time and the requestor's binding.

    ``since`` is the receipt's ``Used at`` instant: an earlier marked
    reviewer entry belongs to an older pause. ``requestor`` is the proved
    requestor's live pane when it runs Claude and ``marked_input`` its complete
    marked resume command, rebuilt from the receipt, so the ledger binds its
    Q23 file and applies the Q24 exception.
    """

    root: CanonicalRoot
    reviewer: PaneRecord
    since: datetime
    requestor: PaneRecord | None = None
    marked_input: str | None = None


class WaitAbsence(Protocol):
    """Injected Claude lifecycle-ledger decision over one wait scope."""

    def decide(self, scope: WaitScope) -> LedgerDecision | None:
        """Return the ledger's absence decision, ``None`` when no pinned ledger applies."""
        ...


class UnprovedAbsence:
    """``WaitAbsence`` while no Claude ledger profile is pinned: absence is never proved."""

    def decide(self, scope: WaitScope) -> LedgerDecision | None:
        """Report no decision."""
        del scope


@dataclass(frozen=True)
class WaitVerdict:
    """Whether the reviewer may be activated now; the refusal is ``None`` when it may, with report-only notes."""

    refusal: Refusal | None
    notes: tuple[str, ...] = ()


def _reviewer_entry(command: ObservedCommand) -> bool:
    """Return whether a typed command is a ``review-resume`` that certainly selects the reviewer."""
    classified = classify_command(command.text)
    return (
        classified is not None and classified.kind is CommandKind.REVIEW_RESUME
        and classified.role is SessionRole.REVIEWER and not classified.uncertain
    )


def reviewer_active(exchange: ExchangeSnapshot, reviewer: PaneRecord, commands: Sequence[ObservedCommand] | None) -> bool:
    """Return whether the reviewer already serves the exact exchange, by protocol and pane evidence together."""
    generation, claim = exchange.ownership_generation, exchange.marked_claim
    if exchange.owner is not Actor.REVIEWER or generation is None:
        return False
    if claim is not None and claim.issued_generation == generation:
        return claim.evidence.pane_id == reviewer.pane_id
    return bool(commands) and _reviewer_entry(commands[-1])


def prior_delivery(commands: Sequence[ObservedCommand], reviewer: PaneRecord, since: datetime) -> bool:
    """Return whether a marked reviewer entry reached this pane since the receipt, or at an unknown time.

    A marked ``review-resume`` whose marker does not parse is uncertain too.
    """
    for command in commands:
        classified = classify_command(command.text)
        if classified is None or classified.kind is not CommandKind.REVIEW_RESUME or MARKER_FLAG not in command.text.split():
            continue
        try:
            marker = marker_in_command(command.text)
        except ArtifactError:
            return True
        dated = command.at is None or command.at >= since
        if marker.role is SessionRole.REVIEWER and marker.pane_id == reviewer.pane_id and dated:
            return True
    return False


def _resting(activity: PaneActivity | None) -> Refusal | None:
    """Require the reviewer pane idle and ready, with no draft or question."""
    if activity is None:
        return Refusal("reviewer-state-unknown")
    if activity.blocked:
        return Refusal("reviewer-blocked")
    if activity.question:
        return Refusal("reviewer-question")
    if activity.draft_held:
        return Refusal("reviewer-draft")
    if activity.state not in _IDLE_STATES or activity.ready is not True:
        return Refusal("reviewer-busy")
    return None


@dataclass(frozen=True)
class ReviewerWait:
    """Positive no-wait evidence for one reviewer pane: its history, its Codex screen and the Claude ledger."""

    history: CommandHistory
    probe: ScreenProbe
    absence: WaitAbsence
    live_wait: Callable[[CanonicalRoot], str] | None = None

    def commands(self, reviewer: PaneRecord) -> tuple[ObservedCommand, ...] | None:
        """Return the reviewer pane's typed commands, oldest first, ``None`` when unreadable."""
        return self.history.commands(reviewer)

    def verdict(self, scope: WaitScope, host: Host, activity: PaneActivity | None, commands: Sequence[ObservedCommand] | None) -> WaitVerdict:
        """Permit activation only on a resting pane, no uncertain earlier delivery and proved absence of any wait.

        ``commands`` is the reviewer history read once for this decision, so
        the leave-alone check and this verdict judge the same evidence.
        """
        resting = _resting(activity)
        if resting is not None:
            return WaitVerdict(resting)
        if commands is None:
            return WaitVerdict(Refusal("reviewer-history-unreadable"))
        if prior_delivery(commands, scope.reviewer, scope.since):
            return WaitVerdict(Refusal("reviewer-delivery-uncertain"))
        if self.live_wait:
            reason = self.live_wait(scope.root)
            if not reason and self.probe.probe(scope.reviewer) is not ScreenVerdict.IDLE_EMPTY:
                reason = "reviewer-editor-unproved"
            return WaitVerdict(Refusal(reason) if reason else None)
        return self._codex(scope.reviewer) if host is Host.CODEX else self._claude(scope)

    def _codex(self, reviewer: PaneRecord) -> WaitVerdict:
        """Require a fresh supported idle, empty-input capture with no active turn."""
        verdict = self.probe.probe(reviewer)
        if verdict is ScreenVerdict.IDLE_EMPTY:
            return WaitVerdict(None)
        return WaitVerdict(Refusal("codex-wait-unproved"), (f"screen-{verdict.value}",))

    def _claude(self, scope: WaitScope) -> WaitVerdict:
        """Require the lifecycle ledger to prove that no host-managed waiting work remains."""
        decision = self.absence.decide(scope)
        if decision is None:
            return WaitVerdict(Refusal("claude-ledger-unavailable"))
        if decision.absence is Absence.PROVED:
            return WaitVerdict(None)
        return WaitVerdict(Refusal("claude-wait-unproved"), tuple(f"ledger-{reason.code}" for reason in decision.reasons))


__all__ = [
    "ReviewerWait",
    "UnprovedAbsence",
    "WaitAbsence",
    "WaitScope",
    "WaitVerdict",
    "prior_delivery",
    "reviewer_active",
]


# eof
