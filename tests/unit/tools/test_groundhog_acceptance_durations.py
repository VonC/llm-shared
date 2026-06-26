"""Acceptance tests for the green-but-slow ghog full run (Q34, Q47).

Split out of ``test_groundhog_acceptance.py`` for the repo line budget,
mirroring the ``test_groundhog_acceptance_day.py`` split: this file proves
the duration-outlier feature end to end. Each scenario drives ``cli.main``
through the same faked process boundary as the other acceptance files (a
canned pytest transcript and exit code through the runner's process
factory), so the real parsing of the ``slowest durations`` block, the pure
true-outlier rule, the two-line floor file, the exit-8 classification and
the windowed report all run for real.

The slow transcript carries one freak call an order of magnitude above a
tight bulk: its six call times ``[1.83, 0.05, 0.04, 0.03, 0.02, 0.01]`` give
a median of ``0.035s``, recorded as the auto floor ``k * median = 0.35s`` on
line 1, while the gate uses the one-second default floor; only the ``1.83s``
call clears one second and is far out by the modified z-score (Q46). The tidy
transcript drops the freak, so nothing reaches the one-second floor and the
run is green from the start (Q41).

Fix: step 6 adds the exclusion scenarios on the same faked boundary. The
freak's node id is seeded into the ``[exclusion]`` section through
``exclusions.py`` before the run, so the real read of the section, the rule's
spare-and-classify post-step, the section rewrite and the report block all run
end to end. A freak within two seconds of its recorded baseline is spared and
reads ``ok`` with no outlier window (Q54); one crept more than two seconds
slower keeps the green run on exit 8 with ``excluded=1`` and a restore
instruction, its baseline never raised (Q57, Q65); a faster freak has the tool
ratchet the baseline down, or remove the entry once it drops below the floor
(Q60, Q69); a recorded node absent from the run is reported ``(not run)`` and
removed as stale (Q61); and the ``ghog exclude`` command writes a new entry at
its measured time (Q62).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from tests.unit.tools.groundhog_acceptance_support import (
    Spawns,
    assert_closing_grammar,
    make_deps,
)
from tools.groundhog import cli, exclusions, floor, reporting_nextstep
from tools.groundhog.models import (
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_TEST_FAILURES,
    PYTEST_TEST_FAILURES,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    import pytest

# The freak call, an order of magnitude above the bulk (Q46).
_FREAK: Final = "tests/test_slow.py::test_freak"
# The slow run's call times: median 0.035s; the auto floor k*median = 0.35s is
# recorded on line 1, but the gate uses the one-second default, so only the
# 1.83s freak clears one second and is far out by the z-score (Q46).
_SLOW_CALLS: Final = (
    (_FREAK, 1.83),
    ("tests/test_ok.py::test_4", 0.05),
    ("tests/test_ok.py::test_3", 0.04),
    ("tests/test_ok.py::test_2", 0.03),
    ("tests/test_ok.py::test_1", 0.02),
    ("tests/test_ok.py::test_0", 0.01),
)
# A tight run with no freak: nothing reaches the one-second default floor.
_TIDY_CALLS: Final = (
    ("tests/test_ok.py::test_3", 0.04),
    ("tests/test_ok.py::test_2", 0.03),
    ("tests/test_ok.py::test_1", 0.02),
    ("tests/test_ok.py::test_0", 0.01),
)
# The coverage TOTAL line at the default gate, so the run is green on tests
# and coverage and the timing verdict is the last thing judged (Q34).
_GATE_MET: Final = "TOTAL    100    0   100%"
# A line-2 override well above the freak, so the call is spared on purpose.
_HIGH_OVERRIDE: Final = 5.0
# The window header above the flagged outliers (Q47), asserted as user text.
_WINDOW_HEADER: Final = "Duration outliers"
# The report snippets a green-but-slow run must print (Q37, Q47, Q58): the
# window header, the freak's node/time/ratio line, the marked floor, the
# average, the fix next-step and the closing counters/exit triple -- a run with
# no exclusions reads excluded=0. Folded into one tuple so the scenario asserts
# them in a loop instead of one statement each.
_SLOW_REPORT: Final = (
    _WINDOW_HEADER,
    f"{_FREAK}  1.83s  52x median",
    "-- floor 1.00s --",
    "avg=",
    reporting_nextstep.MSG_OUTLIERS,
    "outliers=1 excluded=0 exit=8",
)
# The exclusion block header rendered after the floor window (Q58), asserted as
# user text the same way as the window header above.
_EXCLUSION_HEADER: Final = "Excluded (accepted slow"
# An excluded freak within tolerance: recorded at the 1.83s the slow transcript
# times it at, so the call reads ``ok`` and the baseline is left alone (Q56).
_OK_BASELINE: Final = 1.83
# A slower-drifted freak: recorded at 6.80s, crept to 9.42s -- 2.62s over its
# baseline, so the run restores it and stays on exit 8 (Q57, Q63).
_DRIFT_BASELINE: Final = 6.80
_DRIFT_CURRENT: Final = 9.42
# A faster freak still above the floor: recorded at 3.92s, now 1.30s, so the
# tool ratchets the baseline down to that time and stays green (Q60, Q69).
_FASTER_BASELINE: Final = 3.92
_FASTER_CURRENT: Final = 1.30
# A faster freak under the one-second floor: recorded at 2.54s, now 0.30s, so
# the tool removes the entry and hands the call back to the normal rule (Q60).
_REMOVED_BASELINE: Final = 2.54
_REMOVED_CURRENT: Final = 0.30
# A stale freak: recorded at 4.10s but absent from the run, so the tool reports
# it ``(not run)`` and removes the entry (Q61).
_STALE_BASELINE: Final = 4.10
# The measured time the exclude subcommand records for a new entry (Q62).
_EXCLUDE_SECONDS: Final = 11.41


def _with_freak(freak_secs: float) -> tuple[tuple[str, float], ...]:
    """Return the slow call set with the freak retimed to a drift value (Q56).

    The tight bulk of :data:`_SLOW_CALLS` is reused unchanged; only the freak's
    call time is replaced, so each exclusion scenario times the freak at the
    value that drives its baseline verdict -- slower, faster, or below the floor.

    Args:
        freak_secs: The freak's call-phase seconds for this scenario.

    Returns:
        The (node, call seconds) pairs, the freak first then the tight bulk.
    """
    return ((_FREAK, freak_secs), *_SLOW_CALLS[1:])


def _durations_block(calls: Sequence[tuple[str, float]]) -> list[str]:
    """Build a ``slowest durations`` block, one call line per timed call.

    A slow setup line is appended for the first call to prove the rule reads
    the call phase only (Q36): a setup of ``2.00s``, above the one-second
    floor, must never reach the durations map or the median.

    Args:
        calls: The (node, call seconds) pairs to render.

    Returns:
        The banner, the call lines, and the one ignored setup line.
    """
    lines = ["================= slowest durations ================="]
    lines.extend(f"{secs:.2f}s call     {node}" for node, secs in calls)
    lines.append(f"2.00s setup    {calls[0][0]}")
    return lines


def _full_transcript(calls: Sequence[tuple[str, float]]) -> list[str]:
    """Build a green ghog full transcript ending in a durations block.

    Args:
        calls: The (node, call seconds) pairs; one PASSED result per call,
            and the same calls timed in the ``slowest durations`` block.

    Returns:
        The transcript lines: the collected count, the PASSED results, the
        coverage TOTAL at the gate, the durations block, the final summary.
    """
    count = len(calls)
    lines = [f"collected {count} items"]
    for index, (node, _secs) in enumerate(calls):
        percent = (index + 1) * 100 // count
        lines.append(f"{node} PASSED [{percent:>4}%]")
    lines.append(_GATE_MET)
    lines.extend(_durations_block(calls))
    lines.append(f"====== {count} passed, 2 warnings in 0.10s ======")
    return lines


def _failing_transcript(calls: Sequence[tuple[str, float]]) -> list[str]:
    """Build a failing full transcript that still carries a durations block.

    The durations are captured, but the outlier verdict is judged last (Q34),
    so a failing run withholds it whatever the timings show.

    Args:
        calls: The (node, call seconds) pairs of the durations block.

    Returns:
        The transcript lines: one passing and one failing result, the
        FAILURES section, the durations block, the final summary.
    """
    lines = [
        "collected 2 items",
        "tests/test_a.py::test_one PASSED [ 50%]",
        "tests/test_a.py::test_two FAILED [100%]",
        "=================== FAILURES ===================",
        "E   AssertionError: 1 == 2",
    ]
    lines.extend(_durations_block(calls))
    lines.append("====== 1 failed, 1 passed in 0.20s ======")
    return lines


def test_atd1_green_but_slow_run_exits_eight(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D1: a green run with one freak call exits 8 with the window (Q34)."""
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_DURATION_OUTLIERS
    assert "--durations=0" in spawns.commands[0]
    assert floor.floor_path(tmp_path).is_file()
    out = capsys.readouterr().out
    for snippet in _SLOW_REPORT:
        assert snippet in out
    assert_closing_grammar(out)


