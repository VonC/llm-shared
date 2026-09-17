"""Explicit synthetic and inspected native adapters with bounded JSONL cursors.

Only locally inspected Codex 0.154.0 and Claude 2.1.272/2.1.273 shapes are accepted.
Native usage is not a request-completeness certificate. Every mismatch or
damaged stream produces a gap; unrelated observations never enter accounting.
Local pending-return markers establish A-arm timing without coverage authority.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from typing import TYPE_CHECKING

from .models import (
    EvidenceRecord,
    identity_digest,
    number_value,
    object_value,
    reject,
    text_value,
    usage_value,
)
from .telemetry_claude import BOOKKEEPING, ClaudeTelemetry

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
PROBE_KINDS = frozenset({"benchmark_prompt", "source_start", "source_ready", "normal_turn_end",
                         "pending_return", "useful_continuation", "final_turn_end", "consumption", "delivery"})


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
    native_bound: bool = False


@dataclass
class Telemetry:
    """Bind exact-thread streams, fan out Claude blocks and retain accounting uncertainty."""

    manifest: TrialManifest
    chunk_size: int = 65536
    max_line_bytes: int = 1048576
    _cursors: list[_Cursor] = field(init=False, default_factory=list[_Cursor])
    _claude_records: ClaudeTelemetry = field(init=False)

    def __post_init__(self) -> None:
        """Initialize cursors from manifest baselines, never from file freshness."""
        if self.chunk_size <= 0 or self.max_line_bytes < self.chunk_size:
            reject("Read bounds require 0 < chunk size <= maximum line size")
        self._cursors = [_Cursor(spec, spec.offset, f"stream-{index}", identity=spec.file_id)
                         for index, spec in enumerate(self.manifest.streams)]
        self._claude_records = ClaudeTelemetry(self.manifest, self._native_usage)

    def normalize_many(self, raw: JsonObject, location: str, ingested_at: float) -> list[EvidenceRecord]:
        """Retain every inspected Claude tool block with one response usage total."""
        if self.manifest.host == "claude" and self.manifest.build == "2.1.273" and raw.get("type") != "probe_event":
            try:
                self._verify_version()
                if "schema" in raw:
                    reject("Native streams cannot contain synthetic certificates")
                return self._claude_records.normalize(raw, location, ingested_at)
            except ValueError as error:
                return [self.gap(str(error), location, ingested_at)]
        return [self.normalize(raw, location, ingested_at)]

    @property
    def positions(self) -> dict[str, int]:
        """Return byte positions suitable for explicit collector checkpoints."""
        return {str(cursor.spec.path): cursor.offset for cursor in self._cursors}

    def normalize(self, raw: JsonObject, location: str, ingested_at: float) -> EvidenceRecord:
        """Validate identity and preserve original time instead of ingestion time."""
        try:
            if self.manifest.schema != "synthetic-v1":
                return self._native(raw, location, ingested_at)
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

    def _native(self, raw: JsonObject, location: str, ingested_at: float) -> EvidenceRecord:
        """Keep response usage separate from unobserved native request attempts."""
        self._verify_version()
        host = self.manifest.host
        if raw.get("type") == "probe_event":
            return self._probe_event(raw, location, ingested_at)
        if "schema" in raw:
            reject("Native streams cannot contain synthetic certificates")
        if host == "claude" and self.manifest.build == "2.1.273":
            return self._claude_records.normalize(raw, location, ingested_at)[0]
        timestamp = datetime.fromisoformat(text_value(raw, "timestamp"))
        if timestamp.tzinfo is None:
            reject("Native timestamp requires an explicit timezone")
        kind = text_value(raw, "type")
        if host == "codex":
            event_id, normalized, data = self._codex(raw, kind, location)
        else:
            event_id, normalized, data = self._claude(raw, kind, location)
        return EvidenceRecord(f"{host}:{event_id}", normalized, timestamp.timestamp(), ingested_at,
                              location, data, synthetic=False)

    def _verify_version(self) -> None:
        versions = {"codex": {"0.154.0"}, "claude": {"2.1.272", "2.1.273"}}
        host, build = self.manifest.host, self.manifest.build
        if build not in versions.get(host, set()) or self.manifest.schema != f"{host}-native-{build}":
            reject("Unverified telemetry schema")

    def _codex(self, raw: JsonObject, kind: str, location: str) -> tuple[str, str, JsonObject]:
        payload = object_value(raw.get("payload"))
        if kind == "token_usage_record":
            if payload.get("thread_id") != self.manifest.thread:
                reject("Native thread identity mismatch")
            event_id = text_value(payload, "response_id")
            return event_id, "usage_completion", self._native_usage(object_value(payload.get("usage")), "codex", event_id)
        normalized = "native_observation"
        if kind == "event_msg":
            # Consumers must bind this turn ID before arming a route.
            normalized = {"task_complete": "native_turn_complete", "turn_aborted": "native_interruption",
                          "task_started": "native_turn_started"}.get(text_value(payload, "type"), normalized)
        return identity_digest(location), normalized, payload

    def _claude(self, raw: JsonObject, kind: str, location: str) -> tuple[str, str, JsonObject]:
        if raw.get("sessionId") != self.manifest.thread or raw.get("version") != self.manifest.build:
            reject("Native thread or build identity mismatch")
        if kind != "assistant":
            return identity_digest(location), "native_observation", {"native_type": kind}
        message = object_value(raw.get("message"))
        event_id = text_value(raw, "requestId") + ":" + text_value(message, "id")
        data = self._native_usage(object_value(message.get("usage")), "claude", text_value(raw, "requestId"))
        return event_id, "usage_completion", data

    def _probe_event(self, raw: JsonObject, location: str, ingested_at: float) -> EvidenceRecord:
        for key in ("schema", "host", "build", "thread", "profile", "source_id"):
            if raw.get(key) != getattr(self.manifest, key):
                reject(f"Probe event identity mismatch: {key}")
        kind = text_value(raw, "kind")
        if kind not in PROBE_KINDS:
            reject("Probe events cannot certify native request/usage coverage")
        return EvidenceRecord(text_value(raw, "event_id"), kind, number_value(raw, "at"), ingested_at,
                              location, object_value(raw.get("data")), synthetic=False)

    @staticmethod
    def _native_usage(raw: JsonObject, host: str, attempt_id: str) -> JsonObject:
        usage: JsonObject = {"input": raw.get("input_tokens"), "output": raw.get("output_tokens")}
        if host == "codex":
            usage.update(cached_input=raw.get("cached_input_tokens"), reasoning=raw.get("reasoning_output_tokens"))
        else:
            parts = [raw.get(key) for key in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")]
            # Claude reports cache read/write input separately from uncached input.
            valid = [value for value in parts if isinstance(value, int) and not isinstance(value, bool) and value >= 0]
            usage["input"] = sum(valid) if len(valid) == len(parts) else None
            usage["cached_input"] = raw.get("cache_read_input_tokens")
            details = raw.get("output_tokens_details")
            usage["reasoning"] = details.get("thinking_tokens") if isinstance(details, dict) else None
        validated: JsonObject = dict(usage_value(usage))
        return {"attempt_id": attempt_id, "epoch": "native", "usage": validated}

    def _bind_native(self, cursor: _Cursor, stream: BinaryIO) -> None:
        """Verify the selected file's host identity even when its header precedes the baseline."""
        if self.manifest.schema == "synthetic-v1" or cursor.native_bound:
            return
        self._verify_version()
        path = cursor.spec.path.resolve()
        if cursor.spec.role == "probe":
            if "a.shared-wait-service" not in path.parts:
                reject("Probe stream must be in the explicit ignored evidence directory")
        elif not path.is_relative_to(self.manifest.home.resolve()):
            reject("Native stream must belong to the explicit host home")
        stream.seek(0)
        remaining = self.max_line_bytes
        while remaining:
            line = stream.readline(min(remaining, self.max_line_bytes))
            if not line:
                break
            remaining -= len(line)
            raw = object_value(json.loads(line))
            if self._header_matches(raw, cursor.spec.role):
                cursor.native_bound = True
                return
        reject("Native stream identity header unavailable")

    def _header_matches(self, raw: JsonObject, role: str) -> bool:
        if role == "probe":
            if raw.get("type") != "probe_meta":
                reject("Probe stream header missing")
            if any(raw.get(key) != getattr(self.manifest, key) for key in ("schema", "host", "thread", "profile", "source_id", "build")):
                reject("Probe stream header identity mismatch")
            return True
        return self._host_header(raw)

    def _host_header(self, raw: JsonObject) -> bool:
        if self.manifest.host == "codex" and raw.get("type") == "session_meta":
            payload = object_value(raw.get("payload"))
            if payload.get("id") != self.manifest.thread or payload.get("cli_version") != self.manifest.build:
                reject("Native header thread or build mismatch")
            return True
        if self.manifest.host == "claude" and raw.get("sessionId") == self.manifest.thread:
            if raw.get("type") in BOOKKEEPING and "version" not in raw:
                return False
            if raw.get("version") != self.manifest.build:
                reject("Native header build mismatch")
            return True
        return False

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
                self._bind_native(cursor, stream)
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
        except ValueError as error:
            yield self.gap(str(error), cursor.label, at)

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
        cursor.native_bound = False
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
                if cursor.spec.role == "telemetry" and raw.get("type") == "probe_event":
                    reject("Probe event in a native telemetry stream")
                records.extend(self.normalize_many(raw, location, at))
            except (ValueError, UnicodeError):
                records.append(self.gap("Malformed JSONL record", location, at))
        if len(cursor.pending) > self.max_line_bytes:
            records.append(self.gap("Oversized partial JSONL record", cursor.label, at))
            cursor.pending, cursor.discarding = b"", True
        return records


# eof
