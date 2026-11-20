"""Example tests of Codex delivery, its single recovery Enter and the screen readings.

Step 6 of v0.14.0 resume-paused: a Codex send needs a pre-input capture
proving the input box empty. When the command is not accepted, one Enter may
follow only after two identical captures show exactly this send's command
unsubmitted, the fresh recovery checks pass and budget remains; an edit, a
working or placeholder line, a repeated command, a failed capture or check,
a changed profile or an expired budget withholds it, and it is never
repeated. The Codex clear is confirmed on screen. All time is a fake clock.

Code review round 1 adds: a selector collision appearing before the Enter, a
proof or capture completing after the deadline, the bounds granted to every
transport call, a multiline draft and an unrecognized line below the input
box, an edit during the recovery checks (the last ownership capture follows
them), and an old cleared banner with only an unrelated line changing.

Code review round 2 adds: a repeated or missing footer line, the concrete
Codex prover whose nested capture gets only the last half second of the
budget, and a recovery check that spends the budget before the last capture.

Code review round 3 adds: the concrete Codex prover composed from the
budget-bounded readers, whose version read leaves its capture only the time
still available or none, and two ordered recovery checks where the first
spends the budget and the second is never asked.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.resume_paused_test_support import FakeSessionStore
from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    CODEX_PANE,
    CODEX_PROFILE,
    EMPTY,
    FOOTER,
    HUMAN,
    IDLE,
    PLACEHOLDER,
    PROMPT,
    SCREEN,
    SESSION,
    T0,
    WEB,
    WEB_PANE,
    World,
    action,
    checkout,
    observation,
    record,
    submitted,
    typed,
)
from tests.unit.tools.test_resume_paused_input.test_resume_paused_input_tdd import (
    FakeVersions,
)
from tools.resume_paused_budget import (
    BoundedCapture,
    BoundedSessionStore,
    BoundedVersions,
)
from tools.resume_paused_delivery import (
    InputLine,
    background_shell,
    cleared,
    deliver_run,
    read_input,
)
from tools.resume_paused_delivery_model import (
    ClearOutcome,
    DeliveryOutcome,
    Phase,
    Refusal,
)
from tools.resume_paused_input import CodexInputProver
from tools.resume_paused_marker import MARKER_FLAG, Marker
from tools.resume_paused_models import SessionRole
from tools.resume_paused_plan_model import RunPlan
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from tools.resume_paused_codex import CodexPaneProfile
    from tools.resume_paused_delivery_model import (
        ActionReport,
        CheckoutDelivery,
        DeliveryProfile,
        InputScreen,
        ProverFactory,
        Remaining,
        SendStep,
    )
    from tools.resume_paused_evidence import PaneObservation
    from tools.resume_paused_input import InputProver, PaneRecord

COMMAND = f"$llm-shared:resume-session --resume-paused 04.rp1.{CODEX_PANE}.requestor.b4"
MARKED = f"$llm-shared:resume-session {MARKER_FLAG} {Marker('0123456789abcdef0123456789abcdef', CODEX_PANE, SessionRole.REQUESTOR, 'a' * 64).render()}"
BANNER = "New conversation started."
CLEARED = (BANNER, PROMPT + PLACEHOLDER, FOOTER)
SELECTOR = f"session:{SESSION} name:Codex*api"


@dataclass
class RecoveryCheck:
    """Pre-send check refusing only the recovery Enter, recording every phase."""

    seen: list[Phase] = field(default_factory=list[Phase])

    def check(self, step: SendStep) -> Refusal | None:
        """Refuse the recovery Enter."""
        self.seen.append(step.phase)
        return Refusal("prompt-changed") if step.phase is Phase.RECOVERY else None


@dataclass
class EditingCheck:
    """Pre-send check during which the person edits the input box, before the recovery Enter."""

    world: World

    def check(self, step: SendStep) -> Refusal | None:
        """Let the recovery checks pass while the input box changes."""
        if step.phase is Phase.RECOVERY:
            self.world.transport.captures[CODEX_PANE] = [typed(COMMAND + " and more")]
        return None


def codex(*captures: tuple[str, ...] | None, world: World | None = None) -> World:
    """Declare the Codex pane, listed and idle, with its captures in order."""
    world = world or World()
    world.transport.observations = [observation(record(CODEX_PANE))]
    world.transport.captures[CODEX_PANE] = list(captures)
    return world


def only(deliveries: tuple[CheckoutDelivery, ...]) -> ActionReport:
    """Return the single action report of a single delivered checkout."""
    (delivery,) = deliveries
    (report,) = delivery.reports
    return report


def stalled(world: World, seconds: float = 60) -> None:
    """Make the ask stall: it spends time, exits non-zero and leaves the command unsubmitted."""
    world.transport.exit_code = 1
    world.transport.on_ask = lambda _command: world.clock.advance(seconds)


def proving(world: World) -> None:
    """Make the Enter submit the command, which the input proof then shows."""
    world.transport.on_enter = lambda: world.codex.proved.add((CODEX_PANE, COMMAND))


def enters(world: World) -> list[tuple[str, ...]]:
    """Return every Enter sent."""
    return [call for call in world.transport.calls if call[0] == "enter"]


def test_a_codex_resume_with_an_empty_input_box_is_accepted_by_its_input_proof() -> None:
    """No recovery is needed when the ask submitted the command."""
    world = codex(EMPTY)
    world.transport.on_ask = lambda command: world.codex.proved.add((CODEX_PANE, command))
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.recovery) == (DeliveryOutcome.ACCEPTED, ())
    assert world.transport.calls == [("observe",), ("capture", CODEX_PANE), ("ask", SELECTOR, COMMAND)]


@pytest.mark.parametrize(
    ("captures", "profile", "expected"),
    [
        ((typed("a draft"),), CODEX_PROFILE, ("pane-draft", False)),
        ((("no input line",),), CODEX_PROFILE, ("screen-unsupported", True)),
        ((("OpenAI Codex", PROMPT + PLACEHOLDER, "an unrecognized line"),), CODEX_PROFILE, ("screen-unsupported", True)),
        ((None,), CODEX_PROFILE, ("capture-failed", True)),
        ((EMPTY,), replace(CODEX_PROFILE, screen=None), ("screen-unsupported", True)),
    ],
)
def test_a_codex_send_needs_a_proved_empty_input_box(
    captures: tuple[tuple[str, ...] | None, ...], profile: DeliveryProfile, expected: tuple[str, bool],
) -> None:
    """A draft skips; an unreadable or unsupported screen fails; nothing is typed."""
    world = codex(*captures)
    world.profiles.by_pane[CODEX_PANE] = [profile]
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.reason, report.failed) == (DeliveryOutcome.REFUSED, *expected)
    assert world.transport.sent() == []


def test_a_stalled_unsubmitted_command_gets_one_rechecked_enter_within_the_budget() -> None:
    """A capture, the fresh recovery checks, an identical last capture, then one pane-targeted Enter; then acceptance."""
    world = codex(EMPTY, typed(COMMAND))
    stalled(world)
    proving(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.recovery, report.notes) == (DeliveryOutcome.ACCEPTED, (Phase.RESUME,), ("resume-ask-exit-1",))
    assert world.transport.calls == [
        ("observe",), ("capture", CODEX_PANE), ("ask", SELECTOR, COMMAND),
        ("capture", CODEX_PANE), ("observe",), ("capture", CODEX_PANE), ("enter", SESSION, CODEX_PANE),
    ]
    assert world.clock.sleeps[0] == 1.0


def test_every_blocking_call_of_a_send_is_bounded_by_its_remaining_budget() -> None:
    """Before the send the call bound applies; the ask gets the whole budget, the Enter what is left."""
    world = codex(EMPTY, typed(COMMAND))
    stalled(world)
    proving(world)
    world.deliver(checkout(action(CODEX_PANE, COMMAND)))
    assert world.transport.bounds == [
        ("observe", 30.0), ("capture", 30.0), ("ask", 100.0),
        ("capture", 30.0), ("observe", 30.0), ("capture", 30.0), ("enter", 39.0),
    ]


def test_a_proof_completing_after_the_deadline_is_not_acceptance() -> None:
    """A proof started before the deadline but finished after it leaves the send unconfirmed, with no further read."""
    world = codex(EMPTY)

    def slow_ask(command: str) -> None:
        world.codex.proved.add((CODEX_PANE, command))
        world.clock.advance(98)

    world.transport.on_ask = slow_ask
    world.codex.on_prove = lambda: world.clock.advance(3)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.reason) == (DeliveryOutcome.UNCONFIRMED, "acceptance-unproved")
    assert world.transport.calls[-1][0] == "ask"


@dataclass
class SlowVersions:
    """Codex version evidence whose read spends declared seconds of the clock."""

    world: World
    seconds: float

    def evidence(self, pane: PaneRecord) -> tuple[str, CodexPaneProfile] | None:
        """Spend the declared time, then return the pinned synthetic version."""
        self.world.clock.advance(self.seconds)
        return FakeVersions().evidence(pane)


def bounded_codex(world: World, version_seconds: float) -> ProverFactory:
    """Compose the concrete Codex prover from budget-bounded readers, as Step 8 does."""

    def build(remaining: Remaining) -> InputProver:
        store = BoundedSessionStore(FakeSessionStore({}), remaining)
        capture = BoundedCapture(world.transport.capture, remaining)
        return CodexInputProver(store, capture, BoundedVersions(SlowVersions(world, version_seconds), remaining), 0)

    return build


@pytest.mark.parametrize(("version_seconds", "capture_bound"), [(0.0, 0.5), (0.3, 0.2), (1.0, None)])
def test_the_concrete_codex_prover_reads_only_while_time_is_left(version_seconds: float, capture_bound: float | None) -> None:
    """Code review rounds 2 and 3: a proof started half a second before the deadline grants its capture what is left after the version read, or skips it."""
    world = codex(EMPTY)
    stalled(world, 99.5)
    world.transport.on_capture = lambda count: world.clock.advance(1) if count > 1 else None
    world.factories[Host.CODEX] = bounded_codex(world, version_seconds)
    report = only(world.deliver(checkout(action(CODEX_PANE, MARKED))))
    assert report.outcome is DeliveryOutcome.UNCONFIRMED
    after_ask = world.transport.bounds[world.transport.bounds.index(("ask", 100.0)) + 1 :]
    assert after_ask == ([] if capture_bound is None else [("capture", capture_bound)])


@dataclass
class RecordingRecoveryCheck:
    """Recovery check recording each phase it is asked about, refusing nothing."""

    seen: list[Phase] = field(default_factory=list[Phase])

    def check(self, step: SendStep) -> Refusal | None:
        """Record the phase."""
        self.seen.append(step.phase)
        return None


def test_a_spent_budget_skips_every_later_recovery_check() -> None:
    """Code review round 3: once the first of two recovery checks spends the budget, the second is never asked."""
    world = codex(EMPTY, typed(COMMAND))
    second = RecordingRecoveryCheck()
    world.checks = (SlowCheck(world), second)
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert "resume-recovery-withheld-deadline-passed" in report.notes
    assert second.seen == [Phase.RESUME]
    assert enters(world) == []


@dataclass
class SlowCheck:
    """Recovery check that spends most of the remaining budget."""

    world: World

    def check(self, step: SendStep) -> Refusal | None:
        """Spend 45 seconds before the recovery Enter."""
        if step.phase is Phase.RECOVERY:
            self.world.clock.advance(45)
        return None


def test_a_recovery_check_that_spends_the_budget_stops_before_the_last_capture() -> None:
    """Code review round 2: no further capture, profile read or Enter starts once the checks spent the budget."""
    world = codex(EMPTY, typed(COMMAND))
    world.checks = (SlowCheck(world),)
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert "resume-recovery-withheld-deadline-passed" in report.notes
    assert [call[0] for call in world.transport.calls] == ["observe", "capture", "ask", "capture", "observe"]
    assert enters(world) == []


@dataclass
class SlowProfiles:
    """Profile gate whose second read, the recovery one, spends 45 seconds."""

    world: World
    calls: int = 0

    def profile(self, pane: PaneRecord) -> DeliveryProfile | None:
        """Return the Codex profile, slowly on the recovery read."""
        del pane
        self.calls += 1
        if self.calls == len(("resume", "recovery")):
            self.world.clock.advance(45)
        return CODEX_PROFILE


def test_a_slow_recovery_profile_read_stops_before_the_last_capture() -> None:
    """The profile read ends the recovery checks; once it spent the budget, no capture or Enter follows."""
    world = codex(EMPTY, typed(COMMAND))
    stalled(world)
    ports = replace(world.ports(), profiles=SlowProfiles(world))
    report = only(deliver_run(RunPlan(dry_run=False, failures=(), checkouts=(checkout(action(CODEX_PANE, COMMAND)),)), HUMAN, ports))
    assert (report.outcome, report.recovery) == (DeliveryOutcome.UNCONFIRMED, ())
    assert [call[0] for call in world.transport.calls] == ["observe", "capture", "ask", "capture", "observe"]


@pytest.mark.parametrize("slow_capture", [2, 3])
def test_an_ownership_capture_completing_after_the_deadline_sends_no_enter(slow_capture: int) -> None:
    """Neither the first nor the last ownership capture may lead to an Enter once the budget is spent."""
    world = codex(EMPTY, typed(COMMAND))
    stalled(world)
    world.transport.on_capture = lambda count: world.clock.advance(45) if count == slow_capture else None
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.recovery) == (DeliveryOutcome.UNCONFIRMED, ())
    assert enters(world) == []


def test_the_recovery_enter_is_never_repeated_and_the_deadline_never_resets() -> None:
    """Still unaccepted after the one Enter: unconfirmed at exactly 100 seconds after the send."""
    world = codex(EMPTY, typed(COMMAND))
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.reason, report.failed, report.recovery) == (DeliveryOutcome.UNCONFIRMED, "acceptance-unproved", True, (Phase.RESUME,))
    assert len(enters(world)) == 1
    assert world.clock.current == T0 + timedelta(seconds=100)
    assert [call for call in world.transport.calls if call[0] == "ask"] == [("ask", SELECTOR, COMMAND)]


def test_an_enter_tuios_refused_is_reported_and_not_retried() -> None:
    """The one Enter is spent even when TUIOS did not send it."""
    world = codex(EMPTY, typed(COMMAND))
    stalled(world)
    world.transport.entered = False
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.recovery, report.notes) == ((Phase.RESUME,), ("resume-ask-exit-1", "resume-recovery-enter-refused"))
    assert len(enters(world)) == 1


@pytest.mark.parametrize(
    ("after", "reason"),
    [
        ((typed(COMMAND), typed(COMMAND + " edited")), "changed"),
        ((("OpenAI Codex", PROMPT + COMMAND, "• Working (1s)", FOOTER),), "capture"),
        ((("OpenAI Codex", PROMPT + COMMAND, "  " + PLACEHOLDER, FOOTER),), "capture"),
        ((("OpenAI Codex", PROMPT + COMMAND, "and a second draft line", FOOTER),), "capture"),
        ((("OpenAI Codex", PROMPT + COMMAND, FOOTER, FOOTER),), "capture"),
        ((("OpenAI Codex", PROMPT + COMMAND),), "capture"),
        ((("history " + COMMAND, PROMPT + COMMAND, FOOTER),), "capture"),
        ((typed(COMMAND[:-1]),), "capture"),
        ((None,), "capture"),
    ],
)
def test_an_edited_ambiguous_or_unreadable_input_box_withholds_the_enter(after: tuple[tuple[str, ...] | None, ...], reason: str) -> None:
    """An edit, a working, placeholder or draft line below, a repeated or missing footer, a repeat, other text or a failed capture."""
    world = codex(EMPTY, *after)
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.recovery) == (DeliveryOutcome.UNCONFIRMED, ())
    assert f"resume-recovery-withheld-{reason}" in report.notes
    assert enters(world) == []


def test_a_submitted_command_needs_no_enter_while_acceptance_is_awaited() -> None:
    """An empty input box after the send is no recovery case; acceptance alone decides."""
    world = codex(EMPTY, submitted(COMMAND))
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.notes) == (DeliveryOutcome.UNCONFIRMED, ("resume-ask-exit-1",))
    assert enters(world) == []


def test_fresh_recovery_checks_withhold_the_enter() -> None:
    """An injected check refusing the recovery Enter stops it; the resume itself was checked first."""
    check = RecoveryCheck()
    world = codex(EMPTY, typed(COMMAND), world=World(checks=(check,)))
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert "resume-recovery-withheld-prompt-changed" in report.notes
    assert (check.seen, enters(world)) == ([Phase.RESUME, Phase.RECOVERY], [])


def test_an_edit_during_the_recovery_checks_withholds_the_enter() -> None:
    """The last ownership capture follows the slow checks, so an edit made meanwhile is seen."""
    world = codex(EMPTY, typed(COMMAND))
    world.checks = (EditingCheck(world),)
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert "resume-recovery-withheld-changed" in report.notes
    assert enters(world) == []


@pytest.mark.parametrize(
    ("recovery_listing", "reason"),
    [
        (observation(), "target-absent"),
        (observation(record(CODEX_PANE), activity={CODEX_PANE: replace(IDLE, blocked_by="permission")}), "pane-blocked"),
        (observation(record(CODEX_PANE), record(WEB_PANE, WEB, name="Codex-api")), "selector-ambiguous"),
    ],
)
def test_a_target_gone_blocked_or_colliding_at_recovery_withholds_the_enter(recovery_listing: PaneObservation, reason: str) -> None:
    """The recovery listing is fresh: a vanished UUID, a question or a new selector collision forbids the Enter."""
    world = codex(EMPTY, typed(COMMAND))
    world.transport.observations = [observation(record(CODEX_PANE)), recovery_listing]
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert f"resume-recovery-withheld-{reason}" in report.notes
    assert enters(world) == []


def test_a_changed_profile_at_recovery_withholds_the_enter() -> None:
    """The pane's pinned profile is selected again and must not change within the action."""
    world = codex(EMPTY, typed(COMMAND))
    world.profiles.by_pane[CODEX_PANE] = [CODEX_PROFILE, replace(CODEX_PROFILE, clear_command="/clear")]
    stalled(world)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert "resume-recovery-withheld-profile-changed" in report.notes
    assert enters(world) == []


