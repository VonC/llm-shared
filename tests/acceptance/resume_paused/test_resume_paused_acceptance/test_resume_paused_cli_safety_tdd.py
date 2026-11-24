"""Caller, preview, name validation, reporting and compatibility scenarios of resume_paused (Step 8).

The production composition runs over fake TUIOS and real temporary
checkouts: a recognized agent caller is refused before any listing; a dry run
types and writes nothing; unmatched exclusion or switch names refuse all
input; exclusions, protected panes and unusable pauses are reported with
their exit codes; a switch that cannot apply fails; independent checkouts,
custom artifact homes and malformed receipts are classified separately. The
installed ``tuitp`` launcher's grammar (the receipt's ``Prompt``,
``SHA-256`` and ``Project root`` lines, the prompt's first-line heading and
``- Session role:`` line) still reads what a marked resume leaves, and legacy
manual resumes keep their reading.

Fix (Step 8 code review round 1): a shell in the saved reviewer slot reads as
no LLM counterpart, in the preview and after the run, never as the saved
Claude reviewer; every target names its saved routing and validation result.
"""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.resume_paused.fakes import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    THIRD_PANE,
    WORKING,
    Scenario,
    record,
)
from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    prompt_text,
    receipt_text,
    write,
)
from tools.resume_paused_delivery_model import CLAUDE_WAIT_SCOPE
from tools.resume_paused_evidence import PaneActivity
from tools.resume_paused_models import PROMPT_NAME, RECEIPT_NAME, PromptDigest
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from pathlib import Path

HEAD = "'Step 2 tests' paused by claude at 2026-11-17 17:37, prompt unused"
REQUESTOR = "requestor codex llm-shared_resume-paused/requestor | pane 77e5f39c (saved routing, validated)"
REVIEWER = "reviewer claude llm-shared_resume-paused/reviewer | pane 2fd92f30 (saved routing, validated)"
OTHER_PANE = "0c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f"
LISTING = ("tuios", "list-agents", "--all-sessions", "--json")
LAUNCHER_LINE = re.compile(r"- (Prompt|SHA-256|Project root): (.*)")


def no_input(scenario: Scenario) -> bool:
    """Return whether nothing was typed into any pane."""
    return scenario.tuios.inputs() == []


@pytest.mark.parametrize(
    ("environ", "ancestry", "signal"),
    [
        ({"CLAUDECODE": "1"}, ("cmd.exe",), "agent-environment-marker"),
        ({"CODEX_THREAD_ID": "t"}, ("cmd.exe",), "agent-environment-marker"),
        ({}, ("cmd.exe", "claude.exe", "WindowsTerminal.exe"), "agent-ancestor"),
    ],
)
@pytest.mark.parametrize("argv", [(), ("--dry-run",)], ids=["run", "preview"])
def test_a_recognized_agent_caller_is_refused_before_tuios_is_listed(
    tmp_path: Path, argv: tuple[str, ...], environ: dict[str, str], ancestry: tuple[str, ...], signal: str,
) -> None:
    """Normal and preview launches from an agent touch no pane and no artifact, and exit 1 (Q16=B, Q20=A)."""
    scenario = Scenario(tmp_path)
    scenario.environ, scenario.ancestry = environ, ancestry
    before = scenario.evidence()
    code, lines = scenario.run(*argv)
    assert (code, lines) == (1, [f"REFUSED run: agent-caller: {signal} (human-only command: agents must not run it); no input sent"])
    assert scenario.tuios.calls == []
    assert scenario.evidence() == before


def test_a_dry_run_reports_every_intended_command_and_writes_nothing(tmp_path: Path) -> None:
    """The preview names both marked commands, the clear and the conditional reviewer with its limits code."""
    scenario = Scenario(tmp_path)
    before = scenario.evidence()
    code, lines = scenario.run("--dry-run", "--clear")
    assert code == 0
    assert lines[0].startswith(f"PLAN checkout: {HEAD}; {REQUESTOR}: clear, then $llm-shared:resume-session --resume-paused {1:032x}.rp1.")
    assert f"; {REVIEWER}: after takeover, /review-resume --resume-paused {2:032x}.rp1.{REVIEWER_PANE}.reviewer." in lines[0]
    assert lines[0].endswith(f"[{CLAUDE_WAIT_SCOPE}]")
    assert lines[1] == "omitted 0 pane(s) without a prompt-bearing target; dry run, nothing typed"
    assert set(scenario.tuios.calls) == {LISTING}
    assert scenario.evidence() == before
    assert not scenario.journal.exists()


@pytest.mark.parametrize(
    ("argv", "line"),
    [
        (("--except", "nowhere"), "REFUSED run: except-unmatched: nowhere; no input sent"),
        (("--dry-run", "--switch-roles", "nowhere,checkout"), "REFUSED run: switch-unmatched: nowhere; no input sent"),
        (("--switch-roles", "reviewer | pane"), "REFUSED run: switch-unmatched: reviewer | pane; no input sent"),
    ],
)
def test_an_unmatched_exclusion_or_switch_name_prevents_all_input(tmp_path: Path, argv: tuple[str, ...], line: str) -> None:
    """Names match sessions, folders and, for exclusions only, pane labels; any unmatched name refuses the whole run."""
    scenario = Scenario(tmp_path)
    assert scenario.run(*argv) == (1, [line])
    assert scenario.tuios.calls == [LISTING]


