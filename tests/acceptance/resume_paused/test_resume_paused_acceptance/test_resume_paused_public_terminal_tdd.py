"""Exercise the shipping terminal adapters and marked receiver against temporary checkout artifacts."""

from __future__ import annotations

import io
from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.resume_paused.fakes import (
    NATURES,
    REQUESTOR_PANE,
    REVIEWER_PANE,
    THIRD_PANE,
    Scenario,
    record,
    scenario_routing,
    single_agent,
)
from tools import resume_paused as cli
from tools.resume_paused_artifacts import read_checkout_snapshot
from tools.resume_paused_claim import marked_claim_verifier
from tools.resume_paused_delivery_model import Phase
from tools.resume_paused_dispatch import read_dispatch
from tools.resume_paused_evidence import ScreenVerdict
from tools.resume_paused_input import CarriedIdentity, TuiosDiscovery
from tools.resume_paused_marker import marker_in_command
from tools.resume_paused_models import RECEIPT_NAME, SessionRole
from tools.resume_paused_profiles import Host
from tools.resume_paused_terminal import COMMANDS, clear_observed, editor_state
from tools.resume_paused_transport import TuiosTransport
from tools.resume_paused_validation import ValidationRequest, default_validator
from tools.review_exchange_models import ReviewRole
from tools.review_exchange_models_coordination import MarkedClaimEvidence
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from pathlib import Path

    from tests.acceptance.resume_paused.fakes import FakePane
    from tools.resume_paused_models import CanonicalRoot

CODEX = ("\x1b[1m\u203a\x1b[0m \x1b[2mAsk Codex to do anything\x1b[0m    ", "", "  model and checkout", "  ? for shortcuts")
BORDER = "─" * 80
CLAUDE = (BORDER, "\u276f\xa0\x1b[2mTry running the tests\x1b[0m    ", BORDER, "  ? for shortcuts")
EDITORS = {Host.CLAUDE: CLAUDE, Host.CODEX: CODEX}


def receive(scenario: Scenario, host: Host, command: str) -> None:
    """Validate the delivered text and perform the receiver's receipt and locked claim writes."""
    marker = marker_in_command(command)
    env = {"TUIOS_PANE_ID": marker.pane_id}
    validator = default_validator(env, scenario.checkout.clock.now)
    validator.discovery = TuiosDiscovery(scenario.tuios)
    result = validator.validate(ValidationRequest(scenario.root, command, host))
    assert result.valid, result.reasons
    if command.startswith(COMMANDS[host].resume + " "):
        scenario.checkout.consume(marker)
    if marker.role in {SessionRole.REVIEWER, SessionRole.REQUESTOR}:
        carried = CarriedIdentity(marker.pane_id, marker.launch_id) if host is Host.CODEX else None
        role = ReviewRole(marker.role.value)
        verifier = marked_claim_verifier(scenario.root, marker.render(), role, host, carried, environ=env)
        claim_selected(scenario.checkout.core, role, NATURES[host], round_number=1, occurrence=1, override=True, marked=verifier)


def configure(scenario: Scenario, pane: FakePane, host: Host) -> None:
    """Show physical editor rows and attach a receiver with the pane's exact terminal identity."""
    pane.screen = pane.physical_editor = EDITORS[host]
    pane.agent = partial(receive, scenario, host)


def run(scenario: Scenario, *args: str) -> tuple[int, str]:
    """Invoke main with the public adapters over the scenario's fake terminal."""
    runtime = scenario.runtime()
    runtime = replace(runtime, hosts=cli.terminal_hosts(scenario.tuios.runner_for, runtime.exchanges))
    out = io.StringIO()
    code = cli.main(list(args), stdout=out, runtime=lambda: runtime)
    return code, out.getvalue()


