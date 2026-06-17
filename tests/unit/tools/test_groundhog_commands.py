"""Unit tests for the duration-outlier wiring of the groundhog commands.

Cover Step 4: a green-but-slow full run exits 8 with the windowed list, the
fix step and the ``avg=``/``outliers=`` verdict, and writes ``a.ghog.outliers``
(Q34, Q37, Q42, Q47); a tidy run exits 0 with ``outliers=0``; a raised override
spares the slow call; a failing run keeps exit 2 and withholds the timing
verdict (outliers judged last). The classification precedence is asserted
directly, and the user-mode bar carries the same verdict in its postfix (Q37).

Also cover Step 3: a full run whose freak is in the ``[exclusion]`` section
within tolerance spares it from the outliers, exits 0 with no outlier window,
renders the exclusion block, and writes the managed section back (Q54, Q58).

The one faked element is the process boundary (a canned pytest transcript with
a ``slowest durations`` block injected through the runner's process factory),
so the real parsing, rule, floor, classification and report run together.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.unit.tools.groundhog_acceptance_support import Spawns, make_deps
from tools.groundhog import cli, commands, exclusions, floor, reporting
from tools.groundhog.durations import DurationCall, DurationSummary
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_TEST_FAILURES,
    Mode,
    RunResult,
    RunStats,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# A pre-written override that sits above the freak, so it is spared (Q43).
_OVERRIDE = 10.0
_GATE_FULL = 100.0
# Calls near the median plus one order-of-magnitude freak: the single outlier.
_FREAK_NODE = "tests/test_slow.py::test_freak"
_SLOW_CALLS = (
    ("tests/test_a.py::test_one", 0.10),
    ("tests/test_b.py::test_two", 0.12),
    ("tests/test_c.py::test_three", 0.08),
    ("tests/test_d.py::test_four", 0.10),
    ("tests/test_e.py::test_five", 0.11),
    (_FREAK_NODE, 5.00),
)
# A tidy suite: every call near the median, so nothing clears the floor.
_TIDY_CALLS = (
    ("tests/test_a.py::test_one", 0.10),
    ("tests/test_b.py::test_two", 0.12),
    ("tests/test_c.py::test_three", 0.08),
    ("tests/test_d.py::test_four", 0.10),
    ("tests/test_e.py::test_five", 0.11),
)


class _FakeBar:
    """A fake user bar satisfying the ProgressBar protocol (Q20)."""

    def __init__(self) -> None:
        """Start with empty recordings."""
        self.postfixes: list[str] = []
        self.closed = False

    def update(self, n: int) -> object:
        """Ignore one advance.

        Args:
            n: Finished tests since the previous advance.

        Returns:
            None.
        """
        del n
        return None

    def set_postfix_str(self, s: str) -> object:
        """Record one postfix update.

        Args:
            s: The counters text.

        Returns:
            None.
        """
        self.postfixes.append(s)
        return None

    def close(self) -> object:
        """Record the close.

        Returns:
            None.
        """
        self.closed = True
        return None


def _full_transcript(
    calls: tuple[tuple[str, float], ...],
    *,
    total_line: str | None = "TOTAL    100    0   100%",
    failing: bool = False,
) -> list[str]:
    """Build a full-run transcript carrying a slowest-durations block.

    Args:
        calls: The (node, call seconds) pairs, one per test.
        total_line: The coverage TOTAL line, or ``None`` to omit it.
        failing: Whether the first test fails, making the run red.

    Returns:
        The transcript lines: results, the TOTAL line, the durations block,
        then the final summary banner that closes the capture.
    """
    count = len(calls)
    lines = [f"collected {count} items"]
    for index, (node, _) in enumerate(calls):
        percent = (index + 1) * 100 // count
        status = "FAILED" if failing and index == 0 else "PASSED"
        lines.append(f"{node} {status} [{percent:>4}%]")
    if total_line is not None:
        lines.append(total_line)
    lines.append("=============== slowest durations ===============")
    lines.extend(f"{secs:.2f}s call     {node}" for node, secs in calls)
    tally = "1 failed, 5 passed" if failing else f"{count} passed, 2 warnings"
    lines.append(f"====== {tally} in 0.10s ======")
    return lines


def _result(stats: RunStats, pytest_exit: int) -> RunResult:
    """Build a non-crashed run result for the classification tests.

    Args:
        stats: The run statistics.
        pytest_exit: The pytest child exit code.

    Returns:
        The run result.
    """
    return RunResult(
        stats=stats,
        pytest_exit=pytest_exit,
        crashed=False,
        failure_block=(),
        tail=(),
    )


def _invocation(root: Path) -> cli.Invocation:
    """Build a full-run invocation for the classification tests.

    Args:
        root: The project root.

    Returns:
        The invocation.
    """
    return cli.Invocation(
        sub="full",
        files=(),
        no_cov=False,
        mode=Mode.LLM,
        root=root,
    )


def _summary(outliers: tuple[DurationCall, ...]) -> DurationSummary:
    """Build a duration verdict for the postfix test.

    Args:
        outliers: The flagged outliers carried by the verdict.

    Returns:
        The summary, with a fixed average and floor.
    """
    return DurationSummary(
        average=0.10,
        outliers=outliers,
        runners_up=(),
        floor=1.05,
        median=0.10,
    )


def _green_full(stats: RunStats) -> RunStats:
    """Mark statistics green on tests and coverage for classification.

    Args:
        stats: The statistics to complete.

    Returns:
        The same statistics with a full coverage percentage.
    """
    stats.cov_percent = _GATE_FULL
    return stats


def test_classify_judges_outliers_last(tmp_path: Path) -> None:
    """Exit 8 only on a green run; a gap or a failure keeps its code (Q34)."""
    invocation = _invocation(tmp_path)
    green = _result(_green_full(RunStats()), 0)
    assert commands.classify(invocation, green, _GATE_FULL, 1) == (
        EXIT_DURATION_OUTLIERS
    )
    assert commands.classify(invocation, green, _GATE_FULL, 0) == EXIT_OBJECTIVE_MET
    low = RunStats()
    low.cov_percent = 90.0
    assert commands.classify(invocation, _result(low, 0), _GATE_FULL, 1) == (
        EXIT_COVERAGE_GAP
    )
    failing = RunStats()
    failing.failed = 1
    assert commands.classify(invocation, _result(failing, 1), _GATE_FULL, 1) == (
        EXIT_TEST_FAILURES
    )


def test_postfix_appends_the_timing_verdict() -> None:
    """The closed-bar postfix gains avg= and outliers= once judged (Q37)."""
    stats = RunStats()
    stats.cov_percent = _GATE_FULL
    plain = commands.postfix(stats)
    assert "avg=" not in plain
    outlier = DurationCall(node=_FREAK_NODE, seconds=5.0, ratio=50.0)
    judged = commands.postfix(stats, _summary((outlier,)))
    assert "avg=0.100s" in judged
    assert "outliers=1" in judged


def test_full_green_but_slow_exits_8(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A green-but-slow full run exits 8 with the window and the fix (Q34)."""
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_DURATION_OUTLIERS
    out = capsys.readouterr().out
    assert "Duration outliers" in out
    assert _FREAK_NODE in out
    assert reporting.MSG_OUTLIERS in out
    assert "a.ghog.outliers above" in out
    assert "avg=" in out
    assert "outliers=1" in out
    assert "exit=8" in out


