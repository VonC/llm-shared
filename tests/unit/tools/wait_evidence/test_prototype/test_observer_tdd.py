"""Exercise the standalone collector with fake time and isolated native records."""

# ruff: noqa: PLR2004 - Measured durations and explicit protocol examples.

from __future__ import annotations

import json
from datetime import UTC, datetime
from threading import Event
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from watchdog.events import FileModifiedEvent, FileMovedEvent, FileOpenedEvent

from tests.unit.tools.wait_evidence.test_prototype.test_prototype_tdd import (
    experiment,
    request,
)
from tools.wait_evidence import probe_cli
from tools.wait_evidence.models import object_value, text_value
from tools.wait_evidence.probe_observer import Changed, Observation, observe, record
from tools.wait_evidence.prototype import Prototype, Route

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.wait_evidence.models import JsonObject

pytestmark = pytest.mark.timeout(10)


def prepared(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, mode: str = "trial") -> Path:
    """Prepare a genuine isolated manifest around a redacted native stream."""
    series = experiment(tmp_path, monkeypatch)
    data = request(series)
    data["mode"] = mode
    stream = tmp_path / "rollout.jsonl"
    stream.write_text(json.dumps({"type": "session_meta", "timestamp": "1970-01-01T00:00:01Z",
                                  "payload": {"id": data["thread"], "cli_version": "0.154.0"}}) + "\n", encoding="utf-8")
    data["streams"] = [str(stream)]
    directory = series.prepare(data, 11)
    monkeypatch.setattr("tools.wait_evidence.probe_cli.time.time", Mock(return_value=100.0))
    probe_cli.register(directory)
    return directory


def completion(path: Path, at: float, *, turn: str = "registering", kind: str = "task_complete", message: str = "pending") -> None:
    """Append the locally inspected Codex normal-end shape."""
    row = {"timestamp": datetime.fromtimestamp(at, UTC).isoformat(), "type": "event_msg",
           "payload": {"type": kind, "turn_id": turn, "last_agent_message": message}}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row) + "\n")


