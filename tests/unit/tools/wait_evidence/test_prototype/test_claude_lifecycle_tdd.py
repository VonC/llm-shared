"""Exercise independent Claude processes with real files and virtual time."""

# ruff: noqa: PLR2004 - Fixed protocol boundaries are the test evidence.

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from tests.unit.tools.wait_evidence.test_prototype.test_prototype_tdd import (
    experiment,
    request,
)
from tests.unit.tools.wait_evidence.test_telemetry.test_claude273_tdd import (
    answer,
    native,
)
from tools.wait_evidence import claude_monitor, claude_observer, probe_cli, probe_files
from tools.wait_evidence.claude_monitor import Watch, read_json
from tools.wait_evidence.claude_observer import ClaudeObservation, observe_claude
from tools.wait_evidence.models import object_value

if TYPE_CHECKING:
    from pathlib import Path
    from typing import TextIO

    from tools.wait_evidence.models import JsonValue

pytestmark = pytest.mark.timeout(10)


def prepared(root: Path, monkeypatch: pytest.MonkeyPatch, mode: str = "baseline") -> Path:
    """Freeze and bind a real stream containing inspected pre-header bookkeeping."""
    series = experiment(root, monkeypatch)
    series.settings.update(host="claude", build="2.1.273", schema="claude-native-2.1.273", model="claude-opus-5",
                           configuration={"permission_mode": "auto", "effort": "xhigh", "mode": "normal"},
                           monitor_schema={"type": "object"})
    data = request(series)
    data["mode"] = mode
    path = root / "native.jsonl"
    rows = [{"type": "custom-title", "sessionId": data["thread"], "customTitle": "seed"},
            {"type": "user", "sessionId": data["thread"], "version": "2.1.273", "timestamp": "1970-01-01T00:00:01Z"}]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    data["streams"] = [str(path)]
    return series.prepare(data, 11)


