"""Unit tests for the groundhog CLI seams.

Cover the mode pick (Q03), the root resolution, the exit-code paths of the
CLI (Q12), and the user-mode bar flow against a fake bar (Q20).

Fix: the bar finish now tops the bar off — a completed run fills it to
the collected total even when some result lines escaped the parser, and
a crashed run only catches up to the parsed count; both paths covered.

Fix: cover the exclude subcommand (Q62) — it writes the node id and its
measured time into the ``[exclusion]`` section of ``a.ghog.outliers`` (in
the artifact home) and exits 0, with the floor lines seeded.

Fix: cover the exit-9 refusal of a root with no pytest suite. A pytest
subcommand exits 9 before any pytest lookup, and a day walk runs check.bat
first, then stops at its first pytest step.

Fix: the exclude confirmation names ``a.ghog.outliers`` at its real location
in the artifact home, not as a bare project-root file name.

Fix (v0.13.0 full_suite_levels, Step 1): the direct classification and
setup-reason cases moved to ``test_groundhog_verdicts``, the label and
postfix cases to ``test_groundhog_progress``, beside the helpers that moved
out of ``commands.py``; the user-bar flows stay here, driving the moved
progress sink through the CLI. The file now also routes every dispatch path
of ``main`` (status, the live-run refusal, the detached walk, init, and the
script's ``__main__`` guard), so it covers ``cli.py`` on its own.
"""

from __future__ import annotations

import runpy
import sys
from dataclasses import replace
from typing import TYPE_CHECKING, cast

import pytest

from tools.groundhog import (
    cli,
    exclusions,
    floor,
    reporting_nextstep,
    status,
)
from tools.groundhog.models import (
    EXIT_NOT_PYTEST_PROJECT,
    EXIT_OBJECTIVE_MET,
    EXIT_RUN_LIVE,
    EXIT_RUN_LOST,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    PYTEST_INTERNAL_ERROR,
    Mode,
)

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

_TWO_TESTS = 2
_THREE_TESTS = 3


class _FakeProcess:
    """A canned child process: scripted output lines and exit code."""

    def __init__(self, lines: list[str], returncode: int) -> None:
        """Script the child.

        Args:
            lines: The output lines, newline free.
            returncode: The exit code returned by wait().
        """
        self.stdout = iter([f"{line}\n" for line in lines])
        self._returncode = returncode

    def wait(self) -> int:
        """Return the scripted exit code.

        Returns:
            The scripted exit code.
        """
        return self._returncode


class _FakeBar:
    """A fake user bar satisfying the ProgressBar protocol (Q20)."""

    def __init__(self) -> None:
        """Start with empty recordings."""
        self.updates: list[int] = []
        self.postfixes: list[str] = []
        self.closed = False

    def update(self, n: int) -> object:
        """Record one advance.

        Args:
            n: Finished tests since the previous advance.

        Returns:
            None.
        """
        self.updates.append(n)
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


def _deps(
    lines: list[str],
    code: int,
    bars: list[_FakeBar],
    which_result: str | None = "pytest",
    *,
    pytest_project: bool = True,
) -> cli.Deps:
    """Build CLI deps around one canned child process.

    Args:
        lines: The scripted child output lines.
        code: The scripted child exit code.
        bars: Receives the fake bars created by the bar factory.
        which_result: The pytest lookup result.
        pytest_project: The pytest-suite probe result for the root.

    Returns:
        The injectable seams.
    """

    def _pytest_project(root: Path) -> bool:
        del root
        return pytest_project

    def _factory(command: list[str], cwd: Path) -> subprocess.Popen[str]:
        del command, cwd
        return cast("subprocess.Popen[str]", _FakeProcess(lines, code))

    def _which(name: str) -> str | None:
        del name
        return which_result

    def _bar_factory(total: int, description: str) -> _FakeBar:
        del total, description
        bar = _FakeBar()
        bars.append(bar)
        return bar

    return cli.Deps(
        popen_factory=_factory,
        clock=lambda: 0.0,
        bar_factory=_bar_factory,
        which=_which,
        pytest_project=_pytest_project,
    )


def test_pick_mode_rules() -> None:
    """Force flags win, then the TTY decides (Q03)."""
    assert cli.pick_mode(user=True, llm=False, tty=False) is Mode.USER
    assert cli.pick_mode(user=False, llm=True, tty=True) is Mode.LLM
    assert cli.pick_mode(user=False, llm=False, tty=True) is Mode.USER
    assert cli.pick_mode(user=False, llm=False, tty=False) is Mode.LLM


def test_stdout_is_tty_returns_a_bool() -> None:
    """The TTY probe returns a boolean for the mode pick (Q03)."""
    assert isinstance(cli._stdout_is_tty(), bool)