class TestObservation:
    """Native gates and finite observation use ordinary code and retained evidence."""

    def test_timer_arms_only_for_exact_normal_turn(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Unrelated completions never authorize a same-thread queue operation."""
        directory = prepared(tmp_path, monkeypatch)
        sent = Mock(return_value="receipt")
        observation = Observation(directory, "registering", Route("direct-turn-evidence", lambda: "idle", sent))
        completion(tmp_path / "rollout.jsonl", 120, turn="other")
        observation.tick(130)
        assert observation.prototype.snapshot()["gate"] is None
        completion(tmp_path / "rollout.jsonl", 140)
        observation.tick(150)
        observation.tick(340)
        assert sent.call_count == 1
        assert observation.prototype.snapshot()["normal_end_at"] == 140

    def test_interrupted_native_turn_suppresses_release(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A native interruption keeps the outcome durable without sending."""
        directory = prepared(tmp_path, monkeypatch)
        completion(tmp_path / "rollout.jsonl", 120, kind="turn_aborted")
        observation = Observation(directory, "registering", Route("unavailable", lambda: "idle", lambda _: None))
        observation.tick(340)
        assert observation.prototype.snapshot()["suppressed"] == "interrupted"
        assert observation.prototype.snapshot()["ready_at"] == 340

    def test_lost_send_response_retains_observation_without_retry(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Transport loss leaves the collector running to observe a possible accepted wake."""
        directory = prepared(tmp_path, monkeypatch)
        completion(tmp_path / "rollout.jsonl", 120)
        send = Mock(side_effect=OSError("connection lost"))
        observation = Observation(directory, "registering", Route("direct-turn-evidence", lambda: "idle", send))
        observation.tick(340)
        observation.tick(341)
        assert observation.prototype.snapshot()["delivery"] == "receipt-unknown"
        assert send.call_count == 1

    def test_duplicate_window_and_separate_drain_end_in_retained_report(self, tmp_path: Path,
                                                                     monkeypatch: pytest.MonkeyPatch) -> None:
        """An ordinary wait visits the duplicate boundary before draining telemetry."""
        directory = prepared(tmp_path, monkeypatch)
        completion(tmp_path / "rollout.jsonl", 120)
        completion(tmp_path / "rollout.jsonl", 342, turn="wake", message="WAIT_TEST_DONE")
        record(directory, "useful_continuation", 341, {"automatic": True, "evidence": "native:123"})
        clock = [342.0]
        delays: list[float] = []
        monkeypatch.setattr("tools.wait_evidence.probe_observer.time.time", lambda: clock[0])
        monkeypatch.setattr("tools.wait_evidence.probe_observer.time.monotonic", lambda: clock[0])
        observation = Observation(directory, "registering", Route("direct-turn-evidence", lambda: "idle", lambda _: "receipt"))

        def wait(seconds: float) -> None:
            delays.append(seconds)
            clock[0] += seconds

        observation.run(wait)
        report = object_value(json.loads((directory / "report.json").read_text(encoding="utf-8")))
        assert report["synthetic"] is False
        assert report["status"] == "inconclusive"
        assert 120 in delays

    @pytest.mark.parametrize("marker", ["native", "operator", "absent"])
    def test_baseline_stays_unchanged_with_measurement_separate_from_gate(self, tmp_path: Path,
                                                                       monkeypatch: pytest.MonkeyPatch, marker: str) -> None:
        """Ten minutes are measured after normal end without releasing the source."""
        directory = prepared(tmp_path, monkeypatch, mode="baseline")
        observation = Observation(directory, "registering", Route("unavailable", lambda: "idle", lambda _: None))
        if marker == "native":
            completion(tmp_path / "rollout.jsonl", 120)
        elif marker == "operator":
            observation.prototype.mark_normal_end(120)
        deadline = observation.tick(130)
        assert deadline == (820 if marker == "absent" else 840)
        assert observation.prototype.snapshot()["ready_at"] is None
        if marker != "native":
            assert observation.prototype.snapshot()["gate"] is None

    @pytest.mark.parametrize("with_route", [False, True])
    def test_watcher_cleanup_and_selected_stream_notifications(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                              *, with_route: bool) -> None:
        """The outer process watches explicit paths and always releases its watcher."""
        directory = prepared(tmp_path, monkeypatch)
        if with_route:
            path = directory / "manifest.json"
            data = object_value(json.loads(path.read_text(encoding="utf-8")))
            data["arm"] = "B-prototype"
            path.write_text(json.dumps(data), encoding="utf-8")
        watcher = Mock()
        monkeypatch.setattr("tools.wait_evidence.probe_observer.Observer", Mock(return_value=watcher))

        def run(_self: Observation, wait: Callable[[float], object]) -> None:
            wait(0)

        monkeypatch.setattr(Observation, "run", run)
        observe(directory, "registering", tmp_path / "codex.exe" if with_route else None)
        watcher.start.assert_called_once()
        watcher.stop.assert_called_once()
        ready = Event()
        handler = Changed({tmp_path / "selected"}, ready)
        handler.on_any_event(FileOpenedEvent(str(tmp_path / "selected")))
        handler.on_any_event(FileModifiedEvent(str(tmp_path / "unrelated")))
        assert not ready.is_set()
        handler.on_any_event(FileModifiedEvent(str(tmp_path / "selected")))
        assert ready.is_set()

    def test_replacement_destination_wakes_observer(self, tmp_path: Path) -> None:
        """An atomic replacement of a selected stream wakes its observer."""
        ready = Event()
        handler = Changed({tmp_path / "selected"}, ready)
        handler.on_any_event(FileMovedEvent(str(tmp_path / "temporary"), str(tmp_path / "selected")))
        assert ready.is_set()

    def test_restart_preserves_markers_and_first_final_window(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Replayed native events cannot duplicate markers or extend the finite window."""
        directory = prepared(tmp_path, monkeypatch)
        completion(tmp_path / "rollout.jsonl", 120)
        completion(tmp_path / "rollout.jsonl", 342, turn="wake", message="WAIT_TEST_DONE")
        route = Route("unavailable", lambda: "idle", lambda _: None)
        first = Observation(directory, "registering", route)
        assert first.tick(350) == 582
        retained = (directory / "probe-events.jsonl").read_bytes()
        resumed = Observation(directory, "registering", route)
        assert resumed.tick(360) == 582
        assert (directory / "probe-events.jsonl").read_bytes() == retained
        completion(tmp_path / "rollout.jsonl", 370, turn="duplicate", message="WAIT_TEST_DONE")
        assert resumed.tick(380) == 582

    def test_terminal_snapshot_retains_partial_and_last_arriving_measurement(self, tmp_path: Path,
                                                                           monkeypatch: pytest.MonkeyPatch) -> None:
        """Final drain keeps late rows and reports a damaged trailing JSON record."""
        directory = prepared(tmp_path, monkeypatch)
        observation = Observation(directory, "registering", Route("unavailable", lambda: "idle", lambda _: None))
        monkeypatch.setattr("tools.wait_evidence.probe_observer.time.time", Mock(return_value=1000.0))
        monkeypatch.setattr("tools.wait_evidence.probe_observer.time.monotonic", Mock(return_value=1000.0))
        with (tmp_path / "rollout.jsonl").open("ab") as stream:
            stream.write(b'{"unfinished":')
        observation.run(lambda _: pytest.fail("past the finite observation deadline"))
        report = object_value(json.loads((directory / "report.json").read_text(encoding="utf-8")))
        assert "Incomplete JSONL record" in str(report["gaps"])


class TestProbeCommands:
    """Accept evidence-backed A-arm timing without manufacturing normal-end authority."""

    def test_state_commands_and_consumption(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Exercise source, status, markers, consume and suppression on durable state."""
        directory = prepared(tmp_path, monkeypatch)
        args = ["--directory", str(directory)]
        monkeypatch.setattr("tools.wait_evidence.probe_cli.time.sleep", Mock())
        monkeypatch.setattr("tools.wait_evidence.probe_cli.time.time", Mock(side_effect=[200.0, 340.0]))
        assert probe_cli.main(["source", *args]) == 0
        monkeypatch.setattr("tools.wait_evidence.probe_cli.time.time", Mock(return_value=341.0))
        assert probe_cli.main(["source", *args]) == 0
        assert probe_cli.main(["status", *args]) == 0
        assert probe_cli.main(["mark-normal-end", *args]) == 0
        state = Prototype(directory).snapshot()
        assert state["gate"] is None
        assert probe_cli.main(["consume", *args, "--event", text_value(state, "event_id"), "--thread", text_value(state, "thread")]) == 0
        assert probe_cli.main(["suppress", *args, "--reason", "stop"]) == 0

    def test_baseline_release_is_rejected(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """The source CLI cannot accidentally release an unchanged-source baseline."""
        directory = prepared(tmp_path, monkeypatch, mode="baseline")
        with pytest.raises(ValueError, match="baselines cannot release"):
            probe_cli.source(Prototype(directory))

    @pytest.mark.parametrize("kind", ["pending_return", "useful_continuation"])
    def test_operator_measurements_and_observe_dispatch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str) -> None:
        """Only evidence-referenced timing measurements can cross the CLI boundary."""
        directory = prepared(tmp_path, monkeypatch)
        path = tmp_path / "measurement.json"
        measurement: JsonObject = {"kind": kind, "at": 341, "data": {"evidence": "native:123", "automatic": True}}
        path.write_text(json.dumps(measurement), encoding="utf-8")
        assert probe_cli.main(["mark", "--directory", str(directory), "--measurement", str(path)]) == 0
        measurement["kind"] = "coverage"
        path.write_text(json.dumps(measurement), encoding="utf-8")
        with pytest.raises(ValueError, match="Only prompt"):
            probe_cli.main(["mark", "--directory", str(directory), "--measurement", str(path)])
        runner = Mock()
        monkeypatch.setattr("tools.wait_evidence.probe_cli.observe", runner)
        assert probe_cli.main(["observe", "--directory", str(directory), "--registering-turn", "registering"]) == 0
        runner.assert_called_once_with(directory, "registering", None)


# eof
