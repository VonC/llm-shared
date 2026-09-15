"""Preserve separate evidence arms, failed trials, context controls and versions."""

# ruff: noqa: PLR2004 - Synthetic deltas and quantiles are explicit expected evidence.

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    collect,
    lifecycle,
    manifest_data,
)
from tools.wait_evidence.reports import (
    _select,
    _statistics,
    main,
    summarize,
    write_report,
)

if TYPE_CHECKING:
    from tools.wait_evidence.models import TrialReport

pytestmark = pytest.mark.timeout(10)


def trial(root: Path, arm: str, inputs: int | None, **changes: object) -> TrialReport:
    """Produce a synthetic report with explicit treatment and matching controls."""
    report = collect(root, lifecycle()).report(486)
    report["arm"] = arm
    report["run_id"] = f"run-{arm}"
    report["thread_identity"] = f"thread-{arm}"
    report["usage"]["input"] = inputs
    for key, value in changes.items():
        if key == "status":
            report["status"] = str(value)
        if key == "context_tokens" and isinstance(value, int):
            report["context_tokens"] = value
    return report


class TestReports:
    """Report publication is exclusive and summaries preserve inconvenient results."""

    def test_paired_delta_and_counts(self, tmp_path: Path) -> None:
        """A matched pair reports its raw costs and negative treatment delta."""
        reports = [trial(tmp_path, "A", 100), trial(tmp_path, "B-prototype", 30)]
        result = summarize(reports)
        assert result["tested"] == 2
        assert result["passed"] == 2
        assert result["input_delta_statistics"] == {
            "series-1/B-prototype": {"median": -70, "minimum": -70, "maximum": -70},
        }
        assert result["trials"] == reports

    @pytest.mark.parametrize("status", ["failed", "invalid", "inconclusive"])
    def test_failed_and_inconclusive_trials_are_retained(self, tmp_path: Path, status: str) -> None:
        """Unsuccessful treatment runs remain visible and do not enter success medians."""
        reports = [trial(tmp_path, "A", 100), trial(tmp_path, "B-prototype", 30, status=status)]
        result = summarize(reports)
        assert result[status] == 1
        assert result["tested"] == 2
        assert result["input_delta_statistics"] == {}

    def test_mismatched_context_and_ambiguous_pairs(self, tmp_path: Path) -> None:
        """Context beyond five percent and multiple treatments never form valid pairs."""
        classic = trial(tmp_path, "A", 100)
        prototype = trial(tmp_path, "B-prototype", 30, context_tokens=12000)
        assert summarize([classic, prototype])["input_delta_statistics"] == {}
        assert summarize([classic, prototype, trial(tmp_path, "B-service", 20)])["tested"] == 3
        assert summarize([classic])["input_delta_statistics"] == {}
        assert summarize([classic, trial(tmp_path, "B-service", None)])["input_delta_statistics"] == {}

    @given(st.lists(st.integers(), min_size=1, max_size=50))
    def test_linear_selection_matches_order_statistics(self, values: list[int]) -> None:
        """The bounded-group selector handles duplicates and negative values."""
        rank = len(values) // 2
        assert _select(values, rank) == sorted(values)[rank]

    def test_empty_and_even_statistics(self) -> None:
        """No samples means unknown statistics; even counts use the central pair."""
        assert _statistics([]) == {"median": None, "minimum": None, "maximum": None}
        assert _statistics([5, 1, 8, 2]) == {"median": 3.5, "minimum": 1, "maximum": 8}

    def test_relative_report_path_rejected(self, tmp_path: Path) -> None:
        """Output cannot silently depend on the caller directory."""
        with pytest.raises(ValueError, match="absolute"):
            write_report(Path("report.json"), trial(tmp_path, "A", 10))

    def test_cli_snapshot_and_exclusive_output(self, tmp_path: Path) -> None:
        """The CLI records explicit snapshots and rejects replacement of a version."""
        manifest = tmp_path / "manifest.json"
        manifest.write_text(json.dumps(manifest_data(tmp_path)), encoding="utf-8")
        stream = tmp_path / "events.jsonl"
        stream.write_text("\n".join(json.dumps(row) for row in lifecycle()) + "\n",
                          encoding="utf-8")
        args = ["--manifest", str(manifest), "--output", str(tmp_path / "report.json"), "--as-of", "486"]
        assert main(args) == 0
        assert main(args) == 2

    def test_cli_rejects_relative_manifest(self, tmp_path: Path) -> None:
        """Input path validation occurs before any output creation."""
        assert main(["--manifest", "relative.json", "--output", str(tmp_path / "report.json"),
                     "--as-of", "486"]) == 2
        assert not (tmp_path / "report.json").exists()

    def test_cli_detects_replacement_after_manifest_publication(self, tmp_path: Path) -> None:
        """A new CLI reader cannot silently trust a replaced telemetry file."""
        stream = tmp_path / "events.jsonl"
        stream.write_bytes(b"")
        manifest = tmp_path / "manifest.json"
        manifest.write_text(json.dumps(manifest_data(tmp_path)), encoding="utf-8")
        replacement = tmp_path / "replacement.jsonl"
        replacement.write_text("\n".join(json.dumps(row) for row in lifecycle()) + "\n", encoding="utf-8")
        replacement.replace(stream)
        output = tmp_path / "report.json"
        assert main(["--manifest", str(manifest), "--output", str(output), "--as-of", "486"]) == 0
        report = json.loads(output.read_text(encoding="utf-8"))
        assert report["status"] == "inconclusive"
        assert report["strict_zero_inference"] is False
        assert any("Telemetry rotation or truncation" in gap for gap in report["gaps"])
        assert report["source_duration"] == 240

    def test_cli_retains_unfinished_input_as_inconclusive(self, tmp_path: Path) -> None:
        """An unfinished JSONL tail must appear as a gap in the published snapshot."""
        manifest = tmp_path / "manifest.json"
        manifest.write_text(json.dumps(manifest_data(tmp_path)), encoding="utf-8")
        (tmp_path / "events.jsonl").write_text(
            "\n".join(json.dumps(row) for row in lifecycle()) + '\n{"pending":', encoding="utf-8",
        )
        output = tmp_path / "report.json"
        assert main(["--manifest", str(manifest), "--output", str(output), "--as-of", "486"]) == 0
        report = json.loads(output.read_text(encoding="utf-8"))
        assert report["status"] == "inconclusive"
        assert report["strict_zero_inference"] is False
        assert any("Incomplete JSONL record" in gap for gap in report["gaps"])
        assert any("Missing baseline stream identity" in gap for gap in report["gaps"])

    def test_reused_thread_or_changed_bounds_invalidates_pair(self, tmp_path: Path) -> None:
        """Freshness and fixed series windows are experiment controls."""
        first, second = trial(tmp_path, "A", 100), trial(tmp_path, "B-prototype", 30)
        second["thread_identity"] = first["thread_identity"]
        assert summarize([first, second])["input_delta_statistics"] == {}
        second["thread_identity"] = "fresh"
        second["timing_bounds"] = {**second["timing_bounds"], "wake": 90}
        assert summarize([first, second])["input_delta_statistics"] == {}

    def test_changed_series_bounds_and_repeated_trials_are_retained(self, tmp_path: Path) -> None:
        """Changed windows cannot enter one series median and repeats remain visible."""
        first, second = trial(tmp_path, "A", 100), trial(tmp_path, "B-prototype", 30)
        third, fourth = trial(tmp_path, "A", 200), trial(tmp_path, "B-prototype", 20)
        for row in (third, fourth):
            row["pair_id"] = "pair-2"
            row["run_id"] += "-2"
            row["timing_bounds"] = {**row["timing_bounds"], "wake": 90}
        result = summarize([first, second, third, fourth])
        assert result["tested"] == 4
        assert result["input_delta_statistics"] == {}
        assert summarize([fourth, third, second, first])["input_delta_statistics"] == {}
        third["pair_id"] = "pair-1"
        assert summarize([first, second, third])["repeated"] == 1

    def test_two_versions_of_one_run_cannot_inflate_trial_count(self, tmp_path: Path) -> None:
        """Select an explicit amended snapshot instead of counting both as fresh trials."""
        first = trial(tmp_path, "A", 100)
        second: TrialReport = {**first, "version": 2}
        with pytest.raises(ValueError, match="one report version"):
            summarize([first, second])

# eof
