"""Acceptance tests for groundhog, the per-subcommand scenarios.

Each scenario drives ``cli.main`` end to end; the one faked element is
the process boundary (a canned pytest transcript and exit code injected
through the runner's process factory), so the real parsing,
classification, reporting and baseline behavior is asserted. A final
test runs the script through its ``__main__`` guard, like the other
tools.

Fix: split for the repo line budget — the shared fakes live in
``groundhog_acceptance_support.py`` and the day-walk scenarios in
``test_groundhog_acceptance_day.py``.
"""

from __future__ import annotations

import io
import runpy
import sys
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    CHECK_FAIL_CODE,
    FakeProcess,
    Spawns,
    SteppingClock,
    assert_closing_grammar,
    failing_transcript,
    make_deps,
    passing_transcript,
)
from tools.groundhog import baseline, cli, commands, reporting_nextstep
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
)

if TYPE_CHECKING:
    from pathlib import Path

_CADENCE_TESTS = 20
_CADENCE_LINES = 11
_FLOOR_LINES = 6


def test_at1_green_full_run_reaches_the_objective(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT1: a green full run exits 0 with cov=100 and the nag (Q09)."""
    transcript = passing_transcript(4, "TOTAL    100    0   100%")
    spawns = Spawns(transcript, 0)
    (tmp_path / ".testmondata").write_text("stale", encoding="utf-8")
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert not (tmp_path / ".testmondata").exists()
    assert "--testmon" in spawns.commands[0]
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_FULL_OK in out
    assert "cov=100" in out
    assert "nag: warn=2 xfail=0 worth a look" in out
    assert "exit=0" in out
    assert_closing_grammar(out)


def test_at2_full_failures_write_the_baseline(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT2: failures exit 2, full context, baseline and focus hint."""
    spawns = Spawns(failing_transcript(), 1)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_TEST_FAILURES
    assert baseline.read_baseline(tmp_path) == (
        "tests/test_a.py::test_two",
        "tests/test_b.py::test_three",
    )
    out = capsys.readouterr().out
    assert "E   AssertionError: 1 == 2" in out
    assert "Next: ghog single tests/test_a.py tests/test_b.py" in out
    assert "cov=withheld" in out
    assert_closing_grammar(out)


def test_at3_focus_run_prints_the_two_lists(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT3: a focus run splits still-failing and suspects (Q07)."""
    baseline.write_baseline(
        tmp_path,
        ["tests/test_a.py::test_two", "tests/test_b.py::test_three"],
    )
    transcript = [
        "collected 2 items",
        "tests/test_a.py::test_two FAILED [ 50%]",
        "tests/test_b.py::test_three PASSED [100%]",
        "=================== FAILURES ===================",
        "E   AssertionError",
    ]
    spawns = Spawns(transcript, 1)
    argv = [
        "single",
        "tests/test_a.py",
        "tests/test_b.py",
        "--root",
        str(tmp_path),
        "--llm",
    ]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_TEST_FAILURES
    out = capsys.readouterr().out
    assert "Still failing in focus (fix these first):" in out
    assert "- tests/test_a.py::test_two" in out
    assert "- tests/test_b.py::test_three" in out
    assert reporting_nextstep.MSG_SINGLE_RESTART in out
    assert_closing_grammar(out)


def test_at4_green_focus_run_restarts_the_chain(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT4: a green focus run restarts the walk with ghog day (Q30)."""
    baseline.write_baseline(tmp_path, ["tests/test_a.py::test_two"])
    transcript = [
        "collected 1 items",
        "tests/test_a.py::test_two PASSED [100%]",
    ]
    spawns = Spawns(transcript, 0)
    argv = ["single", "tests/test_a.py", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert reporting_nextstep.MSG_SINGLE_GREEN in capsys.readouterr().out


def test_at5_coverage_gap_and_gate_reached(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT5: a gap exits 3 toward covg; affected at the gate exits 0."""
    transcript = passing_transcript(2, None)
    transcript.extend(
        [
            "Name                  Stmts   Miss  Cover   Missing",
            "src/pkg/mod.py          120      7    94%   48, 86-88, 100",
            "TOTAL    100    3    97%",
        ],
    )
    gap = Spawns(transcript, 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(gap))
    assert code == EXIT_COVERAGE_GAP
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_GAP_LINES_HEADER in out
    assert "src/pkg/mod.py" in out
    assert reporting_nextstep.MSG_COVERAGE_GAP in out
    assert_closing_grammar(out)
    reached = Spawns(passing_transcript(2, "TOTAL    100    0   100%"), 0)
    code = cli.main(
        ["affected", "--root", str(tmp_path), "--llm"],
        make_deps(reached),
    )
    assert code == EXIT_OBJECTIVE_MET
    assert reporting_nextstep.MSG_AFFECTED_COV_OK in capsys.readouterr().out


def test_at6_crash_prints_the_crash_block(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT6: a mid-run crash exits 4 with the immediate-fix block (Q06)."""
    transcript = [
        "collected 10 items",
        "tests/test_a.py::test_one PASSED [ 10%]",
        "tests/test_a.py::test_two PASSED [ 20%]",
        "INTERNALERROR> Traceback (most recent call last):",
        'INTERNALERROR>   File "conftest.py", line 9',
    ]
    spawns = Spawns(transcript, 3)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_SUITE_CRASH
    assert baseline.read_baseline(tmp_path) is None
    out = capsys.readouterr().out
    assert "ghog: the test suite crashed mid-run." in out
    assert "- tests/test_a.py::test_two" in out
    assert "Fix the test suite now:" in out
    assert "exit=4" in out
    assert_closing_grammar(out)


def test_at7_unreadable_total_line_is_loud(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT7: a covered run without a TOTAL line exits 5 (Q19)."""
    spawns = Spawns(passing_transcript(2, None), 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_SETUP_ERROR
    out = capsys.readouterr().out
    assert "TOTAL line not found" in out
    assert "cov=unread" in out
    assert_closing_grammar(out)


def test_at8_check_missing_and_failing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT8: a missing check.bat skips (Q10); a failing one passes through."""
    spawns = Spawns(["never used"], 0)
    code = cli.main(["check", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_CHECK_MISSING in out
    assert spawns.commands == []
    check_bat = tmp_path / "check.bat"
    check_bat.write_text("@echo off\nexit /b 7\n", encoding="utf-8")
    failing = Spawns(["compile error detail"], CHECK_FAIL_CODE)
    code = cli.main(["check", "--root", str(tmp_path), "--llm"], make_deps(failing))
    assert code == CHECK_FAIL_CODE
    out = capsys.readouterr().out
    assert "compile error detail" in out
    assert reporting_nextstep.MSG_CHECK_FAIL in out
    assert failing.commands == [["cmd.exe", "/d", "/c", str(check_bat)]]
    assert_closing_grammar(out)


def test_at8_check_green_points_at_affected(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT8: a green check.bat points at the uncovered affected run."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    spawns = Spawns(["all compiled"], 0)
    code = cli.main(["check", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert reporting_nextstep.MSG_CHECK_OK in capsys.readouterr().out


def test_at14_lying_check_bat_is_treated_as_failed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT14: ERROR lines with exit 0 fail the check with a notice (Q26)."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    transcript = [
        " ERROR : [check.bat] Ruff check failed for project 'demo' with status '1'",
        " OK    : [check.bat] EOF check passed for project 'demo'",
        " ERROR : [check.bat] Check failed for project 'demo' with status '1'.",
    ]
    spawns = Spawns(transcript, 0)
    code = cli.main(["check", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == 1
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_CHECK_EXIT_MISMATCH in out
    assert reporting_nextstep.MSG_CHECK_FAIL in out
    assert "exit=1" in out


def test_at17_colored_error_lines_still_trip_the_guard(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT17: ANSI-colored ERROR lines are detected and re-emitted plain."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    transcript = [
        "\x1b[92m OK    \x1b[0m: [check.bat] Ty check passed",
        "\x1b[91m ERROR \x1b[0m: [check.bat] Check failed with status '1'.",
    ]
    spawns = Spawns(transcript, 0)
    code = cli.main(["check", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == 1
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_CHECK_EXIT_MISMATCH in out
    assert " ERROR : [check.bat] Check failed with status '1'." in out
    assert "\x1b" not in out


def test_at17_unencodable_characters_are_replaced(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AT17: a line outside the stream's code page logs with placeholders."""
    buffer = io.BytesIO()
    stream = io.TextIOWrapper(buffer, encoding="ascii")
    monkeypatch.setattr(sys, "stdout", stream)
    cli._configure_logging()
    commands.emit_line("info: └── protocol member")
    stream.flush()
    content = buffer.getvalue()
    assert b"protocol member" in content
    assert b"?" in content


def test_at9_cadence_one_line_per_percent_step(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT9: LLM mode emits one progress line per 10% step (Q04)."""
    transcript = passing_transcript(_CADENCE_TESTS, "TOTAL   10   0   100%")
    spawns = Spawns(transcript, 0)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    progress = [line for line in out.splitlines() if line.startswith("ghog full:")]
    assert len(progress) == _CADENCE_LINES


def test_at9_silence_floor_keeps_the_run_alive(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT9: the 60-second floor emits between percent steps (Q04)."""
    transcript = [
        "collected 1000 items",
        "tests/test_ok.py::test_0 PASSED [  1%]",
        "tests/test_ok.py::test_1 PASSED [  1%]",
        "tests/test_ok.py::test_2 PASSED [  1%]",
        "tests/test_ok.py::test_3 PASSED [  1%]",
        "tests/test_ok.py::test_4 PASSED [  1%]",
    ]
    spawns = Spawns(transcript, 1)
    deps = cli.Deps(
        popen_factory=spawns,
        clock=SteppingClock(),
        which=lambda _name: "pytest",
    )
    cli.main(["affected", "--no-cov", "--root", str(tmp_path), "--llm"], deps)
    out = capsys.readouterr().out
    progress = [
        line
        for line in out.splitlines()
        if line.startswith("ghog affected --no-cov:")
    ]
    assert len(progress) == _FLOOR_LINES


def test_at15_nothing_affected_is_green_and_says_so(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT15: a zero-test affected run stays green with the explicit note."""
    transcript = ["", "no tests ran in 0.12s"]
    spawns = Spawns(transcript, 5)
    argv = ["affected", "--no-cov", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_NO_TESTS_RUN in out
    assert reporting_nextstep.MSG_AFFECTED_NOCOV_OK in out


def test_script_runs_through_its_main_guard(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The cli script runs as __main__ and exits with the contract code."""
    transcript = [
        "collected 1 items",
        "tests/test_a.py::test_one PASSED [100%]",
    ]

    def _fake_popen(*args: object, **kwargs: object) -> object:
        del args, kwargs
        return FakeProcess(transcript, 0)

    def _fake_which(_name: str) -> str:
        return "pytest"

    monkeypatch.setattr("subprocess.Popen", _fake_popen)
    monkeypatch.setattr("shutil.which", _fake_which)
    script_path = cli.__file__
    argv = [
        script_path,
        "single",
        "tests/test_a.py",
        "--root",
        str(tmp_path),
        "--llm",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(script_path, run_name="__main__")
    assert excinfo.value.code == EXIT_OBJECTIVE_MET


# eof
