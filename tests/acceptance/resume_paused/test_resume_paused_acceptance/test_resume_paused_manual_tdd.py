"""Exercise the manual receiver and the launcher's final dispatch check on shared prompt bytes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.acceptance.resume_paused.fakes import REQUESTOR_PANE, REVIEWER_PANE, Scenario
from tools.resume_paused_artifacts import read_checkout_snapshot
from tools.resume_paused_delivery_model import Phase
from tools.resume_paused_dispatch import SharedDelivery, read_dispatch
from tools.resume_paused_manual import main, manual_evidence, record_attempt
from tools.resume_paused_marker import MARKER_FLAG
from tools.resume_paused_models import ArtifactError, SessionRole
from tools.resume_paused_plan_model import ActionKind, PlannedAction
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("phase", [Phase.CLEAR, Phase.RESUME])
def test_manual_attempt_after_planning_blocks_dispatch(tmp_path: Path, phase: Phase) -> None:
    """A previously valid plan cannot reserve clear or resume after another pane registers."""
    scenario = Scenario(tmp_path)
    scenario.single()
    snapshot = read_checkout_snapshot(scenario.root)
    assert snapshot.prompt
    role = SessionRole.IMPLEMENTATION
    marker = scenario.checkout.marker(REQUESTOR_PANE, role, "1" * 32, live=None)
    pane = scenario.requestor.record
    command = f"$llm-shared:resume-session {MARKER_FLAG} {marker.render()}"
    action = PlannedAction(ActionKind.RESUME, role, Host.CODEX, pane.session, pane.pane_id, pane.name, command)
    record_attempt(snapshot, "resume-session", Host.CLAUDE, REVIEWER_PANE, scenario.guard)
    with pytest.raises(ArtifactError, match="manual-resume-attempt"):
        SharedDelivery(scenario.runtime().exchanges).check(pane, action, phase, snapshot.prompt.digest)
    assert read_dispatch(snapshot, phase) is None


def test_repeated_attempt_keeps_first_pane_and_scopes_to_prompt_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The receiver entry point keeps the first source, and a replacement prompt starts independently."""
    scenario = Scenario(tmp_path)
    snapshot = read_checkout_snapshot(scenario.root)
    monkeypatch.chdir(scenario.root)
    for pane, host in [(REVIEWER_PANE, "claude"), (REQUESTOR_PANE, "codex")]:
        monkeypatch.setenv("TUIOS_PANE_ID", pane)
        assert main(["--host", host, "--command", "resume-session"]) == 0
    first = manual_evidence(snapshot)
    assert first
    assert first.pane_id == REVIEWER_PANE
    assert first.detail == "resume-session (claude)"
    scenario.single()
    assert manual_evidence(read_checkout_snapshot(scenario.root)) is None


def test_guard_contention_and_damaged_registration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A held checkout refuses registration. A partial or invalid record still prevents a bulk send."""
    scenario = Scenario(tmp_path)
    snapshot = read_checkout_snapshot(scenario.root)
    with scenario.guard.acquire(snapshot.root), pytest.raises(ArtifactError, match="manual-resume-guard-held"):
        record_attempt(snapshot, "resume-session", Host.CODEX, None, scenario.guard)
    assert manual_evidence(snapshot) is None
    assert snapshot.home
    path = snapshot.home / record_attempt(snapshot, "resume-session", Host.CODEX, None, scenario.guard)
    path.write_text('{"at":"2026-11-27T09:00:00+00:00","command":"bad","host":"codex","pane":null}', encoding="utf-8")
    with pytest.raises(ArtifactError, match="manual-attempt-unreadable"):
        manual_evidence(snapshot)
    monkeypatch.chdir(scenario.root)
    monkeypatch.setenv("TUIOS_PANE_ID", "bad-pane")
    assert main(["--command", "resume-session", "--host", "codex"]) == 1


def test_missing_prompt_needs_no_registration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Unrouted manual sessions continue through their ordinary receiver checks."""
    monkeypatch.chdir(tmp_path)
    assert main(["--command", "resume-session", "--host", "codex"]) == 0
    with pytest.raises(ArtifactError, match="manual-attempt-unreadable"):
        manual_evidence(read_checkout_snapshot(tmp_path))


# eof
