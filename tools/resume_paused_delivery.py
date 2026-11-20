"""Guarded, deadline-driven pane delivery of the human-launched bulk resume.

Step 6 of v0.14.0 resume-paused executes the Step 5 plan, one safe action at
a time per checkout, while independent checkouts progress concurrently:

1. ``deliver_run`` delivers nothing for a dry run or a run-wide refusal; it
   runs one worker per planned checkout on a thread pool, and at most one
   input operation is active per pane across the run.
2. Each worker takes its checkout's OS guard without waiting (a held guard
   skips the checkout) and holds it across the whole protected sequence:
   the resume action first, then each conditional reviewer through the
   injected ``Takeover`` (Step 7), which may deliver it under the same guard.
   The guard is released on every exit.
3. Immediately before every clear, resume, reviewer command and recovery
   Enter, one fresh observation is taken and the target must pass
   ``target_refusal`` (identity, protections, eligibility), the transport's
   selector must resolve to exactly its full UUID (``PaneTransport.select``
   keeps the TUIOS syntax in the adapter), every injected pre-send check must pass,
   and the pane's pinned delivery profile must be selected again, unchanged.
   A failed check stops that send without input. No profile is pinned yet
   (plan Q05), so every real pane is refused before any input.
4. ``--clear`` clears only the resumed conversation, never a counterpart. A
   Claude clear is skipped as redundant when the agent log shows a clear after
   the pause and no later prompt; the resume is still delivered. Otherwise the
   clear must be confirmed (Claude: a clear event after the send and a ready
   pane; Codex: one more pinned cleared line than before, on an empty input
   box); an unconfirmed clear fails the action and no resume follows.
5. Every send (the clear and the command) has its own fixed 100-second budget,
   recovery included (design Q05=A); the transport's 60-second stall bound
   lies inside it. Acceptance needs the supported profile and Step 1's full
   latest-input proof, plus, for Claude, the command's prompt event in the
   agent log. Observation backs off from half a second to five seconds and
   never passes the deadline. Unproved acceptance at the deadline is an
   unconfirmed failure; nothing is ever retyped.
6. Only Codex may get one recovery Enter per send: the pre-input capture
   must prove the input box empty, then a capture must show exactly this
   send's command as the whole input box, once on screen, with exactly the
   pinned footer below it; the fresh recovery checks run, then a last capture
   must be identical. The deadline is never reset. Any other capture, an edit
   between captures, a failed check or an expired budget withholds it for good.
7. A background-shell line in the pre-input capture is reported only: no
   shell is enumerated, stopped or duplicated.

Fix (code review round 1): the recovery Enter's checks resolve the selector
again from their fresh listing, while the Enter still names the full UUID.
Every blocking transport call of a send is bounded by its remaining budget,
and a proof, capture or check that completes at or after the deadline is
never acted on. The whole input box is read: every line below the input
line must be the pinned footer, so a multiline draft never reads as the
command, and the last ownership capture follows the slow recovery checks. A
Codex clear is confirmed only by one more pinned cleared line than the
pre-clear capture shows, so an old banner with an unrelated screen change
never confirms it.

Fix (code review round 2): each acceptance proof uses a prover built for the
remaining budget, so the Codex prover's nested capture is bounded by it; no
step starts once a slow log read, listing, check or capture spent the budget.
The lines below the input line must be exactly the pinned footer layout, so
a footer-shaped draft line, a repeated footer or a missing one never reads
as an empty or owned input box.

Fix (code review round 3): the prover factory receives the send's
remaining-time callable, so every nested read of a proof is bounded by the
time left when it starts (``tools.resume_paused_budget``), and the injected
checks stop before each check once the budget is spent.

Nothing here writes an artifact, parses arguments or reads a conversation.
"""

from __future__ import annotations

import re
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import StrEnum
from functools import partial
from typing import TYPE_CHECKING, Final, cast