def test_full_run_seeds_the_floor_file(tmp_path: Path) -> None:
    """A first full run writes the auto floor and seeds the default (Q45)."""
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    # Line 1 holds the auto floor; line 2 the one-second default (Q45, Q48).
    assert (tmp_path / floor.FLOOR_FILE).is_file()
    assert floor.read_floor(tmp_path) == floor.DEFAULT_FLOOR


def test_full_tidy_run_exits_0_with_zero_outliers(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A tidy full run exits 0 and prints a single slowest-call line (Q47)."""
    spawns = Spawns(_full_transcript(_TIDY_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "Slowest call:" in out
    assert "outliers=0" in out
    assert "Duration outliers" not in out


def test_full_run_respects_a_raised_override(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An override above the freak spares it, so the run exits 0 (Q43)."""
    (tmp_path / floor.FLOOR_FILE).write_text(f"0.0\n{_OVERRIDE}\n", encoding="utf-8")
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert "outliers=0" in capsys.readouterr().out
    # The override on line 2 is preserved across the run's floor rewrite (Q40).
    assert floor.read_floor(tmp_path) == _OVERRIDE


def test_full_run_spares_an_excluded_call(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An excluded freak within tolerance is spared, so the run exits 0 (Q54, Q58)."""
    # Seed the freak into the [exclusion] section at its current call time.
    (tmp_path / floor.FLOOR_FILE).write_text(
        f"0.0\n{floor.DEFAULT_FLOOR}\n[exclusion]\n{_FREAK_NODE} = 5.00\n",
        encoding="utf-8",
    )
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "outliers=0" in out
    assert "Duration outliers" not in out
    # The exclusion block reports the accepted freak with its recorded baseline.
    assert "Excluded (accepted slow" in out
    assert _FREAK_NODE in out
    assert "recorded=5.00s" in out
    # The within-tolerance baseline is kept, so the section survives the run (Q56).
    assert exclusions.read_exclusions(tmp_path) == {_FREAK_NODE: 5.0}


def test_full_failing_run_withholds_the_timing_verdict(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failing run keeps exit 2 and withholds the outliers (judged last)."""
    spawns = Spawns(_full_transcript(_SLOW_CALLS, failing=True), 1)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_TEST_FAILURES
    out = capsys.readouterr().out
    assert "outliers=withheld" in out
    assert "Duration outliers" not in out
    assert "avg=" not in out


def _user_deps(spawns: Spawns, bars: list[_FakeBar]) -> cli.Deps:
    """Build user-mode CLI deps recording every bar the run creates.

    Args:
        spawns: The recording process factory.
        bars: Receives the fake bars created by the bar factory.

    Returns:
        The injectable seams, forcing the user bar.
    """

    def _bar_factory(total: int, description: str) -> _FakeBar:
        del total, description
        bar = _FakeBar()
        bars.append(bar)
        return bar

    return cli.Deps(
        popen_factory=spawns,
        clock=lambda: 0.0,
        bar_factory=_bar_factory,
        which=lambda _name: "pytest",
    )


def test_user_mode_bar_carries_the_timing_verdict(tmp_path: Path) -> None:
    """The closed user bar shows the avg= and outliers= verdict (Q20, Q37)."""
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    bars: list[_FakeBar] = []
    code = cli.main(
        ["full", "--root", str(tmp_path), "--user"],
        _user_deps(spawns, bars),
    )
    assert code == EXIT_DURATION_OUTLIERS
    assert bars
    assert bars[0].closed is True
    assert "avg=" in bars[0].postfixes[-1]
    assert "outliers=1" in bars[0].postfixes[-1]


def test_user_mode_without_tests_closes_no_bar(tmp_path: Path) -> None:
    """A user run that collects nothing never opens a bar (Q20)."""
    # PYTEST_NO_TESTS on an uncovered affected run is a green, bar-less run.
    spawns = Spawns(["", "no tests ran in 0.10s"], 5)
    bars: list[_FakeBar] = []
    code = cli.main(
        ["affected", "--no-cov", "--root", str(tmp_path), "--user"],
        _user_deps(spawns, bars),
    )
    assert code == EXIT_OBJECTIVE_MET
    assert bars == []


# eof
