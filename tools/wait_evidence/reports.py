"""Immutable evidence snapshots and paired summaries with explicit unknowns.

Reports retain each treatment label and failed trial. Medians use linear
selection; grouping uses direct identities instead of pairwise searches.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from .collector import Collector
from .models import TrialManifest, object_value, reject
from .telemetry import Telemetry

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .models import TrialReport

SELECTION_GROUP_SIZE = 5
CONTEXT_TOLERANCE = 0.05


def write_report(path: Path, report: TrialReport) -> None:
    """Create exactly one immutable report version at an explicit output path."""
    if not path.is_absolute():
        reject("Report output must be an explicit absolute path")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")


def _select(values: list[int], rank: int) -> int:
    """Select an order statistic with bounded five-element sorting only."""
    if len(values) <= SELECTION_GROUP_SIZE:
        return sorted(values)[rank]
    medians = [sorted(values[start:start + 5])[len(values[start:start + 5]) // 2]
               for start in range(0, len(values), 5)]
    pivot = _select(medians, len(medians) // 2)
    lower: list[int] = []
    upper: list[int] = []
    equal = 0
    for value in values:
        if value < pivot:
            lower.append(value)
        elif value > pivot:
            upper.append(value)
        else:
            equal += 1
    if rank < len(lower):
        return _select(lower, rank)
    if rank < len(lower) + equal:
        return pivot
    return _select(upper, rank - len(lower) - equal)


def _statistics(values: list[int]) -> dict[str, int | float | None]:
    if not values:
        return {"median": None, "minimum": None, "maximum": None}
    count = len(values)
    median = (_select(values, count // 2) + _select(values, (count - 1) // 2)) / 2
    return {"median": median, "minimum": min(values), "maximum": max(values)}


def summarize(reports: Sequence[TrialReport]) -> dict[str, object]:
    """Keep raw trials and summarize compatible exact pairs without relabeling arms."""
    groups = _group_reports(reports)
    invalid_series = _invalid_series(reports)
    pairs: list[dict[str, object]] = []
    deltas: dict[str, list[int]] = defaultdict(list)
    for (series_id, pair_id), trials in groups.items():
        classic, treatment = _arms(trials)
        row: dict[str, object] = {"series_id": series_id, "pair_id": pair_id,
                                  "runs": [trial["run_id"] for trial in trials], "status": "inconclusive"}
        if len(classic) == len(treatment) == 1:
            first, second = classic[0], treatment[0]
            row.update(_pair(first, second))
            if series_id in invalid_series:
                row["status"] = "invalid"
            _retain_delta(row, trials, deltas)
        pairs.append(row)
    counts = Counter(report["status"] for report in reports)
    return {
        "tested": len(reports), "valid": counts["passed"] + counts["failed"],
        "passed": counts["passed"], "failed": counts["failed"], "invalid": counts["invalid"],
        "inconclusive": counts["inconclusive"], "trials": list(reports), "pairs": pairs,
        "repeated": len(reports) - len({(row["series_id"], row["pair_id"], row["arm"]) for row in reports}),
        "input_delta_statistics": {key: _statistics(values) for key, values in deltas.items()},
    }


def _group_reports(reports: Sequence[TrialReport]) -> dict[tuple[str, str], list[TrialReport]]:
    groups: dict[tuple[str, str], list[TrialReport]] = defaultdict(list)
    runs: set[tuple[str, str]] = set()
    for report in reports:
        identity = (report["series_id"], report["run_id"])
        if identity in runs:
            reject("Select one report version per run before summarizing")
        runs.add(identity)
        groups[report["series_id"], report["pair_id"]].append(report)
    return groups


def _invalid_series(reports: Sequence[TrialReport]) -> set[str]:
    """Reject changed windows or reused conversations independently of input order."""
    bounds: dict[str, dict[str, float]] = {}
    threads: dict[str, str] = {}
    invalid: set[str] = set()
    for row in reports:
        series = row["series_id"]
        if bounds.setdefault(series, row["timing_bounds"]) != row["timing_bounds"]:
            invalid.add(series)
        previous = threads.get(row["thread_identity"])
        if previous is not None:
            invalid.update((series, previous))
        threads[row["thread_identity"]] = series
    return invalid


def _arms(trials: Sequence[TrialReport]) -> tuple[list[TrialReport], list[TrialReport]]:
    classic = [trial for trial in trials if trial["arm"] == "A"]
    treatment = [trial for trial in trials if trial["arm"] in ("B-prototype", "B-service")]
    return classic, treatment


def _pair(first: TrialReport, second: TrialReport) -> dict[str, object]:
    match = all(first[key] == second[key] for key in (
        "host", "build", "model", "configuration_hash", "seed_hashes", "synthetic",
        "repository_identity", "timing_bounds",
    ))
    tolerance = abs(first["context_tokens"] - second["context_tokens"]) / max(first["context_tokens"], second["context_tokens"])
    match = match and tolerance <= CONTEXT_TOLERANCE and first["thread_identity"] != second["thread_identity"]
    a_input, b_input = first["usage"]["input"], second["usage"]["input"]
    delta = b_input - a_input if a_input is not None and b_input is not None else None
    return {"arm": second["arm"], "context_difference_fraction": tolerance,
            "status": "matched" if match else "invalid", "input_a": a_input,
            "input_b": b_input, "input_delta": delta, "attempts_a": first["attempts"],
            "attempts_b": second["attempts"], "attempt_delta": second["attempts"] - first["attempts"]}


def _retain_delta(row: dict[str, object], trials: list[TrialReport], deltas: dict[str, list[int]]) -> None:
    delta = row.get("input_delta")
    if row["status"] != "matched" or not isinstance(delta, int):
        return
    if all(trial["status"] == "passed" for trial in trials):
        key = f"{row['series_id']}/{row['arm']}"
        deltas.setdefault(key, []).append(delta)


def main(argv: Sequence[str] | None = None) -> int:
    """Read an explicit finite snapshot; incomplete evidence stays inconclusive."""
    parser = argparse.ArgumentParser(description="Collect explicitly selected synthetic wait evidence")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--as-of", type=float, required=True,
                        help="UTC epoch seconds for this offline snapshot; does not assert completeness")
    parser.add_argument("--version", type=int, default=1)
    arguments = parser.parse_args(argv)
    manifest_path: Path = arguments.manifest
    output_path: Path = arguments.output
    try:
        if not manifest_path.is_absolute():
            reject("Manifest path must be absolute")
        with manifest_path.open(encoding="utf-8") as stream:
            manifest = TrialManifest.from_dict(object_value(json.load(stream)))
        adapter, collector = Telemetry(manifest), Collector(manifest)
        for record in adapter.snapshot(arguments.as_of):
            collector.ingest(record)
        for record in adapter.finish(arguments.as_of):
            collector.ingest(record)
        write_report(output_path, collector.report(arguments.as_of, version=arguments.version))
    except (OSError, ValueError) as error:
        sys.stderr.write(f"Evidence collection failed: {error}\n")
        return 2
    return 0


# eof
