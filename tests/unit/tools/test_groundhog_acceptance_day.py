"""Acceptance tests for the ghog day walk scenarios.

Split out of ``test_groundhog_acceptance.py`` for the repo line budget:
this file covers the day-walk behavior — the ordered chain and its stops
(AT11, Q22), the lying-check stop (AT14, Q26), the unaffected-step
continuation (AT15, Q27) and the source-snapshot noop (AT16, Q28) —
through the same faked process boundary as the per-subcommand file.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tests.unit.tools.groundhog_acceptance_support import (
    CHECK_FAIL_CODE,
    QueueSpawns,
    assert_closing_grammar,
    make_deps,
    passing_transcript,
)
from tools.groundhog import cli, reporting_nextstep, snapshot
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_OBJECTIVE_MET,
    EXIT_TEST_FAILURES,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_at11_day_walks_the_whole_chain(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT11: a green ghog day spawns check, affected --no-cov, full (Q22)."""
    check_bat = tmp_path / "check.bat"
    check_bat.write_text("@echo off\n", encoding="utf-8")
    spawns = QueueSpawns(
        [
            (["compile ok"], 0),
            (passing_transcript(2, None), 0),
            (passing_transcript(4, "TOTAL    100    0   100%"), 0),
        ],
    )
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == len(("check", "affected", "full"))
    assert spawns.commands[0] == ["cmd.exe", "/d", "/c", str(check_bat)]
    assert "--no-cov" in spawns.commands[1]
    assert "--cov-report" in spawns.commands[2]
    out = capsys.readouterr().out
    assert "ghog check done" in out
    assert "ghog affected --no-cov done" in out
    assert "ghog full done" in out
    assert reporting_nextstep.MSG_FULL_OK in out
    assert_closing_grammar(out)


def test_at11_day_stops_at_a_failing_check(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT11: a failing check.bat stops the walk with its own code (Q22)."""
    (tmp_path / "check.bat").write_text("@echo off\nexit /b 7\n", encoding="utf-8")
    spawns = QueueSpawns([(["compile error detail"], CHECK_FAIL_CODE)])
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == CHECK_FAIL_CODE
    assert len(spawns.commands) == 1
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_CHECK_FAIL in out
    assert "ghog affected" not in out


def test_at11_day_stops_at_failing_affected(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT11: failing affected tests stop the walk before the full run."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    failing = [
        "collected 1 items",
        "tests/test_a.py::test_one FAILED [100%]",
        "=================== FAILURES ===================",
        "E   AssertionError",
    ]
    spawns = QueueSpawns([(["compile ok"], 0), (failing, 1)])
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_TEST_FAILURES
    assert len(spawns.commands) == len(("check", "affected"))
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_AFFECTED_NOCOV_FAIL in out
    assert "ghog full done" not in out


def test_at11_day_skips_a_missing_check(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT11: without check.bat the walk goes straight to the tests (Q10)."""
    spawns = QueueSpawns(
        [
            (passing_transcript(2, None), 0),
            (passing_transcript(2, "TOTAL    100    3    97%"), 0),
        ],
    )
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_COVERAGE_GAP
    assert len(spawns.commands) == len(("affected", "full"))
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_CHECK_MISSING in out
    assert reporting_nextstep.MSG_COVERAGE_GAP in out


def test_at14_day_stops_on_a_lying_check_bat(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT14: the day walk stops at the check step on the mismatch (Q26)."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    spawns = QueueSpawns(
        [([" ERROR : [check.bat] Check failed with status '1'."], 0)],
    )
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == 1
    assert len(spawns.commands) == 1
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_CHECK_EXIT_MISMATCH in out
    assert "ghog affected" not in out


def test_at15_day_walk_continues_past_an_unaffected_step(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT15: the day walk reaches full when nothing was affected (Q27)."""
    spawns = QueueSpawns(
        [
            (["no tests ran in 0.05s"], 5),
            (passing_transcript(4, "TOTAL    100    0   100%"), 0),
        ],
    )
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == len(("affected", "full"))
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_NO_TESTS_RUN in out
    assert reporting_nextstep.MSG_FULL_OK in out


def test_at16_green_day_records_the_snapshot_and_noops(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT16: a green walk writes the marker; the next walk is a noop."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("pass\n", encoding="utf-8")
    spawns = QueueSpawns(
        [
            (passing_transcript(2, None), 0),
            (passing_transcript(4, "TOTAL    100    0   100%"), 0),
        ],
    )
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert snapshot.marker_path(tmp_path).is_file()
    capsys.readouterr()
    again = QueueSpawns([])
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(again))
    assert code == EXIT_OBJECTIVE_MET
    assert again.commands == []
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_DAY_NOOP in out
    assert "ghog day done" in out


def test_at16_force_and_changes_re_arm_the_walk(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT16: --force walks again, and so does a changed Python file."""
    source = tmp_path / "mod.py"
    source.write_text("pass\n", encoding="utf-8")
    snapshot.write_marker(tmp_path)
    forced = QueueSpawns(
        [
            (passing_transcript(2, None), 0),
            (passing_transcript(2, "TOTAL    100    0   100%"), 0),
        ],
    )
    argv = ["day", "--force", "--root", str(tmp_path), "--llm"]
    assert cli.main(argv, make_deps(forced)) == EXIT_OBJECTIVE_MET
    assert len(forced.commands) == len(("affected", "full"))
    capsys.readouterr()
    source.write_text("pass  # changed\n", encoding="utf-8")
    changed = QueueSpawns(
        [
            (passing_transcript(2, None), 0),
            (passing_transcript(2, "TOTAL    100    0   100%"), 0),
        ],
    )
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(changed))
    assert code == EXIT_OBJECTIVE_MET
    assert len(changed.commands) == len(("affected", "full"))


def test_at16_failing_walk_records_no_snapshot(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT16: a failing walk leaves no marker behind."""
    failing = [
        "collected 1 items",
        "tests/test_a.py::test_one FAILED [100%]",
    ]
    spawns = QueueSpawns([(failing, 1)])
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_TEST_FAILURES
    assert not snapshot.marker_path(tmp_path).is_file()
    assert reporting_nextstep.MSG_DAY_NOOP not in capsys.readouterr().out


def test_day_brackets_each_step_with_timestamped_headers(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each day step is framed by vvv/^^^ banners and timestamped headers."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    spawns = QueueSpawns(
        [
            (["compile ok"], 0),
            (passing_transcript(2, None), 0),
            (passing_transcript(4, "TOTAL    100    0   100%"), 0),
        ],
    )
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    project = re.escape(tmp_path.name)
    timestamp = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d"
    assert re.search(rf"{project}: -{{20,}}", out)
    assert re.search(rf"{project}: -+ v+ -+", out)
    assert re.search(rf"{project}: -+ \^+ -+", out)
    for label in ("check", "affected --no-cov", "full"):
        step = re.escape(label)
        assert re.search(rf"{project}: == ghog {step} == started \| {timestamp}", out)
        assert re.search(
            rf"{project}: == ghog {step} == ended \| {timestamp} \| duration=\d+\.\d+s",
            out,
        )


# eof
