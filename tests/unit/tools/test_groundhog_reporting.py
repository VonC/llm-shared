"""Unit tests for the groundhog report contract (Q04, Q16).

Cover the key=value progress and closing lines, the coverage placeholder
rules, the cadence governor (percent step and silence floor), the crash
block (Q06) and the nag line (Q09).

Fix: the run-state table tests — the next-step messages of every branch, the
exit-8 outlier next step and the focus comparison lines (Q07) — move to
``test_groundhog_reporting_nextstep.py`` alongside the production split of
``reporting.py`` into ``reporting_nextstep.py``. What stays here is the
progress, closing line, crash block and nag line text.

Fix: cover the duration-outlier additions (Q37, Q47) — the ``avg=``/
``outliers=`` suffix of the final progress line and the bar, and the
``outliers=`` value of the closing line through ``ClosingMetrics``.

Fix: cover the per-test exclusion additions (Q58, Q65) — the slower-drift
count behind ``excluded_count`` and the ``excluded=`` value of the closing
line through ``ClosingMetrics``.
"""

from __future__ import annotations

from tools.groundhog import reporting
from tools.groundhog.durations import (
    STATUS_OK,
    STATUS_SLOWER,
    DurationCall,
    DurationExclusion,
    DurationSummary,
)
from tools.groundhog.models import (
    EXIT_OBJECTIVE_MET,
    EXIT_TEST_FAILURES,
    RunStats,
)

_PARTIAL_COVERAGE = 97.4
# A duration verdict with one flagged outlier, for the suffix and exit-8 cases.
_AVERAGE = 0.012
_FLOOR = 1.65
_OUTLIER = DurationCall(node="tests/test_slow.py::test_freak", seconds=5.0, ratio=30.0)
# Two excluded calls for the excluded= count and field: one within tolerance
# (ok, never counted) and one slower-drifted (counted, drives the fix, Q65).
_OK_EXCLUSION = DurationExclusion(
    node="tests/test_kept.py::test_ok",
    recorded=11.41,
    current=11.33,
    status=STATUS_OK,
)
_SLOWER_EXCLUSION = DurationExclusion(
    node="tests/test_kept.py::test_drift",
    recorded=6.80,
    current=9.42,
    status=STATUS_SLOWER,
)


def _summary(
    *,
    outliers: tuple[DurationCall, ...],
    exclusions: tuple[DurationExclusion, ...] = (),
) -> DurationSummary:
    """Build a duration verdict for the report-line tests.

    Args:
        outliers: The flagged outliers carried by the verdict.
        exclusions: The accepted-slow records carried by the verdict.

    Returns:
        The summary, with a fixed average, floor and median.
    """
    return DurationSummary(
        average=_AVERAGE,
        outliers=outliers,
        runners_up=(),
        floor=_FLOOR,
        median=0.1,
        exclusions=exclusions,
    )


class _FakeClock:
    """A controllable monotonic clock for the cadence governor."""

    def __init__(self) -> None:
        """Start the clock at zero."""
        self.now = 0.0

    def __call__(self) -> float:
        """Return the current fake time.

        Returns:
            The fake monotonic time.
        """
        return self.now


def _stats(**values: int) -> RunStats:
    """Build run statistics with keyword overrides.

    Args:
        values: RunStats integer fields to override.

    Returns:
        The statistics object.
    """
    stats = RunStats()
    for name, value in values.items():
        setattr(stats, name, value)
    return stats


def test_format_percent_drops_the_trailing_zero() -> None:
    """100.0 renders as 100 and 97.4 stays 97.4."""
    assert reporting.format_percent(100.0) == "100"
    assert reporting.format_percent(_PARTIAL_COVERAGE) == "97.4"


def test_progress_line_grammar() -> None:
    """The progress line carries the key=value grammar (Q16)."""
    stats = _stats(total=250, done=125, failed=2, warnings=1)
    line = reporting.progress_line("full", stats)
    assert line == "ghog full: 50% (125/250) fail=2 warn=1 xfail=0"


def test_progress_line_with_unknown_total() -> None:
    """Before the collected line, the percent stays at zero."""
    line = reporting.progress_line("full", _stats(done=0))
    assert line.startswith("ghog full: 0% (0/0)")


def test_progress_line_appends_the_summary_on_the_final_line() -> None:
    """The final full-run line carries the avg= and outliers= verdict (Q37)."""
    stats = _stats(total=250, done=250)
    plain = reporting.progress_line("full", stats)
    assert "avg=" not in plain
    judged = reporting.progress_line("full", stats, _summary(outliers=(_OUTLIER,)))
    assert judged == "ghog full: 100% (250/250) fail=0 warn=0 xfail=0 avg=0.012s outliers=1"


def test_progress_suffix_is_the_avg_and_count() -> None:
    """The shared suffix builds the avg= and outliers= keys (Q37)."""
    suffix = reporting.progress_suffix(_summary(outliers=(_OUTLIER,)))
    assert suffix == "avg=0.012s outliers=1"


def test_outliers_text_rules() -> None:
    """outliers= reads skipped, withheld or the count (Q37)."""
    # An unmeasured run (any subcommand but full) skips the verdict.
    assert (
        reporting.outliers_text(_stats(), None, measured=False)
        == reporting.OUTLIERS_SKIPPED
    )
    # A failing full run withholds the verdict, judged last.
    assert (
        reporting.outliers_text(_stats(failed=1), None, measured=True)
        == reporting.OUTLIERS_WITHHELD
    )
    # A full run that captured no durations skips the verdict.
    assert (
        reporting.outliers_text(_stats(), None, measured=True)
        == reporting.OUTLIERS_SKIPPED
    )
    # A judged full run reports the flagged count.
    counted = reporting.outliers_text(
        _stats(),
        _summary(outliers=(_OUTLIER,)),
        measured=True,
    )
    assert counted == "1"


