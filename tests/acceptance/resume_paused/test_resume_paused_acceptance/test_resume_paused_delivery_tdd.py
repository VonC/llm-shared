"""Clear, transport, guard, recovery and receiver-failure scenarios of resume_paused (Step 8).

The production composition types through the real ``TuiosTransport`` into a
fake ``tuios``: a confirmed clear precedes the resume and a redundant Claude
clear is skipped; every ask is one shell-free argument list; a checkout whose
guard another launch holds is skipped with no input; only tool-owned,
unsubmitted Codex input gets the single recovery Enter; lost or unconfirmed
input fails and is never retyped; a receiving agent that stops before a
protected write fails or leaves the reviewer pending, never activated.

Fix (Step 8 code review round 1): a resume recorded in the session journal
after planning skips the first send, and a journal unreadable at that send
fails it, both with no input: the pre-send recheck reads the journal again.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from tests.acceptance.resume_paused.fakes import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    Scenario,
)
from tests.unit.tools.resume_paused_receiver_test_support import Step
from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    write,
)
from tools.resume_paused_delivery_model import CLAUDE_WAIT_SCOPE, LogEvent, LogKind
from tools.resume_paused_evidence import JournalIndex, JournalResume, ScreenVerdict
from tools.resume_paused_marker import marker_in_command
from tools.resume_paused_models import PROMPT_NAME, RECEIPT_NAME, CanonicalRoot
from tools.resume_paused_transport import ask_arguments

if TYPE_CHECKING:
    from pathlib import Path

HEAD = "'Step 2 tests' paused by claude at 2026-11-17 17:37, prompt unused"
REQUESTOR = "requestor codex llm-shared_resume-paused/requestor | pane 77e5f39c (saved routing, validated)"
REVIEWER = "reviewer claude llm-shared_resume-paused/reviewer | pane 2fd92f30 (saved routing, validated)"
LIMITS = f"[{CLAUDE_WAIT_SCOPE}]"


def natives(scenario: Scenario) -> list[str]:
    """Return the native command of every ask, and ``Enter`` for every recovery key, in order."""
    return ["Enter" if call[1] == "send-keys" else call[-1].split(" ", 1)[0] for call in scenario.tuios.inputs()]


def test_a_confirmed_codex_clear_precedes_the_resume(tmp_path: Path) -> None:
    """``--clear`` clears only the resumed requestor, confirms it on screen, then resumes it."""
    scenario = Scenario(tmp_path)
    code, lines = scenario.run("--clear")
    assert (code, lines[0]) == (0, f"DONE checkout: {HEAD}; {REQUESTOR}: cleared, accepted, claimed g2; {REVIEWER}: accepted, claimed g3 {LIMITS}")
    assert natives(scenario) == ["/new", "$llm-shared:resume-session", "/review-resume"]


def test_a_redundant_claude_clear_is_skipped_but_the_resume_is_still_sent(tmp_path: Path) -> None:
    """A Claude clear logged after the pause with no later prompt makes ``--clear`` redundant (Q12=A)."""
    scenario = Scenario(tmp_path)
    scenario.probe = {REQUESTOR_PANE: ScreenVerdict.IDLE_EMPTY}
    assert scenario.reviewer.log is not None
    scenario.reviewer.log.append(LogEvent(LogKind.CLEAR, scenario.clock.now() - timedelta(hours=1)))
    code, lines = scenario.run("--switch-roles", "checkout", "--clear")
    assert code == 0
    assert "requestor claude llm-shared_resume-paused/reviewer | pane 2fd92f30 (saved routing, validated): already cleared, accepted, claimed g2" in lines[0]
    assert natives(scenario) == ["/resume-session", "$llm-shared:review-resume"]


def test_an_unconfirmed_clear_fails_and_no_resume_follows(tmp_path: Path) -> None:
    """A clear that never shows its confirmation fails within its own budget; nothing else is typed."""
    scenario = Scenario(tmp_path)
    scenario.requestor.clears = False
    code, lines = scenario.run("--clear")
    assert code == 1
    assert lines[0] == (
        f"FAIL checkout: {HEAD}; {REQUESTOR}: clear unconfirmed, unconfirmed: clear-unconfirmed; "
        f"{REVIEWER}: skipped: requestor-not-accepted {LIMITS}"
    )
    assert natives(scenario) == ["/new"]
    assert not (scenario.root / ".reviews" / RECEIPT_NAME).exists()


def test_every_ask_is_one_shell_free_argument_list(tmp_path: Path) -> None:
    """The marked command, with its spaces and ``$``, is one argument after ``--``; the selector names one pane."""
    scenario = Scenario(tmp_path)
    scenario.run()
    first = scenario.tuios.inputs()[0]
    command = first[-1]
    assert command.startswith("$llm-shared:resume-session --resume-paused ")
    assert first == ask_arguments("session:llm-shared_resume-paused name:requestor*|*pane", command)


def test_a_checkout_whose_guard_another_launch_holds_is_skipped(tmp_path: Path) -> None:
    """Only the guard holder may revalidate and deliver; the other launch skips with no input and succeeds."""
    scenario = Scenario(tmp_path)
    with scenario.guard.acquire(CanonicalRoot.from_path(scenario.root)):
        code, lines = scenario.run()
    assert (code, lines[0]) == (0, f"SKIP checkout: {HEAD}; guard held; {REQUESTOR}: not sent; {REVIEWER}: not sent")
    assert scenario.tuios.inputs() == []


def test_tool_owned_unsubmitted_codex_input_gets_one_recovery_enter(tmp_path: Path) -> None:
    """The exact command left in the input box is submitted by one full-id Enter, then accepted (Q11=C)."""
    scenario = Scenario(tmp_path)
    scenario.requestor.typing = "hold"
    code, lines = scenario.run()
    assert (code, lines[0]) == (
        0, f"DONE checkout: {HEAD}; {REQUESTOR}: accepted, claimed g2, recovery enter; {REVIEWER}: accepted, claimed g3 {LIMITS}",
    )
    assert natives(scenario) == ["$llm-shared:resume-session", "Enter", "/review-resume"]
    assert scenario.tuios.inputs()[1][-3:] == ("-w", REQUESTOR_PANE, "Enter")


def _journal_after_planning(scenario: Scenario, journal: JournalIndex) -> None:
    """Replace the session journal once the planning listing is taken, before the first send's fresh listing."""

    def record_later(listings: int) -> None:
        """Make the declared journal current from the second listing on."""
        if listings >= 2:  # noqa: PLR2004 - the first listing is the planning one
            scenario.sessions = journal

    scenario.tuios.on_listing = record_later


