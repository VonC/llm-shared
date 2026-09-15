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
from tools.wait_evidence.models import EvidenceRecord, TrialManifest
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

# eof
