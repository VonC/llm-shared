"""Unit tests for the groundhog CLI seams.

Cover the mode pick (Q03), the root resolution, the exit-code
classification (Q12), the setup reasons, the labels and postfix (Q20),
and the user-mode bar flow against a fake bar.

Fix: follow the cli.py line-budget split — the classification, reason,
label and postfix helpers now live in ``tools.groundhog.commands``.

Fix: the bar finish now tops the bar off — a completed run fills it to
the collected total even when some result lines escaped the parser, and
a crashed run only catches up to the parsed count; both paths covered.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from tools.groundhog import cli, commands, reporting, runner
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    PYTEST_INTERNAL_ERROR,
    PYTEST_NO_TESTS,
    PYTEST_USAGE_ERROR,
    Mode,
    RunResult,
    RunStats,
)

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

    import pytest

_GATE_FULL = 100.0
_GATE_LOW = 90.0
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
) -> cli.Deps:
    """Build CLI deps around one canned child process.

    Args:
        lines: The scripted child output lines.
        code: The scripted child exit code.
        bars: Receives the fake bars created by the bar factory.
        which_result: The pytest lookup result.

    Returns:
        The injectable seams.
    """

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
    )


def _result(stats: RunStats, pytest_exit: int, *, crashed: bool = False) -> RunResult:
    """Build a run result for classification tests.

    Args:
        stats: The run statistics.
        pytest_exit: The pytest child exit code.
        crashed: The crash flag.

    Returns:
        The run result.
    """
    return RunResult(
        stats=stats,
        pytest_exit=pytest_exit,
        crashed=crashed,
        failure_block=(),
        tail=(),
    )


def _invocation(sub: str, *, no_cov: bool, root: Path) -> cli.Invocation:
    """Build an invocation for direct helper tests.

    Args:
        sub: The subcommand name.
        no_cov: The coverage toggle.
        root: The project root.

    Returns:
        The invocation.
    """
    return cli.Invocation(
        sub=sub,
        files=(),
        no_cov=no_cov,
        mode=Mode.LLM,
        root=root,
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
    assert reporting.MSG_AFFECTED_NOCOV_FAIL in out
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
    assert reporting.MSG_NO_BASELINE in capsys.readouterr().out


def test_classify_usage_error(tmp_path: Path) -> None:
    """A pytest usage error is a setup error (Q12)."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    result = _result(RunStats(), PYTEST_USAGE_ERROR)
    assert commands.classify(invocation, result, _GATE_FULL) == EXIT_SETUP_ERROR


def test_classify_crash_wins(tmp_path: Path) -> None:
    """The crash flag beats every other signal (Q06)."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    result = _result(RunStats(), 0, crashed=True)
    assert commands.classify(invocation, result, _GATE_FULL) == EXIT_SUITE_CRASH


def test_classify_no_tests_per_subcommand(tmp_path: Path) -> None:
    """No tests collected: green for affected, setup error elsewhere."""
    full = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    affected = _invocation(runner.SUB_AFFECTED, no_cov=False, root=tmp_path)
    bare = _result(RunStats(), PYTEST_NO_TESTS)
    assert commands.classify(full, bare, _GATE_FULL) == EXIT_SETUP_ERROR
    assert commands.classify(affected, bare, None) == EXIT_OBJECTIVE_MET
    covered = RunStats()
    covered.cov_percent = _GATE_LOW
    below = _result(covered, PYTEST_NO_TESTS)
    assert commands.classify(affected, below, _GATE_FULL) == EXIT_COVERAGE_GAP


def test_classify_coverage_rules(tmp_path: Path) -> None:
    """Coverage classification: gate, parse miss and gap (Q14, Q19)."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    unread = _result(RunStats(), 0)
    assert commands.classify(invocation, unread, _GATE_FULL) == EXIT_SETUP_ERROR
    low = RunStats()
    low.cov_percent = _GATE_LOW
    assert commands.classify(invocation, _result(low, 0), _GATE_FULL) == (
        EXIT_COVERAGE_GAP
    )
    full = RunStats()
    full.cov_percent = _GATE_FULL
    assert commands.classify(invocation, _result(full, 0), _GATE_FULL) == (
        EXIT_OBJECTIVE_MET
    )
    assert commands.classify(invocation, _result(RunStats(), 0), None) == (
        EXIT_OBJECTIVE_MET
    )


def test_classify_failures(tmp_path: Path) -> None:
    """Failing tests classify as exit 2 before any coverage look."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    stats = RunStats()
    stats.failed = 1
    assert commands.classify(invocation, _result(stats, 1), _GATE_FULL) == (
        EXIT_TEST_FAILURES
    )


def test_setup_reason_per_precondition() -> None:
    """Every setup-error reason names its failing precondition."""
    usage = _result(RunStats(), PYTEST_USAGE_ERROR)
    assert "usage error" in commands.setup_reason(usage, measured=True)
    empty = _result(RunStats(), PYTEST_NO_TESTS)
    assert "no tests collected" in commands.setup_reason(empty, measured=True)
    unread = _result(RunStats(), 0)
    assert "TOTAL line not found" in commands.setup_reason(unread, measured=True)
    assert commands.setup_reason(unread, measured=False) == "ghog: setup error."


def test_sub_label_for_the_ptanc_variant(tmp_path: Path) -> None:
    """The label spells the --no-cov variant (Q16)."""
    nocov = _invocation(runner.SUB_AFFECTED, no_cov=True, root=tmp_path)
    assert commands.sub_label(nocov) == "affected --no-cov"
    plain = _invocation(runner.SUB_AFFECTED, no_cov=False, root=tmp_path)
    assert commands.sub_label(plain) == "affected"


def test_postfix_with_and_without_coverage() -> None:
    """The bar postfix adds the coverage once parsed (Q20)."""
    stats = RunStats()
    assert commands.postfix(stats) == "fail=0 warn=0 xfail=0"
    stats.cov_percent = _GATE_FULL
    assert commands.postfix(stats) == "fail=0 warn=0 xfail=0 cov=100"


# eof
