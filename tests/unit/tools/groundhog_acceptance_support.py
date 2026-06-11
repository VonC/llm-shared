"""Shared fakes and transcript builders of the groundhog acceptance tests.

Split out of ``test_groundhog_acceptance.py`` for the repo line budget:
both acceptance files (the subcommand scenarios and the day-walk
scenarios) fake the same single element — the process boundary — through
these helpers, so the real parsing, classification, reporting and
baseline behavior stays under test.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

from tools.groundhog import cli, reporting

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

# The non-contract exit code used for check.bat passthrough scenarios.
CHECK_FAIL_CODE: Final = 7
# The keys of the closing-line grammar (Q16).
_GRAMMAR_KEYS: Final = ("fail=", "warn=", "xfail=", "cov=", "exit=")


class FakeProcess:
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


class Spawns:
    """A recording process factory around one canned child."""

    def __init__(self, lines: list[str], returncode: int) -> None:
        """Script the factory.

        Args:
            lines: The scripted output lines.
            returncode: The scripted exit code.
        """
        self._lines = lines
        self._returncode = returncode
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], cwd: Path) -> subprocess.Popen[str]:
        """Record the spawn and return the canned child.

        Args:
            command: The child command line.
            cwd: The child working directory.

        Returns:
            The canned process, seen as a Popen.
        """
        del cwd
        self.commands.append(command)
        return cast(
            "subprocess.Popen[str]",
            FakeProcess(self._lines, self._returncode),
        )


class QueueSpawns:
    """A recording factory yielding one canned child per spawn (AT11)."""

    def __init__(self, children: list[tuple[list[str], int]]) -> None:
        """Script the children, in spawn order.

        Args:
            children: One (lines, exit code) pair per expected spawn.
        """
        self._children = list(children)
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], cwd: Path) -> subprocess.Popen[str]:
        """Record the spawn and return the next canned child.

        Args:
            command: The child command line.
            cwd: The child working directory.

        Returns:
            The canned process, seen as a Popen.
        """
        del cwd
        self.commands.append(command)
        lines, code = self._children.pop(0)
        return cast("subprocess.Popen[str]", FakeProcess(lines, code))


class SteppingClock:
    """A clock jumping one silence floor per reading (Q04)."""

    def __init__(self) -> None:
        """Start at zero."""
        self.now = 0.0

    def __call__(self) -> float:
        """Return the time, then jump past the silence floor.

        Returns:
            The fake monotonic time.
        """
        current = self.now
        self.now += reporting.SILENCE_FLOOR_SECONDS + 1.0
        return current


def make_deps(spawns: Spawns | QueueSpawns) -> cli.Deps:
    """Build CLI deps around a recording factory.

    Args:
        spawns: The recording process factory.

    Returns:
        The injectable seams.
    """
    return cli.Deps(
        popen_factory=spawns,
        clock=lambda: 0.0,
        which=lambda _name: "pytest",
    )


def passing_transcript(count: int, total_line: str | None) -> list[str]:
    """Build a passing pytest transcript.

    Args:
        count: The collected and passing test count.
        total_line: The coverage TOTAL line, or ``None`` to omit it.

    Returns:
        The transcript lines.
    """
    lines = [f"collected {count} items"]
    for index in range(count):
        percent = (index + 1) * 100 // count
        lines.append(f"tests/test_ok.py::test_{index} PASSED [{percent:>4}%]")
    if total_line is not None:
        lines.append(total_line)
    lines.append(f"====== {count} passed, 2 warnings in 0.10s ======")
    return lines


def failing_transcript() -> list[str]:
    """Build a failing pytest transcript with a FAILURES block.

    Returns:
        The transcript lines.
    """
    return [
        "collected 3 items",
        "tests/test_a.py::test_one PASSED [ 33%]",
        "tests/test_a.py::test_two FAILED [ 66%]",
        "tests/test_b.py::test_three FAILED [100%]",
        "=================== FAILURES ===================",
        "______ test_two ______",
        "E   AssertionError: 1 == 2",
        "============ short test summary info ============",
        "FAILED tests/test_a.py::test_two - AssertionError",
        "====== 2 failed, 1 passed in 0.20s ======",
    ]


def assert_closing_grammar(out: str) -> None:
    """Assert the closing line carries every contract key (AT10, Q16).

    Args:
        out: The captured run output.
    """
    closing = [line for line in out.splitlines() if " done fail=" in line]
    assert closing
    for key in _GRAMMAR_KEYS:
        assert key in closing[-1]


# eof
