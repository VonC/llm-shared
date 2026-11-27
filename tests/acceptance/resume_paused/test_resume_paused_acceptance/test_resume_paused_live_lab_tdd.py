"""Exercise the guest acceptance verifier with isolated artifacts and synthetic pane inventory."""

from __future__ import annotations

import json
import subprocess
from dataclasses import replace
from typing import TYPE_CHECKING
from unittest.mock import Mock
from uuid import UUID

import pytest

from tests.acceptance.resume_paused import live_guest, live_lab
from tests.acceptance.resume_paused.fakes import FakePane, Scenario, record
from tests.acceptance.resume_paused.live_cases import CASES, DELIVER, Row
from tests.acceptance.resume_paused.live_checks import (
    Observation,
    check_delta,
    check_receiver,
    check_reports,
    observe,
)
from tests.acceptance.resume_paused.live_faults import Fault
from tests.acceptance.resume_paused.live_fixtures import (
    LABELS,
    SESSIONS,
    inventory,
    seed,
)
from tests.acceptance.resume_paused.live_power import waiter_arguments
from tests.acceptance.resume_paused.test_resume_paused_acceptance.test_resume_paused_public_terminal_tdd import (
    EDITORS,
    run,
)
from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    receipt_text,
)
from tests.unit.tools.test_review_exchange_lifecycle.test_review_exchange_lifecycle_tdd import (
    _harness,
)
from tools.llm_nature import LlmNature
from tools.resume_paused_artifacts import read_checkout_snapshot
from tools.resume_paused_delivery_model import Phase
from tools.resume_paused_dispatch import Dispatch
from tools.resume_paused_evidence import read_session_journal
from tools.resume_paused_marker import LiveExchange, Marker, resolve_assignment
from tools.resume_paused_models import RECEIPT_NAME, SessionRole
from tools.resume_paused_profiles import CommandResult, Host
from tools.resume_paused_transport import enter_arguments, resolve_selector
from tools.review_exchange_cli_parser import parser_for
from tools.review_exchange_models import ReviewRole
from tools.review_exchange_models_coordination import MarkedClaimEvidence
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from pathlib import Path

    from tools.resume_paused_input import PaneRecord


def _inventory(lab: Path) -> dict[str, PaneRecord]:
    for root in ("alpha", "bravo"):
        (lab / root).mkdir()
    (lab / "bravo/.review-artifacts.ini").write_text("[review-artifacts]\nhome = .lab-reviews\n", encoding="utf-8")
    records = tuple(record(str(UUID(int=index)), Host(label.split()[0].lower()), lab / SESSIONS[session][0], name=label, session=session)
                    for index, (label, session) in enumerate(LABELS.items(), start=1))
    return inventory(lab, records)


@pytest.mark.parametrize("case", ["bulk", "pair", "switch", "hibernate", "routes", "damaged"])
def test_seed_uses_the_actual_panes_and_artifact_home(tmp_path: Path, case: str) -> None:
    """The exact review parses as pending and both default and custom homes resolve their intended pause."""
    panes = _inventory(tmp_path)
    digests = seed(tmp_path, case, panes)
    for name, digest in digests.items():
        snapshot = read_checkout_snapshot(tmp_path / name)
        if case == "damaged" and name == "alpha":
            assert snapshot.diagnostic
        else:
            assert snapshot.prompt
            assert snapshot.prompt.digest.value == digest
    if "bravo" in digests:
        assert (tmp_path / "bravo/.lab-reviews").is_dir()


def test_waiter_uses_independent_guest_document(tmp_path: Path) -> None:
    """Exercise the real CLI parser against the separate hibernation waiter fixture."""
    seed(tmp_path, "hibernate", _inventory(tmp_path))
    args = waiter_arguments(tmp_path / "alpha")
    options = parser_for("wait-request").parse_args(args[3:])
    assert options.document.endswith("plan.v0.1.0.lab-waiter.md")
    assert options.timeout_seconds == int(args[-1])


def test_native_pair_adoption_keeps_prompt_and_checks_reviewer(tmp_path: Path) -> None:
    """A native paired pause must carry the exact counterpart recorded by the lab."""
    panes = _inventory(tmp_path)
    digests = seed(tmp_path, "pair", panes)
    assert seed(tmp_path, "capture-pair", panes) == digests
    panes["Claude primary"] = panes["Claude secondary"]
    with pytest.raises(AssertionError):
        seed(tmp_path, "capture-pair", panes)


