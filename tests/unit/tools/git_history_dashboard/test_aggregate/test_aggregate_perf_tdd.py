"""Count aggregation work instead of waiting for a quadratic runtime timeout.

Different input sizes span the same year and five projects. Each commit can
enter at most two tallies (global and project), and the input is scanned once.
The real aggregation and output assertions remain inside the measured test.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest

from tools.git_history_dashboard import aggregate

if TYPE_CHECKING:
    from collections.abc import Iterator

# How many projects the synthetic commits fan out across.
PERF_PROJECT_COUNT = 5
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
        day = _BASE_DAY - datetime.timedelta(days=i * (PERF_SPAN_DAYS - 1) // (count - 1))
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


@pytest.mark.parametrize("count", [10, 50, 100])
def test_combined_aggregation_stays_linear(count: int, monkeypatch: pytest.MonkeyPatch) -> None:
    """Increasing history size requires one scan and at most two tally updates."""
    commits = _synthetic_commits(count)
    record = aggregate._record_commit  # noqa: SLF001 - count work without replacing behavior
    updates = 0
    reads = 0

    def counted_record(commit: aggregate.Commit, tallies: aggregate._CommitTallies) -> bool:  # noqa: SLF001
        nonlocal updates
        updates += 1
        return record(commit, tallies)

    class History:
        """Count input visits while permitting multiple iterations to be detected."""

        def __iter__(self) -> Iterator[aggregate.Commit]:
            nonlocal reads
            for commit in commits:
                reads += 1
                yield commit

    monkeypatch.setattr(aggregate, "_record_commit", counted_record)
    payload = aggregate.aggregate(History())
    assert payload["total_commits"] == count
    assert len(payload["projects"]) == PERF_PROJECT_COUNT
    assert len(payload["dates"]) == PERF_SPAN_DAYS
    assert reads == count
    assert updates <= 2 * count


# eof
