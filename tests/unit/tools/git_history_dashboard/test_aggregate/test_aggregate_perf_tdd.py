"""Perf gate for the combined multi-repo git-history aggregation.

Step 0 (v0.8.0): a linear-time guard for the combined aggregation the
git_history_dashboard tool will gain in Step 1.1. The combined aggregation
module (``tools.git_history_dashboard.aggregate``) does not exist yet, so it is
imported dynamically with ``importlib`` behind a guard: the static type-checkers
never resolve the not-yet-existing module, and the gate is marked ``xfail``
(non-strict) until then. It fails now on the missing module, xpasses once
``aggregate.py`` lands in Step 1, and the ``xfail`` marker is removed in
Step 1.1.

The ``@pytest.mark.timeout`` bound is the guard itself: once the aggregation
exists, a future ``O(n^2)`` regression in the per-project breakdown over the
synthetic many-commit fixture trips the timeout.
"""

from __future__ import annotations

import datetime
import importlib
from typing import Any

import pytest

# The combined aggregation module lands in Step 1; import it dynamically so the
# static type-checkers do not try to resolve a not-yet-existing module, and
# guard the call so Step 0 collection never errors. Until the module exists the
# handle is None, so the gate xfails on the assert below.
_aggregate: Any
try:
    _aggregate = importlib.import_module("tools.git_history_dashboard.aggregate")
except ImportError:
    _aggregate = None

# Many commits so a quadratic aggregation would blow the timeout, yet a linear
# pass stays in milliseconds. Step 1.1 re-tags these per project once the
# Commit record carries a project field.
PERF_COMMIT_COUNT = 6000
# A generous wall-clock bound: linear aggregation finishes far inside it.
PERF_TIMEOUT_SECONDS = 8
# The synthetic commits fan out across a year so the daily/weekly series stay
# dense rather than collapsing onto a single day.
PERF_SPAN_DAYS = 365

_BASE_DAY = datetime.date(2026, 6, 1)
_TYPES = ("feat", "fix", "docs", "test", "refactor", "chore")
_SCOPES = ("cli", "io", "core", "web", "domain")
_AUTHORS = ("Ann Dev", "Bob Dev", "Cy Dev", "Di Dev")


def _synthetic_commits(count: int) -> list[tuple[str, str, str, str]]:
    """Return ``count`` synthetic commit tuples, newest first, over a year.

    Each tuple matches the current ``(sha, iso_date, author, subject)`` shape
    the aggregation consumes. The commits cycle through conventional types,
    scopes, and authors and spread across ``PERF_SPAN_DAYS`` so the aggregation
    does real per-day and per-week work. Step 1.1 tags these per project once
    the ``Commit`` record gains a project field.

    Args:
        count: How many commit tuples to generate.

    Returns:
        A newest-first list of ``count`` commit tuples.
    """
    commits: list[tuple[str, str, str, str]] = []
    for i in range(count):
        day = _BASE_DAY - datetime.timedelta(days=i % PERF_SPAN_DAYS)
        hour = i % 24
        iso_date = f"{day.isoformat()} {hour:02d}:00:00 +0000"
        sha = f"{i:040x}"
        author = _AUTHORS[i % len(_AUTHORS)]
        ctype = _TYPES[i % len(_TYPES)]
        scope = _SCOPES[i % len(_SCOPES)]
        subject = f"{ctype}({scope}): synthetic commit {i}"
        commits.append((sha, iso_date, author, subject))
    return commits


class TestCombinedAggregationPerf:
    """Linear-time guard for the combined multi-repo aggregation (Step 0).

    The combined aggregation module lands in Step 1.1; until then this gate
    xfails on the missing ``aggregate`` module. The timeout makes a future
    ``O(n^2)`` regression in the per-project breakdown trip the gate.
    """

    @pytest.mark.timeout(PERF_TIMEOUT_SECONDS)
    @pytest.mark.xfail(
        reason="combined aggregation lands in Step 1.1",
        strict=False,
    )
    def test_combined_aggregation_stays_linear(self) -> None:
        """Aggregating many commits returns within the timeout bound."""
        # Fails (xfail) until Step 1 creates the aggregation module.
        assert _aggregate is not None
        commits = _synthetic_commits(PERF_COMMIT_COUNT)

        payload = _aggregate.aggregate(commits)

        assert payload["total_commits"] == PERF_COMMIT_COUNT


# eof