@pytest.mark.parametrize("host", list(EDITORS))
def test_clear_and_resume_with_a_bound_receipt(tmp_path: Path, host: Host) -> None:
    """Both native clear/resume pairs produce a bound receipt."""
    scenario = Scenario(tmp_path)
    scenario.checkout.publish(scenario_routing(scenario.root, single_agent(host=host)), role="implementation")
    pane = scenario.pane(REQUESTOR_PANE, host)
    configure(scenario, pane, host)
    code, report = run(scenario, "--clear")
    assert code == 0, report
    assert "cleared, accepted, prompt consumed" in report
    clear, resume = scenario.tuios.inputs()
    assert clear[-1] == COMMANDS[host].clear
    assert resume[-1].startswith(COMMANDS[host].resume + " ")
    assert all(call[call.index("--confirm") + 1] == "fake-selection" for call in (clear, resume))
    assert (scenario.root / ".reviews" / RECEIPT_NAME).is_file()


def test_a_copied_preview_cannot_authorize_a_receiver(tmp_path: Path) -> None:
    """Preview prints the command but supplies no dispatch reservation."""
    scenario = Scenario(tmp_path)
    scenario.single()
    configure(scenario, scenario.requestor, Host.CODEX)
    code, report = run(scenario, "--dry-run")
    assert code == 0
    command = COMMANDS[Host.CODEX].resume + report.split(COMMANDS[Host.CODEX].resume, 1)[1].splitlines()[0]
    validator = default_validator({"TUIOS_PANE_ID": REQUESTOR_PANE}, scenario.checkout.clock.now)
    validator.discovery = TuiosDiscovery(scenario.tuios)
    assert read_dispatch(read_checkout_snapshot(scenario.root), Phase.RESUME) is None
    assert validator.validate(ValidationRequest(scenario.root, command, Host.CODEX)).reasons == ("dispatch-mismatch",)
    assert not scenario.tuios.inputs()


def test_lost_send_is_reserved_across_launches(tmp_path: Path) -> None:
    """A stalled ask without a receipt or owned editor never types a second time."""
    scenario = Scenario(tmp_path)
    scenario.single()
    configure(scenario, scenario.requestor, Host.CODEX)
    scenario.requestor.typing = "drop"
    code, report = run(scenario)
    assert code == 1
    assert "acceptance-unproved" in report
    calls = scenario.tuios.inputs()
    assert len(calls) == 1
    run(scenario)
    assert scenario.tuios.inputs() == calls


@pytest.mark.parametrize(("host", "prefix"), [(Host.CLAUDE, "⏺ "), (Host.CODEX, "• "), (Host.CODEX, "• Expected output: ")])
def test_receiver_failure_before_receipt(tmp_path: Path, host: Host, prefix: str) -> None:
    """Only a complete failure line from this launch ends the acceptance wait."""
    scenario = Scenario(tmp_path)
    scenario.checkout.publish(scenario_routing(scenario.root, single_agent(host=host)), role="implementation")
    pane = scenario.pane(REQUESTOR_PANE, host)
    configure(scenario, pane, host)

    def fail(command: str) -> None:
        launch = marker_in_command(command).launch_id
        pane.screen = (f"resume-paused {'f' * 32} failed", f"\x1b[1m{prefix}\x1b[0mresume-paused {launch} failed", *EDITORS[host])

    pane.agent = fail
    code, report = run(scenario)
    assert code == 1, report
    assert ("acceptance-unproved" if "Expected" in prefix else "receiver-failed") in report
    assert len(scenario.tuios.inputs()) == 1


@pytest.mark.parametrize("reason", ["", "reviewer-wait-active", "reviewer-wait-unknown"])
def test_reviewer_activation_observes_current_waiters(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, reason: str) -> None:
    """Only a claimed requestor and an observable absence of live waiters allow a second claim."""
    scenario = Scenario(tmp_path)
    marker = scenario.checkout.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, "1" * 32)
    scenario.checkout.consume(marker)
    evidence = MarkedClaimEvidence(marker.launch_id, marker.pane_id, "codex", marker.binding, 1, 1)
    claim_selected(scenario.checkout.core, ReviewRole.REQUESTOR, NATURES[Host.CODEX], round_number=1, occurrence=1, override=True, marked=lambda _record, _occurrence: evidence)
    configure(scenario, scenario.requestor, Host.CODEX)
    configure(scenario, scenario.reviewer, Host.CLAUDE)

    def waiter(_root: CanonicalRoot) -> str:
        return reason

    monkeypatch.setattr(cli, "waiter_reason", waiter)
    code, report = run(scenario)
    assert code == 0, report
    if reason:
        assert reason in report
        assert not scenario.reviewer.typed
    else:
        assert "claimed g3" in report
        assert scenario.reviewer.typed[0][0].startswith("/review-resume ")


