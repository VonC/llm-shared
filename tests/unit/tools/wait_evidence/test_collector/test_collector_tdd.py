"""Prove exact accounting and conservative coverage with synthetic evidence."""

# ruff: noqa: PLR2004 - Expected synthetic measurements belong beside assertions.

from __future__ import annotations

import json
import os
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.wait_evidence.collector import Collector
from tools.wait_evidence.models import TrialManifest, number_value
from tools.wait_evidence.reports import write_report
from tools.wait_evidence.telemetry import Telemetry

if TYPE_CHECKING:
    from tools.wait_evidence.models import JsonObject

pytestmark = pytest.mark.timeout(10)


def stream_data(path: Path, offset: int = 0) -> JsonObject:
    """Freeze a fixture's file identity and bounded pre-offset fingerprint."""
    result: JsonObject = {"path": str(path), "offset": offset}
    if path.exists():
        stat = path.stat()
        with path.open("rb") as stream:
            stream.seek(max(0, offset - 4096))
            anchor = stream.read(min(offset, 4096))
        result.update(file_id=[stat.st_dev, stat.st_ino], anchor_sha256=sha256(anchor).hexdigest())
    return result


def manifest_data(root: Path) -> JsonObject:
    """Build an explicit synthetic trial with an established counter baseline."""
    return {
        "series_id": "series-1", "pair_id": "pair-1", "run_id": "run-b",
        "arm": "B-prototype", "host": "synthetic", "build": "test-1",
        "thread": "thread-1", "profile": "profile-1", "schema": "synthetic-v1",
        "model": "synthetic-model", "configuration_hash": "a" * 64,
        "repository": str(root), "home": str(root / "home"),
        "seed_hashes": {"umbrella": "b" * 64, "child": "c" * 64},
        "context_tokens": 10000, "source_id": "source-1",
        "ready_at": 0, "created_at": 1,
        "wake_bound": 60, "duplicate_window": 120, "drain_bound": 120,
        "streams": [stream_data(root / "events.jsonl")],
        "baselines": {"epoch-1": {"input": 100, "cached_input": 20,
                                   "output": 10, "reasoning": 2}},
        "cached_input_included": True, "reasoning_included": True,
    }


def event(kind: str, at: float, **data: object) -> JsonObject:
    """Create one schema-labelled event; arbitrary extras remain JSON values."""
    if kind == "coverage":
        data.setdefault("since", 1)
    return {
        "schema": "synthetic-v1", "host": "synthetic", "build": "test-1",
        "thread": "thread-1", "profile": "profile-1", "source_id": "source-1",
        "event_id": f"{kind}-{at}-{data.get('attempt_id', '')}",
        "kind": kind, "at": at, "data": json.loads(json.dumps(data)),
    }


def collect(root: Path, rows: list[JsonObject]) -> Collector:
    """Normalize explicit synthetic rows without filesystem discovery or waits."""
    manifest = TrialManifest.from_dict(manifest_data(root))
    collector = Collector(manifest)
    adapter = Telemetry(manifest)
    for offset, row in enumerate(rows):
        record = adapter.normalize(row, f"events.jsonl:{offset}", number_value(row, "at"))
        collector.ingest(record)
    return collector


def lifecycle() -> list[JsonObject]:
    """An ordinary registration end followed by one automatic useful turn."""
    return [
        event("benchmark_prompt", 2), event("source_start", 3),
        event("normal_turn_end", 5), event("source_ready", 243),
        event("useful_continuation", 244, automatic=True),
        event("consumption", 245, logical_id="result-1"),
        event("final_turn_end", 246, marker="WAIT_TEST_DONE"),
        event("coverage", 366, requests=True, usage=True, through=366),
    ]