def test_atd2_tidy_run_reaches_the_objective(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D2: a durations block with no freak exits 0 with outliers=0 (Q41)."""
    spawns = Spawns(_full_transcript(_TIDY_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "Slowest call:" in out
    assert reporting_nextstep.MSG_FULL_OK in out
    assert "outliers=0 excluded=0 exit=0" in out
    assert _WINDOW_HEADER not in out
    assert_closing_grammar(out)


def test_atd3_override_above_the_freak_exits_zero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D3: a line-2 override above the freak spares it, exit 0 (Q43)."""
    floor.write_floor(tmp_path, 0.0, _HIGH_OVERRIDE)
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    # The run rewrites line 1 to its auto floor but preserves the override.
    assert floor.read_floor(tmp_path) == _HIGH_OVERRIDE
    out = capsys.readouterr().out
    assert "outliers=0 excluded=0 exit=0" in out
    assert _WINDOW_HEADER not in out


def test_atd4_first_run_seeds_the_floor_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D4: no file - the run seeds line 1, line 2 with the default (Q45)."""
    assert not floor.floor_path(tmp_path).exists()
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_DURATION_OUTLIERS
    # Line 2 is seeded with the one-second default; line 1 with the auto floor.
    assert floor.read_floor(tmp_path) == floor.DEFAULT_FLOOR
    written = floor.floor_path(tmp_path).read_text(encoding="utf-8").splitlines()
    assert len(written) == len(("auto", "override"))
    assert float(written[0]) > 0
    assert _WINDOW_HEADER in capsys.readouterr().out


def test_atd5_failure_withholds_the_timing_verdict(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D5: a failing run with timings keeps exit 2, withholds outliers (Q34)."""
    spawns = Spawns(_failing_transcript(_SLOW_CALLS), PYTEST_TEST_FAILURES)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_TEST_FAILURES
    # Outliers are judged last, so no floor file is written on a failing run.
    assert not floor.floor_path(tmp_path).exists()
    out = capsys.readouterr().out
    assert "outliers=withheld excluded=withheld exit=2" in out
    assert _WINDOW_HEADER not in out


def test_atd6_excluded_freak_within_tolerance_exits_zero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D6: a freak in [exclusion] within 2s of its baseline reads ok (Q54)."""
    exclusions.write_exclusions(tmp_path, {_FREAK: _OK_BASELINE})
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    # The freak is spared, so no outlier window forms; the block reads it ok.
    assert _WINDOW_HEADER not in out
    assert _EXCLUSION_HEADER in out
    assert f"{_FREAK}  recorded=1.83s  current=1.83s  ok" in out
    assert "outliers=0 excluded=0 exit=0" in out
    # An ok call neither drifts nor ratchets, so its baseline is left in place.
    assert exclusions.read_exclusions(tmp_path) == {_FREAK: _OK_BASELINE}
    assert_closing_grammar(out)


def test_atd7_slower_drift_exits_eight_with_restore(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D7: a freak 2s+ over its baseline exits 8, excluded=1 (Q57, Q65)."""
    exclusions.write_exclusions(tmp_path, {_FREAK: _DRIFT_BASELINE})
    spawns = Spawns(_full_transcript(_with_freak(_DRIFT_CURRENT)), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_DURATION_OUTLIERS
    out = capsys.readouterr().out
    # The slower-drift drives exit 8 with a restore-to-baseline instruction.
    assert "recorded=6.80s  current=9.42s  restore to within 2s of 6.80s" in out
    assert "outliers=0 excluded=1 exit=8" in out
    # The baseline is never raised: the recorded 6.80s survives the drift (Q57).
    assert exclusions.read_exclusions(tmp_path) == {_FREAK: _DRIFT_BASELINE}
    assert_closing_grammar(out)


def test_atd8_faster_freak_ratchets_the_baseline_down(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D8: a freak 2s+ faster but above the floor lowers the baseline (Q60, Q69)."""
    exclusions.write_exclusions(tmp_path, {_FREAK: _FASTER_BASELINE})
    spawns = Spawns(_full_transcript(_with_freak(_FASTER_CURRENT)), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "recorded=3.92s  current=1.30s  baseline lowered to 1.30s" in out
    assert "outliers=0 excluded=0 exit=0" in out
    # The tool ratchets the recorded baseline down to the faster time.
    assert exclusions.read_exclusions(tmp_path) == {_FREAK: _FASTER_CURRENT}
    assert_closing_grammar(out)


def test_atd9_faster_freak_below_floor_is_removed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D9: a freak now under the floor has the tool drop the entry (Q60)."""
    exclusions.write_exclusions(tmp_path, {_FREAK: _REMOVED_BASELINE})
    spawns = Spawns(_full_transcript(_with_freak(_REMOVED_CURRENT)), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "recorded=2.54s  current=0.30s  removed (now under the floor)" in out
    assert "outliers=0 excluded=0 exit=0" in out
    # The entry is gone, so the call returns to the normal floor rule.
    assert exclusions.read_exclusions(tmp_path) == {}
    assert_closing_grammar(out)


def test_atd10_stale_entry_is_reported_and_removed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D10: a recorded node absent from the run is removed as stale (Q61)."""
    exclusions.write_exclusions(tmp_path, {_FREAK: _STALE_BASELINE})
    spawns = Spawns(_full_transcript(_TIDY_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "recorded=4.10s  current=(not run)  removed (stale)" in out
    assert "outliers=0 excluded=0 exit=0" in out
    # The dead entry is dropped, so a typo'd node id cannot accumulate.
    assert exclusions.read_exclusions(tmp_path) == {}
    assert_closing_grammar(out)


def test_atd11_exclude_subcommand_writes_a_new_entry(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT-D11: the exclude subcommand accepts one call at its measured time (Q62)."""
    spawns = Spawns([], 0)
    argv = ["exclude", _FREAK, str(_EXCLUDE_SECONDS), "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    # The entry lands in the [exclusion] section at its measured baseline.
    assert exclusions.read_exclusions(tmp_path) == {_FREAK: _EXCLUDE_SECONDS}
    assert _FREAK in out
    assert "ghog exclude done" in out
    assert "exit=0" in out


# eof
