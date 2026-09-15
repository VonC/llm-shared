"""Exercise incomplete boundaries, counter epochs and tool ancestry explicitly."""

# ruff: noqa: PLR2004 - The small synthetic counts describe each regression.

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    collect,
    event,
    lifecycle,
)
from tools.wait_evidence.models import Arm
from tools.wait_evidence.telemetry import Telemetry

if TYPE_CHECKING:
    from pathlib import Path

    from tools.wait_evidence.models import JsonObject, JsonValue

pytestmark = pytest.mark.timeout(10)


def completion(at: float, identity: str, inputs: int, epoch: str = "epoch-1") -> JsonObject:
    """Supply a complete token record so omitted coverage stays intentional."""
    return event("usage_completion", at, attempt_id=identity, epoch=epoch,
                 usage={"input": inputs, "cached_input": 0, "output": 2, "reasoning": 1})


class TestCollectorEdges:
    """Evidence loss never becomes zero, while compatible epochs count once."""

    @pytest.mark.parametrize("missing", [
        "benchmark_prompt", "source_start", "normal_turn_end", "source_ready",
        "useful_continuation", "final_turn_end",
    ])
    def test_missing_boundary_prevents_success(self, tmp_path: Path, missing: str) -> None:
        """A coverage declaration does not supply missing lifecycle evidence."""
        rows = [row for row in lifecycle() if row["kind"] != missing]
        report = collect(tmp_path, rows).report(486)
        assert report["strict_zero_inference"] is False
        assert report["request_coverage"] == "incomplete"

    def test_conflicting_event_and_request_identities(self, tmp_path: Path) -> None:
        """Conflicting duplicate payloads remain a coverage gap after deduplication."""
        request = event("request_attempt", 244, attempt_id="a", end_at=245)
        conflict = event("request_attempt", 244, attempt_id="a", end_at=246)
        duplicate_id = event("request_attempt", 243, attempt_id="a", end_at=245)
        rows = [*lifecycle(), request, conflict, duplicate_id, completion(246, "a", 10)]
        report = collect(tmp_path, rows).report(486)
        assert report["attempts"] == 1
        assert report["request_coverage"] == "incomplete"
        assert any("Conflicting" in gap for gap in report["gaps"])

    @pytest.mark.parametrize("end", [None, "later", 243])
    def test_unknown_request_interval_prevents_zero(self, tmp_path: Path, end: JsonValue) -> None:
        """Missing or backwards request end times cannot be called idle."""
        rows = [*lifecycle(), event("request_attempt", 244, attempt_id="a", end_at=end)]
        report = collect(tmp_path, rows).report(486)
        assert report["request_coverage"] == "incomplete"
        assert report["strict_zero_inference"] is False
        assert report["usage"]["input"] is None

    @pytest.mark.parametrize("end", [None, "later", 243])
    def test_unknown_interval_is_not_an_observed_crossing(self, tmp_path: Path, end: JsonValue) -> None:
        """Unknown intervals retain unknown costs instead of inventing a crossing."""
        rows = [*lifecycle(), event("request_attempt", 244, attempt_id="a", end_at=end),
                completion(246, "a", 10)]
        report = collect(tmp_path, rows).report(486)
        assert report["phase_attempts"]["unknown"] == 1
        assert report["cross_phase_attempts"] == 0
        assert report["phase_usage"]["unknown"]["input"] == 10

    def test_missing_registration_keeps_request_phase_unknown(self, tmp_path: Path) -> None:
        """A known request cannot fill in the missing start of the idle interval."""
        rows = [row for row in lifecycle() if row["kind"] != "normal_turn_end"]
        rows.append(event("request_attempt", 100, attempt_id="a", end_at=101))
        report = collect(tmp_path, rows).report(486)
        assert report["phase_attempts"]["unknown"] == 1
        assert report["request_coverage"] == "incomplete"
        assert report["strict_zero_inference"] is False

    def test_conflicting_attempt_payload_in_distinct_events(self, tmp_path: Path) -> None:
        """Different event IDs do not legitimize contradictory data for one attempt."""
        rows = [*lifecycle(),
            event("request_attempt", 244, attempt_id="a", end_at=245),
            event("request_attempt", 245, attempt_id="a", end_at=246),
        ]
        report = collect(tmp_path, rows).report(486)
        assert report["attempts"] == 1
        assert report["request_coverage"] == "incomplete"
        assert any("Conflicting attempt_id" in gap for gap in report["gaps"])

    def test_seed_and_auxiliary_costs_are_separate(self, tmp_path: Path) -> None:
        """Pre-prompt preparation and auxiliary approvals do not inflate wait costs."""
        rows = [*lifecycle(),
            event("request_attempt", -2, attempt_id="seed", end_at=-1),
            completion(0, "seed", 90),
            event("request_attempt", 100, attempt_id="approval", end_at=101, scope="auxiliary"),
            completion(102, "approval", 20),
            event("request_attempt", 244, attempt_id="result", end_at=246),
            completion(247, "result", 10),
        ]
        report = collect(tmp_path, rows).report(486)
        assert report["usage"]["input"] == 10
        assert report["phase_usage"]["seed"]["input"] == 90
        assert report["phase_usage"]["auxiliary"]["input"] == 20
        assert report["quiet_attempts"] == 0
        assert report["strict_zero_inference"] is True

    def test_counter_reset_starts_an_independent_baseline(self, tmp_path: Path) -> None:
        """A reset epoch and a repeated cumulative sample are reconciled once."""
        rows = [*lifecycle(),
            event("request_attempt", 2, attempt_id="register", end_at=5),
            completion(6, "register", 10),
            event("counter_reset", 240, epoch="epoch-2", usage={
                "input": 0, "cached_input": 0, "output": 0, "reasoning": 0}),
            event("request_attempt", 244, attempt_id="result", end_at=246),
            completion(247, "result", 20, "epoch-2"),
            event("cumulative_usage", 248, epoch="epoch-2", attempt_ids=["result"], usage={
                "input": 20, "cached_input": 0, "output": 2, "reasoning": 1}),
        ]
        report = collect(tmp_path, rows).report(486)
        assert report["usage"]["input"] == 30
        assert report["usage"]["output"] == 4
        assert report["usage_coverage"] == "complete"

    @pytest.mark.parametrize(("epoch", "covered", "inputs"), [
        ("missing", ["a"], 110), ("epoch-1", None, 110),
        ("epoch-1", [1], 110), ("epoch-1", ["other"], 110),
        ("epoch-1", ["a"], 99), ("epoch-1", ["a"], 111),
    ])
    def test_unreconciled_cumulative_counts_are_unknown(
        self, tmp_path: Path, epoch: str, covered: JsonValue, inputs: int,
    ) -> None:
        """Unknown spans, missing baselines and counter disagreement cannot yield totals."""
        rows = [*lifecycle(), event("request_attempt", 244, attempt_id="a", end_at=246),
            completion(247, "a", 10, epoch),
            event("cumulative_usage", 248, epoch=epoch, attempt_ids=covered, usage={
                "input": inputs, "cached_input": 20, "output": 12, "reasoning": 3}),
        ]
        report = collect(tmp_path, rows).report(486)
        assert report["usage"]["input"] is None
        assert report["usage_coverage"] == "incomplete"

    @pytest.mark.parametrize("malformed", [
        event("request_attempt", 244, end_at=246),
        event("usage_completion", 247, attempt_id="a", epoch="epoch-1", usage=False),
        event("counter_reset", 240, usage={}),
        event("counter_reset", 240, epoch="epoch-1", usage={"input": 1}),
        event("cumulative_usage", 248, usage={}),
    ])
    def test_invalid_accounting_payloads_retain_gaps(self, tmp_path: Path, malformed: JsonObject) -> None:
        """Malformed identity and epoch fields are explicit evidence failures."""
        report = collect(tmp_path, [*lifecycle(), malformed]).report(486)
        assert report["usage_coverage"] == "incomplete"
        assert report["gaps"]

    @pytest.mark.parametrize("parents", [
        [], [event("tool_call", 10, call_id="child")],
        [event("tool_call", 10, call_id="child", parent_id="parent"),
         event("tool_call", 11, call_id="parent", parent_id="child")],
    ])
    def test_unresolved_tool_ancestry_cannot_prove_zero(self, tmp_path: Path, parents: list[JsonObject]) -> None:
        """Missing parents and cycles terminate with an explicit correlation gap."""
        rows = [*lifecycle(), *parents, event("tool_result", 12, call_id="child", observation="unchanged")]
        report = collect(tmp_path, rows).report(486)
        assert report["polling_calls"] == 1
        assert report["wait_induced_attempts"] == 0
        assert report["strict_zero_inference"] is False

    def test_shared_tool_parent_counts_one_attempt(self, tmp_path: Path) -> None:
        """Two unchanged observations share a request without charging it twice."""
        rows = [*lifecycle(), event("request_attempt", 10, attempt_id="a", end_at=20),
            event("tool_call", 11, call_id="parent", attempt_id="a"),
            event("tool_call", 12, call_id="first", parent_id="parent"),
            event("tool_call", 13, call_id="second", parent_id="parent"),
            event("tool_result", 14, call_id="first", observation="unchanged"),
            event("tool_result", 15, call_id="second", observation="unchanged"),
            event("tool_result", 16, call_id="useful", observation="terminal"),
        ]
        collector = collect(tmp_path, rows)
        report = collector.report(486)
        assert report["polling_calls"] == 2
        assert report["wait_induced_attempts"] == 1
        assert report["wait_induced_input"] is None
        adapter = Telemetry(collector.manifest)
        collector.ingest(adapter.normalize(event("usage_completion", 21, attempt_id="a", usage=False), "late:1", 487))
        assert collector.report(487, version=2)["wait_induced_input"] is None

    def test_late_evidence_changes_only_the_new_snapshot(self, tmp_path: Path) -> None:
        """Both ingestion time and actual request time constrain a snapshot."""
        collector = collect(tmp_path, lifecycle())
        adapter = Telemetry(collector.manifest)
        row = event("request_attempt", 100, attempt_id="late", end_at=110)
        collector.ingest(adapter.normalize(row, "late:0", 490))
        assert collector.report(486)["strict_zero_inference"] is True
        report = collector.report(490, version=2)
        assert report["quiet_attempts"] == 1
        assert report["strict_zero_inference"] is False

    def test_future_conflict_does_not_rewrite_an_earlier_snapshot(self, tmp_path: Path) -> None:
        """A conflict is attributed when it arrived, just like an ordinary record."""
        collector = collect(tmp_path, lifecycle())
        adapter = Telemetry(collector.manifest)
        conflict = event("normal_turn_end", 5, conflicting=True)
        collector.ingest(adapter.normalize(conflict, "late:0", 490))
        assert collector.report(486)["strict_zero_inference"] is True
        assert collector.report(490)["strict_zero_inference"] is False

    def test_classic_uses_pending_return_for_wait_boundary(self, tmp_path: Path) -> None:
        """The classic arm can pass while recording polling; it never claims strict zero."""
        collector = collect(tmp_path, [*lifecycle(), event("pending_return", 6)])
        collector.manifest = replace(collector.manifest, arm=Arm.CLASSIC)
        report = collector.report(486)
        assert report["quiet_duration"] == 237
        assert report["status"] == "passed"
        assert report["strict_zero_inference"] is False

    def test_discontinuity_invalidates_the_trial(self, tmp_path: Path) -> None:
        """Suspension evidence remains visible and requires retaining and repeating the pair."""
        report = collect(tmp_path, [*lifecycle(), event("clock_discontinuity", 100)]).report(486)
        assert report["status"] == "invalid"
        assert report["strict_zero_inference"] is False

    def test_utc_jump_does_not_finish_monotonic_drain(self, tmp_path: Path) -> None:
        """Advancing the wall clock cannot spend the monotonic observation budget."""
        collector = collect(tmp_path, lifecycle()[:-1])
        assert collector.drained(366, monotonic_at=1000) is False
        assert collector.drained(600, monotonic_at=1001) is False
        assert collector.report(600)["status"] == "invalid"
        assert collector.drained(719, monotonic_at=1120) is True

    def test_offline_clock_does_not_claim_a_live_drain(self, tmp_path: Path) -> None:
        """An offline as-of timestamp alone is not elapsed-time evidence."""
        collector = collect(tmp_path, lifecycle()[:-1])
        assert collector.drained(10000) is False
        with pytest.raises(ValueError, match="monotonic"):
            collector.drained(10000, monotonic_at=float("nan"))

    def test_backwards_monotonic_time_invalidates_drain(self, tmp_path: Path) -> None:
        """Broken process clock observations cannot preserve a passing trial."""
        collector = collect(tmp_path, lifecycle()[:-1])
        collector.drained(366, monotonic_at=1000)
        collector.drained(367, monotonic_at=999)
        assert collector.report(486)["status"] == "invalid"

    @pytest.mark.parametrize(("now", "version"), [(float("nan"), 1), (486, 0)])
    def test_invalid_report_parameters(self, tmp_path: Path, now: float, version: int) -> None:
        """Nonfinite snapshots and invalid version numbers fail before publication."""
        with pytest.raises(ValueError, match="positive version"):
            collect(tmp_path, lifecycle()).report(now, version=version)


# eof