def test_resolve_root_with_override(tmp_path: Path) -> None:
    """The --root override resolves without any .git lookup."""
    assert cli._resolve_root(str(tmp_path)) == tmp_path.resolve()


def test_resolve_root_without_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Without --root the shared project-root lookup is used."""

    def _fake_root(_start: Path) -> Path:
        return tmp_path

    monkeypatch.setattr(cli, "find_project_root", _fake_root)
    assert cli._resolve_root(None) == tmp_path


def test_main_reports_a_missing_project_root(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failed root lookup is the setup-error exit (Q12)."""

    def _boom(_start: Path) -> Path:
        message = "Could not find project root with .git directory."
        raise FileNotFoundError(message)

    monkeypatch.setattr(cli, "find_project_root", _boom)
    bars: list[_FakeBar] = []
    code = cli.main(["full", "--llm"], _deps([], 0, bars))
    assert code == EXIT_SETUP_ERROR
    assert "ghog:" in capsys.readouterr().out


def test_main_without_pytest_is_a_setup_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A missing pytest executable exits 5 with the Q21 hint."""
    bars: list[_FakeBar] = []
    deps = _deps([], 0, bars, which_result=None)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_SETUP_ERROR
    out = capsys.readouterr().out
    assert "pytest not found" in out
    assert "exit=5" in out


def test_main_outside_a_pytest_project_exits_9(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A root with no pytest suite exits 9 before any pytest lookup."""
    looked_up: list[str] = []

    def _which(name: str) -> str | None:
        looked_up.append(name)
        return None

    bars: list[_FakeBar] = []
    deps = replace(_deps([], 0, bars, pytest_project=False), which=_which)
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_NOT_PYTEST_PROJECT
    assert looked_up == []
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_NOT_PYTEST_PROJECT in out
    assert reporting_nextstep.MSG_NOT_PYTEST_PROJECT_NEXT in out
    assert "pytest not found" not in out
    assert "ghog full done" in out
    assert "exit=9" in out


