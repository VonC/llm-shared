"""Unit tests for the duration-outlier wiring of the groundhog commands.

Cover Step 4: a green-but-slow full run exits 8 with the windowed list, the
fix step and the ``avg=``/``outliers=`` verdict, and writes ``a.ghog.outliers``
in the artifact home (Q34, Q37, Q42, Q47); a tidy run exits 0 with
``outliers=0``; a raised override spares the slow call; a failing run keeps
exit 2 and withholds the timing
verdict (outliers judged last). The user-mode bar carries the same verdict in
its postfix (Q37).

Also cover Step 3: a full run whose freak is in the ``[exclusion]`` section
within tolerance spares it from the outliers, exits 0 with no outlier window,
renders the exclusion block, and writes the managed section back (Q54, Q58).

The one faked element is the process boundary (a canned pytest transcript with
a ``slowest durations`` block injected through the runner's process factory),
so the real parsing, rule, floor, classification and report run together.

Fix: the deps also fake the pytest-suite probe as a pytest project, so the
scenarios run from a bare temporary root.

Fix (v0.13.0 full_suite_levels, Step 1): the direct outliers-last
classification case moved to ``test_groundhog_verdicts`` and the postfix
verdict case to ``test_groundhog_progress``, beside the helpers that moved
out of ``commands.py``; the end-to-end duration scenarios stay here. The file
now also drives every remaining executor path of ``commands.py`` through the
CLI, so it covers that module on its own: check.bat missing or exiting 0 over
colored ERROR lines, the exit-9 and missing-pytest stops, a sequential full
run (testmon reset, baseline, nag), its coverage-gap rows and missing TOTAL
reason, a crash, a covered affected run, a focus run with and without a
baseline, and init success and failure.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tests.unit.tools.groundhog_acceptance_support import (
    Spawns,
    failing_transcript,
    make_deps,
    passing_transcript,
)
from tools.groundhog import (
    baseline,
    cli,
    commands,
    exclusions,
    floor,
    init_files,
    reporting_nextstep,
)
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_NOT_PYTEST_PROJECT,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    GroundhogError,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# A pre-written override that sits above the freak, so it is spared (Q43).
_OVERRIDE = 10.0
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


def _assert_blank_before(out: str, marker: str) -> None:
    """Assert the rendered report separates a named line from prior content."""
    lines = out.splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith(marker))
    assert lines[index - 1] == ""


def _assert_green_but_slow_report(out: str) -> None:
    """Assert the green-but-slow full run emits the actionable report."""
    assert "Duration outliers" in out
    assert "Duration warnings requiring action:" in out
    assert _FREAK_NODE in out
    assert "shorten below the floor with margin" in out
    assert reporting_nextstep.MSG_OUTLIERS in out
    # The exit-8 hint now names the add-exclusion command, not raising line 2.
    assert "ghog exclude" in out
    assert "avg=" in out
    assert "outliers=1" in out
    assert "exit=8" in out
    _assert_blank_before(out, "Duration outliers")


def test_section_keeps_an_existing_blank_separator() -> None:
    """A pre-separated report block is not given a second blank line."""
    assert commands._section(["", "Next: ghog full"]) == ["", "Next: ghog full"]


def test_full_green_but_slow_exits_8(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A green-but-slow full run exits 8 with the window and the fix (Q34)."""
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["timings", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_DURATION_OUTLIERS
    out = capsys.readouterr().out
    _assert_green_but_slow_report(out)


def test_full_run_seeds_the_floor_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A first full run writes the auto floor and seeds the default (Q45)."""
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    cli.main(["timings", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    # Line 1 holds the auto floor; line 2 the one-second default (Q45, Q48).
    assert floor.floor_path(tmp_path).is_file()
    assert not (tmp_path / floor.FLOOR_FILE).exists()
    assert floor.read_floor(tmp_path) == floor.DEFAULT_FLOOR
    # The exit-8 hint names the floor file where it lives, the artifact home.
    assert f"line 2 of {floor.floor_path(tmp_path)} (" in capsys.readouterr().out


def test_full_tidy_run_exits_0_with_zero_outliers(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A tidy full run exits 0 and prints a single slowest-call line (Q47)."""
    spawns = Spawns(_full_transcript(_TIDY_CALLS), 0)
    code = cli.main(["timings", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "Slowest call:" in out
    assert "outliers=0" in out
    assert "Duration outliers" not in out
    _assert_blank_before(out, "Slowest call:")
    _assert_blank_before(out, reporting_nextstep.MSG_TIMINGS_OK)


def test_full_run_respects_a_raised_override(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An override above the freak spares it, so the run exits 0 (Q43)."""
    floor.floor_path(tmp_path).write_text(f"0.0\n{_OVERRIDE}\n", encoding="utf-8")
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["timings", "--root", str(tmp_path), "--llm"], make_deps(spawns))
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
    floor.floor_path(tmp_path).write_text(
        f"0.0\n{floor.DEFAULT_FLOOR}\n[exclusion]\n{_FREAK_NODE} = 5.00\n",
        encoding="utf-8",
    )
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    code = cli.main(["timings", "--root", str(tmp_path), "--llm"], make_deps(spawns))
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
    code = cli.main(["timings", "--root", str(tmp_path), "--llm"], make_deps(spawns))
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
        pytest_project=lambda _root: True,
    )


def test_user_mode_bar_carries_the_timing_verdict(tmp_path: Path) -> None:
    """The closed user bar shows the avg= and outliers= verdict (Q20, Q37)."""
    spawns = Spawns(_full_transcript(_SLOW_CALLS), 0)
    bars: list[_FakeBar] = []
    code = cli.main(
        ["timings", "--root", str(tmp_path), "--user"],
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


def _run(argv: list[str], spawns: Spawns, root: Path) -> int:
    """Run one LLM-mode subcommand on a root through the CLI.

    Args:
        argv: The subcommand and its own arguments.
        spawns: The recording process factory.
        root: The project root.

    Returns:
        The contract exit code.
    """
    return cli.main([*argv, "--root", str(root), "--llm"], make_deps(spawns))


def test_check_without_check_bat_is_skipped(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A root without check.bat spawns nothing and moves on (Q10)."""
    spawns = Spawns([], 0)
    assert _run(["check"], spawns, tmp_path) == EXIT_OBJECTIVE_MET
    assert spawns.commands == []
    assert reporting_nextstep.MSG_CHECK_MISSING in capsys.readouterr().out


def test_check_error_lines_fail_a_zero_exit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Colored ERROR lines turn a 0 exit into a failed check (Q26, Q29)."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    lines = ["\x1b[32m OK    : [check.bat] fine\x1b[0m", "\x1b[31m ERROR : [check.bat] boom\x1b[0m"]
    assert _run(["check"], Spawns(lines, 0), tmp_path) == 1
    out = capsys.readouterr().out
    assert " ERROR : [check.bat] boom" in out
    assert "\x1b[" not in out
    assert reporting_nextstep.MSG_CHECK_EXIT_MISMATCH in out


def test_pytest_steps_stop_before_pytest(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No pytest suite exits 9; a missing pytest executable exits 5 (Q21)."""

    def _no_suite(_root: Path) -> bool:
        return False

    def _no_pytest(_name: str) -> str | None:
        return None

    deps = make_deps(Spawns([], 0))
    argv = ["single", "tests/test_a.py", "--root", str(tmp_path), "--llm"]
    assert cli.main(argv, replace(deps, pytest_project=_no_suite)) == EXIT_NOT_PYTEST_PROJECT
    assert cli.main(argv, replace(deps, which=_no_pytest)) == EXIT_SETUP_ERROR
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_NOT_PYTEST_PROJECT in out
    assert reporting_nextstep.MSG_NO_PYTEST in out
    assert "ghog single done" in out


def test_sequential_full_run_resets_testmon_and_records_the_baseline(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A green sequential full run resets testmon, records failures and nags (Q05, Q09)."""
    (tmp_path / ".testmondata").write_text("stale", encoding="utf-8")
    spawns = Spawns(passing_transcript(2, "TOTAL    100    0   100%"), 0)
    assert _run(["full"], spawns, tmp_path) == EXIT_OBJECTIVE_MET
    assert not (tmp_path / ".testmondata").exists()
    assert baseline.read_baseline(tmp_path) == ()
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_FULL_OK in out
    assert "nag: warn=2 xfail=0 worth a look" in out


def test_full_run_gap_and_missing_total_are_reported(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A gap lists the uncovered rows (Q24); a missing TOTAL names the reason (Q19)."""
    gap = passing_transcript(1, None)
    gap.extend(
        [
            "Name                  Stmts   Miss  Cover   Missing",
            "src/pkg/mod.py          120      7    94%   48, 86-88",
            "TOTAL    100    3    97%",
        ],
    )
    assert _run(["full"], Spawns(gap, 0), tmp_path) == EXIT_COVERAGE_GAP
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_GAP_LINES_HEADER in out
    assert "src/pkg/mod.py" in out
    assert _run(["full"], Spawns(passing_transcript(1, None), 0), tmp_path) == EXIT_SETUP_ERROR
    assert "coverage TOTAL line not found" in capsys.readouterr().out


def test_crashed_run_prints_the_crash_block(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A mid-run crash exits 4 with the crash block and no baseline (Q06)."""
    lines = [
        "collected 2 items",
        "tests/test_a.py::test_one PASSED [ 50%]",
        "INTERNALERROR> Traceback (most recent call last):",
    ]
    assert _run(["full"], Spawns(lines, 3), tmp_path) == EXIT_SUITE_CRASH
    assert baseline.read_baseline(tmp_path) is None
    assert "ghog: the test suite crashed mid-run." in capsys.readouterr().out


def test_covered_affected_run_reaches_the_gate(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A covered affected run at the gate needs no full run (Q14)."""
    spawns = Spawns(passing_transcript(1, "TOTAL    100    0   100%"), 0)
    assert _run(["affected"], spawns, tmp_path) == EXIT_OBJECTIVE_MET
    assert reporting_nextstep.MSG_AFFECTED_COV_OK in capsys.readouterr().out


def test_single_run_compares_with_the_full_run_baseline(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A focus run skips the comparison without a baseline, then uses it (Q07, Q18)."""
    argv = ["single", "tests/test_a.py"]
    assert _run(argv, Spawns(failing_transcript(), 1), tmp_path) == EXIT_TEST_FAILURES
    assert reporting_nextstep.MSG_NO_BASELINE in capsys.readouterr().out
    baseline.write_baseline(tmp_path, ["tests/test_a.py::test_two"])
    assert _run(argv, Spawns(failing_transcript(), 1), tmp_path) == EXIT_TEST_FAILURES
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_NO_BASELINE not in out
    assert reporting_nextstep.MSG_SINGLE_RESTART in out


def test_init_reports_success_and_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Init registers the pointers, or exits 5 naming a missing instruction (Q23)."""
    deps = replace(make_deps(Spawns([], 0)), home=lambda: tmp_path / "home")
    argv = ["init", "--root", str(tmp_path), "--llm"]
    assert cli.main(argv, deps) == EXIT_OBJECTIVE_MET
    assert "ghog init done" in capsys.readouterr().out

    def _missing(root: Path, home: Path | None = None) -> list[str]:
        del root, home
        message = "instruction file missing"
        raise GroundhogError(message)

    monkeypatch.setattr(init_files, "run_init", _missing)
    assert cli.main(argv, deps) == EXIT_SETUP_ERROR
    assert "ghog: instruction file missing" in capsys.readouterr().out


# eof