def test_an_excluded_checkout_folder_is_skipped_with_no_input(tmp_path: Path) -> None:
    """Excluding the folder skips its whole checkout; the run succeeds."""
    scenario = Scenario(tmp_path)
    assert scenario.run("--except", "CHECKOUT") == (0, [
        f"SKIP checkout: {HEAD}; skip excluded: checkout folder",
        "omitted 2 pane(s) without a prompt-bearing target",
    ])
    assert no_input(scenario)


def test_an_excluded_reviewer_label_lets_only_the_requestor_resume(tmp_path: Path) -> None:
    """An excluded counterpart is never typed into; its requestor still resumes."""
    scenario = Scenario(tmp_path)
    code, lines = scenario.run("--except", "reviewer | pane")
    assert (code, lines[0]) == (0, f"DONE checkout: {HEAD}; {REQUESTOR}: accepted, claimed g2; {REVIEWER}: skipped: excluded")
    assert [call[-1].split(" ", 1)[0] for call in scenario.tuios.inputs()] == ["$llm-shared:resume-session"]


def test_resume_evidence_on_an_excluded_pane_still_suppresses_the_checkout(tmp_path: Path) -> None:
    """A resume typed after the pause in any pane of the checkout, an excluded one included, suppresses it (design)."""
    scenario = Scenario(tmp_path)
    third = scenario.pane(THIRD_PANE, Host.CLAUDE, name="third | pane")
    third.typed.append(("/resume-session", scenario.clock.now()))
    code, lines = scenario.run("--except", "third | pane")
    assert code == 0
    assert lines[0].startswith(f"SKIP checkout: {HEAD}; skip already-resuming; evidence command: resume-session, pane 5b1c0d2e, at ")
    assert no_input(scenario)


@pytest.mark.parametrize(
    ("activity", "reason"),
    [
        (PaneActivity("idle", "user", draft_held=False, question="Proceed?", ready=True), "pane-blocked"),
        (PaneActivity("idle", "", draft_held=True, question="", ready=True), "pane-draft"),
        (WORKING, "pane-busy"),
    ],
)
def test_blocked_draft_and_busy_panes_receive_nothing(tmp_path: Path, activity: PaneActivity, reason: str) -> None:
    """A protected resume target is an expected skip with no input anywhere."""
    scenario = Scenario(tmp_path)
    scenario.requestor.activity = activity
    code, lines = scenario.run()
    assert code == 0
    assert lines[0].startswith(f"SKIP checkout: {HEAD}; skip {reason}: ")
    assert no_input(scenario)


def test_a_reviewer_slot_holding_a_shell_never_gets_a_reviewer_command(tmp_path: Path) -> None:
    """A CMD pane is never reported or typed into as a reviewer; the requestor still resumes."""
    scenario = Scenario(tmp_path)
    scenario.reviewer.record = record(REVIEWER_PANE, None, scenario.root, name="reviewer | pane")
    shell = "no LLM counterpart llm-shared_resume-paused/reviewer | pane 2fd92f30 (saved routing, not validated: target-not-agent)"
    code, lines = scenario.run("--dry-run")
    assert (code, lines[0].split("; ")[-1]) == (0, f"{shell}: skip target-not-agent")
    code, lines = scenario.run()
    assert (code, lines[0]) == (0, f"DONE checkout: {HEAD}; {REQUESTOR}: accepted, claimed g2; {shell}: skipped: target-not-agent")
    assert all("reviewer claude" not in line for line in lines)
    assert len(scenario.tuios.inputs()) == 1


def test_a_single_agent_pause_resumes_across_hosts_without_a_counterpart(tmp_path: Path) -> None:
    """A Claude-authored pause resumes its Codex implementation pane; the marker carries the author override."""
    scenario = Scenario(tmp_path)
    scenario.single()
    code, lines = scenario.run()
    assert (code, lines[0]) == (0, (
        f"DONE checkout: {HEAD}; implementation codex llm-shared_resume-paused/requestor | pane 77e5f39c (saved routing, validated): accepted, prompt consumed"
    ))
    receipt = (scenario.root / ".reviews" / RECEIPT_NAME).read_text(encoding="utf-8")
    assert "- Paused by: claude\n" in receipt
    assert "- Resumed by: chatgpt\n" in receipt


def test_a_switch_naming_a_checkout_without_a_saved_pair_fails_with_no_input(tmp_path: Path) -> None:
    """``--switch-roles`` on a single-agent pause is a classification failure of that checkout."""
    scenario = Scenario(tmp_path)
    scenario.single()
    code, lines = scenario.run("--switch-roles", "checkout")
    assert (code, lines[0]) == (1, f"ERROR checkout: {HEAD}; error switch-not-applicable: no saved requestor pair")
    assert no_input(scenario)


