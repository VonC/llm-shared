"""Shared project, transcript and proof helpers of the level acceptance tests.

v0.13.0 full_suite_levels, Step 2: both acceptance files of this package drive
``cli.main`` on a ``tmp_path`` project through the faked process boundary of
``groundhog_acceptance_support``; these helpers build the project, the canned
children of each step (an interrupted child among them), and the saved proof
a scenario starts from.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from tests.unit.tools.groundhog_acceptance_support import (
    QueueSpawns,
    failing_transcript,
    make_deps,
    passing_transcript,
)
from tools.groundhog import cli, runner, snapshot

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from tools.groundhog.levels import FullLevel

# One canned child: its output lines and its exit code.
type Child = tuple[list[str], int]

# A covered full run meeting the default 100% gate, and one below it.
GREEN_TOTAL: Final = "TOTAL    100    0   100%"
GAP_TOTAL: Final = "TOTAL    100    3    97%"
# The one call far above the one-second floor in the slow durations block.
FREAK_NODE: Final = "tests/test_slow.py::test_freak"
_CALLS: Final = (
    ("tests/test_a.py::test_one", 0.10),
    ("tests/test_b.py::test_two", 0.12),
    ("tests/test_c.py::test_three", 0.08),
    ("tests/test_d.py::test_four", 0.10),
    ("tests/test_e.py::test_five", 0.11),
    (FREAK_NODE, 5.00),
)
# The canned children of the steps every scenario starts with.
CHECK_OK: Final[Child] = (["compile ok"], 0)
AFFECTED_OK: Final[Child] = (passing_transcript(2, None), 0)
FULL_GREEN: Final[Child] = (passing_transcript(4, GREEN_TOTAL), 0)
FULL_GAP: Final[Child] = (passing_transcript(4, GAP_TOTAL), 0)
TESTS_FAILING: Final[Child] = (failing_transcript(), 1)
TIMINGS_GREEN: Final[Child] = (passing_transcript(4, None), 0)
CRASHING: Final[Child] = (
    ["collected 2 items", "tests/test_a.py::test_one PASSED [ 50%]", "INTERNALERROR> boom"],
    3,
)
# pytest's real interruption banners, as the installed pytest prints them: a
# bare or messaged KeyboardInterrupt and an explicit pytest.exit.
_INTERRUPT_BANNER: Final = "!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!"
_EXIT_BANNER: Final = "!!!!!!!!!!!!!!!!!!!!!!! _pytest.outcomes.Exit: stopped !!!!!!!!!!!!!!!!!!!!!!!!"
# Each banner with its return code: pytest's interrupted exit 2, then a
# pytest.exit with its own return code 1 or 0 on a suite that never finished.
_INTERRUPTIONS: Final = (
    (_INTERRUPT_BANNER, 2),
    ("!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt: stopped !!!!!!!!!!!!!!!!!!!!!!!!!!", 2),
    (_EXIT_BANNER, 2),
    (_EXIT_BANNER, 1),
    (_EXIT_BANNER, 0),
)
# One interrupted child per banner and return code.
INTERRUPTED_CHILDREN: Final[tuple[Child, ...]] = tuple(
    (["collected 2 items", "tests/test_a.py::test_one PASSED [ 50%]", banner], code)
    for banner, code in _INTERRUPTIONS
)
# The test ids of INTERRUPTED_CHILDREN, in the same order.
INTERRUPTION_IDS: Final = ("bare", "message", "exit", "exit-code-1", "exit-code-0")
FAILED_THEN_INTERRUPTED: Final[Child] = (
    ["collected 2 items", "tests/test_a.py::test_one FAILED [ 50%]", _INTERRUPT_BANNER],
    2,
)


def project(root: Path, *, parallel: bool = False) -> Path:
    """Build a project: check.bat, one source file, and the parallel marker.

    Args:
        root: The ``tmp_path`` project root.
        parallel: Whether the project opts its full run into xdist workers.

    Returns:
        The project root.
    """
    (root / "check.bat").write_text("@echo off\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "mod.py").write_text("VALUE = 1\n", encoding="utf-8")
    if parallel:
        (root / runner.PARALLEL_MARKER).write_text("opt in\n", encoding="utf-8")
    return root


def slow_transcript(total_line: str | None = GREEN_TOTAL) -> list[str]:
    """Build a passing transcript whose durations block holds one freak call.

    Args:
        total_line: The coverage TOTAL line, ``None`` for an uncovered run.

    Returns:
        The transcript lines, the durations block before the final banner.
    """
    lines = [f"collected {len(_CALLS)} items"]
    lines.extend(f"{node} PASSED [ 50%]" for node, _ in _CALLS)
    if total_line is not None:
        lines.append(total_line)
    lines.append("=============== slowest durations ===============")
    lines.extend(f"{seconds:.2f}s call     {node}" for node, seconds in _CALLS)
    lines.append(f"====== {len(_CALLS)} passed in 0.10s ======")
    return lines


def run(
    root: Path,
    argv: list[str],
    children: list[Child],
    environ: Mapping[str, str] | None = None,
) -> tuple[int, QueueSpawns]:
    """Run one ghog command on the project in LLM mode.

    Args:
        root: The project root.
        argv: The subcommand and its own arguments.
        children: The canned children, in spawn order.
        environ: The environment variables the run sees.

    Returns:
        The exit code and the recording factory.
    """
    spawns = QueueSpawns(children)
    code = cli.main([*argv, "--root", str(root), "--llm"], make_deps(spawns, environ))
    return code, spawns


def save(root: Path, proof: FullLevel) -> None:
    """Record a whole-suite proof on the project's current sources.

    Args:
        root: The project root.
        proof: The proof to record.
    """
    snapshot.save_proof(
        root,
        snapshot.WHOLE_SCOPE_KEY,
        snapshot.WHOLE_SCOPE_FINGERPRINT,
        snapshot.source_digest(root),
        proof,
    )


def saved(root: Path) -> FullLevel | None:
    """Return the proof the whole-suite marker records, ``None`` without one.

    Args:
        root: The project root.

    Returns:
        The recorded proof level, or ``None``.
    """
    marker = snapshot.read_proof_marker(snapshot.marker_path(root))
    return None if marker is None else marker.proof


# eof