def test_day_outside_a_pytest_project_stops_after_the_check(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The day walk runs check.bat, then exits 9 at the first pytest step."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    bars: list[_FakeBar] = []
    deps = _deps([" OK    : [check.bat] fine"], 0, bars, pytest_project=False)
    code = cli.main(["day", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_NOT_PYTEST_PROJECT
    out = capsys.readouterr().out
    assert "ghog check done" in out
    assert "ghog affected --no-cov done" in out
    assert "exit=9" in out
    assert "ghog full done" not in out


def test_user_mode_drives_the_bar(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """User mode advances the bar and carries the counters (Q20)."""
    lines = [
        "collected 2 items",
        "tests/test_a.py::test_one PASSED [ 50%]",
        "tests/test_a.py::test_two PASSED [100%]",
        "TOTAL    10    0   100%",
        "====== 2 passed in 0.10s ======",
    ]
    bars: list[_FakeBar] = []
    deps = _deps(lines, 0, bars)
    code = cli.main(["full", "--root", str(tmp_path), "--user"], deps)
    assert code == EXIT_OBJECTIVE_MET
    assert len(bars) == 1
    assert sum(bars[0].updates) == _TWO_TESTS
    assert bars[0].closed is True
    assert bars[0].postfixes[-1] == "fail=0 warn=0 xfail=0 cov=100"
    assert "exit=0" in capsys.readouterr().out


def test_user_mode_tops_off_the_bar_on_completion(tmp_path: Path) -> None:
    """A finished run fills the bar to the collected total (Q20).

    The third result line carries a parameterized node id with a space,
    which the parser pattern does not count; the final top-off still
    leaves the bar at 100%.
    """
    lines = [
        "collected 3 items",
        "tests/test_a.py::test_one PASSED [ 33%]",
        "tests/test_a.py::test_two PASSED [ 66%]",
        "tests/test_a.py::test_three[two words] PASSED [100%]",
        "TOTAL    10    0   100%",
        "====== 3 passed in 0.10s ======",
    ]
    bars: list[_FakeBar] = []
    deps = _deps(lines, 0, bars)
    code = cli.main(["full", "--root", str(tmp_path), "--user"], deps)
    assert code == EXIT_OBJECTIVE_MET
    assert sum(bars[0].updates) == _THREE_TESTS
    assert bars[0].closed is True


def test_user_mode_keeps_the_bar_short_on_a_crash(tmp_path: Path) -> None:
    """A crashed run closes the bar at the parsed count, not full (Q06)."""
    lines = [
        "collected 3 items",
        "tests/test_a.py::test_one PASSED [ 33%]",
        "INTERNALERROR> Traceback (most recent call last):",
    ]
    bars: list[_FakeBar] = []
    deps = _deps(lines, PYTEST_INTERNAL_ERROR, bars)
    code = cli.main(["full", "--root", str(tmp_path), "--user"], deps)
    assert code == EXIT_SUITE_CRASH
    assert sum(bars[0].updates) == 1
    assert bars[0].closed is True


def test_affected_no_cov_failure_message(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failing uncovered affected run points back at the fix loop."""
    lines = [
        "collected 1 items",
        "tests/test_a.py::test_one FAILED [100%]",
    ]
    bars: list[_FakeBar] = []
    deps = _deps(lines, 1, bars)
    argv = ["affected", "--no-cov", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, deps)
    assert code == EXIT_TEST_FAILURES
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_AFFECTED_NOCOV_FAIL in out
    assert "ghog affected --no-cov done" in out


def test_single_without_baseline_notice(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A cold focus run states the missing baseline (Q18)."""
    lines = [
        "collected 1 items",
        "tests/test_a.py::test_one PASSED [100%]",
    ]
    bars: list[_FakeBar] = []
    deps = _deps(lines, 0, bars)
    argv = ["single", "tests/test_a.py", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, deps)
    assert code == EXIT_OBJECTIVE_MET
    assert reporting_nextstep.MSG_NO_BASELINE in capsys.readouterr().out


def test_exclude_subcommand_writes_the_entry(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The exclude subcommand records the node and its measured time (Q62)."""
    # A parametrized id with a space survives as one positional argument.
    node = "tests/test_slow.py::test_freak[two words]"
    bars: list[_FakeBar] = []
    deps = _deps([], 0, bars)
    argv = ["exclude", node, "11.41", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, deps)
    assert code == EXIT_OBJECTIVE_MET
    # The entry is persisted in the [exclusion] section at its measured time.
    assert exclusions.read_exclusions(tmp_path) == {node: 11.41}
    out = capsys.readouterr().out
    assert node in out
    # The confirmation names the floor file where it lives, the artifact home.
    assert f"in {tmp_path.resolve() / '.reviews' / floor.FLOOR_FILE};" in out
    assert "ghog exclude done" in out
    assert "exit=0" in out


def test_main_routes_status_then_refuses_a_live_run(tmp_path: Path) -> None:
    """Status replays the lifecycle; a run over a live one refuses (Q32)."""
    bars: list[_FakeBar] = []
    assert cli.main(["status", "--root", str(tmp_path), "--llm"]) == EXIT_RUN_LOST
    status.write_running(tmp_path, "day")
    code = cli.main(["full", "--root", str(tmp_path), "--llm"], _deps([], 0, bars))
    assert code == EXIT_RUN_LIVE
    assert bars == []


def test_main_routes_a_detached_day_walk(tmp_path: Path) -> None:
    """A detached day walk is handed to the survivor spawn (Q32)."""
    spawned: list[list[str]] = []

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del log_path, preamble, cwd
        spawned.append(command)
        status.write_running(tmp_path, "day")
        return 1

    def _no_sleep(_seconds: float) -> None:
        return None

    bars: list[_FakeBar] = []
    deps = replace(_deps([], 0, bars), detach_factory=_factory, sleep=_no_sleep)
    code = cli.main(["day", "--detach", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_RUN_LIVE
    assert len(spawned) == 1


def test_main_routes_init(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Init registers the skill pointers outside the lifecycle bracket (Q23)."""
    bars: list[_FakeBar] = []
    deps = replace(_deps([], 0, bars), home=lambda: tmp_path / "home")
    assert cli.main(["init", "--root", str(tmp_path), "--llm"], deps) == EXIT_OBJECTIVE_MET
    assert "ghog init done" in capsys.readouterr().out


def test_cli_script_runs_as_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The cli script runs through its __main__ guard with the contract code."""
    transcript = ["collected 1 items", "tests/test_a.py::test_one PASSED [100%]"]

    def _fake_popen(*args: object, **kwargs: object) -> object:
        del args, kwargs
        return _FakeProcess(transcript, 0)

    def _fake_which(_name: str) -> str:
        return "pytest"

    monkeypatch.setattr("subprocess.Popen", _fake_popen)
    monkeypatch.setattr("shutil.which", _fake_which)
    # The script keeps the real pytest-suite probe, so the root needs a marker.
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    script_path = cli.__file__
    argv = [script_path, "single", "tests/test_a.py", "--root", str(tmp_path), "--llm"]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(script_path, run_name="__main__")
    assert raised.value.code == EXIT_OBJECTIVE_MET


# eof