@pytest.mark.parametrize("verdict", ["pass", "fail"])
def test_live_verdict_requires_and_preserves_operator_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], verdict: str,
) -> None:
    """A completed recovery can still fail if the expected reply never appeared."""
    (tmp_path / "case.json").write_text('{"case":"recovery"}', encoding="utf-8")
    with pytest.raises(AssertionError, match="Complete the command steps"):
        live_lab._verdict(tmp_path)
    step = tmp_path / "step-1"
    step.mkdir()
    (step / "passed.json").touch()
    live_lab._status(tmp_path)
    assert "Awaiting operator observation" in capsys.readouterr().out
    note = "Saw RP-ACK-alpha in Codex peer" if verdict == "pass" else "Codex peer never replied"
    prompt = Mock(side_effect=[verdict, note])
    monkeypatch.setattr("builtins.input", prompt)
    for _ in range(2):
        if verdict == "pass":
            live_lab._verdict(tmp_path)
            assert "PASS recovery" in capsys.readouterr().out
        else:
            with pytest.raises(AssertionError, match=note):
                live_lab._verdict(tmp_path)
    assert json.loads((tmp_path / "observation.json").read_text(encoding="utf-8")) == {"case": "recovery", "verdict": verdict, "note": note}


def test_history_records_only_a_prior_cross_host_resume(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Both pauses remain unused and only bravo has evidence from a different agent."""
    panes = _inventory(tmp_path)
    journal = tmp_path / "journal.md"
    monkeypatch.setattr(live_lab, "_panes", Mock(return_value=panes))
    monkeypatch.setattr(live_lab, "journal_path", Mock(return_value=journal))
    live_lab._seed_case(tmp_path, "history", "boot")
    prompt = read_checkout_snapshot(tmp_path / "alpha").prompt
    assert prompt
    assert prompt.author == "gemini"
    assert not observe(tmp_path / "alpha", journal).resumes
    (resumed,) = observe(tmp_path / "bravo", journal).resumes
    assert resumed.startswith("chatgpt ")


def test_inventory_rejects_a_duplicate_uuid(tmp_path: Path) -> None:
    """Two Codex labels cannot share one pane."""
    panes = _inventory(tmp_path)
    panes["Codex peer"] = replace(panes["Codex peer"], pane_id=panes["Codex primary"].pane_id)
    with pytest.raises(AssertionError, match="Ambiguous pane UUID"):
        inventory(tmp_path, tuple(panes.values()))


@pytest.mark.parametrize("origin", ["codex.exe", "claude.exe"])
def test_agent_is_refused_before_any_launcher_query(monkeypatch: pytest.MonkeyPatch, origin: str) -> None:
    """Even the preflight cannot start a process from a recognized agent."""
    monkeypatch.setattr(live_guest, "process_ancestry", lambda: [origin])
    command = Mock()
    monkeypatch.setattr(live_guest, "run", command)
    if live_guest.os.name == "nt":
        with pytest.raises(AssertionError, match="human Windows Terminal"):
            live_guest.guest()
    else:
        with pytest.raises(AssertionError, match="Requires Windows"):
            live_guest.guest()
    command.assert_not_called()


@pytest.mark.parametrize(("fresh", "records", "saved_ledger"), [
    (True, [{"name": "personal"}], False), (True, [{"name": "saved", "saved": True}], False),
    (True, [], True), (False, [{"name": name, "saved": True} for name in SESSIONS], False),
])
def test_foreign_or_saved_namespace_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, fresh: bool, records: list[dict[str, object]], saved_ledger: bool) -> None:
    """Fresh and running preconditions refuse before reconciliation."""
    ledger = tmp_path / "state.json"
    if saved_ledger:
        ledger.touch()
    monkeypatch.setattr(live_guest, "run", Mock(return_value=subprocess.CompletedProcess([], 0, json.dumps(records), "")))
    monkeypatch.setattr(live_guest, "executable", Mock(return_value=tmp_path / "unused"))
    with pytest.raises(AssertionError):
        live_guest.check_namespace(tmp_path, ledger, fresh=fresh)


def test_live_ledger_checks_tabs_and_session_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A valid layout passes, and an extra tab refuses even with the correct pane set."""
    ledger = tmp_path / "state.json"
    sessions = {name: {"name": name, "folder": str(tmp_path / root), "kind": kind, "id": label, "status": "ready"}
                for name, (root, kind, label) in SESSIONS.items()}
    tab = {"spec": {"kind": "tuios", "title": "Acceptance", "window": "resume-lab", "sessions": list(SESSIONS)}}
    state = {"version": 1, "sessions": sessions, "tabs": {"first": tab}}
    ledger.write_text(json.dumps(state), encoding="utf-8")
    (tmp_path / "tuitp.list").write_text(live_guest.LAYOUT, encoding="utf-8")
    monkeypatch.setattr(live_guest, "run", Mock(return_value=subprocess.CompletedProcess([], 0, json.dumps(list(sessions.values())), "")))
    monkeypatch.setattr(live_guest, "executable", Mock(return_value=tmp_path / "unused"))
    live_guest.check_namespace(tmp_path, ledger, fresh=False)
    ledger.write_text(json.dumps(state | {"tabs": {"first": tab, "foreign": tab}}), encoding="utf-8")
    with pytest.raises(AssertionError, match="Acceptance tab"):
        live_guest.check_namespace(tmp_path, ledger, fresh=False)


@pytest.mark.parametrize("case", ["bulk", "clear", "names", "routes", "history"])
def test_live_cases_accept_shipping_reports(tmp_path: Path, case: str) -> None:
    """Run the lab's actual seeded roots and read-only steps through the public adapters with fake TUIOS."""
    panes = _inventory(tmp_path)
    seed(tmp_path, case, panes)
    scenario = Scenario(tmp_path)
    scenario.tuios.panes.clear()
    for pane in panes.values():
        editor = EDITORS[Host(pane.name.split()[0].lower())]
        scenario.tuios.add(FakePane(pane, screen=editor, physical_editor=editor))
    if case == "history":
        live_lab.record_prior_resume(tmp_path / "bravo", scenario.journal)
        scenario.sessions = read_session_journal(scenario.journal)
    steps = CASES[case] if case == "names" else CASES[case][:1]
    for step in steps:
        check_reports(step, [run(scenario, *step.args)])
    assert not scenario.tuios.inputs()


def test_concurrent_report_requires_one_winner_per_checkout() -> None:
    """A split win is valid. Two skipped roots or two winning launches are failures."""
    step = CASES["concurrent"][0]
    first = (0, "DONE alpha: accepted\nSKIP bravo: guard held")
    second = (0, "SKIP alpha: already-resuming\nDONE bravo: accepted")
    check_reports(step, [first, second])
    with pytest.raises(AssertionError, match="matching report"):
        check_reports(step, [first, first])


@pytest.mark.parametrize("output", ["", "DONE alpha broken", "DONE alpha: accepted\nDONE alpha: accepted"])
def test_invalid_reports_cannot_pass(output: str) -> None:
    """Missing, malformed and duplicate output all fail verification."""
    with pytest.raises(AssertionError):
        check_reports(CASES["capture"][-1], [(0, output)])


def test_changed_readonly_and_extra_dispatch_are_detected() -> None:
    """Concurrent reservations for distinct digests cannot disappear behind a common phase."""
    before = Observation({}, {}, [])
    after = Observation({"private": "changed"}, {}, [])
    with pytest.raises(AssertionError, match="protected checkout"):
        check_delta(before, after, Row("SKIP"), "chatgpt")
    after = Observation({}, {f"a.resume-paused.{d}.resume.local.json": "bytes" for d in ("a", "b")}, ["chatgpt t"])
    with pytest.raises(AssertionError, match="New dispatch"):
        check_delta(before, after, DELIVER, "chatgpt")


def test_receipt_must_match_the_selected_codex_peer(tmp_path: Path) -> None:
    """A correct digest and host do not authorize a receipt from the other Codex pane."""
    panes = _inventory(tmp_path)
    digest = seed(tmp_path, "bulk", panes)["alpha"]
    root = tmp_path / "alpha"
    snapshot = read_checkout_snapshot(root)
    assert snapshot.routing
    assert snapshot.routing.routing
    assert snapshot.prompt
    assert snapshot.home
    role = SessionRole.IMPLEMENTATION
    pane = panes["Codex peer"]
    assignment = resolve_assignment(snapshot.routing.routing, snapshot.prompt.digest, pane.pane_id, role, None)
    marker = Marker("a" * 32, pane.pane_id, role, assignment.digest())
    dispatch = Dispatch(f"$llm-shared:resume-session --resume-paused {marker.render()}", None)
    dispatch.save(snapshot.home / f"a.resume-paused.{digest}.{Phase.RESUME}.local.json")
    fields: dict[str, str | None] = {"Launch id": marker.launch_id, "Assignment binding": marker.binding, "Receiving pane": pane.pane_id, "Resumed by": "chatgpt"}
    path = snapshot.home / RECEIPT_NAME
    path.write_text(receipt_text(3, digest, root, fields), encoding="utf-8")
    check_receiver(root, "bulk", digest, DELIVER, panes)
    fields["Receiving pane"] = panes["Codex primary"].pane_id
    path.write_text(receipt_text(3, digest, root, fields), encoding="utf-8")
    with pytest.raises(AssertionError, match="receipt missing"):
        check_receiver(root, "bulk", digest, DELIVER, panes)


def test_reviewer_proof_requires_the_reserved_generation(tmp_path: Path) -> None:
    """A real reviewer claim with the right launch and pane still needs to follow its reservation."""
    panes = _inventory(tmp_path)
    digest = seed(tmp_path, "pair", panes)["alpha"]
    root = tmp_path / "alpha"
    snapshot = read_checkout_snapshot(root)
    assert snapshot.home
    assert snapshot.prompt
    assert snapshot.routing
    assert snapshot.routing.routing
    pane = panes["Claude primary"]
    role = SessionRole.REVIEWER
    assignment = resolve_assignment(snapshot.routing.routing, snapshot.prompt.digest, pane.pane_id, role, LiveExchange(1, 1))
    marker = Marker("e" * 32, pane.pane_id, role, assignment.digest())
    command = f"/review-resume --resume-paused {marker.render()}"
    path = snapshot.home / f"a.resume-paused.{digest}.reviewer.local.json"
    core, _, _, _ = _harness(root)
    evidence = MarkedClaimEvidence(marker.launch_id, pane.pane_id, "claude", marker.binding, 1, 1)
    claim_selected(core, ReviewRole.REVIEWER, LlmNature.CLAUDE, round_number=1, occurrence=1, override=True, marked=lambda _record, _occurrence: evidence)
    Dispatch(command, 1).save(path)
    row = Row("DONE", phases=("reviewer",))
    check_receiver(root, "pair", digest, row, panes)
    path.unlink()
    Dispatch(command, 3).save(path)
    with pytest.raises(AssertionError, match="reserved generation"):
        check_receiver(root, "pair", digest, row, panes)


def test_changed_fixture_stops_before_launch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An unexpected pause in the second checkout cannot be discovered by a live child."""
    panes = _inventory(tmp_path)
    digests = seed(tmp_path, "bulk", panes)
    command = Mock()
    monkeypatch.setattr(live_lab, "_logs", command)
    monkeypatch.setattr(live_lab, "journal_path", Mock(return_value=tmp_path / "journal.md"))
    with pytest.raises(AssertionError, match="unexpected pause in bravo"):
        live_lab._step(tmp_path, "bulk", 0, {"alpha": digests["alpha"]}, panes)
    command.assert_not_called()


@pytest.mark.parametrize("case", ["stall", "recovery"])
def test_fault_injector_only_touches_the_bound_target(tmp_path: Path, case: str) -> None:
    """The lost ask sends nothing. The unsubmitted ask pastes once and permits only the production Enter."""
    pane = _inventory(tmp_path)["Codex peer"]
    marker = Marker("a" * 32, pane.pane_id, SessionRole.IMPLEMENTATION, "b" * 64)
    text = f"$llm-shared:resume-session --resume-paused {marker.render()}"
    args = ("tuios", "ask-agent", "--select", resolve_selector([pane], pane).selector or "", "--confirm", "token", "--", text)
    delegate = Mock()
    delegate.run.return_value = CommandResult(0, "")
    fault = Fault(case, pane)
    fault.send(delegate, args)
    if case == "stall":
        delegate.run.assert_not_called()
    else:
        delegate.run.assert_called_once_with(("tuios", "send-text", "-s", pane.session, "-w", pane.pane_id, text))
        fault.send(delegate, enter_arguments(pane.session, pane.pane_id))
        assert fault.operations == ["paste", "enter"]
    with pytest.raises(AssertionError):
        fault.send(delegate, args)


@pytest.mark.parametrize("success", [True, False])
def test_dispatch_checkpoint_and_failure_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, success: bool) -> None:
    """Exercise the real step controller. An unexpected child report locks the failed attempt with its evidence."""
    panes = _inventory(tmp_path)
    digests = seed(tmp_path, "bulk", panes)
    monkeypatch.setattr(live_lab, "journal_path", Mock(return_value=tmp_path / "journal.md"))
    monkeypatch.setattr(live_lab, "_logs", Mock(return_value=(0, "PLAN alpha: $llm-shared:resume-session\nPLAN bravo: /resume-session" if success else "")))
    if success:
        live_lab._step(tmp_path, "bulk", 0, digests, panes)
        assert live_lab._next_index(tmp_path, "bulk") == 1
    else:
        with pytest.raises(AssertionError, match="Missing checkout"):
            live_lab._step(tmp_path, "bulk", 0, digests, panes)
        with pytest.raises(AssertionError, match="Interrupted or failed"):
            live_lab._next_index(tmp_path, "bulk")
    assert (tmp_path / "step-1/immediate-alpha.json").is_file()
    assert (tmp_path / "step-1/passed.json").exists() == success


# eof