def test_excluded_count_counts_only_slower() -> None:
    """The count is the slower-drifted exclusions only, ``ok`` left out (Q65)."""
    summary = _summary(outliers=(), exclusions=(_OK_EXCLUSION, _SLOWER_EXCLUSION))
    assert reporting.excluded_count(summary) == 1
    # No exclusions at all is a clean zero, parallel to outliers=0.
    assert reporting.excluded_count(_summary(outliers=())) == 0


def test_excluded_text_rules() -> None:
    """excluded= reads skipped, withheld or the slower-drift count (Q58, Q65)."""
    # An unmeasured run (any subcommand but full) skips the verdict.
    assert (
        reporting.excluded_text(_stats(), None, measured=False)
        == reporting.OUTLIERS_SKIPPED
    )
    # A failing full run withholds the verdict, judged last.
    assert (
        reporting.excluded_text(_stats(failed=1), None, measured=True)
        == reporting.OUTLIERS_WITHHELD
    )
    # A full run that captured no durations skips the verdict.
    assert (
        reporting.excluded_text(_stats(), None, measured=True)
        == reporting.OUTLIERS_SKIPPED
    )
    # A judged full run reports the slower-drifted exclusion count alone.
    summary = _summary(outliers=(), exclusions=(_OK_EXCLUSION, _SLOWER_EXCLUSION))
    assert reporting.excluded_text(_stats(), summary, measured=True) == "1"


def test_cov_text_rules() -> None:
    """cov= reads skipped, withheld, unread or the percentage (Q16)."""
    assert reporting.cov_text(_stats(), measured=False) == reporting.COV_SKIPPED
    assert (
        reporting.cov_text(_stats(failed=1), measured=True) == reporting.COV_WITHHELD
    )
    assert reporting.cov_text(_stats(), measured=True) == reporting.COV_UNREAD
    covered = _stats()
    covered.cov_percent = 100.0
    assert reporting.cov_text(covered, measured=True) == "100"


def test_closing_line_grammar() -> None:
    """The closing line merges the alias echo with the keys (Q16, Q37, Q58)."""
    line = reporting.closing_line(
        "pdfss",
        "full",
        _stats(failed=2, warnings=1),
        EXIT_TEST_FAILURES,
        reporting.ClosingMetrics(
            reporting.COV_WITHHELD,
            reporting.OUTLIERS_WITHHELD,
            reporting.OUTLIERS_WITHHELD,
        ),
    )
    assert line == (
        "pdfss: ghog full done fail=2 warn=1 xfail=0 "
        "cov=withheld outliers=withheld excluded=withheld exit=2"
    )


def test_closing_metrics_default_the_timing_keys_to_skipped() -> None:
    """A run that times no calls leaves outliers= and excluded= skipped (Q37, Q58)."""
    line = reporting.closing_line(
        "pdfss",
        "check",
        _stats(),
        EXIT_OBJECTIVE_MET,
        reporting.ClosingMetrics(reporting.COV_SKIPPED),
    )
    assert "cov=skipped outliers=skipped excluded=skipped exit=0" in line


def test_nag_line_only_with_material() -> None:
    """The nag line appears only when warnings or xfails remain (Q09)."""
    assert reporting.nag_line(_stats()) is None
    assert reporting.nag_line(_stats(warnings=3, xfailed=1)) == (
        "nag: warn=3 xfail=1 worth a look"
    )


def test_crash_block_carries_tests_tail_and_instruction() -> None:
    """The crash block lists the last tests and the instruction (Q06)."""
    stats = _stats()
    stats.last_started = ["tests/test_a.py::test_one"]
    block = reporting.crash_block(stats, ("Traceback line",))
    assert block[0] == "ghog: the test suite crashed mid-run."
    assert "- tests/test_a.py::test_one" in block
    assert "  Traceback line" in block
    assert block[-1].startswith("Fix the test suite now:")


def test_governor_emits_per_percent_step() -> None:
    """One line per crossed 10% bucket, none in between (Q04)."""
    clock = _FakeClock()
    governor = reporting.ProgressGovernor(clock)
    stats = _stats(total=20)
    assert governor.should_emit(stats) is True
    stats.done = 1
    assert governor.should_emit(stats) is False
    stats.done = 2
    assert governor.should_emit(stats) is True


def test_governor_emits_on_the_silence_floor() -> None:
    """A long quiet stretch forces a line out (Q04)."""
    clock = _FakeClock()
    governor = reporting.ProgressGovernor(clock)
    stats = _stats(total=1000)
    assert governor.should_emit(stats) is True
    stats.done = 1
    clock.now = reporting.SILENCE_FLOOR_SECONDS
    assert governor.should_emit(stats) is True


def test_governor_stays_silent_before_collection() -> None:
    """Without a collected total there is nothing to report (Q04)."""
    governor = reporting.ProgressGovernor(_FakeClock())
    assert governor.should_emit(_stats()) is False


def test_step_ended_line_formats_duration_in_human_units() -> None:
    """The day-walk end header breaks the step duration into h/m/s units."""
    when = "2026-06-26T12:44:33+02:00"
    head = f"proj: == ghog full == ended | {when} | duration="
    assert reporting.step_ended_line("proj", "full", when, 45.3) == f"{head}45.3s"
    assert reporting.step_ended_line("proj", "full", when, 291.9) == f"{head}4m 51.9s"
    assert (
        reporting.step_ended_line("proj", "full", when, 3661.4)
        == f"{head}1h 01m 01.4s"
    )


# eof