@pytest.mark.parametrize("spent", [100, 99.5])
def test_an_exhausted_budget_leaves_no_time_for_a_recovery_enter(spent: float) -> None:
    """The ask used the budget, or the second capture would fall after the deadline: unconfirmed, no Enter."""
    world = codex(EMPTY, typed(COMMAND))
    stalled(world, spent)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND))))
    assert (report.outcome, report.recovery) == (DeliveryOutcome.UNCONFIRMED, ())
    assert enters(world) == []
    assert world.clock.current == T0 + timedelta(seconds=100)


def test_a_codex_clear_is_confirmed_on_screen_then_the_resume_follows() -> None:
    """The cleared line on an empty input box, on a changed screen, confirms the new conversation."""
    world = codex(EMPTY, CLEARED)
    world.transport.on_ask = lambda command: world.codex.proved.add((CODEX_PANE, command))
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND, clear=True))))
    assert (report.outcome, report.clear) == (DeliveryOutcome.ACCEPTED, ClearOutcome.CONFIRMED)
    assert [call[2] for call in world.transport.calls if call[0] == "ask"] == ["/new", COMMAND]


@pytest.mark.parametrize(
    "screens",
    [
        (EMPTY,),
        (("12:00", BANNER, PROMPT + PLACEHOLDER, FOOTER), ("12:01", BANNER, PROMPT + PLACEHOLDER, FOOTER)),
    ],
)
def test_an_unconfirmed_codex_clear_stops_the_resume(screens: tuple[tuple[str, ...], ...]) -> None:
    """An unchanged screen, or an old banner with only an unrelated line changing, never confirms the clear."""
    world = codex(*screens)
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND, clear=True))))
    assert (report.outcome, report.reason, report.clear) == (DeliveryOutcome.UNCONFIRMED, "clear-unconfirmed", ClearOutcome.UNCONFIRMED)
    assert [call[2] for call in world.transport.calls if call[0] == "ask"] == ["/new"]


