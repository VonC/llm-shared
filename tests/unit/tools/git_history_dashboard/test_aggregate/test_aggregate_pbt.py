"""Property test for the git-history dashboard per-project breakdown.

Step 1.1 (v0.8.0): the page recomputes a filtered view by summing the
``by_project`` slices of the visible projects, so the invariant that must always
hold is that, for every additive series, the per-project slices sum back to the
top-level series. This drives random tagged-commit lists through ``aggregate``
and checks that invariant for the list series (``totals``, ``by_hour``,
``by_weekday``, ``week_totals``) and the mapping series (``by_author``,
``by_type``), split into two tests to keep each one simple.
"""

from __future__ import annotations

import datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.git_history_dashboard import aggregate

_PROJECTS = ("alpha", "beta", "gamma")
_AUTHORS = ("Ann", "Bob", "Cy")
_TYPES = ("feat", "fix", "docs", "chore")
_SCOPES = ("cli", "io", "")
_BASE_DAY = datetime.date(2026, 1, 1)
_MAX_DAY_OFFSET = 120
_HOURS_IN_DAY = 24
_DAYS_IN_WEEK = 7


def _commit(encoded: bytes) -> aggregate.Commit:
    """Decode every supported field combination from one compact generated record."""
    offset = int.from_bytes(encoded[:2]) % (_MAX_DAY_OFFSET + 1)
    hour = encoded[2] % _HOURS_IN_DAY
    day = _BASE_DAY + datetime.timedelta(days=offset)
    iso_date = f"{day.isoformat()} {hour:02d}:00:00 +0000"
    index = int.from_bytes(encoded[3:6]) % 1_000_000
    author = _AUTHORS[encoded[6] % len(_AUTHORS)]
    ctype = _TYPES[encoded[7] % len(_TYPES)]
    scope = _SCOPES[encoded[8] % len(_SCOPES)]
    subject = f"{ctype}({scope}): change {index}" if scope else f"{ctype}: change {index}"
    project = _PROJECTS[encoded[9] % len(_PROJECTS)]
    return aggregate.Commit(str(index), iso_date, author, subject, project)


def _sum_columns(columns: list[list[int]], length: int) -> list[int]:
    """Return the element-wise sum of several equal-length integer series."""
    out = [0] * length
    for column in columns:
        for i, value in enumerate(column):
            out[i] += value
    return out


def _sum_maps(maps: list[dict[str, int]]) -> dict[str, int]:
    """Return the key-wise sum of several integer mappings."""
    out: dict[str, int] = {}
    for mapping in maps:
        for name, value in mapping.items():
            out[name] = out.get(name, 0) + value
    return out


@pytest.mark.parametrize("_batch", range(5))
@settings(max_examples=2, deadline=None)
@given(st.lists(st.binary(min_size=10, max_size=10).map(_commit), min_size=1, max_size=10))
def test_per_project_list_series_sum_to_top_level(_batch: int, commits: list[aggregate.Commit]) -> None:
    """The per-project list series sum back to the top-level list series."""
    data = aggregate.aggregate(commits)
    slices = list(data["by_project"].values())

    assert _sum_columns([s["totals"] for s in slices], len(data["totals"])) == data["totals"]
    assert _sum_columns([s["by_hour"] for s in slices], _HOURS_IN_DAY) == data["by_hour"]
    assert _sum_columns([s["by_weekday"] for s in slices], _DAYS_IN_WEEK) == data["by_weekday"]
    assert (
        _sum_columns([s["week_totals"] for s in slices], len(data["week_totals"]))
        == data["week_totals"]
    )


@pytest.mark.parametrize("_batch", range(5))
@settings(max_examples=2, deadline=None)
@given(st.lists(st.binary(min_size=10, max_size=10).map(_commit), min_size=1, max_size=10))
def test_per_project_count_series_sum_to_top_level(_batch: int, commits: list[aggregate.Commit]) -> None:
    """The per-project mapping series sum back to the top-level mapping series."""
    data = aggregate.aggregate(commits)
    slices = list(data["by_project"].values())

    assert _sum_maps([s["by_author"] for s in slices]) == data["by_author"]
    assert _sum_maps([s["by_type"] for s in slices]) == data["by_type"]


# eof
