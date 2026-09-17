"""Native gating and bounded windows for Claude controlled observations."""

# ruff: noqa: PLR2004 - Fixed protocol timestamps are the assertions' evidence.

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    manifest_data,
)
from tools.wait_evidence import claude_observer
from tools.wait_evidence.claude_monitor import consume, deliver, prepare
from tools.wait_evidence.claude_observer import ClaudeObservation
from tools.wait_evidence.models import EvidenceRecord, JsonObject
from tools.wait_evidence.probe_driver import save
from tools.wait_evidence.prototype import Prototype

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.timeout(10)


def observation(root: Path, mode: str = "trial", arm: str = "B-prototype") -> ClaudeObservation:
    """Prepare a small explicit run without launching a host or wall-clock timer."""
    directory = root / "a.shared-wait-service" / "claude"
    directory.mkdir(parents=True)
    data = manifest_data(root)
    data.update(host="claude", build="2.1.273", schema="claude-native-2.1.273", model="claude-opus-5",
                source_seconds=240, baseline_seconds=600, mode=mode, arm=arm, wait_id="wait", event_id="event",
                monitor_schema={"type": "object"}, configuration={"effort": "xhigh", "permission_mode": "auto"})
    prompt = prepare(directory, data)
    save(directory / "manifest.json", data)
    (directory / "benchmark.txt").write_text(prompt, encoding="utf-8")
    registration: JsonObject = {key: data[key] for key in ("thread", "source_id", "wait_id", "event_id", "profile")}
    registration.update(source_start=20, due_at=260, baseline=mode == "baseline")
    Prototype.create(directory, registration)
    save(directory / "registration.json", registration)
    save(directory / "bridge-armed.json", registration)
    return ClaudeObservation(directory)


def emit(observer: ClaudeObservation, kind: str, at: float, data: JsonObject) -> None:
    """Feed normalized native evidence through the observer's real dispatch."""
    observer.native(EvidenceRecord(str(at) + kind, kind, at, at, "native:fixture", data, synthetic=False))


def prompt(observer: ClaudeObservation) -> None:
    """Bind the registering turn to the exact prepared human input."""
    emit(observer, "native_user", 10, {"origin": "human", "native_uuid": "human", "text": observer.prompt})


def arm(observer: ClaudeObservation) -> None:
    """Use a loaded schema, exact Monitor invocation and correlated success."""
    prompt(observer)
    emit(observer, "native_observation", 11, {"attachment": {"type": "deferred_tools_record", "entries": [
        {"name": "Monitor", "input_schema": observer.raw["monitor_schema"]},
    ]}})
    emit(observer, "tool_call", 21, {"name": "Monitor", "call_id": "monitor", "input": observer.raw["monitor_input"], "turn_id": "human"})
    emit(observer, "tool_result", 22, {"call_id": "monitor", "is_error": False, "content": "Monitor started (task task1, expires in 20m)"})
    emit(observer, "native_turn_complete", 30, {"turn_id": "human", "last_agent_message": observer.raw["armed_marker"]})


