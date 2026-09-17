"""Typed synthetic trial identities, normalized evidence and coverage contracts.

Manifest parsing rejects implicit locations and unbounded measurement windows.
Unknown token fields stay unknown instead of becoming reassuring zeroes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import NoReturn, TypedDict

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]
type Usage = dict[str, int | None]

TOKEN_FIELDS = ("input", "cached_input", "output", "reasoning")
SHA256_LENGTH = 64
FILE_ID_PARTS = 2
INITIAL_DRAIN_SECONDS = 120


def reject(reason: str) -> NoReturn:
    """Reject evidence that cannot satisfy a typed measurement contract."""
    raise ValueError(reason)


def identity_digest(*parts: str) -> str:
    """Compare private identities without publishing their original values."""
    return sha256("\0".join(parts).encode("utf-8")).hexdigest()


def object_value(value: JsonValue) -> JsonObject:
    """Require a JSON object at a schema boundary."""
    if not isinstance(value, dict):
        reject("Expected a JSON object")
    return value


def text_value(data: JsonObject, key: str) -> str:
    """Require a nonempty explicit string field."""
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        reject(f"Missing or invalid string: {key}")
    return value


def number_value(data: JsonObject, key: str) -> float:
    """Require a finite timestamp or duration, excluding JSON booleans."""
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        reject(f"Missing or nonfinite number: {key}")
    return float(value)


def usage_value(value: JsonValue) -> Usage:
    """Preserve missing token counters and reject invalid known counters."""
    data = object_value(value)
    result: Usage = {}
    for name in TOKEN_FIELDS:
        count = data.get(name)
        if count is not None and (isinstance(count, bool) or not isinstance(count, int) or count < 0):
            reject(f"Invalid usage counter: {name}")
        result[name] = count
    return result


class Arm(StrEnum):
    """Separate classic, preliminary prototype and reserved service evidence."""

    CLASSIC = "A"
    PROTOTYPE = "B-prototype"
    SERVICE = "B-service"


class Phase(StrEnum):
    """Nonoverlapping cost buckets; durations also report overlapping intervals."""

    SEED = "seed"
    REGISTRATION = "registration"
    QUIET = "quiet_wait"
    WAKE = "wake_latency"
    CONTINUATION = "useful_continuation"
    DUPLICATE = "duplicate_observation"
    AUXILIARY = "auxiliary"
    AFTER = "after_observation"
    CROSS_BOUNDARY = "cross_boundary"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class StreamSpec:
    """A selected native or probe stream with frozen position and continuity evidence."""

    path: Path
    offset: int
    file_id: tuple[int, int] | None = None
    anchor_sha256: str | None = None
    role: str = "telemetry"

    @classmethod
    def from_dict(cls, data: JsonObject) -> StreamSpec:
        """Validate a stream without discovering files or interpreting cwd."""
        path = Path(text_value(data, "path"))
        offset = data.get("offset")
        if not path.is_absolute():
            reject("Telemetry paths must be absolute")
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            reject("Stream offsets must be nonnegative integers")
        role = cls._role(data)
        if data.get("file_id") is None and data.get("anchor_sha256") is None:
            return cls(path, offset, role=role)
        file_id = cls._file_id(data.get("file_id"))
        anchor = text_value(data, "anchor_sha256")
        if len(anchor) != SHA256_LENGTH or any(char not in "0123456789abcdef" for char in anchor):
            reject("Stream anchor requires a SHA-256 hash")
        return cls(path, offset, file_id, anchor, role)

    @staticmethod
    def _role(data: JsonObject) -> str:
        role = data.get("role", "telemetry")
        if not isinstance(role, str) or role not in {"telemetry", "probe"}:
            reject("Unknown stream role")
        return role

    @staticmethod
    def _file_id(value: JsonValue) -> tuple[int, int]:
        if not isinstance(value, list) or len(value) != FILE_ID_PARTS:
            reject("Stream file identity requires device and inode")
        numbers = [item for item in value if isinstance(item, int) and not isinstance(item, bool) and item >= 0]
        if len(numbers) != FILE_ID_PARTS:
            reject("Stream file identity requires nonnegative integers")
        return numbers[0], numbers[1]


@dataclass(frozen=True)
class TrialManifest:
    """Frozen series controls and exact identities supplied before the prompt."""

    series_id: str
    pair_id: str
    run_id: str
    arm: Arm
    host: str
    build: str
    thread: str
    profile: str
    schema: str
    model: str
    configuration_hash: str
    repository: Path
    home: Path
    seed_hashes: dict[str, str]
    context_tokens: int
    source_id: str
    ready_at: float
    created_at: float
    wake_bound: float
    duplicate_window: float
    drain_bound: float
    streams: tuple[StreamSpec, ...]
    baselines: dict[str, Usage]
    cached_input_included: bool | None
    reasoning_included: bool | None

    @classmethod
    def from_dict(cls, data: JsonObject) -> TrialManifest:
        """Validate all measurement controls without reading private seed files."""
        bounds = cls._bounds(data)
        ready, created = number_value(data, "ready_at"), number_value(data, "created_at")
        if ready > created:
            reject("Create the manifest after seed READY")
        baselines = object_value(data.get("baselines"))
        return cls(
            series_id=text_value(data, "series_id"), pair_id=text_value(data, "pair_id"),
            run_id=text_value(data, "run_id"), arm=Arm(text_value(data, "arm")),
            host=text_value(data, "host"), build=text_value(data, "build"),
            thread=text_value(data, "thread"), profile=text_value(data, "profile"),
            schema=text_value(data, "schema"), model=text_value(data, "model"),
            configuration_hash=cls._hash(text_value(data, "configuration_hash")),
            repository=cls._path(data, "repository"), home=cls._path(data, "home"),
            seed_hashes=cls._seeds(data), context_tokens=cls._context(data),
            source_id=text_value(data, "source_id"), ready_at=ready, created_at=created,
            wake_bound=bounds["wake_bound"], duplicate_window=bounds["duplicate_window"],
            drain_bound=bounds["drain_bound"], streams=cls._streams(data),
            baselines={name: usage_value(value) for name, value in baselines.items()},
            cached_input_included=cls._semantics(data, "cached_input_included"),
            reasoning_included=cls._semantics(data, "reasoning_included"),
        )

    @staticmethod
    def _semantics(data: JsonObject, key: str) -> bool | None:
        value = data.get(key)
        if value is not None and not isinstance(value, bool):
            reject("Token inclusion semantics must be boolean or unknown")
        return value

    @staticmethod
    def _path(data: JsonObject, key: str) -> Path:
        path = Path(text_value(data, key))
        if not path.is_absolute():
            reject("Repository and home must be explicit absolute paths")
        return path

    @staticmethod
    def _hash(value: str) -> str:
        if len(value) != SHA256_LENGTH or any(char not in "0123456789abcdef" for char in value):
            reject("Frozen seeds and configuration require SHA-256 hashes")
        return value

    @classmethod
    def _seeds(cls, data: JsonObject) -> dict[str, str]:
        seeds = object_value(data.get("seed_hashes"))
        if not seeds:
            reject("Frozen seed hashes are required")
        return {name: cls._hash(text_value(seeds, name)) for name in seeds}

    @staticmethod
    def _context(data: JsonObject) -> int:
        context = data.get("context_tokens")
        if isinstance(context, bool) or not isinstance(context, int) or context <= 0:
            reject("Context size must be a positive integer")
        return context

    @staticmethod
    def _bounds(data: JsonObject) -> dict[str, float]:
        bounds = {key: number_value(data, key) for key in ("wake_bound", "duplicate_window", "drain_bound")}
        if any(value <= 0 for value in bounds.values()):
            reject("Series timing bounds must be positive and finite")
        if bounds["drain_bound"] != INITIAL_DRAIN_SECONDS:
            reject("The initial collector schema requires a 120-second drain")
        return bounds

    @staticmethod
    def _streams(data: JsonObject) -> tuple[StreamSpec, ...]:
        streams = data.get("streams")
        if not isinstance(streams, list) or not streams:
            reject("At least one explicit telemetry stream is required")
        selected = tuple(StreamSpec.from_dict(object_value(value)) for value in streams)
        if len({stream.path for stream in selected}) != len(selected):
            reject("Duplicate telemetry stream paths")
        return selected


@dataclass(frozen=True)
class EvidenceRecord:
    """A normalized observation retaining identity, both times and raw location."""

    event_id: str
    kind: str
    at: float
    ingested_at: float
    location: str
    data: JsonObject
    synthetic: bool = True


@dataclass(frozen=True)
class CoverageAssessment:
    """Request completeness and token completeness are independent evidence."""

    request_coverage: str
    usage_coverage: str
    gaps: tuple[str, ...]


class TrialReport(TypedDict):
    """Compact, redacted report shape, retaining inconclusive and failed trials."""

    version: int
    run_id: str
    pair_id: str
    series_id: str
    arm: str
    host: str
    build: str
    model: str
    configuration_hash: str
    seed_hashes: dict[str, str]
    context_tokens: int
    thread_identity: str
    repository_identity: str
    timing_bounds: dict[str, float]
    synthetic: bool
    status: str
    request_coverage: str
    usage_coverage: str
    strict_zero_inference: bool
    attempts: int
    completions: int
    observed_attempts: int
    observed_completions: int
    retries: int
    compactions: int
    quiet_attempts: int
    cross_phase_attempts: int
    polling_calls: int
    wait_tool_calls: int
    non_wait_tool_calls: int
    wait_induced_attempts: int
    wait_induced_input: int | None
    logical_consumptions: int
    logical_wakes: int | None
    usage: Usage
    phase_usage: dict[str, Usage]
    phase_attempts: dict[str, int]
    source_duration: float | None
    quiet_duration: float | None
    wake_latency: float | None
    end_to_end_duration: float | None
    overlap: bool
    collection_complete: bool
    gaps: list[str]
    evidence: list[str]
    evidence_count: int


# eof
