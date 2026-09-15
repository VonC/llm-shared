"""Bound snapshot reads and expose schema, coverage and stream damage."""

# ruff: noqa: PLR2004 - Byte bounds and timestamps are deliberate test controls.

from __future__ import annotations

import io
import json
import os
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    event,
    manifest_data,
    stream_data,
)
from tools.wait_evidence.models import TrialManifest
from tools.wait_evidence.telemetry import Telemetry

if TYPE_CHECKING:
    from tools.wait_evidence.models import JsonObject

pytestmark = pytest.mark.timeout(10)


class TestTelemetryEdges:
    """Unreadable or unverified evidence cannot be reported as a complete stream."""

    @pytest.mark.parametrize("kind", ["unknown", "source_ready"])
    def test_unknown_kind_and_wrong_source(self, tmp_path: Path, kind: str) -> None:
        """Matching thread alone is insufficient when source identity is wrong."""
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)))
        row = event(kind, 100)
        row["source_id"] = "another-source"
        assert adapter.normalize(row, "stream:0", 110).kind == "gap"
        assert adapter.normalize(event("unknown", 100), "stream:1", 110).kind == "gap"

    def test_unverified_manifest_schema_fails_closed(self, tmp_path: Path) -> None:
        """A syntactically valid native label is not an installed schema verification."""
        manifest = replace(TrialManifest.from_dict(manifest_data(tmp_path)), schema="native-unknown")
        assert Telemetry(manifest).normalize(event("compaction", 12), "stream:0", 90).kind == "gap"

    @pytest.mark.parametrize("row", [
        event("coverage", 300, requests=True, usage=True, through=366),
        event("coverage", 366, requests=True, usage=True, through="forever"),
        event("coverage", 366, requests=True, usage=True, through=366, since=10),
    ])
    def test_coverage_range_must_include_baseline_and_not_future(self, tmp_path: Path, row: JsonObject) -> None:
        """A coverage certificate must cover the actual observed interval."""
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)))
        assert adapter.normalize(row, "stream:0", 486).kind == "gap"

    @pytest.mark.parametrize(("chunk_size", "max_line"), [(0, 1), (2, 1)])
    def test_invalid_read_bounds(self, tmp_path: Path, chunk_size: int, max_line: int) -> None:
        """Reject unbounded or contradictory read limits before opening a file."""
        with pytest.raises(ValueError, match="Read bounds"):
            Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)), chunk_size, max_line)

    def test_missing_stream_and_unfinished_record(self, tmp_path: Path) -> None:
        """Unavailable input and an incomplete final line both retain gap evidence."""
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)))
        assert adapter.read(90)[0].kind == "gap"
        (tmp_path / "events.jsonl").write_bytes(b'{"pending":')
        assert adapter.read(91)[0].data["reason"] == "Missing baseline stream identity"
        assert adapter.finish(92)[0].data["reason"] == "Incomplete JSONL record"

    def test_oversized_lines_discard_through_the_next_delimiter(self, tmp_path: Path) -> None:
        """A bounded parser recovers after a long line without parsing its tail."""
        path = tmp_path / "events.jsonl"
        path.write_bytes(b"x" * 25)
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)), 10, 15)
        assert adapter.read(90) == []
        assert adapter.read(91)[0].data["reason"] == "Oversized partial JSONL record"
        assert adapter.read(92) == []
        assert adapter.finish(92)[0].kind == "gap"
        with path.open("ab") as stream:
            stream.write(b"\n{}\n")
        assert adapter.read(93)[0].kind == "gap"
        assert adapter.finish(94) == []

    def test_oversized_complete_line(self, tmp_path: Path) -> None:
        """A newline arriving after a buffered prefix still obeys the line limit."""
        (tmp_path / "events.jsonl").write_bytes(b"x" * 18 + b"\n")
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)), 10, 15)
        assert adapter.read(90) == []
        assert adapter.read(91)[0].data["reason"] == "Oversized JSONL record"

    def test_replaced_file_keeps_generation_evidence(self, tmp_path: Path) -> None:
        """Replacement with a larger file cannot silently inherit the old cursor."""
        path = tmp_path / "events.jsonl"
        path.write_bytes(b"{}\n")
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)))
        adapter.read(90)
        replacement = tmp_path / "replacement.jsonl"
        replacement.write_text(json.dumps(event("compaction", 91)) + "\n", encoding="utf-8")
        replacement.replace(path)
        records = adapter.read(92)
        assert [row.kind for row in records] == ["gap", "compaction"]
        assert "#1:" in records[1].location

    @pytest.mark.parametrize("mutation", ["replacement", "rewrite", "truncation"])
    def test_first_snapshot_checks_manifest_identity(self, tmp_path: Path, mutation: str) -> None:
        """A fresh reader detects changed bytes and reads the replacement from zero."""
        path = tmp_path / "events.jsonl"
        prefix = b"old\n" * (2048 if mutation == "truncation" else 1)
        path.write_bytes(prefix)
        data = manifest_data(tmp_path)
        data["streams"] = [stream_data(path, len(prefix))]
        manifest = TrialManifest.from_dict(data)
        raw = (json.dumps(event("compaction", 12)) + "\n" +
               json.dumps(event("request_attempt", 13, attempt_id="a", end_at=14)) + "\n").encode()
        if mutation == "replacement":
            replacement = tmp_path / "replacement.jsonl"
            replacement.write_bytes(raw)
            replacement.replace(path)
        else:
            path.write_bytes(raw)
        adapter = Telemetry(manifest, chunk_size=32)
        snapshot = adapter.snapshot(90)
        first = next(snapshot)
        with path.open("ab") as stream:
            stream.write(raw * 3)
        records = [first, *snapshot]
        assert [row.kind for row in records] == ["gap", "compaction", "request_attempt"]
        assert records[0].data["reason"] == "Telemetry rotation or truncation"
        assert records[1].location == "stream-0#1:0"
        assert adapter.positions[str(path)] == len(raw)

    def test_missing_baseline_identity_resets_untrusted_offset(self, tmp_path: Path) -> None:
        """A legacy position alone cannot prove which bytes were already counted."""
        path = tmp_path / "events.jsonl"
        path.write_text(json.dumps(event("compaction", 12)) + "\n", encoding="utf-8")
        data = manifest_data(tmp_path)
        data["streams"] = [{"path": str(path), "offset": 4}]
        rows = list(Telemetry(TrialManifest.from_dict(data)).snapshot(90))
        assert [row.kind for row in rows] == ["gap", "compaction"]
        assert rows[0].data["reason"] == "Missing baseline stream identity"

    def test_snapshot_recomputes_budget_after_existing_cursor_reset(self, tmp_path: Path) -> None:
        """Truncation after an earlier read retains new records in the same snapshot."""
        path = tmp_path / "events.jsonl"
        raw = (json.dumps(event("compaction", 12)) + "\n").encode()
        path.write_bytes(raw * 3)
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)), chunk_size=32)
        assert len(list(adapter.snapshot(90))) == 3
        path.write_bytes(raw)
        records = list(adapter.snapshot(91))
        assert [row.kind for row in records] == ["gap", "compaction"]
        assert adapter.positions[str(path)] == len(raw)

    def test_read_sizes_and_seek_positions_are_instrumented(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Observe the actual I/O calls, not just the cursor reported afterwards."""
        raw = (json.dumps(event("compaction", 12)) + "\n").encode()
        reads: list[int | None] = []
        seeks: list[int] = []
        path = tmp_path / "events.jsonl"
        path.write_bytes(raw)
        manifest = TrialManifest.from_dict(manifest_data(tmp_path))
        recorded_stat = path.stat()

        class RecordingStream(io.BytesIO):
            """A finite stream that records read bounds and resumed byte offsets."""

            def read(self, size: int | None = -1) -> bytes:
                reads.append(size)
                return super().read(size)

            def seek(self, offset: int, whence: int = 0) -> int:
                seeks.append(offset)
                return super().seek(offset, whence)

            def fileno(self) -> int:
                return 23

        def open_stream(*_args: object, **_kwargs: object) -> RecordingStream:
            return RecordingStream(raw)

        def stat_stream(_fd: int) -> os.stat_result:
            return recorded_stat

        monkeypatch.setattr(Path, "open", open_stream)
        monkeypatch.setattr(os, "fstat", stat_stream)
        adapter = Telemetry(manifest, chunk_size=32)
        adapter.read(90)
        adapter.read(91)
        assert reads == [32, 32]
        assert seeks == [0, 0, 32]

    def test_snapshot_does_not_chase_newly_appended_bytes(self, tmp_path: Path) -> None:
        """Appending while consuming a snapshot cannot expand its initial budget."""
        path = tmp_path / "events.jsonl"
        raw = (json.dumps(event("compaction", 12)) + "\n").encode()
        path.write_bytes(raw)
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)), chunk_size=32)
        records = adapter.snapshot(90)
        first = next(records)
        with path.open("ab") as stream:
            stream.write(raw * 3)
        assert first.kind == "compaction"
        assert list(records) == []
        assert adapter.positions[str(path)] == len(raw)
        assert str(tmp_path) not in first.location

    def test_missing_snapshot_stream_retains_gap(self, tmp_path: Path) -> None:
        """A missing explicit stream cannot become an empty successful snapshot."""
        adapter = Telemetry(TrialManifest.from_dict(manifest_data(tmp_path)))
        records = list(adapter.snapshot(90))
        assert len(records) == 1
        assert records[0].kind == "gap"


# eof