def test_a_resume_recorded_after_planning_skips_the_first_send(tmp_path: Path) -> None:
    """The pre-send recheck reads the journal again: a later resume entry suppresses the checkout with no input (review round 1)."""
    scenario = Scenario(tmp_path)
    root = CanonicalRoot.from_path(scenario.root)
    _journal_after_planning(scenario, JournalIndex({root: (JournalResume("chatgpt", scenario.clock.now(), root),)}))
    code, lines = scenario.run()
    assert (code, lines[0]) == (0, f"SKIP checkout: {HEAD}; {REQUESTOR}: skipped: journal-resumed; {REVIEWER}: skipped: requestor-not-accepted {LIMITS}")
    assert scenario.tuios.inputs() == []


def test_a_journal_unreadable_at_the_send_fails_it_with_no_input(tmp_path: Path) -> None:
    """An unreadable journal at the pre-send boundary is uncertain duplicate evidence: the send fails, nothing is typed (review round 1)."""
    scenario = Scenario(tmp_path)
    _journal_after_planning(scenario, JournalIndex(error="session journal is unreadable: denied"))
    code, lines = scenario.run()
    assert (code, lines[0]) == (1, f"FAIL checkout: {HEAD}; {REQUESTOR}: failed: duplicate-uncertain; {REVIEWER}: skipped: requestor-not-accepted {LIMITS}")
    assert scenario.tuios.inputs() == []


def test_lost_input_is_unconfirmed_and_never_retyped(tmp_path: Path) -> None:
    """Input that never reaches the pane is unconfirmed after its budget: the launch fails, nothing is retyped."""
    scenario = Scenario(tmp_path)
    scenario.requestor.typing = "drop"
    code, lines = scenario.run()
    assert code == 1
    assert lines[0] == (
        f"FAIL checkout: {HEAD}; {REQUESTOR}: unconfirmed: acceptance-unproved; {REVIEWER}: skipped: requestor-not-accepted {LIMITS}"
    )
    assert natives(scenario) == ["$llm-shared:resume-session"]


def test_a_receiver_stopping_before_its_receipt_fails_the_launch(tmp_path: Path) -> None:
    """A prompt changed after delivery stops the receiver before any write; the launch fails, the reviewer gets nothing."""
    scenario = Scenario(tmp_path)
    agent = scenario.agent(scenario.requestor)

    def edit(step: Step) -> None:
        """Change the saved prompt just before the receipt."""
        if step is Step.RECEIPT:
            write(scenario.root, PROMPT_NAME, scenario.checkout.prompt + b"\nLater note.\n")

    agent.before = edit
    code, lines = scenario.run()
    assert code == 1
    assert lines[0].startswith(f"FAIL checkout: {HEAD}; {REQUESTOR}: accepted, receiver failed: ")
    assert (agent.outcomes[0].written, agent.outcomes[0].stopped_at, agent.outcomes[0].reason) == ([], Step.RECEIPT, "binding-mismatch")
    assert natives(scenario) == ["$llm-shared:resume-session"]
    assert not (scenario.root / ".reviews" / RECEIPT_NAME).exists()


def test_new_typed_input_between_protected_writes_stops_the_receiver_and_fails_the_launch(tmp_path: Path) -> None:
    """A receipt without the requestor's marked claim never activates the reviewer; the receiver's failed line fails the run (Q15)."""
    scenario = Scenario(tmp_path)
    agent = scenario.agent(scenario.requestor)

    def type_more(step: Step) -> None:
        """Type new input into the requestor pane before its journal entry."""
        if step is Step.JOURNAL:
            scenario.requestor.typed.append(("hello", scenario.clock.now()))

    agent.before = type_more
    code, lines = scenario.run()
    assert code == 1
    assert lines[0] == (
        f"FAIL checkout: {HEAD}; {REQUESTOR}: accepted, receiver failed: receiver-failed; {REVIEWER}: skipped: requestor-failed {LIMITS}"
    )
    assert (agent.outcomes[0].written, agent.outcomes[0].stopped_at, agent.outcomes[0].reason) == (
        [Step.RECEIPT], Step.JOURNAL, "marked-input-not-latest",
    )
    launch = marker_in_command(scenario.tuios.inputs()[0][-1]).launch_id
    assert scenario.requestor.results == [f"resume-paused {launch} failed"]
    assert scenario.marked_claim() is None
    assert natives(scenario) == ["$llm-shared:resume-session"]
    assert REVIEWER_PANE not in {call[-1] for call in scenario.tuios.inputs()}


# eof
