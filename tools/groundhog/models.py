"""Shared models and constants for the groundhog pytest reset tool.

groundhog (alias ``ghog``) re-implements the ptr/pta/pts doskey aliases as
subcommands of one entry point, per ``tools/Pytest reset specs.md``. This
module carries the exit-code contract (Q12), the pytest exit-code names used
to classify a child run, the run statistics accumulated while streaming the
child output, and the error type shared by the other groundhog modules.

Fix: the contract gains the two lifecycle codes of Q32 — a live run to
wait on (6) and a lost run to relaunch (7) — used by the ``ghog status``
reporter and the live-run refusal, never by a run's own classification.

Fix: a full run green on tests and coverage that still hides a true
duration outlier returns the new ``EXIT_DURATION_OUTLIERS`` (8), judged
last so it never masks a failure or a coverage gap (Q34).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Final

# Exit-code contract of every groundhog subcommand (Q12).
EXIT_OBJECTIVE_MET: Final = 0
EXIT_TEST_FAILURES: Final = 2
EXIT_COVERAGE_GAP: Final = 3
EXIT_SUITE_CRASH: Final = 4
EXIT_SETUP_ERROR: Final = 5
# A full run green on tests and coverage that still hides a true duration
# outlier (Q34): a run-classification code judged last, only on an
# otherwise-green full run, so it never masks a failure or a coverage gap.
EXIT_DURATION_OUTLIERS: Final = 8
# Lifecycle codes of the Q32 status contract: a run is live (wait and
# poll ghog status), or the last run is lost — killed mid-walk or never
# recorded — and the walk must be relaunched.
EXIT_RUN_LIVE: Final = 6
EXIT_RUN_LOST: Final = 7

# pytest's own exit codes, used to classify the child run.
PYTEST_OK: Final = 0
PYTEST_TEST_FAILURES: Final = 1
PYTEST_INTERRUPTED: Final = 2
PYTEST_INTERNAL_ERROR: Final = 3
PYTEST_USAGE_ERROR: Final = 4
PYTEST_NO_TESTS: Final = 5


class Mode(Enum):
    """Output mode of a run: a user terminal or an LLM transcript (Q03)."""

    USER = "user"
    LLM = "llm"


class GroundhogError(Exception):
    """Fatal error raised by groundhog before or around a pytest run."""


@dataclass
class RunStats:
    """Counters accumulated while a pytest child run streams its output.

    Fix: a full run now also keeps each test's call-phase seconds in
    ``durations`` (Q36), the input the later true-outlier rule judges; any
    other run never sets the ``--durations`` flags, so the map stays empty.

    Attributes:
        total: Number of collected tests, 0 until the collect line is seen.
        done: Number of finished tests.
        failed: Failing or erroring test count.
        warnings: Warning count, read from the final summary line.
        xfailed: Expected-failure count.
        cov_percent: TOTAL coverage percentage, None until parsed (Q19).
        failed_ids: Node ids of the failing tests, in completion order.
        last_started: The most recent test node ids, the crash context (Q06).
        durations: Node id to call-phase seconds, parsed from the slowest
            durations block of a full run; empty on any other run (Q36, Q39).
    """

    total: int = 0
    done: int = 0
    failed: int = 0
    warnings: int = 0
    xfailed: int = 0
    cov_percent: float | None = None
    failed_ids: list[str] = field(default_factory=list[str])
    last_started: list[str] = field(default_factory=list[str])
    durations: dict[str, float] = field(default_factory=dict[str, float])


@dataclass(frozen=True)
class RunResult:
    """Outcome of one pytest child run.

    Attributes:
        stats: Counters parsed from the streamed output.
        pytest_exit: Exit code returned by the pytest child process.
        crashed: True when the run died mid-suite (Q06).
        failure_block: The verbatim FAILURES/ERRORS section lines (Q08).
        tail: The last raw output lines, the crash stack context.
        coverage_block: The term-missing table rows, the covg input
            replayed on a coverage gap (Q24).
    """

    stats: RunStats
    pytest_exit: int
    crashed: bool
    failure_block: tuple[str, ...]
    tail: tuple[str, ...]
    coverage_block: tuple[str, ...] = ()


# eof