from tools.resume_paused_delivery_checks import TargetContext, target_refusal
from tools.resume_paused_delivery_model import (
    ACTION_BUDGET,
    CALL_BOUND_SECONDS,
    ActionReport,
    CheckoutDelivery,
    ClearOutcome,
    DeliveryOutcome,
    GuardState,
    LogKind,
    Phase,
    Refusal,
    SendStep,
)
from tools.resume_paused_models import timestamp_instant
from tools.resume_paused_plan_model import ActionKind, CheckoutOutcome
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from datetime import datetime

    from tools.resume_paused_delivery_model import (
        DeliveryPorts,
        DeliveryProfile,
        InputScreen,
        PreSendCheck,
    )
    from tools.resume_paused_evidence import PaneObservation
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_plan_model import (
        CheckoutPlan,
        PlannedAction,
        PlanRequest,
        RunPlan,
    )

FIRST_WAIT_SECONDS: Final = 0.5
WAIT_CAP_SECONDS: Final = 5.0
CAPTURE_GAP_SECONDS: Final = 1.0
MAX_WORKERS: Final = 8
_READY_STATES: Final = frozenset({"idle", "done"})

type _Acceptance = Callable[[datetime, datetime, tuple[str, ...]], bool]


class InputLine(StrEnum):
    """Reading of a Codex input box after a send."""

    EMPTY = "empty"
    COMMAND = "command"
    OTHER = "other"


def _pattern(text: str) -> re.Pattern[str] | None:
    """Compile one pinned whole-line signature, ``None`` when empty or invalid."""
    if not text:
        return None
    try:
        return re.compile(text)
    except re.error:
        return None


def _input_box(lines: Sequence[str], screen: InputScreen) -> int | None:
    """Return the index of the input box: the last line opened by the input prefix."""
    indexes = [index for index, line in enumerate(lines) if line.startswith(screen.input_prefix)]
    return indexes[-1] if indexes else None


def _submitted(below: Sequence[str], screen: InputScreen) -> bool:
    """Return whether a working line or a new placeholder follows the input line, or the signature is invalid."""
    working = _pattern(screen.working_pattern)
    return working is None or any(working.fullmatch(line) or screen.placeholder in line for line in below)


def _closed(below: Sequence[str], screen: InputScreen) -> bool:
    """Return whether the lines below the input line are exactly the pinned footer layout, line by line."""
    if len(below) != len(screen.footer_lines):
        return False
    patterns = [_pattern(text) for text in screen.footer_lines]
    return all(pattern is not None and pattern.fullmatch(line) for pattern, line in zip(patterns, below, strict=True))


def read_input(lines: Sequence[str], command: str, screen: InputScreen) -> InputLine:
    """Classify the whole input box: empty, exactly this unsubmitted command shown once, or anything else."""
    index = _input_box(lines, screen)
    if index is None or not _closed(lines[index + 1 :], screen):
        return InputLine.OTHER
    text = lines[index].removeprefix(screen.input_prefix)
    if text == screen.placeholder:
        return InputLine.EMPTY
    if not command or text != command or _submitted(lines[index + 1 :], screen):
        return InputLine.OTHER
    return InputLine.COMMAND if sum(command in line for line in lines) == 1 else InputLine.OTHER


def _banners(pattern: re.Pattern[str], lines: Sequence[str]) -> int:
    """Count the captured lines that are the pinned cleared line."""
    return sum(1 for line in lines if pattern.fullmatch(line))


def cleared(before: Sequence[str], after: Sequence[str], screen: InputScreen) -> bool:
    """Return whether a Codex capture shows one more pinned cleared line than before the clear, on an empty input box."""
    banner = _pattern(screen.cleared_pattern)
    if banner is None or read_input(after, "", screen) is not InputLine.EMPTY:
        return False
    return _banners(banner, after) > _banners(banner, before)


def background_shell(lines: Sequence[str], pattern: str) -> bool:
    """Return whether a capture shows the profile's background-shell line."""
    compiled = _pattern(pattern)
    return compiled is not None and any(compiled.fullmatch(line) for line in lines)


def _empty_input(lines: tuple[str, ...] | None, screen: InputScreen | None) -> tuple[str, ...] | Refusal:
    """Return the pre-input Codex capture when its input box shows only the placeholder, or why not."""
    if screen is None:
        return Refusal("screen-unsupported", failed=True)
    if lines is None:
        return Refusal("capture-failed", failed=True)
    index = _input_box(lines, screen)
    if index is None:
        return Refusal("screen-unsupported", failed=True)
    if lines[index].removeprefix(screen.input_prefix) != screen.placeholder:
        return Refusal("pane-draft")
    return lines if _closed(lines[index + 1 :], screen) else Refusal("screen-unsupported", failed=True)


