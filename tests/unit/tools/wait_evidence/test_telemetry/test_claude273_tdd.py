"""Redacted Claude 2.1.273 shapes retain native gates, tools and partial accounting."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    manifest_data,
)
from tools.wait_evidence.models import TrialManifest, object_value
from tools.wait_evidence.telemetry import Telemetry

if TYPE_CHECKING:
    from pathlib import Path

    from tools.wait_evidence.models import EvidenceRecord, JsonObject, JsonValue

pytestmark = pytest.mark.timeout(10)


def adapter(root: Path) -> Telemetry:
    """Use the inspected version with one explicitly bound native conversation."""
    data = manifest_data(root)
    data.update(host="claude", build="2.1.273", schema="claude-native-2.1.273", model="claude-opus-5")
    return Telemetry(TrialManifest.from_dict(data))


def native(parser: Telemetry, kind: str, uuid: str, parent: str = "", **fields: JsonValue) -> JsonObject:
    """Build the inspected common envelope without any real session identifiers."""
    row: JsonObject = {"type": kind, "uuid": uuid, "parentUuid": parent,
                       "sessionId": parser.manifest.thread, "version": "2.1.273",
                       "timestamp": "1970-01-01T00:00:20Z"}
    # JSON fixture values cross the same runtime object validation as live rows.
    row.update(fields)
    return row


def answer(parser: Telemetry, uuid: str = "answer", parent: str = "human", text: str = "READY") -> JsonObject:
    """Repeated content blocks share one completed response usage object."""
    return native(parser, "assistant", uuid, parent, requestId="request", message={
        "id": "message", "model": "claude-opus-5", "stop_reason": "end_turn",
        "content": [{"type": "text", "text": text}],
        "usage": {"input_tokens": 2, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 3,
                  "output_tokens": 7, "output_tokens_details": {"thinking_tokens": 0}},
    })


def read(parser: Telemetry, row: JsonObject) -> list[EvidenceRecord]:
    """Exercise the same fan-out entry point used by captured JSONL streams."""
    return parser.normalize_many(row, "native:" + str(row.get("uuid", "bookkeeping")), 30)


class TestClaude273:
    """Accept inspected bookkeeping while rejecting identity, lifecycle and usage ambiguity."""

    def test_metadata_settings_and_string_tool_errors_retain_their_limits(self, tmp_path: Path) -> None:
        """Inspected envelopes expose configuration without manufacturing a request."""
        parser = adapter(tmp_path)
        row: JsonObject = {"type": "permission-mode", "sessionId": parser.manifest.thread, "permissionMode": "auto"}
        event = read(parser, row)[0]
        assert event.data["permissionMode"] == "auto"
        assert event.data["time_basis"] == "ingestion-only"
        row = native(parser, "user", "result", permissionMode="auto", effortValue="xhigh", toolUseResult="command failed",
                     message={"content": [{"type": "tool_result", "tool_use_id": "call", "is_error": True, "content": "failed"}]})
        event = parser.normalize(row, "native:single", 30)
        assert event.kind == "tool_result"
        assert event.data["effortValue"] == "xhigh"
        assert event.data["native_result"] == "command failed"
        row["schema"] = "synthetic-v1"
        assert read(parser, row)[0].kind == "gap"

    @pytest.mark.parametrize("attachment", [False, True])
    def test_normal_end_requires_end_turn_and_exact_parent_chain(self, tmp_path: Path, *, attachment: bool) -> None:
        """The end-turn text alone cannot arm a native route."""
        parser = adapter(tmp_path)
        read(parser, native(parser, "user", "human", origin={"kind": "human"}, message={"content": "seed"}))
        rows = read(parser, answer(parser))
        assert "native_turn_complete" not in [row.kind for row in rows]
        parent = "answer"
        if attachment:
            read(parser, native(parser, "attachment", "loaded", parent, attachment={"type": "deferred_tools_record", "entries": []}))
            parent = "loaded"
        end = read(parser, native(parser, "system", "end", parent, subtype="turn_duration"))[0]
        assert end.kind == "native_turn_complete"
        assert end.data["turn_id"] == "human"
        assert end.data["assistant_uuid"] == "answer"
        assert end.data["last_agent_message"] == "READY"

    def test_usage_is_counted_once_but_each_tool_block_is_retained(self, tmp_path: Path) -> None:
        """Repeated usage does not erase the associated tool invocation."""
        parser = adapter(tmp_path)
        first = answer(parser)
        rows = read(parser, first)
        usage = next(row for row in rows if row.kind == "usage_completion")
        assert usage.data["usage"] == {"input": 105, "cached_input": 100, "output": 7, "reasoning": 0}
        second = answer(parser, "block2")
        second["timestamp"] = "1970-01-01T00:00:21Z"
        message = object_value(second["message"])
        message.update(stop_reason="tool_use", content=[{"type": "tool_use", "id": "monitor", "name": "Monitor", "input": {"command": "exact"}}])
        rows = read(parser, second)
        assert not any(row.kind == "usage_completion" for row in rows)
        call = next(row for row in rows if row.kind == "tool_call")
        assert call.data["call_id"] == "monitor"
        assert call.data["input"] == {"command": "exact"}

    def test_tool_result_retains_correlation_without_request_attempt(self, tmp_path: Path) -> None:
        """Tool-result evidence remains distinct from inference accounting."""
        parser = adapter(tmp_path)
        result = read(parser, native(parser, "user", "result", "block2", message={"content": [
            {"type": "tool_result", "tool_use_id": "monitor", "is_error": False, "content": "Monitor started (task exact)"},
        ]}))[0]
        assert result.kind == "tool_result"
        assert result.data["call_id"] == "monitor"
        assert result.data["is_error"] is False
        assert result.kind != "request_attempt"

    @pytest.mark.parametrize("kind", ["file-history-snapshot", "queue-operation", "away_summary"])
    def test_known_bookkeeping_cannot_arm_or_certify_requests(self, tmp_path: Path, kind: str) -> None:
        """Known incomplete envelopes carry no lifecycle authority."""
        parser = adapter(tmp_path)
        if kind == "file-history-snapshot":
            row: JsonObject = {"type": kind, "messageId": "history", "snapshot": {"timestamp": "1970-01-01T00:00:21Z"}}
        elif kind == "queue-operation":
            row = native(parser, kind, "queue")
            row.pop("version")
        else:
            row = native(parser, "system", "away", subtype=kind)
        assert [event.kind for event in read(parser, row)] == ["native_observation"]

    @pytest.mark.parametrize("fault", ["thread", "build", "model", "timestamp", "unknown", "missing-parent", "changed-usage"])
    def test_ambiguous_or_uninspected_evidence_is_a_gap(self, tmp_path: Path, fault: str) -> None:
        """Each unsupported identity or shape fails closed."""
        parser = adapter(tmp_path)
        row = answer(parser)
        if fault == "thread":
            row["sessionId"] = "other"
        elif fault == "build":
            row["version"] = "2.1.274"
        elif fault == "model":
            object_value(row["message"])["model"] = "other"
        elif fault == "timestamp":
            row["timestamp"] = "1970-01-01T00:00:21"
        elif fault == "unknown":
            row["type"] = "uninspected"
        elif fault == "missing-parent":
            row = native(parser, "system", "end", "absent", subtype="turn_duration")
        else:
            read(parser, row)
            row = answer(parser, "changed")
            object_value(object_value(row["message"])["usage"])["output_tokens"] = 99
        assert any(event.kind == "gap" for event in read(parser, row))

    @pytest.mark.parametrize("form", ["human-interrupt", "tool-interrupt", "compact", "api-error"])
    def test_interruption_and_compaction_remain_explicit(self, tmp_path: Path, form: str) -> None:
        """Both human and tool interruptions are terminal evidence."""
        parser = adapter(tmp_path)
        row = native(parser, "user", "interrupt", message={"content": "[Request interrupted by user]"})
        if form == "tool-interrupt":
            row = native(parser, "user", "interrupt", toolUseResult={"interrupted": True}, message={"content": []})
        elif form in {"compact", "api-error"}:
            row = native(parser, "system", "interrupt", subtype="compact_boundary" if form == "compact" else "api_error")
        kinds = [event.kind for event in read(parser, row)]
        assert "native_interruption" in kinds
        assert ("compaction" in kinds) == (form == "compact")


# eof
