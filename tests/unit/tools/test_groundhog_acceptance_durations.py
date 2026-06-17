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
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from tests.unit.tools.groundhog_acceptance_support import (
    Spawns,
    assert_closing_grammar,
    make_deps,
)
from tools.groundhog import cli, floor, reporting
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
    reporting.MSG_OUTLIERS,
    "outliers=1 excluded=0 exit=8",
)


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
    assert reporting.MSG_FULL_OK in out
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


# eof
