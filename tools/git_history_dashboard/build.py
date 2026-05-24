#!/usr/bin/env python3
"""Build the git-history dashboard for the calling project.

Exports the commit history with ``git log``, aggregates it by day / week
/ type / scope / weekday / hour, and renders a standalone
``dashboard.html`` alongside the raw ``data.json``.

This tool ships in ``llm-shared`` but always operates on the *calling*
project: it resolves that project's root through the shared
``find_project_root`` helper, which prefers the ``PRJ_DIR`` environment
variable each project's ``senv.bat`` exports. By default it runs the
documented one-liner::

    git log --all --pretty=format:'%H|%ai|%an|%s' --date-order > git_history.csv

writing ``git_history.csv`` into ``<project>/docs/git_history_dashboard/``,
then parses that file. The CSV is a scratch artifact and is git-ignored;
the rendered ``dashboard.html`` and ``data.json`` are versioned in the
calling project so its commit-history snapshots are recorded over time.

Usage
-----
From anywhere inside a project (or, more simply, via the ``ghd`` alias)::

    python <llm-shared>/tools/git_history_dashboard/build.py

Against a different repository::

    python build.py --git-dir /path/to/repo

From a pre-exported CSV, skipping the ``git log`` call::

    python build.py --csv git_history.csv

The dashboard files default to ``<project>/docs/git_history_dashboard/``;
pass ``--out-dir`` to redirect them. No third-party dependencies are
required; the rendered dashboard pulls Chart.js from cdnjs at view time.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import logging
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

if __name__ == "__main__":
    # Running as a script: put the llm-shared root on `sys.path` so the
    # shared `tools` package (and `find_project_root`) imports cleanly.
    with contextlib.suppress(Exception):
        _llm_shared_root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(_llm_shared_root))

from tools import find_project_root

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

HERE = Path(__file__).resolve().parent
LOGGER = logging.getLogger("git_history_dashboard")

# The dashboard output lives under this path inside the calling project.
# ``data.json`` and ``dashboard.html`` are versioned there to record the
# project's commit-history snapshots; ``git_history.csv`` is git-ignored.
DASHBOARD_SUBDIR: tuple[str, ...] = ("docs", "git_history_dashboard")

# Name of the pipe-separated ``git log`` export written next to the dashboard.
GIT_HISTORY_CSV_NAME = "git_history.csv"

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

# A parsed commit row: (sha, iso_date, author, subject).
type Commit = tuple[str, str, str, str]

# A commit row carries exactly these four pipe-separated fields.
_COMMIT_FIELD_COUNT = 4
# Minimum length of an ISO datetime string that still exposes the hour
# at slice ``[11:13]`` (``YYYY-MM-DD HH`` -> 13 characters).
_HOUR_SLICE_MIN_LEN = 13
# UI cap on the recent-commits table.
_RECENT_COMMITS_LIMIT = 10


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
    recent: list[dict[str, str]]
    week_starts: list[str]
    week_totals: list[int]
    week_by_type: dict[str, list[int]]


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


def build_git_log_command(repo_dir: Path) -> list[str]:
    """Return the ``git log`` argv that exports the pipe-separated history.

    Mirrors the documented one-liner
    ``git log --all --pretty=format:'%H|%ai|%an|%s' --date-order``.
    ``--date-order`` keeps the result stable and independent of the
    topological merge order.
    """
    return [
        "git",
        "-C",
        str(repo_dir),
        "log",
        "--all",
        "--pretty=format:%H|%ai|%an|%s",
        "--date-order",
    ]


def export_git_history_csv(repo_dir: Path, csv_path: Path) -> Path:
    """Run ``git log`` against ``repo_dir`` and write the history CSV.

    The fields are pipe-separated (``sha|iso_date|author|subject``).
    Only the first three pipes delimit fields, so a ``|`` inside a commit
    subject -- the trailing field -- is preserved on read. Returns the
    path that was written.
    """
    cmd = build_git_log_command(repo_dir)
    # A fixed `git log` invocation with a caller-supplied repository path
    # only; no shell is used.
    proc = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    # `git log --pretty=format:` omits the trailing newline; add one so
    # the file is a well-formed line-per-commit CSV.
    text = proc.stdout
    if text and not text.endswith("\n"):
        text += "\n"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.write_text(text, encoding="utf-8")
    return csv_path


def iter_commits_from_csv(path: str | Path) -> Iterator[Commit]:
    """Yield commit tuples from a pipe-separated CSV export."""
    with Path(path).open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            parts = line.split("|", 3)
            if len(parts) == _COMMIT_FIELD_COUNT:
                yield parts[0], parts[1], parts[2], parts[3]


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
    """Running per-day/type/scope/hour/weekday tallies for ``aggregate``."""

    per_day: dict[str, dict[str, int]]
    per_day_total: Counter[str]
    per_type: Counter[str]
    per_scope: Counter[str]
    per_hour: Counter[int]
    per_weekday: Counter[int]
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


def _record_commit(commit: Commit, tallies: _CommitTallies) -> None:
    """Bucket one commit into the running tallies; skip un-parseable dates."""
    sha, dt, _author, msg = commit
    clock = _parse_commit_clock(dt)
    if clock is None:
        return
    commit_day, hour = clock
    d = commit_day.isoformat()
    wd = commit_day.weekday()
    ctype, scope = classify(msg)

    day_bucket = tallies.per_day.setdefault(d, {})
    day_bucket[ctype] = day_bucket.get(ctype, 0) + 1
    tallies.per_day_total[d] += 1
    tallies.per_type[ctype] += 1
    if scope:
        tallies.per_scope[scope] += 1
    tallies.per_hour[hour] += 1
    tallies.per_weekday[wd] += 1
    tallies.recent.append({
        "sha": sha[:7],
        "date": dt[:16],
        "type": ctype,
        "scope": scope,
        "msg": msg,
    })


def _build_dashboard_payload(tallies: _CommitTallies) -> DashboardData:
    """Assemble the final ``DashboardData`` payload from a filled tally."""
    # Build a contiguous daily series so the calendar heatmap has no gaps.
    sorted_days = sorted(tallies.per_day_total.keys())
    start = date.fromisoformat(sorted_days[0])
    end = date.fromisoformat(sorted_days[-1])
    dates_list, totals, by_type_day = _build_daily_series(
        tallies.per_day, tallies.per_day_total, start, end,
    )

    # Weekly aggregation (Monday-anchored).
    sorted_weeks = _aggregate_weeks(dates_list, totals, by_type_day)

    # Recent commits are most-recent-first; ``git log --date-order`` emits
    # newest first, so the head of `recent` is already what we want.
    # Trim to a sensible UI cap.
    recent = tallies.recent[:_RECENT_COMMITS_LIMIT]
    return {
        "total_commits": int(sum(tallies.per_day_total.values())),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "types_order": TYPES_ORDER,
        "dates": dates_list,
        "totals": totals,
        "by_type_day": by_type_day,
        "by_type": dict(tallies.per_type.most_common()),
        "by_scope": dict(tallies.per_scope.most_common(15)),
        "by_hour": [tallies.per_hour.get(h, 0) for h in range(24)],
        "by_weekday": [tallies.per_weekday.get(w, 0) for w in range(7)],
        "recent": recent,
        "week_starts": [k for k, _ in sorted_weeks],
        "week_totals": [v["total"] for _, v in sorted_weeks],
        "week_by_type": {t: [v[t] for _, v in sorted_weeks] for t in TYPES_ORDER},
    }


def aggregate(commits: Iterable[Commit]) -> DashboardData:
    """Aggregate an iterable of commit tuples into the dashboard payload."""
    tallies = _empty_tallies()
    for commit in commits:
        _record_commit(commit, tallies)
    if not tallies.per_day_total:
        message = "No commits found."
        raise SystemExit(message)
    return _build_dashboard_payload(tallies)


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


def render(data: DashboardData, template_path: Path) -> str:
    """Substitute aggregated data + highlights into the HTML template."""
    template = template_path.read_text(encoding="utf-8")
    h = compute_highlights(data)
    payload = json.dumps(data, separators=(",", ":"))
    replacements: dict[str, str] = {
        "__DATA__": payload,
        "__TOTAL_COMMITS__": h["total_commits_fmt"],
        "__START__": h["start_fmt"],
        "__END__": h["end_fmt"],
        "__MONTHS__": str(h["months"]),
        "__ACTIVE_DAYS__": h["active_days_fmt"],
        "__TOTAL_DAYS__": h["total_days_fmt"],
        "__ACTIVE_PCT__": f"{h['active_pct']}%",
        "__PEAK_DAY_COUNT__": str(h["peak_day_count"]),
        "__PEAK_DAY_DATE__": h["peak_day_date_fmt"],
        "__PEAK_WEEK_COUNT__": str(h["peak_week_count"]),
        "__PEAK_WEEK_START__": h["peak_week_start_fmt"],
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def run_build(commits_csv: Path, out_dir: Path, template: Path) -> None:
    """Parse the history CSV, aggregate it, and write the dashboard files.

    Reads ``commits_csv``, aggregates the commits, and writes
    ``data.json`` and ``dashboard.html`` into ``out_dir``.
    """
    commits = list(iter_commits_from_csv(commits_csv))
    LOGGER.info("loaded %d commits", len(commits))
    data = aggregate(commits)

    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "data.json"
    html_path = out_dir / "dashboard.html"

    data_path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    html_path.write_text(render(data, template), encoding="utf-8")

    LOGGER.info("wrote %s", data_path)
    LOGGER.info("wrote %s", html_path)


def _parse_args() -> argparse.Namespace:
    """Parse the command-line arguments for the dashboard builder."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument(
        "--git-dir",
        help="Repo to export history from (default: the calling project root).",
    )
    src.add_argument(
        "--csv",
        help="Use a pre-exported pipe-separated CSV instead of running git log.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help=(
            "Directory for dashboard.html and data.json "
            "(default: <project>/docs/git_history_dashboard)."
        ),
    )
    parser.add_argument(
        "--template",
        default=str(HERE / "template.html"),
        help="Path to the HTML template (default: alongside this script).",
    )
    return parser.parse_args()


def main() -> None:
    """Export the calling project's git history and write the dashboard."""
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

    args = _parse_args()
    project_root = find_project_root(Path.cwd())
    dashboard_dir = project_root.joinpath(*DASHBOARD_SUBDIR)
    out_dir = Path(args.out_dir) if args.out_dir else dashboard_dir

    if args.csv:
        commits_csv = Path(args.csv).expanduser().resolve()
    else:
        repo_dir = Path(args.git_dir).expanduser().resolve() if args.git_dir else project_root
        commits_csv = dashboard_dir / GIT_HISTORY_CSV_NAME
        LOGGER.info("exporting git history from %s", repo_dir)
        export_git_history_csv(repo_dir, commits_csv)
        LOGGER.info("wrote %s", commits_csv)

    run_build(commits_csv, out_dir, Path(args.template))


if __name__ == "__main__":
    main()


# eof
