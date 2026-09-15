"""Keep partial token semantics, incomplete phases and negative evidence explicit."""

# ruff: noqa: PLR2004 - Expected synthetic counters and phases are case inputs.

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    collect,
    event,
    lifecycle,
)
from tools.wait_evidence.models import EvidenceRecord

if TYPE_CHECKING:
    from pathlib import Path

    from tools.wait_evidence.models import JsonObject

pytestmark = pytest.mark.timeout(10)


class TestCollectorAccounting:
    """Partial usage and ambiguous timing never manufacture precise measurements."""

    def test_unverified_cached_inclusion_stays_unknown(self, tmp_path: Path) -> None:
        """Known input counters cannot imply uncached counts without inclusion semantics."""
        rows = [*lifecycle(), event("request_attempt", 244, attempt_id="a", end_at=246),
                event("usage_completion", 247, attempt_id="a", epoch="epoch-1",
                      usage={"input": 10, "cached_input": 3, "output": 2, "reasoning": 1})]
        collector = collect(tmp_path, rows)
        collector.manifest = replace(collector.manifest, cached_input_included=None)
        report = collector.report(486)
        assert report["usage"]["input"] == 10
        assert report["usage"]["uncached_input"] is None
        assert report["usage"]["output"] == 2

    def test_cached_counts_larger_than_input_are_not_precise(self, tmp_path: Path) -> None:
        """An inconsistent usage payload cannot pass the usage coverage criterion."""
        rows = [*lifecycle(), event("request_attempt", 244, attempt_id="a", end_at=246),
                event("usage_completion", 247, attempt_id="a", epoch="epoch-1",
                      usage={"input": 3, "cached_input": 10})]
        report = collect(tmp_path, rows).report(486)
        assert report["usage"]["uncached_input"] is None
        assert report["usage_coverage"] == "incomplete"

    def test_prestart_cumulative_record_is_only_a_baseline(self, tmp_path: Path) -> None:
        """A repeated old counter value is not new benchmark work."""
        rows = [*lifecycle(), event("cumulative_usage", 0, epoch="epoch-1", usage={"input": 100})]
        report = collect(tmp_path, rows).report(486)
        assert report["usage"]["input"] == 0

    def test_unknown_baseline_fields_stay_unknown(self, tmp_path: Path) -> None:
        """A current counter cannot recover a missing pre-start counter on its own."""
        rows = [*lifecycle(), event("request_attempt", 244, attempt_id="a", end_at=246),
                event("usage_completion", 247, attempt_id="a", epoch="epoch-1", usage={}),
                event("cumulative_usage", 248, epoch="epoch-1", attempt_ids=["a"], usage={"input": 100})]
        collector = collect(tmp_path, rows)
        collector.manifest = replace(collector.manifest, baselines={"epoch-1": {
            "input": None, "cached_input": None, "output": None, "reasoning": None}})
        assert collector.report(486)["usage"]["input"] is None

    @pytest.mark.parametrize("kind", ["source_start", "normal_turn_end", "final_turn_end"])
    def test_backwards_boundaries_are_a_gap(self, tmp_path: Path, kind: str) -> None:
        """A declared complete stream cannot make backwards lifecycle markers valid."""
        rows = [row for row in lifecycle() if row["kind"] != kind]
        rows.append(event(kind, -1, marker="WAIT_TEST_DONE"))
        report = collect(tmp_path, rows).report(486)
        assert report["request_coverage"] == "incomplete"
        assert report["strict_zero_inference"] is False

    @pytest.mark.parametrize(("at", "phase"), [(246, "useful_continuation"), (250, "duplicate_observation"), (400, "after_observation")])
    def test_phase_edges_keep_actual_request_time(self, tmp_path: Path, at: int, phase: str) -> None:
        """A delayed completion is attributed to the request's actual phase."""
        rows = [*lifecycle(), event("request_attempt", at, attempt_id="a", end_at=at),
                event("usage_completion", 450, attempt_id="a", epoch="epoch-1", usage={"input": 10})]
        report = collect(tmp_path, rows).report(486)
        assert report["phase_attempts"][phase] == 1
        assert report["phase_usage"][phase]["input"] == 10

    def test_request_without_prompt_has_unknown_phase(self, tmp_path: Path) -> None:
        """Missing start evidence prevents assigning a plausible-looking phase."""
        rows = [row for row in lifecycle() if row["kind"] != "benchmark_prompt"]
        rows.append(event("request_attempt", 244, attempt_id="a", end_at=246))
        assert collect(tmp_path, rows).report(486)["phase_attempts"]["unknown"] == 1

    def test_missing_seed_and_auxiliary_usage_stays_outside_benchmark_total(self, tmp_path: Path) -> None:
        """Unobserved auxiliary cost is unknown in its own bucket."""
        rows = [*lifecycle(), event("request_attempt", -2, attempt_id="seed", end_at=-1),
                event("request_attempt", 100, attempt_id="approval", end_at=101, scope="auxiliary")]
        report = collect(tmp_path, rows).report(486)
        assert report["usage"]["input"] == 0
        assert report["phase_usage"]["seed"]["input"] is None
        assert report["phase_usage"]["auxiliary"]["input"] is None

    def test_malformed_normalized_coverage_cannot_end_drain(self, tmp_path: Path) -> None:
        """The accounting port remains conservative if an adapter omits coverage bounds."""
        collector = collect(tmp_path, lifecycle()[:-1])
        collector.ingest(EvidenceRecord("bad-coverage", "coverage", 366, 366, "stream:1",
                                        {"through": "later", "requests": True, "usage": True}))
        assert collector.drained(486) is False
        assert collector.report(486)["request_coverage"] == "incomplete"

    @pytest.mark.parametrize("continuation", [
        event("useful_continuation", 244, automatic=False),
        event("useful_continuation", 242, automatic=True),
    ])
    def test_manual_or_premature_continuation_cannot_pass(self, tmp_path: Path, continuation: JsonObject) -> None:
        """Quiet request telemetry does not establish correct automatic continuation."""
        rows = [row for row in lifecycle() if row["kind"] != "useful_continuation"]
        rows.append(continuation)
        report = collect(tmp_path, rows).report(486)
        assert report["strict_zero_inference"] is False
        assert report["status"] in {"failed", "inconclusive"}

    def test_diagnostic_wait_counts_are_independent_of_polling(self, tmp_path: Path) -> None:
        """Tool naming is diagnostic; unchanged observations determine polling."""
        rows = [*lifecycle(), event("tool_call", 3, call_id="wait", name="functions.wait"),
                event("tool_call", 244, call_id="exec", name="exec"),
                event("delivery", 244, logical_id="result-1"),
                event("delivery", 245, logical_id="result-1")]
        report = collect(tmp_path, rows).report(486)
        assert report["wait_tool_calls"] == 1
        assert report["non_wait_tool_calls"] == 1
        assert report["polling_calls"] == 0
        assert report["logical_wakes"] == 1


# eof