def test_a_codex_clear_left_unsubmitted_gets_its_own_recovery_enter() -> None:
    """The clear is a send of its own: one Enter for its proven unsubmitted command."""
    world = codex(EMPTY, typed("/new"), typed("/new"), typed("/new"), CLEARED)
    world.transport.on_ask = lambda command: world.codex.proved.add((CODEX_PANE, command)) if command == COMMAND else None
    report = only(world.deliver(checkout(action(CODEX_PANE, COMMAND, clear=True))))
    assert (report.outcome, report.clear, report.recovery) == (DeliveryOutcome.ACCEPTED, ClearOutcome.CONFIRMED, (Phase.CLEAR,))


@pytest.mark.parametrize(
    ("lines", "command", "expected"),
    [
        (EMPTY, COMMAND, InputLine.EMPTY),
        (typed(COMMAND), COMMAND, InputLine.COMMAND),
        (typed(COMMAND), "", InputLine.OTHER),
        (("no prompt",), COMMAND, InputLine.OTHER),
        (typed("other"), COMMAND, InputLine.OTHER),
        (submitted(COMMAND), COMMAND, InputLine.EMPTY),
        (("OpenAI Codex", PROMPT + COMMAND, "second line of a draft", FOOTER), COMMAND, InputLine.OTHER),
        (("OpenAI Codex", PROMPT + PLACEHOLDER, "an unrecognized line"), COMMAND, InputLine.OTHER),
        (("OpenAI Codex", PROMPT + COMMAND, FOOTER, FOOTER), COMMAND, InputLine.OTHER),
        (("OpenAI Codex", PROMPT + COMMAND), COMMAND, InputLine.OTHER),
        (("OpenAI Codex", PROMPT + PLACEHOLDER), COMMAND, InputLine.OTHER),
    ],
)
def test_read_input_classifies_the_whole_input_box(lines: tuple[str, ...], command: str, expected: InputLine) -> None:
    """The last prefixed line is the input box; only the pinned footer may follow it."""
    assert read_input(lines, command, SCREEN) is expected


