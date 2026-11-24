"""Takeover, reviewer leave-alone, pending, activation and continuation scenarios of resume_paused (Step 8).

The routed pause of a Codex requestor and a Claude reviewer is resumed through
the production composition over fake TUIOS: the requestor's receiving agent
validates its marker and writes its receipt, journal entry and marked claim
with the real validator and locked claim; the takeover proves that claim;
only then is the missing reviewer activated, after positive no-wait evidence
and under the design Q27=B all-pane idle guard refreshed before the send. A
later launch continues only a verified missing reviewer, leaves an active one
alone, never resends an uncertain earlier delivery, and a switched pair needs
its switch again. The Q27=B cases run on initial activation and on later
continuation alike, through the real guard, not only its limits code.

Fix (Step 8 code review round 2): a reviewer pane that becomes a shell
between the takeover decision and the send gets no input, and the run line
names it no LLM counterpart with its failed validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.resume_paused.fakes import (
    IDLE,
    REQUESTOR_PANE,
    REVIEWER_PANE,
    THIRD_PANE,
    WORKING,
    Scenario,
    record,
)
from tests.unit.tools.test_resume_paused_takeover.takeover_world import FakeAbsence
from tools.resume_paused_delivery_model import CLAUDE_WAIT_SCOPE
from tools.resume_paused_evidence import ScreenVerdict
from tools.resume_paused_models import RECEIPT_NAME
from tools.resume_paused_pane_guard import ClaudeScreen

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.resume_paused_claude_ledger import LedgerDecision
    from tools.resume_paused_reviewer_wait import WaitScope

HEAD = "'Step 2 tests' paused by claude at 2026-11-17 17:37"
REQUESTOR = "requestor codex llm-shared_resume-paused/requestor | pane 77e5f39c (saved routing, validated)"
REVIEWER = "reviewer claude llm-shared_resume-paused/reviewer | pane 2fd92f30 (saved routing, validated)"
LIMITS = f"[{CLAUDE_WAIT_SCOPE}]"
RECEIPT = "evidence receipt: chatgpt, pane 77e5f39c, at 2026-11-18 07:25"


def natives(scenario: Scenario) -> list[str]:
    """Return the native command of every input typed so far, in order."""
    return [call[-1].split(" ", 1)[0] for call in scenario.tuios.inputs()]


def taken_over(tmp_path: Path) -> Scenario:
    """Declare what an earlier launch left: the requestor resumed and claimed, the reviewer still missing."""
    scenario = Scenario(tmp_path)
    scenario.declare_takeover()
    return scenario


def test_one_launch_resumes_the_requestor_proves_its_takeover_and_activates_the_reviewer(tmp_path: Path) -> None:
    """The requestor's receipt and marked claim come first; the reviewer is typed into only after that proof."""
    scenario = Scenario(tmp_path)
    code, lines = scenario.run()
    assert code == 0
    assert lines == [
        f"DONE checkout: {HEAD}, prompt unused; {REQUESTOR}: accepted, claimed g2; {REVIEWER}: accepted, claimed g3 {LIMITS}",
        "omitted 0 pane(s) without a prompt-bearing target",
    ]
    assert natives(scenario) == ["$llm-shared:resume-session", "/review-resume"]
    receipt = (scenario.root / ".reviews" / RECEIPT_NAME).read_text(encoding="utf-8")
    assert "- Schema: 3\n" in receipt
    assert "- Resumed by: chatgpt\n" in receipt
    assert f"- Receiving pane: {REQUESTOR_PANE}\n" in receipt
    assert scenario.marked_claim() == (REVIEWER_PANE, "claude", 3)


def test_a_reviewer_without_no_wait_evidence_stays_pending_and_succeeds(tmp_path: Path) -> None:
    """Pending is a success: only the requestor got input, and its claim stays the current one."""
    scenario = Scenario(tmp_path)
    scenario.absence = FakeAbsence(None)
    code, lines = scenario.run()
    assert (code, lines[0]) == (
        0, f"PENDING checkout: {HEAD}, prompt unused; {REQUESTOR}: accepted, claimed g2; {REVIEWER}: pending: claude-ledger-unavailable {LIMITS}",
    )
    assert natives(scenario) == ["$llm-shared:resume-session"]
    assert scenario.marked_claim() == (REQUESTOR_PANE, "codex", 2)


