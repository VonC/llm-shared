"""Strict cost gates of the leveled ghog day walk (v0.13.0 full_suite_levels).

Step 0 adds these contracts before the leveled walk exists. The value of the
effort is work not done: a default walk that never spawns the full run, an
upgrade that reuses check and affected, a noop on stronger saved proof, and a
grouped walk that runs only its group's test files after one tree walk. Each
gate drives ``cli.main`` through the faked process boundary on a ``tmp_path``
project and asserts the spawned child commands, so it measures the work
avoided rather than wall-clock jitter; its timeout only bounds a runaway walk.

Each gate stays a strict ``xfail`` until its owning step lands: Step 2 removes
the mark from the default-walk, upgrade and noop gates, Step 4 from the two
grouped-walk gates, and both keep the timeout. Before its owner, a gate fails
on an assertion, never by an error: an unknown ``--full`` or ``--group``
option makes argparse exit 2, which :func:`_run` returns as a code, and every
spawn queue holds the children the pre-change walk pops, so no spawn ever
finds an empty queue.

Fix (v0.13.0 full_suite_levels, Step 2): the leveled walk landed, so the
default-walk, upgrade and noop gates lose their ``xfail`` mark and keep their
timeout; Step 4 activates the two grouped gates with their timeouts unchanged.
"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any, Final

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    QueueSpawns,
    make_deps,
    passing_transcript,
)
from tools.groundhog import cli
from tools.groundhog.models import EXIT_OBJECTIVE_MET

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

# The wall-clock bound of every gate: only a runaway walk trips it.
GATE_TIMEOUT_SECONDS: Final = 5
# The ambient selectors no gate may inherit from the developer's shell.
GHOG_FULL_ENV: Final = "GHOG_FULL"
GHOG_GROUP_ENV: Final = "GHOG_GROUP"
# The declared group of the grouped gates and its one resolved test file.
GROUP_NAME: Final = "sentinel"
GROUP_TEST_FILE: Final = "tests/sentinel/test_core.py"
# The children of a default walk: check.bat and affected --no-cov.
DEFAULT_WALK_SPAWNS: Final = 2
# The group children of a grouped walk: affected and full.
GROUP_SPAWNS: Final = 2
# A covered full run that meets the default 100% coverage gate.
_FULL_TOTAL_LINE: Final = "TOTAL    100    0   100%"
_PYPROJECT: Final = '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
_GROUPS: Final = (
    f"[{GROUP_NAME}]\n"
    "tests =\n"
    "    tests/sentinel/**\n"
    "sources =\n"
    "    src/sentinel/**\n"
)
_TEST_BODY: Final = "def test_ok() -> None:\n    assert True\n"


@pytest.fixture(autouse=True)
def clear_ambient_selectors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear GHOG_FULL and GHOG_GROUP, so each gate sees its own selectors."""
    monkeypatch.delenv(GHOG_FULL_ENV, raising=False)
    monkeypatch.delenv(GHOG_GROUP_ENV, raising=False)


def _write(path: pathlib.Path, text: str) -> None:
    """Write one project file, creating its folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _project(root: pathlib.Path) -> pathlib.Path:
    """Build a whole-suite project: check.bat, pyproject.toml, a source, a test.

    Args:
        root: The ``tmp_path`` project root.

    Returns:
        The check.bat path, for the check child assertion.
    """
    check_bat = root / "check.bat"
    _write(check_bat, "@echo off\n")
    _write(root / "pyproject.toml", _PYPROJECT)
    _write(root / "src" / "mod.py", "VALUE = 1\n")
    _write(root / "tests" / "test_mod.py", _TEST_BODY)
    return check_bat


def _grouped_project(root: pathlib.Path) -> pathlib.Path:
    """Add the sentinel group to a project: declaration, source, test, conftest.

    The conftest sits under the matched test folder but is no test file, so
    the group's test side resolves to :data:`GROUP_TEST_FILE` alone.

    Args:
        root: The ``tmp_path`` project root.

    Returns:
        The check.bat path.
    """
    check_bat = _project(root)
    _write(root / ".ghog-groups", _GROUPS)
    _write(root / "src" / "sentinel" / "core.py", "READY = True\n")
    _write(root / GROUP_TEST_FILE, _TEST_BODY)
    _write(root / "tests" / "sentinel" / "conftest.py", "")
    return check_bat


def _green_walk() -> list[tuple[list[str], int]]:
    """Return the three green children of a pre-change walk, in spawn order."""
    return [
        (["compile ok"], 0),
        (passing_transcript(2, None), 0),
        (passing_transcript(4, _FULL_TOTAL_LINE), 0),
    ]


def _green_group_walk() -> list[tuple[list[str], int]]:
    """Return the green children of a grouped pass walk: check, affected, full."""
    return [
        (["compile ok"], 0),
        (passing_transcript(1, None), 0),
        (passing_transcript(1, None), 0),
    ]


def _day(root: pathlib.Path, *options: str) -> list[str]:
    """Build a ``ghog day`` command line on the project root, in LLM mode."""
    return ["day", *options, "--root", str(root), "--llm"]


def _run(argv: Sequence[str], deps: cli.Deps) -> int:
    """Run one ghog invocation, returning an argparse exit as its code.

    Args:
        argv: The ghog arguments.
        deps: The injectable seams around the recording process factory.

    Returns:
        The contract exit code, or argparse's own code (2) for an option the
        CLI does not know yet.
    """
    try:
        return cli.main(argv, deps)
    except SystemExit as error:
        return error.code if isinstance(error.code, int) else 1


def _python_paths(command: Sequence[str], root: pathlib.Path) -> set[pathlib.Path]:
    """Return the resolved ``.py`` positional paths of one child command."""
    return {(root / arg).resolve() for arg in command if arg.endswith(".py")}


def _group_spawn_count(commands: Sequence[Sequence[str]], root: pathlib.Path) -> int:
    """Count the children given exactly the group's test files as paths."""
    expected = {(root / GROUP_TEST_FILE).resolve()}
    return sum(1 for command in commands if _python_paths(command, root) == expected)