class TestCollector:
    """Cover deduplication, attribution, unknown coverage and bounded draining."""

    def test_duplicate_usage_and_baseline_are_counted_once(self, tmp_path: Path) -> None:
        """Cumulative and per-attempt representations reconcile without inflation."""
        baseline = event("cumulative_usage", 0, epoch="epoch-1", usage={
            "input": 100, "cached_input": 20, "output": 10, "reasoning": 2,
        }, attempt_ids=[])
        usage = {"input": 30, "cached_input": 10, "output": 4, "reasoning": 1}
        rows = [*lifecycle(), baseline, baseline,
            event("request_attempt", 244, attempt_id="a1", request_id="r1", end_at=246),
            event("usage_completion", 249, attempt_id="a1", epoch="epoch-1", usage=usage),
            event("usage_completion", 250, attempt_id="a1", epoch="epoch-1", usage=usage),
            event("cumulative_usage", 251, epoch="epoch-1", attempt_ids=["a1"], usage={
                "input": 130, "cached_input": 30, "output": 14, "reasoning": 3,
            }),
        ]
        report = collect(tmp_path, rows).report(486)
        assert report["attempts"] == 1
        assert report["completions"] == 1
        assert report["usage"] == {**usage, "uncached_input": 20}
        assert report["strict_zero_inference"] is True
        assert report["quiet_duration"] == 238
        assert report["wake_latency"] == 1
        assert report["source_duration"] == 240

    def test_usage_does_not_prove_request_coverage(self, tmp_path: Path) -> None:
        """A usage-only source cannot prove zero attempted requests."""
        rows = [*lifecycle()[:-1],
            event("coverage", 486, requests=False, usage=True, through=366),
            event("usage_completion", 10, attempt_id="missing", epoch="epoch-1",
                  usage={"input": 7}),
        ]
        report = collect(tmp_path, rows).report(486)
        assert report["request_coverage"] == "incomplete"
        assert report["strict_zero_inference"] is False
        assert report["usage"]["output"] is None
        assert report["status"] == "inconclusive"

    def test_retries_compaction_and_cross_phase_requests(self, tmp_path: Path) -> None:
        """Transport attempts and ambiguous boundary crossings stay visible."""
        rows = [*lifecycle(),
            event("request_attempt", 4, attempt_id="a1", request_id="r1", end_at=6),
            event("request_attempt", 7, attempt_id="a2", request_id="r1", end_at=8,
                  retry_of="a1", error="transport"),
            event("compaction", 9),
        ]
        report = collect(tmp_path, rows).report(486)
        assert report["attempts"] == 2
        assert report["retries"] == 1
        assert report["compactions"] == 1
        assert report["cross_phase_attempts"] == 1
        assert report["quiet_attempts"] == 2
        assert report["strict_zero_inference"] is False

    def test_nested_polling_uses_call_ids_not_tool_name(self, tmp_path: Path) -> None:
        """A nested generic command observing unchanged work is a polling call."""
        rows = [*lifecycle(),
            event("tool_result", 21, call_id="child", observation="unchanged"),
            event("tool_call", 19, call_id="parent", attempt_id="a1", name="exec"),
            event("tool_call", 20, call_id="child", parent_id="parent",
                  name="arbitrary-command"),
            event("request_attempt", 18, attempt_id="a1", request_id="r1", end_at=22),
            event("usage_completion", 23, attempt_id="a1", epoch="epoch-1",
                  usage={"input": 50}),
        ]
        report = collect(tmp_path, rows).report(486)
        assert report["polling_calls"] == 1
        assert report["wait_induced_attempts"] == 1
        assert report["wait_induced_input"] == 50

    def test_drain_needs_authoritative_completeness(self, tmp_path: Path) -> None:
        """Fake monotonic time drives a 120-second drain without sleeping."""
        collector = collect(tmp_path, lifecycle()[:-1])
        assert collector.drained(365) is False
        assert collector.drained(366, monotonic_at=1000) is False
        assert collector.drained(485, monotonic_at=1119) is False
        assert collector.drained(486, monotonic_at=1120) is True
        assert collector.report(486)["request_coverage"] == "incomplete"
        complete = collect(tmp_path, lifecycle())
        assert complete.drained(366) is True

    def test_early_source_and_duplicate_consumption(self, tmp_path: Path) -> None:
        """Overlapping registration has zero quiet time and cannot pass a baseline."""
        rows = lifecycle()
        rows[3] = event("source_ready", 4)
        rows.append(event("consumption", 247, logical_id="result-2"))
        report = collect(tmp_path, rows).report(486)
        assert report["quiet_duration"] == 0
        assert report["overlap"] is True
        assert report["logical_consumptions"] == 2
        assert report["strict_zero_inference"] is False

    def test_report_versions_never_replace_published_evidence(self, tmp_path: Path) -> None:
        """Late evidence requires another explicit output path and version."""
        collector = collect(tmp_path, lifecycle())
        path = tmp_path / "report.v1.json"
        write_report(path, collector.report(486))
        original = path.read_bytes()
        with pytest.raises(FileExistsError):
            write_report(path, collector.report(487, version=2))
        assert path.read_bytes() == original
        write_report(tmp_path / "report.v2.json", collector.report(487, version=2))

    @pytest.mark.parametrize("outside", [False, True])
    def test_cli_bootstraps_from_script_location(self, tmp_path: Path, *, outside: bool) -> None:
        """Absolute CLI invocation works in either cwd without PYTHONPATH."""
        root = Path(__file__).resolve().parents[5]
        manifest = tmp_path / "manifest.json"
        manifest.write_text(json.dumps(manifest_data(tmp_path)), encoding="utf-8")
        stream = tmp_path / "events.jsonl"
        stream.write_text("\n".join(json.dumps(row) for row in lifecycle()) + "\n",
                          encoding="utf-8")
        output = tmp_path / "report.json"
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        completed = subprocess.run(  # noqa: S603 - fixed interpreter and repository script
            # The standalone collector needs only stdlib. Skip site startup hooks
            # and isolate imports to test its physical-path bootstrap directly.
            [sys.executable, "-I", "-S", str(root / "docs/v0.13.0/collect.shared-wait-service.py"),
             "--manifest", str(manifest), "--output", str(output), "--as-of", "486"],
            cwd=tmp_path if outside else root, env=environment,
            capture_output=True, text=True, check=False, timeout=5,
        )
        assert completed.returncode == 0, completed.stderr
        assert json.loads(output.read_text(encoding="utf-8"))["arm"] == "B-prototype"

# eof
