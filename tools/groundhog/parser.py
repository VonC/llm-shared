"""Streaming parser for the pytest output of a groundhog child run.

The parent process reads the pytest child output live (Q17) and feeds it
line by line to :class:`PytestOutputParser`, which accumulates the run
statistics: collected count, per-test results and node ids (the ``-v``
format), the warnings summary, the TOTAL coverage line (Q19), the verbatim
FAILURES/ERRORS block (Q08), the most recent test ids and the INTERNALERROR
marker used for crash detection (Q06).
"""

from __future__ import annotations

import re
from collections import deque
from typing import Final

from tools.groundhog.models import RunStats

# How many of the most recent test ids are kept as crash context (Q06).
LAST_STARTED_KEPT: Final = 5
# How many raw output lines are kept as the crash stack tail (Q06).
TAIL_LINES_KEPT: Final = 15

# "collected 250 items" (possibly "collected 1 item").
_COLLECTED_RE: Final = re.compile(r"\bcollected (\d+) items?\b")
# One -v result line: "tests/test_a.py::test_one PASSED [ 10%]".
_RESULT_RE: Final = re.compile(
    r"^(?P<node>\S+::\S+) (?P<status>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b",
)
# The pytest-cov terminal report total: "TOTAL    123    0   97%" (Q19).
_TOTAL_RE: Final = re.compile(r"^TOTAL\s+.*?(\d+(?:\.\d+)?)%\s*$")
# The pytest-cov terminal table header, opening the gap capture (Q24).
_COVERAGE_HEADER_RE: Final = re.compile(r"^Name\s+Stmts\s+Miss\s+Cover")
# A section banner: "==== FAILURES ====".
_BANNER_RE: Final = re.compile(r"^=+ (?P<title>.+?) =+$")
# The final tally line: "== 2 failed, 47 passed, 3 warnings in 1.23s ==".
_SUMMARY_RE: Final = re.compile(r"^=+ .* in \d+(?:\.\d+)?s.* =+$")
# The warnings count inside the final tally line.
_WARNINGS_RE: Final = re.compile(r"(\d+) warnings?\b")
# Section banners that carry failure details, captured verbatim (Q08).
_FAILURE_SECTIONS: Final = ("FAILURES", "ERRORS")
# The pytest internal-error marker, a crash signal (Q06).
_INTERNAL_ERROR_PREFIX: Final = "INTERNALERROR"
# Result statuses counted as a failing test.
_FAILING_STATUSES: Final = ("FAILED", "ERROR")
# Result status counted as an expected failure.
_XFAIL_STATUS: Final = "XFAIL"


class PytestOutputParser:
    """Accumulate run statistics from a pytest output stream."""

    def __init__(self) -> None:
        """Start a parser with empty statistics."""
        self.stats = RunStats()
        self.internal_error = False
        self._failure_lines: list[str] = []
        self._capturing_failures = False
        self._coverage_lines: list[str] = []
        self._capturing_coverage = False
        self._last_started: deque[str] = deque(maxlen=LAST_STARTED_KEPT)
        self._tail: deque[str] = deque(maxlen=TAIL_LINES_KEPT)

    @property
    def failure_block(self) -> tuple[str, ...]:
        """Return the captured FAILURES/ERRORS lines, verbatim (Q08)."""
        return tuple(self._failure_lines)

    @property
    def coverage_block(self) -> tuple[str, ...]:
        """Return the term-missing table rows, the covg input (Q24)."""
        return tuple(self._coverage_lines)

    @property
    def tail(self) -> tuple[str, ...]:
        """Return the most recent raw output lines (Q06)."""
        return tuple(self._tail)

    def feed(self, line: str) -> None:
        """Parse one output line of the pytest child run.

        Args:
            line: The raw line, without its trailing newline.
        """
        if line.strip():
            self._tail.append(line)
        if line.startswith(_INTERNAL_ERROR_PREFIX):
            self.internal_error = True
        self._feed_failure_block(line)
        self._feed_coverage_table(line)
        self._feed_counters(line)

    def _feed_failure_block(self, line: str) -> None:
        """Track the verbatim FAILURES/ERRORS section capture (Q08).

        Args:
            line: The raw line being parsed.
        """
        banner = _BANNER_RE.match(line)
        if banner is not None:
            title = banner.group("title")
            if title in _FAILURE_SECTIONS:
                self._capturing_failures = True
                self._failure_lines.append(line)
                return
            self._capturing_failures = False
            return
        if self._capturing_failures:
            self._failure_lines.append(line)

    def _feed_coverage_table(self, line: str) -> None:
        """Capture the term-missing table, header to TOTAL line (Q24).

        Args:
            line: The raw line being parsed.
        """
        if _COVERAGE_HEADER_RE.match(line):
            self._capturing_coverage = True
            self._coverage_lines = [line]
            return
        if not self._capturing_coverage:
            return
        self._coverage_lines.append(line)
        if _TOTAL_RE.match(line):
            self._capturing_coverage = False

    def _feed_counters(self, line: str) -> None:
        """Update the run statistics from one output line.

        Args:
            line: The raw line being parsed.
        """
        collected = _COLLECTED_RE.search(line)
        if collected is not None:
            self.stats.total = int(collected.group(1))
        result = _RESULT_RE.match(line)
        if result is not None:
            self._record_result(result.group("node"), result.group("status"))
        total = _TOTAL_RE.match(line)
        if total is not None:
            self.stats.cov_percent = float(total.group(1))
        if _SUMMARY_RE.match(line) is not None:
            warned = _WARNINGS_RE.search(line)
            if warned is not None:
                self.stats.warnings = int(warned.group(1))

    def _record_result(self, node: str, status: str) -> None:
        """Record one finished test result.

        Args:
            node: The test node id of the result line.
            status: The pytest result status word.
        """
        self.stats.done += 1
        self._last_started.append(node)
        self.stats.last_started = list(self._last_started)
        if status in _FAILING_STATUSES:
            self.stats.failed += 1
            self.stats.failed_ids.append(node)
        if status == _XFAIL_STATUS:
            self.stats.xfailed += 1


# eof