def test_without_a_footer_signature_no_line_may_follow_the_input_line() -> None:
    """An empty footer layout accepts a one-line box and refuses any line below it; an invalid one refuses all."""
    screen = replace(SCREEN, footer_lines=())
    assert read_input(("OpenAI Codex", PROMPT + COMMAND), COMMAND, screen) is InputLine.COMMAND
    assert read_input(typed(COMMAND), COMMAND, screen) is InputLine.OTHER
    assert read_input(typed(COMMAND), COMMAND, replace(SCREEN, footer_lines=("(",))) is InputLine.OTHER


def test_an_invalid_working_signature_never_proves_an_unsubmitted_command() -> None:
    """Without a usable working signature the command is never read as unsubmitted."""
    assert read_input(typed(COMMAND), COMMAND, replace(SCREEN, working_pattern="(")) is InputLine.OTHER


@pytest.mark.parametrize(
    ("before", "after", "screen", "expected"),
    [
        (EMPTY, CLEARED, SCREEN, True),
        (CLEARED, (BANNER, "work", BANNER, PROMPT + PLACEHOLDER, FOOTER), SCREEN, True),
        (CLEARED, CLEARED, SCREEN, False),
        (("12:00", *CLEARED), ("12:01", *CLEARED), SCREEN, False),
        (EMPTY, (BANNER, PROMPT + "text", FOOTER), SCREEN, False),
        (EMPTY, ("Other banner", PROMPT + PLACEHOLDER, FOOTER), SCREEN, False),
        (EMPTY, CLEARED, replace(SCREEN, cleared_pattern=""), False),
    ],
)
def test_a_codex_clear_needs_a_new_banner_on_an_empty_box(
    before: tuple[str, ...], after: tuple[str, ...], screen: InputScreen, expected: bool,  # noqa: FBT001
) -> None:
    """One more cleared line than before is required; an old banner with an unrelated change is not a clear."""
    assert cleared(before, after, screen) is expected


@pytest.mark.parametrize(("pattern", "expected"), [("", False), ("(", False), (r"\d+ shells? running", True), ("other", False)])
def test_background_shell_reads_only_a_usable_signature(pattern: str, expected: bool) -> None:  # noqa: FBT001
    """An empty or invalid signature reports nothing."""
    assert background_shell(("Claude Code", "2 shells running"), pattern) is expected


# eof