class TestClaudeGate:
    """Require native successful registration before any event can be handed off."""

    def test_gate_event_receipt_useful_final_and_separate_windows(self, tmp_path: Path) -> None:
        """Receipt alone cannot count as useful; final alone cannot finish collection."""
        observer = observation(tmp_path)
        arm(observer)
        assert observer.prototype.snapshot()["normal_end_at"] == 30
        assert observer.prototype.advance(259, observer.route) == "waiting"
        assert observer.prototype.advance(260, observer.route) == "accepted"
        event = json.loads((observer.directory / "event.json").read_text())
        assert observer.useful_at is None
        emit(observer, "native_user", 262, {"origin": "task-notification", "native_uuid": "wake", "text":
             "<task-notification><task-id>task1</task-id><summary>Monitor event</summary><event>" + json.dumps(event) + "</event></task-notification>"})
        emit(observer, "tool_call", 265, {"name": "PowerShell", "call_id": "consume", "turn_id": "wake",
                                          "input": {"command": f"& '{observer.directory.as_posix()}/consume.ps1'"}})
        assert observer.useful_at == 265
        consume(observer.directory)
        emit(observer, "native_turn_complete", 270, {"turn_id": "wake", "last_agent_message": "WAIT_TEST_DONE"})
        assert observer.deadline(300) == 510
        assert observer.drain_boundary() == 390
        assert not observer.errors

    @pytest.mark.parametrize("fault", ["schema", "input", "result", "parent", "missing-bridge"])
    def test_incomplete_monitor_evidence_cannot_arm(self, tmp_path: Path, fault: str) -> None:
        """Do not infer successful registration from a marker or a tool name."""
        observer = observation(tmp_path)
        if fault == "schema":
            observer.raw["monitor_schema"] = {"other": True}
        arm(observer)
        # A second mismatching gate is retained as invalid, never repaired.
        if fault == "input":
            emit(observer, "tool_call", 31, {"name": "Monitor", "call_id": "other", "input": {}, "turn_id": "human"})
        elif fault == "result":
            emit(observer, "tool_result", 31, {"call_id": "monitor", "is_error": True, "content": "failed"})
        elif fault == "parent":
            emit(observer, "native_turn_complete", 31, {"turn_id": "wrong", "last_agent_message": observer.raw["armed_marker"]})
        elif fault == "missing-bridge":
            (observer.directory / "bridge-armed.json").unlink()
            emit(observer, "native_turn_complete", 31, {"turn_id": "human", "last_agent_message": observer.raw["armed_marker"]})
        else:
            emit(observer, "native_observation", 31, {"attachment": {"type": "deferred_tools_record", "entries": [
                {"name": "Monitor", "input_schema": {}},
            ]}})
        assert observer.errors
        assert observer.prototype.snapshot()["suppressed"] is not None

    def test_baseline_starts_at_new_native_normal_end(self, tmp_path: Path) -> None:
        """Ignore the old READY interval and retain a distinct telemetry drain."""
        observer = observation(tmp_path, "baseline")
        prompt(observer)
        emit(observer, "tool_call", 21, {"name": "PowerShell", "call_id": "register", "turn_id": "human",
             "input": {"command": f"& '{observer.directory.as_posix()}/register.ps1'"}})
        emit(observer, "native_turn_complete", 30, {"turn_id": "human", "last_agent_message": observer.raw["armed_marker"]})
        assert observer.deadline(40) == 750
        assert observer.drain_boundary() == 630
        assert observer.prototype.advance(800, observer.route) == "waiting"
        emit(observer, "tool_call", 45, {"name": "Read", "call_id": "unexpected", "input": {}, "turn_id": "human"})
        assert observer.errors

    @pytest.mark.parametrize("kind", ["native_interruption", "gap", "native_user"])
    def test_interruption_unknown_evidence_or_human_nudge_invalidates(self, tmp_path: Path, kind: str) -> None:
        """Retain failures and suppress any pending delivery."""
        observer = observation(tmp_path)
        arm(observer)
        emit(observer, kind, 40, {"origin": "human", "text": "continue", "native_uuid": "other", "reason": "unknown"})
        assert observer.errors
        assert observer.prototype.advance(260, observer.route) == "suppressed"

    def test_wrong_event_or_duplicate_consumption_is_rejected(self, tmp_path: Path) -> None:
        """The bridge event must agree with the frozen manifest and durable state."""
        observer = observation(tmp_path)
        arm(observer)
        observer.prototype.advance(260, observer.route)
        consume(observer.directory)
        with pytest.raises(ValueError, match="Duplicate"):
            consume(observer.directory)
        assert observer.prototype.snapshot()["duplicate_consumptions"] == 1
        with pytest.raises(FileExistsError):
            deliver(observer.directory)


