#!/usr/bin/env python3
"""Commit aggregation and the dashboard data model for git_history_dashboard.

Step 1 (v0.8.0): extracted verbatim from ``build.py`` so the hub has room to
grow for the multi-project work.

Step 1.1 (v0.8.0): the data gains a project dimension and an author tally.
``Commit`` is now a ``NamedTuple`` with a ``project`` field; ``aggregate`` makes
one pass building a global tally and a per-project tally, then assembles the
``projects`` list, the ``by_project`` map of per-project sub-aggregates (aligned
to the global date span so they sum to the top-level series), the ``by_author``
counts, and a per-row ``project`` tag on ``recent``. Single-project runs put one
entry in ``projects`` and ``by_project``; the real per-repo tagging arrives with
the multi-repo CLI in Step 2.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING, NamedTuple, TypedDict

if TYPE_CHECKING:
    from collections.abc import Iterable

TYPE_RE = re.compile(r"^([a-zA-Z]+)(?:\([^)]*\))?!?:")
SCOPE_RE = re.compile(r"^[a-zA-Z]+\(([^)]+)\)!?:")
KNOWN_TYPES = {
    "feat", "fix", "docs", "test", "refactor",
    "chore", "build", "style", "perf", "ci",
}
TYPES_ORDER = [
    "feat", "fix", "docs", "test", "refactor",
    "chore", "build", "style", "perf", "ci", "other",
]

# Minimum length of an ISO datetime string that still exposes the hour
# at slice ``[11:13]`` (``YYYY-MM-DD HH`` -> 13 characters).
_HOUR_SLICE_MIN_LEN = 13
# UI cap on the recent-commits table.
_RECENT_COMMITS_LIMIT = 10
# How many of the busiest scopes the dashboard keeps.
_TOP_SCOPES = 15


class Commit(NamedTuple):
    """One parsed commit, tagged with the project it was exported from.

    The project carries through the aggregation so the page can break every
    series down per project. A single-repo run tags all commits with that one
    project; the multi-repo CLI (Step 2) tags each repo's commits with its own.
    """

    sha: str
    iso_date: str
    author: str
    subject: str
    project: str


class ProjectData(TypedDict):
    """One project's slice of the dashboard series, aligned to the global span.

    Every list is indexed by the top-level ``dates`` / ``week_starts``, so the
    page sums the selected projects to recompute any widget. ``recent`` is the
    project's own newest rows, not summed.
    """

    totals: list[int]
    by_type_day: dict[str, list[int]]
    by_type: dict[str, int]
    by_scope: dict[str, int]
    by_hour: list[int]
    by_weekday: list[int]
    by_author: dict[str, int]
    week_totals: list[int]
    week_by_type: dict[str, list[int]]
    recent: list[dict[str, str]]


class DashboardData(TypedDict):
    """The aggregated payload serialized to ``data.json`` and the template."""

    total_commits: int
    start: str
    end: str
    types_order: list[str]
    dates: list[str]
    totals: list[int]
    by_type_day: dict[str, list[int]]
    by_type: dict[str, int]
    by_scope: dict[str, int]
    by_hour: list[int]
    by_weekday: list[int]
    by_author: dict[str, int]
    recent: list[dict[str, str]]
    week_starts: list[str]
    week_totals: list[int]
    week_by_type: dict[str, list[int]]
    projects: list[str]
    by_project: dict[str, ProjectData]


class Highlights(TypedDict):
    """The headline numbers shown in the page header and metric cards."""

    total_commits: int
    total_commits_fmt: str
    active_days: int
    active_days_fmt: str
    total_days: int
    total_days_fmt: str
    active_pct: int
    peak_day_count: int
    peak_day_date_fmt: str
    peak_week_count: int
    peak_week_start_fmt: str
    start_fmt: str
    end_fmt: str
    months: int


def classify(msg: str) -> tuple[str, str]:
    """Return ``(type, scope)`` for a conventional-commit subject line."""
    m_type = TYPE_RE.match(msg)
    ctype = m_type.group(1).lower() if m_type else "other"
    if ctype not in KNOWN_TYPES:
        ctype = "other"
    m_scope = SCOPE_RE.match(msg)
    scope = m_scope.group(1).lower() if m_scope else ""
    return ctype, scope


def _build_daily_series(
    per_day: dict[str, dict[str, int]],
    per_day_total: Counter[str],
    start: date,
    end: date,
) -> tuple[list[str], list[int], dict[str, list[int]]]:
    """Build a gap-free daily series between start and end (inclusive).

    Returns ``(dates, totals, by_type_day)`` where every calendar day in
    the span has an entry, so the calendar heatmap renders without holes.
    """
    dates_list: list[str] = []
    totals: list[int] = []
    by_type_day: dict[str, list[int]] = {t: [] for t in TYPES_ORDER}
    cur = start
    while cur <= end:
        iso = cur.isoformat()
        dates_list.append(iso)
        totals.append(per_day_total.get(iso, 0))
        bucket = per_day.get(iso, {})
        for t in TYPES_ORDER:
            by_type_day[t].append(bucket.get(t, 0))
        cur += timedelta(days=1)
    return dates_list, totals, by_type_day


def _aggregate_weeks(
    dates_list: list[str],
    totals: list[int],
    by_type_day: dict[str, list[int]],
) -> list[tuple[str, dict[str, int]]]:
    """Aggregate the daily series into Monday-anchored weekly buckets."""
    weeks: dict[str, dict[str, int]] = {}
    for i, d_iso in enumerate(dates_list):
        dt_obj = date.fromisoformat(d_iso)
        monday = dt_obj - timedelta(days=dt_obj.weekday())
        key = monday.isoformat()
        week_bucket = weeks.setdefault(
            key,
            {"total": 0, **dict.fromkeys(TYPES_ORDER, 0)},
        )
        week_bucket["total"] += totals[i]
        for t in TYPES_ORDER:
            week_bucket[t] += by_type_day[t][i]
    return sorted(weeks.items())


@dataclass
class _CommitTallies:
    """Running per-day/type/scope/hour/weekday/author tallies for ``aggregate``."""

    per_day: dict[str, dict[str, int]]
    per_day_total: Counter[str]
    per_type: Counter[str]
    per_scope: Counter[str]
    per_hour: Counter[int]
    per_weekday: Counter[int]
    per_author: Counter[str]
    recent: list[dict[str, str]]


def _empty_tallies() -> _CommitTallies:
    """Return a fresh, empty set of tallies ready to receive commits."""
    return _CommitTallies(
        per_day={},
        per_day_total=Counter(),
        per_type=Counter(),
        per_scope=Counter(),
        per_hour=Counter(),
        per_weekday=Counter(),
        per_author=Counter(),
        recent=[],
    )


def _parse_commit_clock(dt: str) -> tuple[date, int] | None:
    """Return ``(day, hour)`` for an ISO commit datetime, or None if unparseable."""
    d = dt[:10]
    try:
        y, m, day_int = (int(x) for x in d.split("-"))
        commit_day = date(y, m, day_int)
    except ValueError:
        return None
    has_hour = len(dt) >= _HOUR_SLICE_MIN_LEN and dt[11:13].isdigit()
    hour = int(dt[11:13]) if has_hour else 0
    return commit_day, hour


def _record_commit(commit: Commit, tallies: _CommitTallies) -> bool:
    """Bucket one commit into the tallies; return False on an un-parseable date.

    Args:
        commit: The commit to record.
        tallies: The running tally to update.

    Returns:
        True when the commit was recorded, False when its date would not parse
        (so the caller skips it for the per-project tally too).
    """
    clock = _parse_commit_clock(commit.iso_date)
    if clock is None:
        return False
    commit_day, hour = clock
    d = commit_day.isoformat()
    wd = commit_day.weekday()
    ctype, scope = classify(commit.subject)

    day_bucket = tallies.per_day.setdefault(d, {})
    day_bucket[ctype] = day_bucket.get(ctype, 0) + 1
    tallies.per_day_total[d] += 1
    tallies.per_type[ctype] += 1
    if scope:
        tallies.per_scope[scope] += 1
    tallies.per_hour[hour] += 1
    tallies.per_weekday[wd] += 1
    tallies.per_author[commit.author] += 1
    tallies.recent.append({
        "sha": commit.sha[:7],
        "date": commit.iso_date[:16],
        "type": ctype,
        "scope": scope,
        "msg": commit.subject,
        "project": commit.project,
    })
    return True


def _project_data(tallies: _CommitTallies, start: date, end: date) -> ProjectData:
    """Build one project's slice of the series over the global ``start..end`` span.

    The daily and weekly series run over the same global span as the top-level,
    so summing the projects reproduces each top-level series exactly.
    """
    dates_list, totals, by_type_day = _build_daily_series(
        tallies.per_day, tallies.per_day_total, start, end,
    )
    sorted_weeks = _aggregate_weeks(dates_list, totals, by_type_day)
    return {
        "totals": totals,
        "by_type_day": by_type_day,
        "by_type": dict(tallies.per_type.most_common()),
        "by_scope": dict(tallies.per_scope.most_common(_TOP_SCOPES)),
        "by_hour": [tallies.per_hour.get(h, 0) for h in range(24)],
        "by_weekday": [tallies.per_weekday.get(w, 0) for w in range(7)],
        "by_author": dict(tallies.per_author.most_common()),
        "week_totals": [v["total"] for _, v in sorted_weeks],
        "week_by_type": {t: [v[t] for _, v in sorted_weeks] for t in TYPES_ORDER},
        "recent": tallies.recent[:_RECENT_COMMITS_LIMIT],
    }


def _build_combined_payload(
    projects: list[str],
    global_tally: _CommitTallies,
    per_project: dict[str, _CommitTallies],
) -> DashboardData:
    """Assemble the combined ``DashboardData`` from the global and per-project tallies.

    The top-level series come from the global tally over the full span; the
    per-project slices are aligned to that same span so they sum back to it.
    """
    sorted_days = sorted(global_tally.per_day_total.keys())
    start = date.fromisoformat(sorted_days[0])
    end = date.fromisoformat(sorted_days[-1])
    dates_list, totals, by_type_day = _build_daily_series(
        global_tally.per_day, global_tally.per_day_total, start, end,
    )
    sorted_weeks = _aggregate_weeks(dates_list, totals, by_type_day)
    by_project = {p: _project_data(per_project[p], start, end) for p in projects}
    return {
        "total_commits": int(sum(global_tally.per_day_total.values())),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "types_order": TYPES_ORDER,
        "dates": dates_list,
        "totals": totals,
        "by_type_day": by_type_day,
        "by_type": dict(global_tally.per_type.most_common()),
        "by_scope": dict(global_tally.per_scope.most_common(_TOP_SCOPES)),
        "by_hour": [global_tally.per_hour.get(h, 0) for h in range(24)],
        "by_weekday": [global_tally.per_weekday.get(w, 0) for w in range(7)],
        "by_author": dict(global_tally.per_author.most_common()),
        "recent": global_tally.recent[:_RECENT_COMMITS_LIMIT],
        "week_starts": [k for k, _ in sorted_weeks],
        "week_totals": [v["total"] for _, v in sorted_weeks],
        "week_by_type": {t: [v[t] for _, v in sorted_weeks] for t in TYPES_ORDER},
        "projects": projects,
        "by_project": by_project,
    }


def aggregate(commits: Iterable[Commit]) -> DashboardData:
    """Aggregate an iterable of tagged commits into the combined dashboard payload.

    One pass fills a global tally and a per-project tally; a commit whose date
    will not parse is skipped in both. An empty history is a hard stop.
    """
    global_tally = _empty_tallies()
    per_project: dict[str, _CommitTallies] = {}
    order: list[str] = []
    for commit in commits:
        if not _record_commit(commit, global_tally):
            continue
        if commit.project not in per_project:
            per_project[commit.project] = _empty_tallies()
            order.append(commit.project)
        _record_commit(commit, per_project[commit.project])
    if not global_tally.per_day_total:
        message = "No commits found."
        raise SystemExit(message)
    return _build_combined_payload(sorted(order), global_tally, per_project)


def compute_highlights(data: DashboardData) -> Highlights:
    """Compute headline numbers shown in the page header and metric cards."""
    totals = data["totals"]
    active_days = sum(1 for t in totals if t > 0)
    peak_idx = max(range(len(totals)), key=lambda i: totals[i])
    peak_day_date = data["dates"][peak_idx]
    peak_day_count = totals[peak_idx]

    week_totals = data["week_totals"]
    peak_week_idx = max(range(len(week_totals)), key=lambda i: week_totals[i])
    peak_week_start = data["week_starts"][peak_week_idx]
    peak_week_count = week_totals[peak_week_idx]

    def fmt_date(iso: str) -> str:
        d = date.fromisoformat(iso)
        return d.strftime("%-d %b %Y") if sys.platform != "win32" else d.strftime("%#d %b %Y")

    def fmt_date_short(iso: str) -> str:
        d = date.fromisoformat(iso)
        return d.strftime("%-d %b %Y") if sys.platform != "win32" else d.strftime("%#d %b %Y")

    start_d = date.fromisoformat(data["start"])
    end_d = date.fromisoformat(data["end"])
    span_days = (end_d - start_d).days + 1
    # Approximate span in months for the metric subtitle.
    months = max(1, round(span_days / 30.4375))

    return {
        "total_commits": data["total_commits"],
        "total_commits_fmt": f"{data['total_commits']:,}",
        "active_days": active_days,
        "active_days_fmt": f"{active_days:,}",
        "total_days": span_days,
        "total_days_fmt": f"{span_days:,}",
        "active_pct": round(100 * active_days / span_days),
        "peak_day_count": peak_day_count,
        "peak_day_date_fmt": fmt_date_short(peak_day_date),
        "peak_week_count": peak_week_count,
        "peak_week_start_fmt": fmt_date_short(peak_week_start),
        "start_fmt": fmt_date(data["start"]),
        "end_fmt": fmt_date(data["end"]),
        "months": months,
    }


__all__ = [
    "Commit",
    "DashboardData",
    "Highlights",
    "ProjectData",
    "aggregate",
    "classify",
    "compute_highlights",
]


# eof
