"""Perf gate for the combined multi-repo git-history aggregation.

Step 0 (v0.8.0): added as an ``xfail`` gate before the aggregation existed, so
it failed on the missing module until the code landed.

Step 1.1 (v0.8.0): the combined aggregation with the per-project breakdown
landed, so the gate runs for real and the ``xfail`` is removed. Aggregating many
commits spread across several projects must finish within the timeout, guarding
the per-project breakdown against an ``O(n^2)`` regression.
"""

from __future__ import annotations

import datetime

import pytest

from tools.git_history_dashboard import aggregate

# Many commits so a quadratic aggregation would blow the timeout, yet a linear
# pass stays in milliseconds.
PERF_COMMIT_COUNT = 3000
# How many projects the synthetic commits fan out across.
PERF_PROJECT_COUNT = 5
# A generous wall-clock bound: linear aggregation finishes far inside it.
PERF_TIMEOUT_SECONDS = 8
# The synthetic commits spread across a year so the daily/weekly series stay
# dense rather than collapsing onto a single day.
PERF_SPAN_DAYS = 365

_BASE_DAY = datetime.date(2026, 6, 1)
_TYPES = ("feat", "fix", "docs", "test", "refactor", "chore")
_SCOPES = ("cli", "io", "core", "web", "domain")
_AUTHORS = ("Ann Dev", "Bob Dev", "Cy Dev", "Di Dev")
_PROJECTS = tuple(f"project-{i}" for i in range(PERF_PROJECT_COUNT))


def _synthetic_commits(count: int) -> list[aggregate.Commit]:
    """Return ``count`` synthetic ``Commit`` records over a year and several projects.

    The commits cycle through conventional types, scopes, authors and projects
    and spread across ``PERF_SPAN_DAYS`` so the aggregation does real per-day,
    per-week and per-project work.

    Args:
        count: How many commit records to generate.

    Returns:
        A newest-first list of ``count`` tagged ``Commit`` records.
    """
    commits: list[aggregate.Commit] = []
    for i in range(count):
        day = _BASE_DAY - datetime.timedelta(days=i % PERF_SPAN_DAYS)
        hour = i % 24
        iso_date = f"{day.isoformat()} {hour:02d}:00:00 +0000"
        sha = f"{i:040x}"
        author = _AUTHORS[i % len(_AUTHORS)]
        ctype = _TYPES[i % len(_TYPES)]
        scope = _SCOPES[i % len(_SCOPES)]
        subject = f"{ctype}({scope}): synthetic commit {i}"
        project = _PROJECTS[i % PERF_PROJECT_COUNT]
        commits.append(aggregate.Commit(sha, iso_date, author, subject, project))
    return commits


class TestCombinedAggregationPerf:
    """Linear-time guard for the combined multi-project aggregation."""

    @pytest.mark.timeout(PERF_TIMEOUT_SECONDS)
    def test_combined_aggregation_stays_linear(self) -> None:
        """Aggregating many commits across projects returns within the timeout."""
        commits = _synthetic_commits(PERF_COMMIT_COUNT)

        payload = aggregate.aggregate(commits)

        assert payload["total_commits"] == PERF_COMMIT_COUNT
        assert len(payload["projects"]) == PERF_PROJECT_COUNT


# eof
