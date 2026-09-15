"""Explicit synthetic telemetry adapter with bounded, persistent JSONL cursors.

Native schemas remain unverified until Step 2. Every mismatch or damaged stream
produces an evidence gap, while unrelated observations never enter accounting.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from hashlib import sha256
from typing import TYPE_CHECKING

from .models import (
    EvidenceRecord,
    identity_digest,
    number_value,
    object_value,
    reject,
    text_value,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import BinaryIO

    from .models import JsonObject, StreamSpec, TrialManifest

KINDS = frozenset({
    "request_attempt", "usage_completion", "cumulative_usage", "counter_reset",
    "tool_call", "tool_result", "benchmark_prompt", "source_start", "source_ready",
    "normal_turn_end", "pending_return", "useful_continuation", "final_turn_end",
    "consumption", "delivery", "compaction", "coverage", "clock_discontinuity",
})
ANCHOR_BYTES = 4096


@dataclass
class _Cursor:
    """Keep byte positions and partial records across bounded read calls."""

    spec: StreamSpec
    offset: int
    label: str
    pending: bytes = b""
    identity: tuple[int, int] | None = None
    baseline_checked: bool = False
    generation: int = 0
    discarding: bool = False


@dataclass
class Telemetry:
    """Normalize only the declared schema and selected exact-thread streams."""

    manifest: TrialManifest
    chunk_size: int = 65536
    max_line_bytes: int = 1048576
    _cursors: list[_Cursor] = field(init=False, default_factory=list[_Cursor])

    def __post_init__(self) -> None:
        """Initialize cursors from manifest baselines, never from file freshness."""
        if self.chunk_size <= 0 or self.max_line_bytes < self.chunk_size:
            reject("Read bounds require 0 < chunk size <= maximum line size")
        self._cursors = [_Cursor(spec, spec.offset, f"stream-{index}", identity=spec.file_id)
                         for index, spec in enumerate(self.manifest.streams)]

    @property
    def positions(self) -> dict[str, int]:
        """Return byte positions suitable for explicit collector checkpoints."""
        return {str(cursor.spec.path): cursor.offset for cursor in self._cursors}

    def normalize(self, raw: JsonObject, location: str, ingested_at: float) -> EvidenceRecord:
        """Validate identity and preserve original time instead of ingestion time."""
        try:
            if self.manifest.schema != "synthetic-v1":
                reject("Unverified telemetry schema")
            for key in ("schema", "host", "build", "thread", "profile", "source_id"):
                if raw.get(key) != getattr(self.manifest, key):
                    reject(f"Telemetry identity mismatch: {key}")
            kind = text_value(raw, "kind")
            if kind not in KINDS:
                reject("Unknown telemetry event kind")
            data = object_value(raw.get("data"))
            at = number_value(raw, "at")
            if kind == "coverage":
                self._validate_coverage(data, at)
            return EvidenceRecord(text_value(raw, "event_id"), kind, number_value(raw, "at"),
                                  ingested_at, location, data)
        except ValueError as error:
            return self.gap(str(error), location, ingested_at)

    def _validate_coverage(self, data: JsonObject, at: float) -> None:
        """A synthetic certificate covers the baseline and never a future interval."""
        since, through = number_value(data, "since"), number_value(data, "through")
        if since > self.manifest.created_at or through > at or since > through:
            reject("Invalid coverage interval")

    @staticmethod
    def gap(reason: str, location: str, at: float) -> EvidenceRecord:
        """Represent loss or invalidity as evidence instead of silent omission."""
        event_id = identity_digest(location, str(at), reason)
        return EvidenceRecord(f"gap:{event_id}", "gap", at, at, location, {"reason": reason})

    def read(self, ingested_at: float) -> list[EvidenceRecord]:
        """Read one bounded chunk per explicitly selected stream."""
        records: list[EvidenceRecord] = []
        for cursor in self._cursors:
            records.extend(self._read_cursor(cursor, ingested_at))
        return records

    def finish(self, ingested_at: float) -> list[EvidenceRecord]:
        """Expose unfinished lines when a snapshot closes, retaining their bytes."""
        return [self.gap("Incomplete JSONL record", cursor.label, ingested_at)
                for cursor in self._cursors if cursor.pending or cursor.discarding]

    def snapshot(self, ingested_at: float) -> Iterator[EvidenceRecord]:
        """Consume a fixed initial byte budget, even when a producer keeps appending."""
        for cursor in self._cursors:
            yield from self._read_cursor(cursor, ingested_at, snapshot=True)

    def _read_cursor(self, cursor: _Cursor, at: float, *, snapshot: bool = False) -> Iterator[EvidenceRecord]:
        try:
            with cursor.spec.path.open("rb") as stream:
                stat = os.fstat(stream.fileno())
                gaps = self._prepare_cursor(cursor, stream, stat, at)
                # Freeze against this open file after any reset, before yielding.
                remaining = max(0, stat.st_size - cursor.offset) if snapshot else self.chunk_size
                stream.seek(cursor.offset)
                yield from gaps
                while remaining:
                    chunk = stream.read(min(self.chunk_size, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield from self._parse_chunk(cursor, chunk, at)
        except OSError:
            yield self.gap("Selected telemetry stream unavailable", cursor.label, at)

    def _prepare_cursor(self, cursor: _Cursor, stream: BinaryIO, stat: os.stat_result,
                        at: float) -> list[EvidenceRecord]:
        identity = stat.st_dev, stat.st_ino
        changed = (cursor.identity is not None and cursor.identity != identity) or stat.st_size < cursor.offset
        reason = "Telemetry rotation or truncation" if changed else ""
        if not cursor.baseline_checked:
            if cursor.spec.file_id is None:
                reason = "Missing baseline stream identity"
            elif not changed and self._anchor_digest(stream, cursor.spec.offset) != cursor.spec.anchor_sha256:
                reason = "Telemetry rotation or truncation"
            cursor.baseline_checked = True
        cursor.identity = identity
        if not reason:
            return []
        cursor.offset, cursor.pending, cursor.discarding = 0, b"", False
        cursor.generation += 1
        return [self.gap(reason, cursor.label, at)]

    def _anchor_digest(self, stream: BinaryIO, offset: int) -> str:
        """Check at most 4 KiB before the baseline with bounded individual reads."""
        start = max(0, offset - ANCHOR_BYTES)
        stream.seek(start)
        digest = sha256()
        for position in range(start, offset, self.chunk_size):
            digest.update(stream.read(min(self.chunk_size, offset - position)))
        return digest.hexdigest()

    def _parse_chunk(self, cursor: _Cursor, chunk: bytes, at: float) -> list[EvidenceRecord]:
        """Parse complete bounded records while retaining the last partial line."""
        records: list[EvidenceRecord] = []
        start = cursor.offset - len(cursor.pending)
        cursor.offset += len(chunk)
        pieces = (cursor.pending + chunk).split(b"\n")
        cursor.pending = pieces.pop()
        for piece in pieces:
            location = f"{cursor.label}#{cursor.generation}:{start}"
            start += len(piece) + 1
            if cursor.discarding:
                cursor.discarding = False
                continue
            if len(piece) > self.max_line_bytes:
                records.append(self.gap("Oversized JSONL record", location, at))
                continue
            try:
                raw = object_value(json.loads(piece.decode("utf-8")))
                records.append(self.normalize(raw, location, at))
            except (ValueError, UnicodeError):
                records.append(self.gap("Malformed JSONL record", location, at))
        if len(cursor.pending) > self.max_line_bytes:
            records.append(self.gap("Oversized partial JSONL record", cursor.label, at))
            cursor.pending, cursor.discarding = b"", True
        return records


# eof