class _PaneSlots:
    """At most one input operation active per pane across the run's workers."""

    def __init__(self) -> None:
        """Start with no pane in use."""
        self._lock = threading.Lock()
        self._busy: set[str] = set()

    def claim(self, pane_id: str) -> bool:
        """Reserve the pane, or return ``False`` when another operation holds it."""
        with self._lock:
            if pane_id in self._busy:
                return False
            self._busy.add(pane_id)
            return True

    def release(self, pane_id: str) -> None:
        """Free the pane."""
        with self._lock:
            self._busy.discard(pane_id)


@dataclass(frozen=True)
class _Prepared:
    """A send that passed every fresh check: the fresh target, its selector and its profile."""

    pane: PaneRecord
    selector: str
    profile: DeliveryProfile


class _Recovery:
    """The single Codex recovery Enter of one send, permitted only by proved ownership and non-submission."""

    def __init__(self, delivery: _ActionDelivery, prepared: _Prepared, phase: Phase, deadline: datetime) -> None:
        """Bind the send whose unsubmitted command may get one Enter before the deadline."""
        self._delivery = delivery
        self._prepared = prepared
        self._phase = phase
        self._deadline = deadline
        self._screen = cast("InputScreen", prepared.profile.screen)
        self._done = False

    def _withhold(self, reason: str) -> None:
        """Forbid the Enter for the rest of this send and note why."""
        self._done = True
        self._delivery.notes.append(f"{self._phase.value}-recovery-withheld-{reason}")

    def attempt(self, command: str) -> None:
        """Send the Enter once when two identical captures prove this send's command unsubmitted."""
        if self._done:
            return
        first = self._delivery.ports.transport.capture(self._prepared.pane, self._delivery.bound(self._deadline))
        if self._remaining() <= 0:
            return
        reading = InputLine.OTHER if first is None else read_input(first, command, self._screen)
        if reading is InputLine.OTHER:
            self._withhold("capture")
        elif reading is InputLine.COMMAND:
            self._confirm(cast("tuple[str, ...]", first))

    def _confirm(self, first: tuple[str, ...]) -> None:
        """Run the fresh recovery checks, then require a last identical capture before pressing Enter once."""
        ports, pane = self._delivery.ports, self._prepared.pane
        ports.sleeper.sleep(min(CAPTURE_GAP_SECONDS, self._remaining()))
        if self._remaining() <= 0:
            return
        refusal = self._delivery.prepare(Phase.RECOVERY, self._deadline)
        if isinstance(refusal, Refusal):
            self._withhold(refusal.reason)
            return
        if self._remaining() <= 0:
            return
        if ports.transport.capture(pane, self._delivery.bound(self._deadline)) != first:
            self._withhold("changed")
            return
        if self._remaining() <= 0:
            return
        self._done = True
        self._delivery.recovery.append(self._phase)
        if not ports.transport.enter(pane.session, pane.pane_id, self._remaining()):
            self._delivery.notes.append(f"{self._phase.value}-recovery-enter-refused")

    def _remaining(self) -> float:
        """Return the seconds left in this send's budget."""
        return self._delivery.remaining(self._deadline)


