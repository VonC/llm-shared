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

Step 1 (v0.8.0): the aggregation moved to ``aggregate.py`` and the rendering to
``render.py``; this module keeps the export, the CSV parse, and the write, and
re-exports the moved names so callers and the ``ghd`` alias are unaffected.

Step 2 (v0.8.0): the command line and the run loop moved to ``cli.py``, which
resolves one or several repo targets and builds one combined dashboard; ``main``
here delegates to it.

Usage
-----
From anywhere inside a project (or, more simply, via the ``ghd`` alias)::

    python <llm-shared>/tools/git_history_dashboard/build.py

Against one or several repositories, writing one combined report::

    python build.py /path/to/repo-a /path/to/repo-b --out-dir /tmp/report

From a pre-exported CSV, skipping the ``git log`` call::

    python build.py --csv git_history.csv

The single-project default output is ``<project>/docs/git_history_dashboard/``;
a multi-project run names its ``--out-dir``. Pass ``--no-open`` to keep the
browser shut. No third-party dependencies are required; the rendered dashboard
pulls Chart.js from cdnjs at view time.
"""

from __future__ import annotations

import contextlib
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if __name__ == "__main__":
    # Running as a script: put the llm-shared root on `sys.path` so the shared
    # `tools` package imports cleanly when build.py is run directly.
    with contextlib.suppress(Exception):
        _llm_shared_root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(_llm_shared_root))

from tools.git_history_dashboard.aggregate import (
    Commit,
    DashboardData,
    Highlights,
    aggregate,
    classify,
    compute_highlights,
)
from tools.git_history_dashboard.render import render

if TYPE_CHECKING:
    from collections.abc import Iterator

LOGGER = logging.getLogger("git_history_dashboard")

# The dashboard output lives under this path inside the calling project.
# ``data.json`` and ``dashboard.html`` are versioned there to record the
# project's commit-history snapshots; ``git_history.csv`` is git-ignored.
DASHBOARD_SUBDIR: tuple[str, ...] = ("docs", "git_history_dashboard")

# Name of the pipe-separated ``git log`` export written next to the dashboard.
GIT_HISTORY_CSV_NAME = "git_history.csv"

# A commit row carries exactly these four pipe-separated fields.
_COMMIT_FIELD_COUNT = 4


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


def iter_commits_from_csv(path: str | Path) -> Iterator[tuple[str, str, str, str]]:
    """Yield raw ``(sha, iso_date, author, subject)`` rows from a CSV export.

    The rows carry no project; ``run_build`` tags each one with the run's
    project as it builds the ``Commit`` records (Step 1.1).
    """
    with Path(path).open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            parts = line.split("|", 3)
            if len(parts) == _COMMIT_FIELD_COUNT:
                yield parts[0], parts[1], parts[2], parts[3]


def write_dashboard(commits: list[Commit], out_dir: Path, template: Path) -> None:
    """Aggregate already-tagged commits and write ``data.json`` + ``dashboard.html``.

    Shared by the single-CSV ``run_build`` and the multi-repo ``cli.run``: it
    aggregates the tagged ``commits`` and writes both files into ``out_dir``.
    """
    LOGGER.info("loaded %d commits", len(commits))
    data = aggregate(commits)

    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "data.json"
    html_path = out_dir / "dashboard.html"

    data_path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    html_path.write_text(render(data, template), encoding="utf-8")

    LOGGER.info("wrote %s", data_path)
    LOGGER.info("wrote %s", html_path)


def run_build(commits_csv: Path, out_dir: Path, template: Path, project: str) -> None:
    """Parse the history CSV, tag each commit with ``project``, write the files.

    Reads ``commits_csv``, tags every parsed row with ``project`` as a
    ``Commit``, and writes the dashboard through ``write_dashboard``.
    """
    commits = [
        Commit(sha, iso_date, author, subject, project)
        for sha, iso_date, author, subject in iter_commits_from_csv(commits_csv)
    ]
    write_dashboard(commits, out_dir, template)


def main() -> None:
    """Entry point: delegate to the multi-repo CLI orchestration in ``cli``.

    The import is local so the module-level import only goes ``cli`` -> ``build``
    (``cli`` reuses these export and write helpers), never back, avoiding a
    circular import.
    """
    from tools.git_history_dashboard import cli  # noqa: PLC0415

    cli.main()


# Re-export the names moved to `aggregate` and `render` in Step 1 so existing
# callers of `build.<name>` (and `from build import ...`) keep working.
__all__ = [
    "Commit",
    "DashboardData",
    "Highlights",
    "aggregate",
    "build_git_log_command",
    "classify",
    "compute_highlights",
    "export_git_history_csv",
    "iter_commits_from_csv",
    "main",
    "render",
    "run_build",
    "write_dashboard",
]


if __name__ == "__main__":
    main()


# eof