class TestPublication:
    """Readiness is an atomic publication, including at the writer's earliest event."""

    def test_json_is_invisible_until_complete_and_never_overwrites(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A watcher cannot open a partial object and retained evidence is immutable."""
        target = tmp_path / "ready.json"
        dump = json.dump

        def writing(value: JsonValue, stream: TextIO, *, indent: int, sort_keys: bool) -> None:
            assert not target.exists()
            dump(value, stream, indent=indent, sort_keys=sort_keys)

        monkeypatch.setattr(probe_files.json, "dump", writing)
        probe_files.save(target, {"complete": True})
        assert read_json(target) == {"complete": True}
        monkeypatch.setattr(probe_files.json, "dump", dump)
        with pytest.raises(FileExistsError):
            probe_files.save(target, {"complete": False})
        assert read_json(target) == {"complete": True}
        assert list(tmp_path.iterdir()) == [target]


class TestBridgeLifecycle:
    """No host process or real delay is required to check the durable handshake."""

    def test_watch_coalesces_and_closes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """The ordinary waiter owns and releases its OS watcher."""
        watcher = Mock()
        monkeypatch.setattr(claude_monitor, "Observer", Mock(return_value=watcher))
        watch = Watch({tmp_path / "event.json", tmp_path / "stop.json"})
        watch.start()
        watch.ready.set()
        watch.wait(0)
        assert not watch.ready.is_set()
        watch.close()
        watcher.schedule.assert_called_once()
        watcher.start.assert_called_once()
        watcher.stop.assert_called_once()
        watcher.join.assert_called_once()

    @pytest.mark.parametrize("action", ["event", "stop", "expired"])
    def test_bridge_waits_for_event_or_retains_terminal_failure(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: str) -> None:
        """Event publication and stopping cannot be confused with model receipt."""
        directory = prepared(tmp_path, monkeypatch, "trial")
        clock = [20.0]
        monkeypatch.setattr(claude_monitor.time, "time", lambda: clock[0])

        def wake(_seconds: float) -> None:
            if action == "expired":
                clock[0] = 500
            else:
                probe_files.save(directory / (action + ".json"), {})

        watch = Mock(wait=wake)
        monkeypatch.setattr(claude_monitor, "Watch", Mock(return_value=watch))
        if action == "event":
            claude_monitor.bridge(directory)
            assert read_json(directory / "bridge-finished.json")["status"] == "event-for-stdout"
        else:
            with pytest.raises(ValueError, match="stopped or deadline"):
                claude_monitor.bridge(directory)
        assert read_json(directory / "registration.json")["due_at"] == 260
        assert read_json(directory / "bridge-armed.json")["thread"] == read_json(directory / "manifest.json")["thread"]
        watch.close.assert_called_once()

    @pytest.mark.parametrize("success", [False, True])
    def test_confirmation_waits_for_durable_bridge_readiness(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, success: bool) -> None:
        """A successful Monitor tool result alone does not prove its command armed."""
        directory = prepared(tmp_path, monkeypatch)

        def wake(_seconds: float) -> None:
            probe_files.save(directory / ("bridge-armed.json" if success else "stop.json"), {"thread": "bound"})

        watch = Mock(wait=wake)
        monkeypatch.setattr(claude_monitor, "Watch", Mock(return_value=watch))
        if success:
            assert claude_monitor.confirm(directory) == {"thread": "bound"}
        else:
            with pytest.raises(ValueError, match="did not arm"):
                claude_monitor.confirm(directory)
        watch.close.assert_called_once()


class TestObservationLifecycle:
    """Drive the real native parser, source state and durable audit with virtual time."""

    @pytest.mark.parametrize("late", [False, True])
    def test_baseline_keeps_a_full_drain_after_late_wakeup(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, late: bool) -> None:
        """The first drain boundary cannot reuse elapsed time after a delayed wakeup."""
        directory = prepared(tmp_path, monkeypatch)
        clock = [20.0]
        monkeypatch.setattr(claude_observer.time, "time", lambda: clock[0])
        observer = ClaudeObservation(directory)
        parser = observer.adapter
        rows = [native(parser, "user", "human", origin={"kind": "human"}, message={"content": observer.prompt})]
        call = answer(parser, "register", text="")
        object_value(call["message"]).update(stop_reason="tool_use", content=[{
            "type": "tool_use", "id": "register", "name": "PowerShell", "input": {"command": f"& '{directory.as_posix()}/register.ps1'"},
        }])
        final = answer(parser, "final", "register", str(observer.raw["armed_marker"]))
        final["requestId"] = "final-request"
        rows.extend([call, final, native(parser, "system", "end", "final", subtype="turn_duration")])
        with observer.manifest.streams[0].path.open("a", encoding="utf-8") as stream:
            stream.write("\n".join(json.dumps(row) for row in rows) + "\n")
        claude_monitor.register(directory)

        def wait(seconds: float) -> None:
            clock[0] += seconds + (5 if late and clock[0] < 620 else 0)

        observer.run(wait)
        audit = read_json(directory / "audit.json")
        assert audit["status"] == "passed", audit
        assert audit["normal_at"] == 20
        assert audit["drain_started"] == (625 if late else 620)
        assert audit["finished_at"] == (745 if late else 740)
        assert audit["strict_idle_supported"] is False
        assert (directory / "retained-stream-0.jsonl").read_bytes() == observer.manifest.streams[0].path.read_bytes()
        assert (directory / "report.json").exists()

    def test_real_parser_gap_invalidates_and_retains_failed_audit(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A generated gap is authoritative even though it is not a native record."""
        directory = prepared(tmp_path, monkeypatch)
        observer = ClaudeObservation(directory)
        gap = observer.adapter.gap("unparsed native bytes", "native:12", 20)
        observer.native(gap)
        assert observer.errors == ["gap: unparsed native bytes"]
        assert observer.deadline(21) == 21
        assert observer.audit(21, None)["status"] == "failed"

    def test_prompt_without_registration_expires_and_partial_tail_is_retained(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A missing command and truncated telemetry cannot leave an unbounded run."""
        directory = prepared(tmp_path, monkeypatch)
        clock = [20.0]
        monkeypatch.setattr(claude_observer.time, "time", lambda: clock[0])
        observer = ClaudeObservation(directory)
        assert observer.deadline(20) == 86420
        row = native(observer.adapter, "user", "human", origin={"kind": "human"}, message={"content": observer.prompt})
        with observer.manifest.streams[0].path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row) + "\n{")
        observer.run(lambda seconds: clock.__setitem__(0, clock[0] + seconds))
        assert clock[0] == 200
        audit = read_json(directory / "audit.json")
        assert audit["status"] == "failed"
        assert audit["errors"]
        assert audit["drain_started"] is None

    @pytest.mark.parametrize("failure", ["", "preflight", "run"])
    def test_process_publishes_readiness_only_after_preflight_and_always_closes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
        """A retained process marker is distinct from readiness and audited completion."""
        directory = prepared(tmp_path, monkeypatch)
        instance = ClaudeObservation(directory)
        if failure == "preflight":
            instance.prompt_at = 12

        def run(_wait: object) -> None:
            assert (directory / "observer-ready.json").exists()
            if failure == "run":
                message = "retained failure"
                raise OSError(message)
            probe_files.save(directory / "audit.json", {"status": "passed"})

        monkeypatch.setattr(instance, "run", run)
        monkeypatch.setattr(claude_observer, "ClaudeObservation", Mock(return_value=instance))
        watch = Mock()
        monkeypatch.setattr(claude_observer, "Watch", Mock(return_value=watch))
        if failure:
            with pytest.raises((OSError, ValueError)):
                observe_claude(directory)
            assert (directory / "observer-failed.json").exists()
            assert not (directory / "observer-finished.json").exists()
        else:
            observe_claude(directory)
            assert read_json(directory / "observer-finished.json")["status"] == "passed"
        assert (directory / "observer-ready.json").exists() == (failure != "preflight")
        watch.start.assert_called_once()
        watch.close.assert_called_once()


class TestClaudeCommands:
    """The CLI selects the host-specific handshake without starting other hosts."""

    @pytest.mark.parametrize("command", ["observe", "claude-bridge", "claude-confirm", "claude-consume"])
    def test_cli_dispatches_exact_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], command: str) -> None:
        """Only confirmation and consumption emit JSON results."""
        directory = prepared(tmp_path, monkeypatch)
        action = Mock(return_value={"accepted": True})
        if command == "observe":
            monkeypatch.setattr(probe_cli, "observe_claude", action)
        else:
            monkeypatch.setattr(claude_monitor, command.removeprefix("claude-"), action)
        assert probe_cli.main([command, "--directory", str(directory)]) == 0
        action.assert_called_once_with(directory)
        output = capsys.readouterr().out
        assert bool(output) == (command in {"claude-confirm", "claude-consume"})

    def test_codex_cannot_guess_registering_turn(self, tmp_path: Path) -> None:
        """A host dispatch failure stays explicit instead of binding the latest turn."""
        probe_files.save(tmp_path / "manifest.json", {"host": "codex"})
        with pytest.raises(ValueError, match="exact registering turn"):
            probe_cli.main(["observe", "--directory", str(tmp_path)])


# eof