class _ActionDelivery:
    """Deliver one planned action under the held guard: its optional clear, then its command."""

    def __init__(self, worker: _CheckoutWorker, action: PlannedAction, checks: tuple[PreSendCheck, ...]) -> None:
        """Bind the action to its checkout worker, with the run's and the caller's extra checks."""
        self.ports = worker.ports
        self._worker = worker
        self._action = action
        self._checks = worker.ports.checks + checks
        self._profile: DeliveryProfile | None = None
        self.recovery: list[Phase] = []
        self.notes: list[str] = []

    def run(self, phase: Phase) -> ActionReport:
        """Clear when requested and confirmed, then send the command and prove its acceptance."""
        clear = ClearOutcome.NONE
        if self._action.clear and self._action.kind is ActionKind.RESUME:
            cleared_outcome = self._clear()
            if isinstance(cleared_outcome, ActionReport):
                return cleared_outcome
            clear = cleared_outcome
        prepared = self.prepare(phase)
        if isinstance(prepared, Refusal):
            return self._report(DeliveryOutcome.REFUSED, prepared, clear)
        command = cast("str", self._action.command)
        sent = self._send(prepared, phase, command, self._accepted(prepared, command))
        if isinstance(sent, Refusal):
            return self._report(DeliveryOutcome.REFUSED, sent, clear)
        if sent is DeliveryOutcome.ACCEPTED:
            return self._report(sent, None, clear)
        return self._report(sent, Refusal("acceptance-unproved", failed=True), clear)

    def remaining(self, deadline: datetime) -> float:
        """Return the seconds left before a send's deadline."""
        return (deadline - self.ports.clock.now()).total_seconds()

    def bound(self, deadline: datetime | None) -> float:
        """Return the seconds one blocking call may take: the send's remaining budget, at most the call bound."""
        return CALL_BOUND_SECONDS if deadline is None else max(0.0, min(CALL_BOUND_SECONDS, self.remaining(deadline)))

    def expired(self, deadline: datetime | None) -> bool:
        """Return whether a send's budget is spent, so no further step may start."""
        return deadline is not None and self.remaining(deadline) <= 0

    def prepare(self, phase: Phase, deadline: datetime | None = None) -> _Prepared | Refusal:
        """Run every fresh check of one imminent send from one new observation, the selector included.

        Within a send, a listing or a check that spends the budget stops the
        preparation before the next step (code review round 2).
        """
        observation = self.ports.transport.observe(self.bound(deadline))
        if observation is None:
            return Refusal("discovery-failed", failed=True)
        target = self._expiry(deadline) or target_refusal(phase, self._action, observation, self._worker.context)
        if isinstance(target, Refusal):
            return target
        selected = self._selected(phase, observation, target, deadline)
        return selected if isinstance(selected, Refusal) else self._profiled(target, selected)

    def _expiry(self, deadline: datetime | None) -> Refusal | None:
        """Return the refusal of a step that would start after the send's deadline."""
        return Refusal("deadline-passed") if self.expired(deadline) else None

    def _selected(self, phase: Phase, observation: PaneObservation, target: PaneRecord, deadline: datetime | None) -> str | Refusal:
        """Resolve the target's selector and run every injected check; budget must remain afterwards."""
        selection = self.ports.transport.select(observation.panes, target)
        if selection.selector is None:
            return Refusal(selection.reason, failed=True)
        step = SendStep(phase, self._worker.context.root, self._action, observation, target)
        for check in self._checks:
            refusal = self._expiry(deadline) or check.check(step)
            if refusal is not None:
                return refusal
        return self._expiry(deadline) or selection.selector

    def _profiled(self, pane: PaneRecord, selector: str) -> _Prepared | Refusal:
        """Select the pane's pinned profile again; it must not change within the action."""
        profile = self.ports.profiles.profile(pane)
        if profile is None or profile.host is not self._action.host:
            return Refusal("host-profile-unsupported", failed=True)
        if self._profile is not None and profile != self._profile:
            return Refusal("profile-changed", failed=True)
        if profile.host not in self.ports.provers:
            return Refusal("input-proof-unavailable", failed=True)
        self._profile = profile
        return _Prepared(pane, selector, profile)

    def _clear(self) -> ClearOutcome | ActionReport:
        """Clear the resumed conversation, or skip a redundant Claude clear; a failure ends the action."""
        prepared = self.prepare(Phase.CLEAR)
        if isinstance(prepared, Refusal):
            return self._report(DeliveryOutcome.REFUSED, prepared, ClearOutcome.NONE)
        if prepared.profile.host is Host.CLAUDE and self._redundant(prepared.pane):
            return ClearOutcome.REDUNDANT
        sent = self._send(prepared, Phase.CLEAR, prepared.profile.clear_command, self._cleared(prepared))
        if isinstance(sent, Refusal):
            return self._report(DeliveryOutcome.REFUSED, sent, ClearOutcome.NONE)
        if sent is DeliveryOutcome.ACCEPTED:
            return ClearOutcome.CONFIRMED
        return self._report(sent, Refusal("clear-unconfirmed", failed=True), ClearOutcome.UNCONFIRMED)

    def _redundant(self, pane: PaneRecord) -> bool:
        """Return whether the log shows a clear after the pause with no later prompt."""
        events, paused = self.ports.log.events(pane), self._worker.paused
        if events is None or paused is None:
            return False
        clears = [index for index, event in enumerate(events) if event.kind is LogKind.CLEAR and event.at > paused]
        return bool(clears) and not any(event.kind is LogKind.PROMPT for event in events[clears[-1] + 1 :])

    def _send(self, prepared: _Prepared, phase: Phase, text: str, accepted: _Acceptance) -> DeliveryOutcome | Refusal:
        """Type one text and observe its acceptance within this send's own budget."""
        before = self._pre_input(prepared)
        if isinstance(before, Refusal):
            return before
        started = self.ports.clock.now()
        deadline = started + ACTION_BUDGET
        asked = self.ports.transport.ask(prepared.selector, text, self.remaining(deadline))
        if asked.exit_code:
            self.notes.append(f"{phase.value}-ask-exit-{asked.exit_code}")
        recovery = _Recovery(self, prepared, phase, deadline) if prepared.profile.host is Host.CODEX else None
        wait = FIRST_WAIT_SECONDS
        while self.remaining(deadline) > 0:
            proved = accepted(started, deadline, before)
            if self.remaining(deadline) <= 0:
                break
            if proved:
                return DeliveryOutcome.ACCEPTED
            if recovery is not None:
                recovery.attempt(text)
            remaining = self.remaining(deadline)
            if remaining > 0:
                self.ports.sleeper.sleep(min(wait, remaining))
                wait = min(wait * 2, WAIT_CAP_SECONDS)
        return DeliveryOutcome.UNCONFIRMED

    def _pre_input(self, prepared: _Prepared) -> tuple[str, ...] | Refusal:
        """Capture the pane before typing: report background shells, require a readable log or an empty Codex input box."""
        pane, profile = prepared.pane, prepared.profile
        lines = self.ports.transport.capture(pane, CALL_BOUND_SECONDS)
        if lines is not None and background_shell(lines, profile.background_pattern):
            self._note("background-shell")
        if profile.host is not Host.CLAUDE:
            return _empty_input(lines, profile.screen)
        if self.ports.log.events(pane) is None:
            return Refusal("agent-log-unreadable", failed=True)
        return lines or ()

    def _note(self, note: str) -> None:
        """Record one report-only note once."""
        if note not in self.notes:
            self.notes.append(note)

    def _accepted(self, prepared: _Prepared, command: str) -> _Acceptance:
        """Return the command's acceptance proof: Step 1's full latest-input proof, and the Claude prompt event.

        The prover is built with the send's remaining-time callable, so each of
        its nested reads is bounded by the time left when it starts (code
        review round 3), and it never starts once a slow log read spent the
        budget.
        """
        pane, factory = prepared.pane, self.ports.provers[prepared.profile.host]
        claude = prepared.profile.host is Host.CLAUDE

        def accepted(started: datetime, deadline: datetime, before: tuple[str, ...]) -> bool:
            del before
            if claude and not self._logged(pane, LogKind.PROMPT, started, command):
                return False
            if self.expired(deadline):
                return False
            return factory(partial(self.remaining, deadline)).prove(pane, command, started, None).proved

        return accepted

    def _cleared(self, prepared: _Prepared) -> _Acceptance:
        """Return the clear's confirmation: Claude clear event and readiness, or the Codex cleared screen."""
        pane, screen = prepared.pane, prepared.profile.screen

        def claude(started: datetime, deadline: datetime, before: tuple[str, ...]) -> bool:
            del before
            return self._logged(pane, LogKind.CLEAR, started) and not self.expired(deadline) and self._ready(pane, deadline)

        def codex(started: datetime, deadline: datetime, before: tuple[str, ...]) -> bool:
            del started
            after = self.ports.transport.capture(pane, self.bound(deadline))
            return after is not None and cleared(before, after, cast("InputScreen", screen))

        return claude if prepared.profile.host is Host.CLAUDE else codex

    def _logged(self, pane: PaneRecord, kind: LogKind, since: datetime, text: str | None = None) -> bool:
        """Return whether the agent log holds such an event since the send."""
        events = self.ports.log.events(pane) or ()
        return any(event.kind is kind and event.at >= since and (text is None or event.text == text) for event in events)

    def _ready(self, pane: PaneRecord, deadline: datetime) -> bool:
        """Return whether a fresh listing shows the pane at rest and ready."""
        observation = self.ports.transport.observe(self.bound(deadline))
        activity = None if observation is None else observation.activity.get(pane.pane_id)
        return activity is not None and activity.state in _READY_STATES and activity.ready is True and not activity.blocked

    def _report(self, outcome: DeliveryOutcome, refusal: Refusal | None, clear: ClearOutcome) -> ActionReport:
        """Return the action's report with its recovery use and notes."""
        reason, failed = ("", False) if refusal is None else (refusal.reason, refusal.failed)
        return ActionReport(self._action, outcome, reason, failed, clear, tuple(self.recovery), tuple(self.notes))