def test_independent_checkouts_and_a_custom_artifact_home_are_planned_separately(tmp_path: Path) -> None:
    """A checkout whose home is declared elsewhere is read there; each prompt-bearing checkout gets its own line."""
    scenario = Scenario(tmp_path)
    scenario.other_checkout("custom", home=".private/reviews")
    code, lines = scenario.run("--dry-run")
    assert code == 0
    assert lines[0].startswith(f"PLAN checkout: {HEAD}; {REQUESTOR}: $llm-shared:resume-session ")
    assert lines[1].startswith(
        f"PLAN custom-checkout: {HEAD}; implementation codex llm-shared_resume-paused/custom | pane 5b1c0d2e (saved routing, validated): "
        f"$llm-shared:resume-session --resume-paused {3:032x}.rp1.{THIRD_PANE}.implementation.",
    )
    assert lines[2] == "omitted 0 pane(s) without a prompt-bearing target; dry run, nothing typed"


def test_a_malformed_receipt_fails_its_checkout_while_an_independent_one_resumes(tmp_path: Path) -> None:
    """Classification errors stay local: the other checkout is still resumed, the run exits 1."""
    scenario = Scenario(tmp_path)
    other = scenario.other_checkout("broken", OTHER_PANE)
    write(other, RECEIPT_NAME, "# Session resume usage receipt\n\n- Schema: 9\n")
    code, lines = scenario.run()
    assert code == 1
    assert lines[0] == (
        f"ERROR broken-checkout: {HEAD.replace('unused', 'error')}; error checkout-unreadable: unsupported usage receipt schema: 9"
    )
    assert lines[1].startswith(f"DONE checkout: {HEAD}; {REQUESTOR}: accepted, claimed g2; ")
    assert OTHER_PANE not in {call[-1] for call in scenario.tuios.inputs()}


def test_a_failed_discovery_or_an_unreadable_history_fails_the_run(tmp_path: Path) -> None:
    """No listing means no input anywhere; unreadable duplicate evidence fails its checkout."""
    scenario = Scenario(tmp_path)
    scenario.tuios.discovery_exit = 1
    assert scenario.run() == (1, ["REFUSED run: discovery-failed; no input sent"])
    scenario.tuios.discovery_exit = 0
    scenario.history.unreadable = {REVIEWER_PANE}
    code, lines = scenario.run()
    assert (code, lines[0]) == (1, f"ERROR checkout: {HEAD}; error duplicate-uncertain: command-history-unreadable {REVIEWER_PANE}")
    assert no_input(scenario)


def test_the_installed_tuitp_grammar_still_reads_a_marked_resume(tmp_path: Path) -> None:
    """The schema 3 receipt keeps the three launcher lines; the prompt keeps its heading and session role line."""
    scenario = Scenario(tmp_path)
    scenario.single()
    assert scenario.run()[0] == 0
    home = scenario.root / ".reviews"
    prompt = (home / PROMPT_NAME).read_bytes()
    lines = prompt.decode("utf-8").splitlines()
    assert lines[0] == "# claude: Resume session: Step 2 tests"
    assert [line for line in lines if line.startswith("- Session role:")] == ["- Session role: implementation"]
    receipt = (home / RECEIPT_NAME).read_text(encoding="utf-8")
    fields = {match[1]: match[2] for line in receipt.splitlines() if (match := LAUNCHER_LINE.fullmatch(line))}
    assert fields == {"Prompt": PROMPT_NAME, "SHA-256": hashlib.sha256(prompt).hexdigest(), "Project root": str(scenario.root)}
    assert receipt.count("- SHA-256: ") == 1
    assert "- Schema: 3\n" in receipt


def test_legacy_pauses_and_manual_resumes_keep_their_reading(tmp_path: Path) -> None:
    """A manual schema 2 receipt reports the prompt used; a prompt without routing is skipped; neither gets input."""
    scenario = Scenario(tmp_path)
    digest = PromptDigest.of(scenario.checkout.prompt).value
    write(scenario.root, RECEIPT_NAME, receipt_text(2, digest, scenario.root))
    code, lines = scenario.run()
    assert (code, lines[0]) == (0, (
        f"SKIP checkout: {HEAD.replace('unused', 'used')}; skip already-used; evidence receipt: claude, pane unknown, at 2026-11-18 07:25"
    ))
    (scenario.root / ".reviews" / RECEIPT_NAME).unlink()
    write(scenario.root, PROMPT_NAME, prompt_text(scenario.root))
    assert scenario.run()[1][0] == f"SKIP checkout: {HEAD}; skip routing-missing; routing unresolved: no target validated or typed into"
    assert no_input(scenario)


def test_a_changed_label_of_the_saved_pane_is_reported_as_a_note(tmp_path: Path) -> None:
    """A changed label of the same validated pane is a report-only note, never a conflict."""
    scenario = Scenario(tmp_path)
    scenario.requestor.record = record(REQUESTOR_PANE, Host.CODEX, scenario.root, name="renamed | pane")
    code, lines = scenario.run("--dry-run")
    assert code == 0
    assert f"{REQUESTOR}: $llm-shared:resume-session " in lines[0]
    assert lines[0].split("; ")[1].endswith("[label-changed]")


# eof