def test_a_later_launch_activates_only_the_verified_missing_reviewer(tmp_path: Path) -> None:
    """The continuation comes from the unchanged prompt, receipt and current claim; the requestor gets nothing."""
    scenario = taken_over(tmp_path)
    code, lines = scenario.run()
    assert (code, lines) == (0, [
        f"DONE checkout: {HEAD}, prompt used; {RECEIPT}; {REVIEWER}: accepted, claimed g3 {LIMITS}",
        "omitted 1 pane(s) without a prompt-bearing target",
    ])
    assert natives(scenario) == ["/review-resume"]


def test_an_active_reviewer_is_left_alone_on_every_later_launch(tmp_path: Path) -> None:
    """Once the reviewer serves the exchange, a new launch types nothing anywhere."""
    scenario = Scenario(tmp_path)
    scenario.declare_reviewer()
    code, lines = scenario.run()
    assert (code, lines[0]) == (0, f"SKIP checkout: {HEAD}, prompt used; {RECEIPT}; {REVIEWER}: skipped: reviewer-active {LIMITS}")
    assert natives(scenario) == []


def test_an_uncertain_earlier_reviewer_delivery_is_never_resent(tmp_path: Path) -> None:
    """A marked reviewer command typed after the receipt but never claimed keeps the reviewer pending, with no input."""
    scenario = taken_over(tmp_path)
    earlier = "/review-resume --resume-paused " + "0" * 31 + f"9.rp1.{REVIEWER_PANE}.reviewer." + "c" * 64
    scenario.reviewer.typed.append((earlier, scenario.clock.now()))
    code, lines = scenario.run()
    assert (code, lines[0]) == (0, f"PENDING checkout: {HEAD}, prompt used; {RECEIPT}; {REVIEWER}: pending: reviewer-delivery-uncertain {LIMITS}")
    assert natives(scenario) == []


def test_a_switched_pair_resumes_the_former_reviewer_then_activates_the_former_requestor(tmp_path: Path) -> None:
    """The Claude pane becomes requestor under its marker's override, the Codex pane reviewer after takeover proof."""
    scenario = Scenario(tmp_path)
    scenario.probe = {REQUESTOR_PANE: ScreenVerdict.IDLE_EMPTY}
    code, lines = scenario.run("--switch-roles", "checkout")
    assert (code, lines[0]) == (0, (
        f"DONE checkout: {HEAD}, prompt unused; roles switched; requestor claude llm-shared_resume-paused/reviewer | pane 2fd92f30 (saved routing, validated): "
        "accepted, claimed g2; reviewer codex llm-shared_resume-paused/requestor | pane 77e5f39c (saved routing, validated): accepted, claimed g3"
    ))
    assert scenario.marked_claim() == (REQUESTOR_PANE, "codex", 3)
    assert natives(scenario) == ["/resume-session", "$llm-shared:review-resume"]


def test_a_switched_continuation_needs_the_switch_again(tmp_path: Path) -> None:
    """Without the flag the switched pair is an explained skip; with it, only the missing former requestor is activated."""
    scenario = Scenario(tmp_path)
    scenario.probe = {REQUESTOR_PANE: ScreenVerdict.IDLE_EMPTY}
    scenario.declare_takeover(switched=True)
    code, lines = scenario.run()
    assert code == 0
    assert lines[0].startswith(f"SKIP checkout: {HEAD}, prompt used; skip switch-required: resumed requestor {REVIEWER_PANE}; ")
    assert natives(scenario) == []
    code, lines = scenario.run("--switch-roles", "checkout")
    assert (code, lines[0].rsplit("; ", 1)[-1]) == (0, "reviewer codex llm-shared_resume-paused/requestor | pane 77e5f39c (saved routing, validated): accepted, claimed g3")
    assert natives(scenario) == ["$llm-shared:review-resume"]


@dataclass
class _ShellAfterDecision(FakeAbsence):
    """Ledger decision that proves absence, after turning the reviewer pane into a shell: the next listing shows it."""

    scenario: Scenario | None = None

    def decide(self, scope: WaitScope) -> LedgerDecision | None:
        """Replace the reviewer's live record by a plain shell once, then decide as declared."""
        if self.scenario is not None:
            self.scenario.reviewer.record = record(REVIEWER_PANE, None, self.scenario.root, name="reviewer | pane")
            self.scenario = None
        return super().decide(scope)


