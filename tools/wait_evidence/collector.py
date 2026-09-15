"""Exact-identity accounting independent of file parsing and report publication.

One indexed pass groups observations for each snapshot. Missing request evidence,
ambiguous phase crossings and damaged telemetry cannot manufacture a zero claim.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import TYPE_CHECKING

from .models import (
    TOKEN_FIELDS,
    Arm,
    CoverageAssessment,
    EvidenceRecord,
    Phase,
    identity_digest,
    number_value,
    reject,
    text_value,
    usage_value,
)

if TYPE_CHECKING:
    from .models import JsonObject, TrialManifest, TrialReport, Usage

MAX_EVIDENCE_REFERENCES = 100
EXCLUDED_PHASES = frozenset({Phase.SEED, Phase.AUXILIARY, Phase.AFTER})


def _empty() -> Usage:
    return dict.fromkeys(TOKEN_FIELDS, 0)


def _unknown() -> Usage:
    return dict.fromkeys(TOKEN_FIELDS, None)


def _add(target: Usage, addition: Usage) -> None:
    for name in TOKEN_FIELDS:
        old, new = target[name], addition[name]
        target[name] = old + new if old is not None and new is not None else None


@dataclass
class _Snapshot:
    """Accounting state shared by independent report calculations."""

    groups: dict[str, list[EvidenceRecord]]
    bounds: dict[str, float]
    requests: dict[str, EvidenceRecord]
    phases: dict[str, Phase]
    quiet: set[str]
    crossing: int
    polling_calls: int
    polling: set[str]
    usage: Usage
    phase_usage: dict[str, Usage]
    completions: dict[str, EvidenceRecord]
    coverage: CoverageAssessment


@dataclass
class _Drain:
    """Measure the local drain with monotonic time and detect wall-clock jumps."""

    window_end: float | None = None
    origin: tuple[float, float] | None = None
    elapsed: float = 0
    discontinuity: bool = False

    def observe(self, end: float, utc: float, monotonic: float) -> None:
        if not math.isfinite(monotonic):
            reject("Drain requires finite monotonic time")
        if self.window_end != end or self.origin is None:
            self.window_end, self.origin, self.elapsed = end, (utc, monotonic), 0
            return
        elapsed = monotonic - self.origin[1]
        clock_tolerance_seconds = 1.0
        if elapsed < self.elapsed or abs((utc - self.origin[0]) - elapsed) > clock_tolerance_seconds:
            self.discontinuity = True
        self.elapsed = max(self.elapsed, elapsed)


@dataclass
class Collector:
    """Own deduplication, baseline epochs, call correlation and finite drain state."""

    manifest: TrialManifest
    _events: dict[str, EvidenceRecord] = field(default_factory=dict[str, EvidenceRecord], init=False)
    _conflicts: dict[str, EvidenceRecord] = field(default_factory=dict[str, EvidenceRecord], init=False)
    _drain: _Drain = field(default_factory=_Drain, init=False)

    def ingest(self, record: EvidenceRecord) -> None:
        """Index one observation, preserving conflicting identities as gaps."""
        previous = self._events.get(record.event_id)
        if previous is not None:
            if (previous.kind, previous.at, previous.data) != (record.kind, record.at, record.data):
                self._conflicts[record.location] = EvidenceRecord(
                    f"conflict:{record.event_id}", "gap", record.at, record.ingested_at, record.location,
                    {"reason": f"Conflicting event identity: {record.location}"})
            return
        self._events[record.event_id] = record

    def _groups(self, now: float) -> dict[str, list[EvidenceRecord]]:
        groups: dict[str, list[EvidenceRecord]] = defaultdict(list)
        for record in chain(self._events.values(), self._conflicts.values()):
            if record.ingested_at <= now and record.at <= now:
                groups[record.kind].append(record)
        return groups

    def _boundaries(self, groups: dict[str, list[EvidenceRecord]]) -> dict[str, float]:
        boundaries: dict[str, float] = {}
        for kind in ("benchmark_prompt", "source_start", "source_ready", "normal_turn_end",
                     "pending_return", "useful_continuation", "final_turn_end"):
            rows = groups.get(kind, [])
            if kind == "final_turn_end":
                rows = [row for row in rows if row.data.get("marker") == "WAIT_TEST_DONE"]
            if rows:
                boundaries[kind] = min(row.at for row in rows)
        return boundaries

    def _end(self, bounds: dict[str, float]) -> float | None:
        final = bounds.get("final_turn_end")
        return None if final is None else final + self.manifest.duplicate_window

    def _boundary_gaps(self, bounds: dict[str, float]) -> set[str]:
        """Require the real lifecycle even when a stream declares full coverage."""
        registration = "pending_return" if self.manifest.arm == Arm.CLASSIC else "normal_turn_end"
        required = {"benchmark_prompt", "source_start", "source_ready", registration,
                    "useful_continuation", "final_turn_end"}
        if required - bounds.keys():
            return {"Missing measurement boundary"}
        edges = (("benchmark_prompt", "source_start"), ("source_start", "source_ready"),
                 ("benchmark_prompt", registration), (registration, "useful_continuation"),
                 ("source_ready", "useful_continuation"), ("useful_continuation", "final_turn_end"))
        if bounds["benchmark_prompt"] <= self.manifest.created_at or any(bounds[a] > bounds[b] for a, b in edges):
            return {"Invalid measurement boundary order"}
        return set()

    def drained(self, now: float, *, monotonic_at: float | None = None) -> bool:
        """Finish early only with authoritative coverage through duplicate observation."""
        groups = self._groups(now)
        end = self._end(self._boundaries(groups))
        if end is None or now < end:
            return False
        if monotonic_at is not None:
            self._drain.observe(end, now, monotonic_at)
        complete = any(row.data.get("requests") is True and row.data.get("usage") is True
                       and self._through(row) >= end for row in groups.get("coverage", []))
        return complete or self._drain.elapsed >= self.manifest.drain_bound

    @staticmethod
    def _through(row: EvidenceRecord) -> float:
        try:
            return number_value(row.data, "through")
        except ValueError:
            return float("-inf")

    def _phase(self, at: float, bounds: dict[str, float]) -> Phase:
        start = bounds.get("benchmark_prompt")
        if start is None:
            return Phase.UNKNOWN
        registration = bounds.get("pending_return" if self.manifest.arm == Arm.CLASSIC else "normal_turn_end")
        ready, useful, final = (bounds.get(key) for key in ("source_ready", "useful_continuation", "final_turn_end"))
        if at == final:
            return Phase.CONTINUATION
        observation_end = self._end(bounds)
        if observation_end is not None and at >= observation_end:
            return Phase.AFTER
        intervals = (
            (Phase.SEED, float("-inf"), start), (Phase.REGISTRATION, start, registration),
            (Phase.QUIET, registration, ready), (Phase.WAKE, ready, useful),
            (Phase.CONTINUATION, useful, final), (Phase.DUPLICATE, final, self._end(bounds)),
        )
        return self._match_interval(at, intervals)

    @staticmethod
    def _match_interval(at: float, intervals: tuple[tuple[Phase, float | None, float | None], ...]) -> Phase:
        """Resolve a finite set of phase boundaries without inventing missing ones."""
        for phase, lower, upper in intervals:
            if lower is not None and upper is not None and lower <= at < upper:
                return phase
        return Phase.UNKNOWN

    @staticmethod
    def _index(rows: list[EvidenceRecord], key: str, gaps: set[str]) -> dict[str, EvidenceRecord]:
        result: dict[str, EvidenceRecord] = {}
        for row in rows:
            value = row.data.get(key)
            if not isinstance(value, str) or not value:
                gaps.add(f"Missing {key}: {row.location}")
                value = row.event_id
            old = result.get(value)
            if old is not None and old.data != row.data:
                gaps.add(f"Conflicting {key}: {row.location}")
            else:
                result[value] = row
        return result

    def _phases(self, requests: dict[str, EvidenceRecord], bounds: dict[str, float],
                gaps: set[str]) -> tuple[dict[str, Phase], set[str], int]:
        phases: dict[str, Phase] = {}
        quiet: set[str] = set()
        crossing = 0
        registration = bounds.get("pending_return" if self.manifest.arm == Arm.CLASSIC else "normal_turn_end")
        ready = bounds.get("source_ready")
        edges = [registration, ready, bounds.get("useful_continuation"), bounds.get("final_turn_end")]
        boundaries = [edge for edge in edges if edge is not None]
        for identity, row in requests.items():
            if row.data.get("scope") == "auxiliary":
                phases[identity] = Phase.AUXILIARY
                continue
            phase = self._phase(row.at, bounds)
            end = self._request_end(row)
            if not math.isfinite(end):
                gaps.add(f"Unknown request interval: {row.location}")
                phase = Phase.UNKNOWN
            if self._overlaps(row.at, end, registration, ready):
                quiet.add(identity)
            if self._crosses(row.at, end, boundaries):
                phase = Phase.CROSS_BOUNDARY
                crossing += 1
            phases[identity] = phase
        return phases, quiet, crossing

    @staticmethod
    def _crosses(start: float, end: float, boundaries: list[float]) -> bool:
        return math.isfinite(end) and any(start < boundary < end for boundary in boundaries)

    @staticmethod
    def _request_end(row: EvidenceRecord) -> float:
        try:
            end = number_value(row.data, "end_at")
            if end < row.at:
                reject("Request end precedes its start")
        except ValueError:
            return float("inf")
        return end

    @staticmethod
    def _overlaps(start: float, end: float, lower: float | None, upper: float | None) -> bool:
        if lower is None or upper is None:
            return False
        return start < upper and end > lower

    def _polling(self, groups: dict[str, list[EvidenceRecord]], gaps: set[str]) -> tuple[int, set[str]]:
        calls = self._index(groups.get("tool_call", []), "call_id", gaps)
        results = self._index(groups.get("tool_result", []), "call_id", gaps)
        owners: dict[str, str | None] = {}
        polling: set[str] = set()
        count = 0
        for call_id, row in results.items():
            if row.data.get("observation") != "unchanged":
                continue
            count += 1
            owner = self._owner(call_id, calls, owners)
            if owner is None:
                gaps.add(f"Unresolved tool ancestry: {row.location}")
            if owner is not None:
                polling.add(owner)
        return count, polling

    @staticmethod
    def _owner(call_id: str, calls: dict[str, EvidenceRecord], owners: dict[str, str | None]) -> str | None:
        trail: set[str] = set()
        current, owner = call_id, None
        while current not in owners:
            if current in trail or current not in calls:
                break
            trail.add(current)
            data = calls[current].data
            candidate = data.get("attempt_id")
            if isinstance(candidate, str):
                owner = candidate
                break
            parent = data.get("parent_id")
            if not isinstance(parent, str):
                break
            current = parent
        else:
            owner = owners[current]
        for visited in trail:
            owners[visited] = owner
        return owner

    def _usage(self, groups: dict[str, list[EvidenceRecord]], phases: dict[str, Phase],
               gaps: set[str]) -> tuple[Usage, dict[str, Usage], dict[str, EvidenceRecord]]:
        completions = self._index(groups.get("usage_completion", []), "attempt_id", gaps)
        per_phase = {str(phase): _empty() for phase in Phase}
        epochs: dict[str, list[tuple[str, Usage, Phase]]] = defaultdict(list)
        for identity, row in completions.items():
            try:
                usage = usage_value(row.data.get("usage"))
                epoch = text_value(row.data, "epoch")
            except ValueError:
                usage, epoch = _unknown(), "unknown"
                gaps.add(f"Invalid usage payload: {row.location}")
            phase = phases.get(identity, Phase.UNKNOWN)
            epochs[epoch].append((identity, usage, phase))
            _add(per_phase[str(phase)], usage)
        baseline = self._baselines(groups, gaps)
        latest = self._cumulative(groups, gaps)
        total = _empty()
        for epoch in dict.fromkeys([*epochs, *latest]):
            measured = [(identity, usage, phase) for identity, usage, phase in epochs[epoch]
                        if phase not in EXCLUDED_PHASES]
            _add(total, self._epoch_total(measured, latest.get(epoch), baseline.get(epoch), gaps))
        self._missing_usage(phases, completions, per_phase, total, gaps)
        for usage in [total, *per_phase.values()]:
            self._uncached(usage, gaps)
        return total, per_phase, completions

    def _baselines(self, groups: dict[str, list[EvidenceRecord]], gaps: set[str]) -> dict[str, Usage]:
        baseline = dict(self.manifest.baselines)
        for row in groups.get("counter_reset", []):
            try:
                epoch = text_value(row.data, "epoch")
                value = usage_value(row.data.get("usage"))
                if epoch in baseline and baseline[epoch] != value:
                    reject("Counter epoch baseline conflict")
                baseline[epoch] = value
            except ValueError:
                gaps.add(f"Invalid counter reset: {row.location}")
        return baseline

    @staticmethod
    def _cumulative(groups: dict[str, list[EvidenceRecord]], gaps: set[str]) -> dict[str, EvidenceRecord]:
        latest: dict[str, EvidenceRecord] = {}
        for row in groups.get("cumulative_usage", []):
            epoch = row.data.get("epoch")
            if not isinstance(epoch, str):
                gaps.add(f"Missing cumulative epoch: {row.location}")
                continue
            previous = latest.get(epoch)
            if previous is None or row.at > previous.at:
                latest[epoch] = row
        return latest

    def _epoch_total(self, measured: list[tuple[str, Usage, Phase]], cumulative: EvidenceRecord | None,
                     baseline: Usage | None, gaps: set[str]) -> Usage:
        subtotal = _empty()
        for _, usage, _ in measured:
            _add(subtotal, usage)
        if cumulative is None or cumulative.at <= self.manifest.created_at:
            return subtotal
        try:
            delta = self._delta(cumulative.data, baseline)
            if self._covered(cumulative.data) != {identity for identity, _, _ in measured}:
                reject("Cumulative and per-request spans cannot be reconciled")
            self._agree(subtotal, delta)
        except ValueError:
            gaps.add(f"Unreconciled cumulative usage: {cumulative.location}")
            return _unknown()
        return delta

    @staticmethod
    def _covered(data: JsonObject) -> set[str]:
        covered = data.get("attempt_ids")
        if not isinstance(covered, list) or any(not isinstance(item, str) for item in covered):
            reject("Cumulative request coverage is unknown")
        return {str(item) for item in covered}

    @staticmethod
    def _agree(subtotal: Usage, delta: Usage) -> None:
        for name in TOKEN_FIELDS:
            known, count = subtotal[name], delta[name]
            if known is not None and count is not None and known != count:
                reject("Cumulative and per-request counts disagree")

    @staticmethod
    def _missing_usage(phases: dict[str, Phase], completions: dict[str, EvidenceRecord],
                       per_phase: dict[str, Usage], total: Usage, gaps: set[str]) -> None:
        for identity in phases.keys() - completions.keys():
            _add(per_phase[str(phases[identity])], _unknown())
            if phases[identity] not in EXCLUDED_PHASES:
                _add(total, _unknown())
            gaps.add("Request has no usage completion")

    def _uncached(self, usage: Usage, gaps: set[str]) -> None:
        inputs, cached = usage["input"], usage["cached_input"]
        usage["uncached_input"] = None
        if inputs is None or cached is None:
            return
        if cached > inputs:
            gaps.add("Cached input exceeds total input")
        elif self.manifest.cached_input_included is True:
            usage["uncached_input"] = inputs - cached

    @staticmethod
    def _delta(data: JsonObject, baseline: Usage | None) -> Usage:
        if baseline is None:
            reject("Missing pre-start counter baseline")
        current = usage_value(data.get("usage"))
        result: Usage = {}
        for name in TOKEN_FIELDS:
            before, after = baseline[name], current[name]
            if before is not None and after is not None and after < before:
                reject("Counter decreased without a new epoch")
            result[name] = after - before if before is not None and after is not None else None
        return result

    def _snapshot(self, now: float) -> _Snapshot:
        groups = self._groups(now)
        bounds = self._boundaries(groups)
        gaps: set[str] = set()
        gaps.update(self._boundary_gaps(bounds))
        gaps.update(str(row.data.get("reason")) for row in groups.get("gap", []))
        requests = self._index(groups.get("request_attempt", []), "attempt_id", gaps)
        phases, quiet, crossing = self._phases(requests, bounds, gaps)
        polling_calls, polling = self._polling(groups, gaps)
        request_gaps = set(gaps)
        total, phase_usage, completions = self._usage(groups, phases, gaps)
        if completions.keys() - requests.keys():
            request_gaps.add("Usage completion has no request attempt")
        if groups.get("clock_discontinuity") or self._drain.discontinuity:
            request_gaps.add("Suspension or UTC discontinuity: retain and repeat pair")
        gaps.update(request_gaps)
        coverage = self._coverage(groups, self._end(bounds), gaps, request_gaps)
        return _Snapshot(groups, bounds, requests, phases, quiet, crossing, polling_calls,
                         polling, total, phase_usage, completions, coverage)

    def _coverage(self, groups: dict[str, list[EvidenceRecord]], end: float | None,
                  gaps: set[str], request_gaps: set[str]) -> CoverageAssessment:
        coverage_rows = [row for row in groups.get("coverage", []) if end is not None and self._through(row) >= end]
        return CoverageAssessment(
            "complete" if not request_gaps and any(row.data.get("requests") is True for row in coverage_rows) else "incomplete",
            "complete" if not gaps and any(row.data.get("usage") is True for row in coverage_rows) else "incomplete",
            tuple(gaps),
        )

    def _quiet_duration(self, bounds: dict[str, float]) -> float | None:
        registration = "pending_return" if self.manifest.arm == Arm.CLASSIC else "normal_turn_end"
        return self._duration(bounds, registration, "source_ready")

    @staticmethod
    def _consumptions(groups: dict[str, list[EvidenceRecord]]) -> int:
        identities = [row.data.get("logical_id") for row in groups.get("consumption", [])]
        return len({identity for identity in identities if isinstance(identity, str)})

    def _correct(self, snapshot: _Snapshot) -> bool:
        latency = self._duration(snapshot.bounds, "source_ready", "useful_continuation")
        if latency is None:
            return False
        automatic = any(row.data.get("automatic") is True and row.at == snapshot.bounds["useful_continuation"]
                        for row in snapshot.groups.get("useful_continuation", []))
        return all((automatic, self._consumptions(snapshot.groups) == 1,
                    self._end(snapshot.bounds) is not None, 0 <= latency <= self.manifest.wake_bound))

    def _strict(self, snapshot: _Snapshot) -> bool:
        return all((self.manifest.arm != Arm.CLASSIC, snapshot.coverage.request_coverage == "complete",
                    self._correct(snapshot), (self._quiet_duration(snapshot.bounds) or 0) > 0,
                    not snapshot.quiet, not snapshot.crossing))

    @staticmethod
    def _polling_input(snapshot: _Snapshot) -> int | None:
        polling_input: int | None = 0
        for identity in snapshot.polling:
            row = snapshot.completions.get(identity)
            try:
                usage = usage_value(row.data.get("usage") if row is not None else None)
                count = usage["input"]
            except ValueError:
                count = None
            polling_input = polling_input + count if polling_input is not None and count is not None else None
        return polling_input

    def _status(self, snapshot: _Snapshot, now: float) -> str:
        if snapshot.groups.get("clock_discontinuity") or self._drain.discontinuity:
            return "invalid"
        coverage = snapshot.coverage
        if coverage.request_coverage != "complete" or coverage.usage_coverage != "complete" or not self.drained(now):
            return "inconclusive"
        passed = self._correct(snapshot) and (self.manifest.arm == Arm.CLASSIC or self._strict(snapshot))
        return "passed" if passed else "failed"

    @staticmethod
    def _tool_diagnostics(groups: dict[str, list[EvidenceRecord]]) -> tuple[int, int, int | None]:
        """Keep literal wait/non-wait counts separate from correlated polling."""
        calls = {str(row.data.get("call_id")): row for row in groups.get("tool_call", [])}
        waits = sum(str(row.data.get("name", "")).rsplit(".", 1)[-1] in {"wait", "sleep", "wait_agent"}
                    for row in calls.values())
        deliveries = groups.get("delivery", [])
        values = [row.data.get("logical_id") for row in deliveries]
        identities = {value for value in values if isinstance(value, str)}
        wakes = len(identities) or None
        return waits, len(calls) - waits, wakes

    def report(self, now: float, *, version: int = 1) -> TrialReport:
        """Build a redacted snapshot; publishing a version is a separate port."""
        if version < 1 or not math.isfinite(now):
            reject("Reports require a positive version and finite observation time")
        snapshot = self._snapshot(now)
        coverage, bounds, groups = snapshot.coverage, snapshot.bounds, snapshot.groups
        quiet_duration = self._quiet_duration(bounds)
        attempts, completions, phase_attempts = self._attempt_counts(snapshot)
        evidence = dict.fromkeys(row.location for rows in groups.values() for row in rows)
        waits, non_waits, wakes = self._tool_diagnostics(groups)
        return {
            "version": version, "run_id": self.manifest.run_id, "pair_id": self.manifest.pair_id,
            "series_id": self.manifest.series_id, "arm": str(self.manifest.arm), "host": self.manifest.host,
            "build": self.manifest.build, "model": self.manifest.model,
            "configuration_hash": self.manifest.configuration_hash, "seed_hashes": self.manifest.seed_hashes,
            "context_tokens": self.manifest.context_tokens, "synthetic": True, "status": self._status(snapshot, now),
            "thread_identity": identity_digest(self.manifest.host, self.manifest.profile, self.manifest.thread),
            "repository_identity": identity_digest(str(self.manifest.repository)),
            "timing_bounds": {"wake": self.manifest.wake_bound, "duplicate": self.manifest.duplicate_window,
                              "drain": self.manifest.drain_bound},
            "request_coverage": coverage.request_coverage, "usage_coverage": coverage.usage_coverage,
            "strict_zero_inference": self._strict(snapshot), "attempts": attempts, "completions": completions,
            "observed_attempts": len(snapshot.requests), "observed_completions": len(snapshot.completions),
            "retries": sum("retry_of" in row.data for row in snapshot.requests.values()),
            "compactions": len(groups.get("compaction", [])), "quiet_attempts": len(snapshot.quiet),
            "cross_phase_attempts": snapshot.crossing, "polling_calls": snapshot.polling_calls,
            "wait_tool_calls": waits, "non_wait_tool_calls": non_waits, "logical_wakes": wakes,
            "wait_induced_attempts": len(snapshot.polling), "wait_induced_input": self._polling_input(snapshot),
            "logical_consumptions": self._consumptions(groups), "usage": snapshot.usage, "phase_usage": snapshot.phase_usage,
            "phase_attempts": phase_attempts, "source_duration": self._duration(bounds, "source_start", "source_ready"),
            "quiet_duration": None if quiet_duration is None else max(0.0, quiet_duration),
            "wake_latency": self._duration(bounds, "source_ready", "useful_continuation"),
            "end_to_end_duration": self._duration(bounds, "benchmark_prompt", "final_turn_end"),
            "overlap": quiet_duration is not None and quiet_duration < 0,
            "collection_complete": self.drained(now), "gaps": list(coverage.gaps),
            "evidence": list(evidence)[:MAX_EVIDENCE_REFERENCES], "evidence_count": len(evidence),
        }

    @staticmethod
    def _attempt_counts(snapshot: _Snapshot) -> tuple[int, int, dict[str, int]]:
        """Separate measurement counts from seed, auxiliary and later observations."""
        per_phase = dict.fromkeys((str(phase) for phase in Phase), 0)
        for phase in snapshot.phases.values():
            per_phase[str(phase)] += 1
        attempts = sum(phase not in EXCLUDED_PHASES for phase in snapshot.phases.values())
        completions = sum(snapshot.phases.get(identity, Phase.UNKNOWN) not in EXCLUDED_PHASES
                          for identity in snapshot.completions)
        return attempts, completions, per_phase

    @staticmethod
    def _duration(bounds: dict[str, float], start: str, end: str) -> float | None:
        return bounds[end] - bounds[start] if start in bounds and end in bounds else None


# eof
