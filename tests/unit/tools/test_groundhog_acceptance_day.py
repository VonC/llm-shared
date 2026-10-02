"""Acceptance tests for the ghog day walk scenarios.

Split out of ``test_groundhog_acceptance.py`` for the repo line budget:
this file covers the day-walk behavior — the ordered chain and its stops
(AT11, Q22), the lying-check stop (AT14, Q26), the unaffected-step
continuation (AT15, Q27) and the source-snapshot noop (AT16, Q28) —
through the same faked process boundary as the per-subcommand file.

Fix (v0.13.0 full_suite_levels, Step 2): the default walk stops after the
affected tests with the skip success line, and ``--full=cov`` walks the whole
three-step chain (AT11); the snapshot is the key=value proof marker, rewritten
with ``proof=none`` by a green default walk, met by the next default walk as a
noop, and removed when a failing walk leaves nothing proven (AT16).
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tests.unit.tools.groundhog_acceptance_support import (
    CHECK_FAIL_CODE,
    QueueSpawns,
    assert_closing_grammar,
    closing_line_of,
    make_deps,
    passing_transcript,
)
from tools.groundhog import cli, reporting_nextstep, snapshot
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_OBJECTIVE_MET,
    EXIT_TEST_FAILURES,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# The covered full run that meets the default 100% coverage gate.
_FULL_GREEN = "TOTAL    100    0   100%"


def _proof(root: Path) -> FullLevel | None:
    """Return the proof recorded by the whole-suite marker, if any."""
    marker = snapshot.read_proof_marker(snapshot.marker_path(root))
    return None if marker is None else marker.proof


def test_at11_default_day_stops_after_the_affected_tests(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT11: a green default walk spawns check and affected, never the full run."""
    check_bat = tmp_path / "check.bat"
    check_bat.write_text("@echo off\n", encoding="utf-8")
    spawns = QueueSpawns([(["compile ok"], 0), (passing_transcript(2, None), 0)])
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == len(("check", "affected"))
    assert spawns.commands[0] == ["cmd.exe", "/d", "/c", str(check_bat)]
    assert "--no-cov" in spawns.commands[1]
    out = capsys.readouterr().out
    assert "ghog full done" not in out
    assert reporting_nextstep.MSG_AFFECTED_NOCOV_OK not in out
    assert reporting_nextstep.success_line(FullLevel.NONE) in out
    closing = closing_line_of(out)
    assert closing.startswith(f"{tmp_path.name}: ghog day done")
    assert closing.endswith("full=none src=default proof=none reused=none scope=whole")
    assert_closing_grammar(out)


def test_at11_cov_day_walks_the_whole_chain(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT11: --full=cov spawns check, affected --no-cov, then the covered full run."""
    check_bat = tmp_path / "check.bat"
    check_bat.write_text("@echo off\n", encoding="utf-8")
    spawns = QueueSpawns(
        [
            (["compile ok"], 0),
            (passing_transcript(2, None), 0),
            (passing_transcript(4, _FULL_GREEN), 0),
        ],
    )
    argv = ["day", "--full=cov", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    check, affected, full = spawns.commands
    assert check == ["cmd.exe", "/d", "/c", str(check_bat)]
    assert ("--no-cov" in affected, "--cov-report" in full, "--durations=0" in full) == (True, True, False)
    out = capsys.readouterr().out
    expected = (
        "ghog check done",
        "ghog affected --no-cov done",
        "ghog full done",
        reporting_nextstep.success_line(FullLevel.COV),
    )
    assert [snippet for snippet in expected if snippet not in out] == []
    assert closing_line_of(out).endswith("full=cov src=param proof=cov reused=none scope=whole")
    assert _proof(tmp_path) is FullLevel.COV
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
    assert reporting_nextstep.check_fail_line(FullLevel.NONE) in out
    assert "ghog affected --no-cov done" not in out
    assert closing_line_of(out).endswith("proof=unproven reused=none scope=whole")


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
    argv = ["day", "--full=cov", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_TEST_FAILURES
    assert len(spawns.commands) == len(("check", "affected"))
    out = capsys.readouterr().out
    assert reporting_nextstep.affected_fail_line(FullLevel.COV) in out
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
    argv = ["day", "--full=cov", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_COVERAGE_GAP
    assert len(spawns.commands) == len(("affected", "full"))
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_CHECK_MISSING in out
    assert reporting_nextstep.coverage_gap_line(FullLevel.COV) in out


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
    assert "ghog affected --no-cov done" not in out


def test_at15_day_walk_continues_past_an_unaffected_step(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT15: a leveled walk reaches full when nothing was affected (Q27)."""
    spawns = QueueSpawns(
        [
            (["no tests ran in 0.05s"], 5),
            (passing_transcript(4, _FULL_GREEN), 0),
        ],
    )
    argv = ["day", "--full=cov", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == len(("affected", "full"))
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_NO_TESTS_RUN in out
    assert reporting_nextstep.success_line(FullLevel.COV) in out


def test_at16_green_day_records_the_proof_and_noops(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT16: a green default walk records proof=none; the next one is a noop."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("pass\n", encoding="utf-8")
    spawns = QueueSpawns([(passing_transcript(2, None), 0)])
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert _proof(tmp_path) is FullLevel.NONE
    capsys.readouterr()
    again = QueueSpawns([])
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(again))
    assert code == EXIT_OBJECTIVE_MET
    assert again.commands == []
    out = capsys.readouterr().out
    assert reporting_nextstep.noop_line(FullLevel.NONE, FullLevel.NONE) in out
    assert closing_line_of(out).endswith("full=none src=default proof=none reused=all scope=whole")


def test_at16_force_and_changes_re_arm_the_walk(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT16: --force walks again, and so does a changed Python file."""
    source = tmp_path / "mod.py"
    source.write_text("pass\n", encoding="utf-8")
    first = QueueSpawns([(passing_transcript(2, None), 0)])
    assert cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(first)) == EXIT_OBJECTIVE_MET
    forced = QueueSpawns([(passing_transcript(2, None), 0)])
    argv = ["day", "--force", "--root", str(tmp_path), "--llm"]
    assert cli.main(argv, make_deps(forced)) == EXIT_OBJECTIVE_MET
    assert len(forced.commands) == len(("affected",))
    capsys.readouterr()
    source.write_text("pass  # changed\n", encoding="utf-8")
    changed = QueueSpawns([(passing_transcript(2, None), 0)])
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(changed))
    assert code == EXIT_OBJECTIVE_MET
    assert len(changed.commands) == len(("affected",))


def test_at16_failing_walk_removes_an_unproven_marker(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT16: a walk that contradicts the none gate leaves no marker behind."""
    (tmp_path / "mod.py").write_text("pass\n", encoding="utf-8")
    green = QueueSpawns([(passing_transcript(2, None), 0)])
    assert cli.main(["day", "--root", str(tmp_path), "--llm"], make_deps(green)) == EXIT_OBJECTIVE_MET
    assert snapshot.marker_path(tmp_path).is_file()
    failing = [
        "collected 1 items",
        "tests/test_a.py::test_one FAILED [100%]",
    ]
    spawns = QueueSpawns([(failing, 1)])
    argv = ["day", "--force", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
    assert code == EXIT_TEST_FAILURES
    assert not snapshot.marker_path(tmp_path).is_file()
    out = capsys.readouterr().out
    assert "is met by saved proof" not in out
    assert closing_line_of(out).endswith("proof=unproven reused=none scope=whole")


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
            (passing_transcript(4, _FULL_GREEN), 0),
        ],
    )
    argv = ["day", "--full=cov", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, make_deps(spawns))
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