def test_a_reviewer_that_becomes_a_shell_before_the_send_gets_no_input_and_reads_no_llm(tmp_path: Path) -> None:
    """The fresh pre-send identity check refuses the shell; the run line names it no LLM counterpart, not validated (round 2)."""
    scenario = Scenario(tmp_path)
    scenario.absence = _ShellAfterDecision(scenario=scenario)
    code, lines = scenario.run()
    shell = "no LLM counterpart llm-shared_resume-paused/reviewer | pane 2fd92f30 (saved routing, not validated: target-not-agent)"
    assert (code, lines[0]) == (0, f"DONE checkout: {HEAD}, prompt unused; {REQUESTOR}: accepted, claimed g2; {shell}: skipped: target-not-agent {LIMITS}")
    assert natives(scenario) == ["$llm-shared:resume-session"]
    assert scenario.marked_claim() == (REQUESTOR_PANE, "codex", 2)


def _busy_other(scenario: Scenario) -> None:
    """Another Claude pane of the checkout reads busy."""
    scenario.pane(THIRD_PANE, scenario.reviewer.host, screen=("Claude Code", "> "), name="third | pane")
    scenario.screens.readings[THIRD_PANE] = ClaudeScreen.BUSY


def _running_command(scenario: Scenario) -> None:
    """The reviewer pane runs a local command whose transcript looks closed: the ledger proves absence, the screen is busy."""
    scenario.screens.readings[REVIEWER_PANE] = ClaudeScreen.BUSY


def _unreadable(scenario: Scenario) -> None:
    """Another Claude pane of the checkout cannot be captured."""
    scenario.pane(THIRD_PANE, scenario.reviewer.host, screen=None, name="third | pane")


def _unknown(scenario: Scenario) -> None:
    """Another Claude pane of the checkout shows a layout the pinned profile does not rebuild."""
    _busy_other(scenario)
    scenario.screens.readings[THIRD_PANE] = ClaudeScreen.UNKNOWN


def _turns_busy(scenario: Scenario) -> None:
    """Another Claude pane is idle when the run plans, then busy at the send's fresh listing."""
    third = scenario.pane(THIRD_PANE, scenario.reviewer.host, screen=("Claude Code", "> "), name="third | pane")

    def flip(listings: int) -> None:
        """Turn the third pane busy after the planning listing."""
        third.activity = IDLE if listings <= 1 else WORKING

    scenario.tuios.on_listing = flip


def _all_idle(scenario: Scenario) -> None:
    """Every Claude pane of the checkout, a third one included, reads idle."""
    scenario.pane(THIRD_PANE, scenario.reviewer.host, screen=("Claude Code", "> "), name="third | pane")


GUARD_CASES = [
    pytest.param(_busy_other, "pending: claude-pane-busy", id="busy-other"),
    pytest.param(_running_command, "pending: claude-pane-busy", id="running-command"),
    pytest.param(_unreadable, "pending: claude-pane-unreadable", id="unreadable"),
    pytest.param(_unknown, "pending: claude-pane-unknown-layout", id="unknown-layout"),
    pytest.param(_turns_busy, "pending: claude-pane-busy", id="turns-busy"),
    pytest.param(_all_idle, "accepted, claimed g3", id="all-idle"),
]


@pytest.mark.parametrize("later", [False, True], ids=["initial", "later"])
@pytest.mark.parametrize(("declare", "outcome"), GUARD_CASES)
def test_the_all_pane_idle_guard_holds_every_claude_reviewer_send(
    tmp_path: Path, declare: Callable[[Scenario], None], outcome: str, *, later: bool,
) -> None:
    """Every live Claude pane of the checkout must read idle at the send; otherwise the reviewer stays pending, no input."""
    scenario = taken_over(tmp_path) if later else Scenario(tmp_path)
    declare(scenario)
    code, lines = scenario.run()
    assert code == 0
    assert lines[0].endswith(f"{REVIEWER}: {outcome} {LIMITS}")
    reviewer_inputs = [native for native in natives(scenario) if native == "/review-resume"]
    assert len(reviewer_inputs) == (1 if outcome.startswith("accepted") else 0)


# eof