def _count_rglob(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Record every ``Path.rglob`` call from now on, each still walking for real.

    Args:
        monkeypatch: The fixture that restores ``Path.rglob`` after the test.

    Returns:
        The live list of rglob patterns, one entry per call.
    """
    original = pathlib.Path.rglob
    patterns: list[str] = []

    def counting(
        self: pathlib.Path,
        pattern: str,
        **options: Any,
    ) -> Iterator[pathlib.Path]:
        patterns.append(pattern)
        return original(self, pattern, **options)

    monkeypatch.setattr(pathlib.Path, "rglob", counting)
    return patterns


@pytest.mark.timeout(GATE_TIMEOUT_SECONDS)
def test_default_walk_spawns_no_full_run(tmp_path: pathlib.Path) -> None:
    """A green default walk spawns check.bat and affected --no-cov, no full run."""
    check_bat = _project(tmp_path)
    spawns = QueueSpawns(_green_walk())
    code = _run(_day(tmp_path), make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == DEFAULT_WALK_SPAWNS
    assert spawns.commands[0] == ["cmd.exe", "/d", "/c", str(check_bat)]
    assert "--no-cov" in spawns.commands[1]


@pytest.mark.timeout(GATE_TIMEOUT_SECONDS)
def test_upgrade_spawns_only_the_full_run(tmp_path: pathlib.Path) -> None:
    """An upgrade to cov reuses check and affected: one covered full child only."""
    _project(tmp_path)
    first = QueueSpawns(_green_walk())
    assert _run(_day(tmp_path), make_deps(first)) == EXIT_OBJECTIVE_MET
    full_green = (passing_transcript(4, _FULL_TOTAL_LINE), 0)
    upgrade = QueueSpawns([full_green, full_green, full_green])
    code = _run(_day(tmp_path, "--full=cov"), make_deps(upgrade))
    assert code == EXIT_OBJECTIVE_MET
    assert len(upgrade.commands) == 1
    full = upgrade.commands[0]
    assert "--cov-report" in full
    assert "--cov-append" not in full
    assert "--durations=0" not in full


@pytest.mark.timeout(GATE_TIMEOUT_SECONDS)
def test_stronger_saved_proof_spawns_nothing(tmp_path: pathlib.Path) -> None:
    """Saved speed proof on a sequential project meets --full=cov: nothing runs."""
    _project(tmp_path)
    proving = QueueSpawns(_green_walk())
    code = _run(_day(tmp_path, "--full=speed"), make_deps(proving))
    assert code == EXIT_OBJECTIVE_MET
    reuse = QueueSpawns(_green_walk())
    code = _run(_day(tmp_path, "--full=cov"), make_deps(reuse))
    assert code == EXIT_OBJECTIVE_MET
    assert reuse.commands == []


@pytest.mark.timeout(GATE_TIMEOUT_SECONDS)
def test_grouped_walk_passes_only_group_test_files(tmp_path: pathlib.Path) -> None:
    """A grouped walk gives affected and full exactly the group's test files."""
    check_bat = _grouped_project(tmp_path)
    spawns = QueueSpawns(_green_group_walk())
    argv = _day(tmp_path, "--full=pass", f"--group={GROUP_NAME}")
    code = _run(argv, make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert spawns.commands[0] == ["cmd.exe", "/d", "/c", str(check_bat)]
    expected = {(tmp_path / GROUP_TEST_FILE).resolve()}
    group_paths = [_python_paths(command, tmp_path) for command in spawns.commands[1:]]
    assert group_paths == [expected, expected]


@pytest.mark.timeout(GATE_TIMEOUT_SECONDS)
def test_grouped_walk_walks_the_tree_once(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One tree walk serves the digest and the group membership of a walk."""
    _grouped_project(tmp_path)
    spawns = QueueSpawns(_green_group_walk())
    walks = _count_rglob(monkeypatch)
    argv = _day(tmp_path, "--full=pass", f"--group={GROUP_NAME}")
    code = _run(argv, make_deps(spawns))
    assert code == EXIT_OBJECTIVE_MET
    assert _group_spawn_count(spawns.commands, tmp_path) == GROUP_SPAWNS
    assert len(walks) == 1


# eof