class TestClaudeFailures:
    """Reject changed identities and unsupported evidence without repairing a run."""

    @pytest.mark.parametrize("fault", ["malformed", "identity", "duplicate", "stream-ended"])
    def test_notification_is_bound_and_unique(self, tmp_path: Path, fault: str) -> None:
        """A stream-ended notice is harmless; another ready notification is not."""
        observer = observation(tmp_path)
        arm(observer)
        observer.prototype.advance(260, observer.route)
        event = json.loads((observer.directory / "event.json").read_text())
        if fault == "identity":
            event["thread"] = "wrong"
        content = "<task-id>task1</task-id><event>" + ("{" if fault == "malformed" else json.dumps(event)) + "</event>"
        if fault == "stream-ended":
            content = "<task-id>task1</task-id><summary>Monitor stream ended</summary>"
        for at in ([261, 262] if fault == "duplicate" else [261]):
            emit(observer, "native_user", at, {"origin": "task-notification", "native_uuid": "wake", "text": content})
        assert bool(observer.errors) == (fault != "stream-ended")

    @pytest.mark.parametrize("fault", ["wrong-turn", "not-ready", "duplicate", "final-only"])
    def test_useful_work_requires_readiness_and_exact_continuation(self, tmp_path: Path, fault: str) -> None:
        """Neither a consume command nor WAIT_TEST_DONE alone proves useful work."""
        observer = observation(tmp_path, arm="A")
        prompt(observer)
        if fault != "not-ready":
            observer.prototype.advance(260, observer.route)
        if fault == "final-only":
            emit(observer, "native_turn_complete", 265, {"turn_id": "human", "last_agent_message": "WAIT_TEST_DONE"})
        else:
            for at in ([265, 266] if fault == "duplicate" else [265]):
                emit(observer, "tool_call", at, {"name": "PowerShell", "call_id": "consume",
                     "turn_id": "wrong" if fault == "wrong-turn" else "human",
                     "input": {"command": f"& '{observer.directory.as_posix()}/consume.ps1'"}})
        assert observer.errors

    @pytest.mark.parametrize("field", ["thread", "result"])
    def test_changed_durable_event_cannot_be_consumed(self, tmp_path: Path, field: str) -> None:
        """The consumer independently validates the content delivered by the bridge."""
        observer = observation(tmp_path)
        arm(observer)
        observer.prototype.advance(260, observer.route)
        path = observer.directory / "event.json"
        event = json.loads(path.read_text())
        event[field] = "wrong"
        path.write_text(json.dumps(event))
        with pytest.raises(ValueError, match="mismatch"):
            consume(observer.directory)
        assert observer.prototype.snapshot()["consumed_at"] is None

    def test_configuration_changes_fail_but_non_authoritative_records_do_not_arm(self, tmp_path: Path) -> None:
        """Synthetic measurements, unrelated results and attachments cannot arm a route."""
        observer = observation(tmp_path)
        observer.native(EvidenceRecord("local", "native_turn_complete", 20, 20, "probe:1", {}))
        emit(observer, "tool_result", 21, {"call_id": "unrelated"})
        emit(observer, "native_observation", 22, {"attachment": {"type": "other"}})
        assert observer.normal_at is None
        emit(observer, "native_observation", 23, {"permissionMode": "changed"})
        assert observer.errors == ["Exposed configuration changed: permissionMode"]

    @pytest.mark.parametrize("complete", [False, True])
    def test_trial_finishes_full_windows_or_retains_missing_wake(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, complete: bool) -> None:
        """Successful consumption waits through both windows; missing wake stays failed."""
        observer = observation(tmp_path)
        arm(observer)
        for stream in observer.manifest.streams:
            stream.path.parent.mkdir(parents=True, exist_ok=True)
            stream.path.write_text("retained native fixture\n")
        monkeypatch.setattr(observer.adapter, "snapshot", Mock(return_value=[]))
        monkeypatch.setattr(observer.adapter, "finish", Mock(return_value=[]))
        clock = [40.0]
        monkeypatch.setattr(claude_observer.time, "time", lambda: clock[0])

        def wait(seconds: float) -> None:
            clock[0] += seconds
            if complete and clock[0] == 260:
                observer.tick(260)
                event = json.loads((observer.directory / "event.json").read_text())
                emit(observer, "native_user", 262, {"origin": "task-notification", "native_uuid": "wake", "text":
                     "<task-id>task1</task-id><event>" + json.dumps(event) + "</event>"})
                emit(observer, "tool_call", 265, {"name": "PowerShell", "call_id": "consume", "turn_id": "wake",
                     "input": {"command": f"& '{observer.directory.as_posix()}/consume.ps1'"}})
                consume(observer.directory)
                emit(observer, "native_turn_complete", 270, {"turn_id": "wake", "last_agent_message": "WAIT_TEST_DONE"})
                clock[0] = 270

        observer.run(wait)
        audit = json.loads((observer.directory / "audit.json").read_text())
        assert audit["status"] == ("passed" if complete else "failed"), audit
        assert audit["finished_at"] == (510 if complete else 560)
        assert audit["wake_latency"] == (5 if complete else None)
        assert audit["request_attempt_coverage"] == "unknown"
        observer.fail("retained late failure", clock[0])
        observer.tick(clock[0])
        assert observer.prototype.snapshot()["suppressed"] == "interrupted"


# eof