@pytest.mark.parametrize("change", ["stable", "draft", "ownership"])
def test_recovery_requires_unchanged_owned_input(tmp_path: Path, change: str) -> None:
    """A changed editor or generation between the two captures prevents the single recovery Enter."""
    scenario = Scenario(tmp_path)
    if change != "ownership":
        scenario.single()
    pane = scenario.requestor
    configure(scenario, pane, Host.CODEX)
    pane.typing = "hold"

    def intervene() -> None:
        scenario.clock.after_sleep = scenario.tuios.flush
        if change == "draft":
            pane.screen = ("\u203a replacement", *CODEX[1:])
        if change == "ownership":
            claim_selected(scenario.checkout.core, ReviewRole.REVIEWER, NATURES[Host.CLAUDE], round_number=1, occurrence=1, override=True)

    scenario.clock.after_sleep = intervene
    code, report = run(scenario)
    inputs = [call[1] for call in scenario.tuios.inputs()]
    if change == "stable":
        assert code == 0, report
        assert inputs == ["ask-agent", "send-keys"]
        assert "prompt consumed" in report
    else:
        assert code == 1, report
        assert inputs == ["ask-agent"]
        assert "recovery-withheld" in report


@pytest.mark.parametrize("damage", ["screen", "dispatch"])
def test_one_damaged_checkout_leaves_the_other_runnable(tmp_path: Path, damage: str) -> None:
    """A changed terminal layout or a partial reservation blocks only its own checkout."""
    scenario = Scenario(tmp_path)
    scenario.single()
    configure(scenario, scenario.requestor, Host.CODEX)
    root = scenario.other_checkout("other")
    pane = scenario.tuios.panes[THIRD_PANE]
    if damage == "dispatch":
        pane.screen = CODEX
        snapshot = read_checkout_snapshot(root)
        assert snapshot.prompt
        digest = snapshot.prompt.digest.value
        (root / ".reviews" / f"a.resume-paused.{digest}.resume.local.json").write_text("{", encoding="utf-8")
    code, report = run(scenario)
    assert code == 1, report
    assert "prompt consumed" in report
    assert not pane.typed
    assert len(scenario.tuios.inputs()) == 1


def test_selector_confirmation_for_a_different_pane_refuses_input(tmp_path: Path) -> None:
    """Even a nonempty selector token cannot authorize an ask for another UUID."""
    scenario = Scenario(tmp_path)
    transport = TuiosTransport(scenario.tuios.runner_for, physical=True)
    selected = transport.select([scenario.requestor.record], scenario.requestor.record)
    assert selected.selector
    outcome = transport.ask(selected.selector, "command", 5, REVIEWER_PANE)
    assert outcome.refusal == "selector-confirmation-unavailable"
    assert not scenario.tuios.inputs()


@pytest.mark.parametrize("host", list(EDITORS))
def test_a_changed_session_still_needs_an_empty_editor(tmp_path: Path, host: Host) -> None:
    """Styled suggestion and ordinary typed text have the same wording but different meanings."""
    original = replace(record(REQUESTOR_PANE, host, tmp_path), agent_session_id="before")
    current = replace(original, agent_session_id="after")
    empty = EDITORS[host]
    typed = tuple(row.replace("\x1b[2m", "") for row in empty)
    assert editor_state(host, typed) is ScreenVerdict.DRAFT
    assert not clear_observed(host, empty, typed, original, current)
    assert clear_observed(host, empty, empty, original, current)


# eof
