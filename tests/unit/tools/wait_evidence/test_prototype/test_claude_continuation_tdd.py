"""Retain exact native causality across the two adjacent Monitor notifications."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_evidence.test_prototype.test_claude_observer_tdd import (
    arm,
    emit,
    observation,
)
from tests.unit.tools.wait_evidence.test_telemetry.test_claude273_tdd import (
    answer,
    native,
    read,
)
from tools.wait_evidence.claude_monitor import consume
from tools.wait_evidence.models import object_value

if TYPE_CHECKING:
    from pathlib import Path

    from tools.wait_evidence.claude_observer import ClaudeObservation
    from tools.wait_evidence.models import EvidenceRecord, JsonObject

pytestmark = pytest.mark.timeout(10)


def feed(observer: ClaudeObservation, row: JsonObject) -> list[EvidenceRecord]:
    """Dispatch all fan-out records through the same parser and observer."""
    events = read(observer.adapter, row)
    for event in events:
        observer.native(event)
    return events


def ready(observer: ClaudeObservation) -> None:
    """Deliver the exact outcome through the real native normalization path."""
    arm(observer)
    observer.prototype.advance(260, observer.route)
    outcome = (observer.directory / "event.json").read_text()
    parser = observer.adapter
    row = native(parser, "user", "wake", origin={"kind": "task-notification"}, message={"content":
                 "<task-notification><task-id>task1</task-id><event>" + outcome + "</event></task-notification>"})
    row["timestamp"] = "1970-01-01T00:04:22Z"
    feed(observer, row)


def ended(observer: ClaudeObservation, fault: str = "none") -> None:
    """Model the inspected ready -> stream-ended parent chain without inference."""
    parser = observer.adapter
    tags = {"task-id": "task1", "tool-use-id": "monitor", "status": "completed"}
    if fault in tags:
        tags[fault] = "wrong"
    content = "".join(f"<{key}>{value}</{key}>" for key, value in tags.items())
    if fault == "duplicate-tag":
        content += "<task-id>task1</task-id>"
    row = native(parser, "user", "ended", "unrelated" if fault == "parent" else "wake",
                 origin={"kind": "human" if fault == "human" else "task-notification"},
                 message={"content": "<task-notification>" + content +
                          '<summary>Monitor "benchmark" stream ended</summary></task-notification>'})
    row["timestamp"] = "1970-01-01T00:04:22.005Z"
    feed(observer, row)


class TestClaudeContinuation:
    """Accept only the exact completed-task child, without changing native turn IDs."""

    def test_batched_stream_end_preserves_useful_wake_and_final_binding(self, tmp_path: Path) -> None:
        """Reproduce live B1: two notices arrive before the consume invocation."""
        observer = observation(tmp_path)
        ready(observer)
        ended(observer)
        parser = observer.adapter
        call = answer(parser, "consume-call", "ended")
        call["timestamp"] = "1970-01-01T00:04:25Z"
        object_value(call["message"]).update(stop_reason="tool_use", content=[{
            "type": "tool_use", "id": "consume", "name": "PowerShell",
            "input": {"command": f"& '{observer.directory.as_posix()}/consume.ps1'"},
        }])
        events = feed(observer, call)
        assert next(event for event in events if event.kind == "tool_call").data["turn_id"] == "ended"
        assert not observer.errors
        consume(observer.directory)
        final = answer(parser, "final", "consume-call", "WAIT_TEST_DONE")
        final["timestamp"] = "1970-01-01T00:04:30Z"
        feed(observer, final)
        normal = native(parser, "system", "normal", "final", subtype="turn_duration")
        normal["timestamp"] = "1970-01-01T00:04:30.001Z"
        feed(observer, normal)
        assert not observer.errors
        assert observer.useful_at == pytest.approx(265)
        assert observer.final_count == 1
        assert observer.prototype.snapshot()["consumed_at"] is not None
        binding = json.loads((observer.directory / "native-continuation.json").read_text())
        assert binding["ready_uuid"] == "wake"
        assert binding["notice_uuid"] == "ended"

    @pytest.mark.parametrize("fault", ["task-id", "tool-use-id", "status", "parent", "human", "duplicate-tag", "before-ready"])
    def test_unrelated_or_ambiguous_notice_cannot_authorize_consumption(self, tmp_path: Path, fault: str) -> None:
        """An ended notice has no authority without exact ready-event ancestry."""
        observer = observation(tmp_path)
        if fault == "before-ready":
            arm(observer)
            ended(observer)
        else:
            ready(observer)
            ended(observer, fault)
        emit(observer, "tool_call", 265, {"name": "PowerShell", "call_id": "consume", "turn_id": "ended",
             "input": {"command": f"& '{observer.directory.as_posix()}/consume.ps1'"}})
        assert observer.errors
        assert observer.useful_at is None
        assert not (observer.directory / "native-continuation.json").exists()

    def test_duplicate_completion_notice_is_retained_without_rebinding(self, tmp_path: Path) -> None:
        """A repeated status notice cannot replace the original causal evidence."""
        observer = observation(tmp_path)
        ready(observer)
        ended(observer)
        original = (observer.directory / "native-continuation.json").read_bytes()
        ended(observer)
        assert observer.errors == ["Duplicate native Monitor completion notice"]
        assert (observer.directory / "native-continuation.json").read_bytes() == original

    def test_missing_turn_never_authorizes_useful_work(self, tmp_path: Path) -> None:
        """Reject absent ancestry even after a verified ready event."""
        observer = observation(tmp_path)
        ready(observer)
        emit(observer, "tool_call", 265, {"name": "PowerShell", "call_id": "consume",
             "input": {"command": f"& '{observer.directory.as_posix()}/consume.ps1'"}})
        assert observer.useful_at is None
        assert observer.errors == ["Consumption lacks exact native continuation binding"]


# eof
