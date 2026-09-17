"""Verify explicit identity and bounded JSONL reads across damaged streams."""

# ruff: noqa: PLR2004 - Expected synthetic measurements belong beside assertions.

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    event,
    manifest_data,
    stream_data,
)
from tools.wait_evidence.collector import Collector
from tools.wait_evidence.models import EvidenceRecord, JsonObject, TrialManifest
from tools.wait_evidence.telemetry import Telemetry

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.timeout(10)


class TestTelemetry:
    """Synthetic schema parsing preserves locations and reports coverage gaps."""

    def test_normalization_preserves_times_and_location(self, tmp_path: Path) -> None:
        """Late ingestion does not replace the original event timestamp."""
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)))
        record = adapter.normalize(event("compaction", 12), "explicit:30", 90)
        assert record.at == 12
        assert record.ingested_at == 90
        assert record.location == "explicit:30"
        assert record.synthetic is True

    @pytest.mark.parametrize("field", ["thread", "profile", "build", "host", "schema"])
    def test_mismatched_identity_fails_coverage(self, tmp_path: Path, field: str) -> None:
        """Another thread or unverified schema never becomes measured work."""
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)))
        row = event("compaction", 12)
        row[field] = "unrelated"
        record = adapter.normalize(row, "explicit:30", 90)
        assert record.kind == "gap"
        assert field in str(record.data)

    def test_partial_lines_resume_from_offsets_in_bounded_chunks(self, tmp_path: Path) -> None:
        """Each pass reads at most the declared byte bound and keeps its tail."""
        path = tmp_path / "events.jsonl"
        raw = (json.dumps(event("compaction", 12)) + "\n").encode()
        path.write_bytes(raw[:-2])
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)), chunk_size=32)
        records: list[EvidenceRecord] = []
        for _ in range((len(raw) // 32) + 1):
            records.extend(adapter.read(90))
        assert not records
        assert adapter.positions[str(path)] == len(raw) - 2
        with path.open("ab") as stream:
            stream.write(raw[-2:])
        records.extend(adapter.read(91))
        assert [record.kind for record in records] == ["compaction"]
        assert records[0].location.endswith(":0")
        assert adapter.read(92) == []

    def test_malformed_and_rotated_files_leave_explicit_gaps(self, tmp_path: Path) -> None:
        """Bad bytes and truncation cannot silently erase attempt evidence."""
        path = tmp_path / "events.jsonl"
        path.write_bytes(b"not-json\n\xff\n")
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)))
        assert [record.kind for record in adapter.read(90)] == ["gap", "gap"]
        path.write_bytes(b"{}\n")
        assert [record.kind for record in adapter.read(91)] == ["gap", "gap"]

    def test_manifest_offset_skips_old_bytes(self, tmp_path: Path) -> None:
        """Recorded pre-start positions govern reads, including in another cwd."""
        path = tmp_path / "events.jsonl"
        prefix = b"old bytes must not parse\n" * 256
        path.write_bytes(prefix + (json.dumps(event("compaction", 12)) + "\n").encode())
        data = manifest_data(tmp_path)
        data["streams"] = [stream_data(path, len(prefix))]
        adapter = Telemetry(TrialManifest.from_dict(data))
        assert [record.kind for record in adapter.read(90)] == ["compaction"]
        assert adapter.read(91) == []

class TestInstalledTelemetry:
    """Redacted shapes inspected locally on Codex 0.154.0 and Claude 2.1.272."""

    @pytest.mark.parametrize("host", ["codex", "claude"])
    def test_usage_is_native_but_cannot_certify_requests(self, tmp_path: Path, host: str) -> None:
        """Completed-response usage does not prove that no other attempt happened."""
        data = manifest_data(tmp_path)
        build = "0.154.0" if host == "codex" else "2.1.272"
        data.update(host=host, build=build, schema=f"{host}-native-{build}")
        manifest = TrialManifest.from_dict(data)
        adapter = Telemetry(manifest)
        row: JsonObject = {"timestamp": "1970-01-01T00:00:20Z"}
        if host == "codex":
            row.update(type="token_usage_record", payload={
                "thread_id": manifest.thread, "turn_id": "turn-one", "response_id": "response-one",
                "usage": {"input_tokens": 10, "cached_input_tokens": 4, "cache_write_input_tokens": 0,
                          "output_tokens": 3, "reasoning_output_tokens": 1, "total_tokens": 13}})
        else:
            row.update(type="assistant", sessionId=manifest.thread, version=build, requestId="response-one",
                       message={"id": "message-one", "usage": {
                           "input_tokens": 2, "cache_read_input_tokens": 4, "cache_creation_input_tokens": 4,
                           "output_tokens": 3, "output_tokens_details": {"thinking_tokens": 1}}})
        record = adapter.normalize(row, "stream-0:200", 30)
        assert record.kind == "usage_completion"
        assert record.synthetic is False
        assert record.data["usage"] == {"input": 10, "cached_input": 4, "output": 3, "reasoning": 1}
        collector = Collector(manifest)
        collector.ingest(record)
        report = collector.report(500)
        assert report["synthetic"] is False
        assert report["request_coverage"] != "complete"
        assert report["status"] != "pass"

    def test_native_unknown_identity_and_schema_cannot_be_coverage(self, tmp_path: Path) -> None:
        """A native stream cannot smuggle synthetic coverage certificates."""
        data = manifest_data(tmp_path)
        data.update(host="codex", build="0.154.0", schema="codex-native-0.154.0")
        adapter = Telemetry(TrialManifest.from_dict(data))
        assert adapter.normalize(event("coverage", 30), "selected", 30).kind == "gap"
        row: JsonObject = {"timestamp": "1970-01-01T00:00:20Z", "type": "token_usage_record",
                           "payload": {"thread_id": "unrelated"}}
        assert adapter.normalize(row, "selected", 30).kind == "gap"
        data["build"] = "future"
        assert Telemetry(TrialManifest.from_dict(data)).normalize(row, "selected", 30).kind == "gap"


# eof