class _CheckoutWorker:
    """Deliver one planned checkout's actions in order under its held guard."""

    def __init__(self, ports: DeliveryPorts, request: PlanRequest, plan: CheckoutPlan, slots: _PaneSlots) -> None:
        """Bind the run's ports and pane slots to one planned checkout."""
        self.ports = ports
        self.context = TargetContext.of(plan.root, request, ports.probe)
        self.paused = timestamp_instant(plan.paused_at) if plan.paused_at else None
        self._plan = plan
        self._slots = slots

    def run(self) -> CheckoutDelivery:
        """Take the checkout's guard without waiting and run the protected sequence while holding it."""
        with self.ports.guard.acquire(self._plan.root) as lease:
            if lease.state is not GuardState.ACQUIRED:
                return CheckoutDelivery(self._plan.root, lease.state)
            return CheckoutDelivery(self._plan.root, lease.state, self._sequence())

    def _sequence(self) -> tuple[ActionReport, ...]:
        """Resume first; each conditional reviewer goes to the takeover only after an accepted resume."""
        reports: list[ActionReport] = []
        resumed: ActionReport | None = None
        for action in self._plan.actions:
            if action.command is None:
                reports.append(ActionReport(action, DeliveryOutcome.REFUSED, action.skip.value if action.skip else "not-planned"))
            elif not action.conditional:
                resumed = self.deliver(action, Phase.RESUME)
                reports.append(resumed)
            elif resumed is not None and resumed.outcome is not DeliveryOutcome.ACCEPTED:
                reports.append(ActionReport(action, DeliveryOutcome.REFUSED, "requestor-not-accepted"))
            else:
                reports.append(self.ports.takeover.reviewer(self, resumed, action))
        return tuple(reports)

    def deliver(self, action: PlannedAction, phase: Phase, checks: tuple[PreSendCheck, ...] = ()) -> ActionReport:
        """Deliver one planned action while no other operation holds its pane."""
        if not self._slots.claim(action.pane_id):
            return ActionReport(action, DeliveryOutcome.REFUSED, "pane-in-use", failed=True)
        try:
            return _ActionDelivery(self, action, checks).run(phase)
        finally:
            self._slots.release(action.pane_id)


def deliver_run(plan: RunPlan, request: PlanRequest, ports: DeliveryPorts) -> tuple[CheckoutDelivery, ...]:
    """Deliver every planned checkout concurrently; a dry run or a run-wide refusal delivers nothing."""
    if not plan.input_allowed:
        return ()
    planned = [checkout for checkout in plan.checkouts if checkout.outcome is CheckoutOutcome.PLANNED and checkout.actions]
    if not planned:
        return ()
    slots = _PaneSlots()
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(planned)), thread_name_prefix="resume-paused") as pool:
        futures = [pool.submit(_CheckoutWorker(ports, request, checkout, slots).run) for checkout in planned]
        return tuple(future.result() for future in futures)


__all__ = [
    "CAPTURE_GAP_SECONDS",
    "FIRST_WAIT_SECONDS",
    "MAX_WORKERS",
    "WAIT_CAP_SECONDS",
    "InputLine",
    "background_shell",
    "cleared",
    "deliver_run",
    "read_input",
]


# eof
