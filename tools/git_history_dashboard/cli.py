#!/usr/bin/env python3
"""Multi-repo orchestration for the git_history_dashboard report (Step 2).

Resolves the run's targets (none means the current project, one means that repo,
several mean a combined run that must name its ``--out-dir``), exports and tags
each repo's commits with its project, builds one combined dashboard, opens it in
the browser unless suppressed, logs a per-repo skip on a failing export, and
returns a run summary. ``build.py`` keeps the export, parse and write building
blocks and delegates its ``main`` here; this module imports those blocks, so the
import only goes cli -> build, never back.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools import find_project_root
from tools.git_history_dashboard import build
from tools.git_history_dashboard.aggregate import Commit

if TYPE_CHECKING:
    from collections.abc import Sequence

LOGGER = logging.getLogger("git_history_dashboard")

# The bundled HTML template, alongside this module in the package directory.
_DEFAULT_TEMPLATE = Path(__file__).resolve().parent / "template.html"


@dataclass(frozen=True)
class Targets:
    """The resolved targets of one report run.

    Attributes:
        repos: The repos to export from, empty when a pre-exported CSV is used.
        out_dir: The folder the combined ``dashboard.html`` and ``data.json``
            are written to.
        csv: A pre-exported pipe-separated CSV, or None for the git-export path.
        csv_project: The project label for the CSV path (the calling project).
    """

    repos: list[Path]
    out_dir: Path
    csv: Path | None
    csv_project: str


@dataclass(frozen=True)
class RunSummary:
    """What one run did, for the printed summary and for the tests.

    Attributes:
        projects: The projects whose commits were aggregated, in run order.
        skipped: The projects whose export failed and were skipped.
        out_dir: The folder the report was written to.
        commit_count: How many commits were aggregated in total.
    """

    projects: list[str]
    skipped: list[str]
    out_dir: Path
    commit_count: int


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the command line for the multi-repo report run."""
    parser = argparse.ArgumentParser(
        prog="git-history-report",
        description="Build a combined git-history dashboard for one or several projects.",
    )
    parser.add_argument(
        "repos",
        nargs="*",
        help="Repo paths to include (default: the current project).",
    )
    parser.add_argument(
        "--csv",
        help="Build from a pre-exported pipe-separated CSV (single project).",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output folder (required for a multi-project run).",
    )
    parser.add_argument(
        "--template",
        default=str(_DEFAULT_TEMPLATE),
        help="Path to the HTML template (default: alongside the tool).",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the dashboard in the browser (for scripts and CI).",
    )
    return parser.parse_args(argv)


def resolve_targets(args: argparse.Namespace) -> Targets:
    """Return the run's targets, raising on a multi-project run with no out-dir.

    None given resolves to the current project; one path keeps that repo's
    default output folder; several paths require an explicit ``--out-dir`` so the
    combined report does not land inside one repo.

    Args:
        args: The parsed command line.

    Returns:
        The resolved ``Targets``.

    Raises:
        SystemExit: When more than one repo is given without ``--out-dir``.
    """
    project_root = find_project_root(Path.cwd())
    out_dir_arg = Path(args.out_dir).expanduser().resolve() if args.out_dir else None
    if args.csv:
        out_dir = out_dir_arg or project_root.joinpath(*build.DASHBOARD_SUBDIR)
        return Targets(
            repos=[],
            out_dir=out_dir,
            csv=Path(args.csv).expanduser().resolve(),
            csv_project=project_root.name,
        )
    repos = [Path(repo).expanduser().resolve() for repo in args.repos] or [project_root]
    if len(repos) > 1 and out_dir_arg is None:
        message = "Pass --out-dir to name the output folder for a multi-project run."
        raise SystemExit(message)
    out_dir = out_dir_arg or repos[0].joinpath(*build.DASHBOARD_SUBDIR)
    return Targets(repos=repos, out_dir=out_dir, csv=None, csv_project="")


def _csv_commits(csv_path: Path, project: str) -> list[Commit]:
    """Return the commits parsed from a pre-exported CSV, tagged with `project`."""
    return [
        Commit(sha, iso_date, author, subject, project)
        for sha, iso_date, author, subject in build.iter_commits_from_csv(csv_path)
    ]


def _export_repo_commits(repo: Path, scratch_csv: Path) -> list[Commit]:
    """Export `repo`'s history to `scratch_csv` and return its tagged commits."""
    build.export_git_history_csv(repo, scratch_csv)
    return [
        Commit(sha, iso_date, author, subject, repo.name)
        for sha, iso_date, author, subject in build.iter_commits_from_csv(scratch_csv)
    ]


def open_in_browser(html_path: Path, *, suppressed: bool) -> None:
    """Open the report in the default browser unless suppressed (the v0.7.0 lesson).

    Args:
        html_path: The rendered ``dashboard.html`` to open.
        suppressed: When True (``--no-open``), only log the path so a script or
            CI run never blocks on a browser, as the activity-report work found
            on Windows.
    """
    if suppressed:
        LOGGER.info("not opening the browser (--no-open); report at %s", html_path)
        return
    webbrowser.open(html_path.as_uri())


def _log_summary(summary: RunSummary) -> None:
    """Log the actions one run took."""
    LOGGER.info("--- run summary ---")
    LOGGER.info("projects: %s", ", ".join(summary.projects) if summary.projects else "(none)")
    if summary.skipped:
        LOGGER.info("skipped: %s", ", ".join(summary.skipped))
    LOGGER.info("commits: %d", summary.commit_count)
    LOGGER.info("output: %s", summary.out_dir)


def run(args: argparse.Namespace) -> RunSummary:
    """Resolve targets, build the combined report, open it, and return the summary.

    A per-repo export that fails is logged and skipped so one bad repo does not
    sink the whole run; the projects that did aggregate, the skips, the output
    folder and the commit count are returned and logged.
    """
    targets = resolve_targets(args)
    template = Path(args.template)
    commits: list[Commit] = []
    processed: list[str] = []
    skipped: list[str] = []
    if targets.csv is not None:
        commits = _csv_commits(targets.csv, targets.csv_project)
        processed.append(targets.csv_project)
    else:
        scratch = targets.out_dir / build.GIT_HISTORY_CSV_NAME
        for repo in targets.repos:
            try:
                commits.extend(_export_repo_commits(repo, scratch))
            except (subprocess.CalledProcessError, OSError) as err:
                # A skipped repo is expected (a bad path or a non-git folder);
                # log the reason as a one-liner, not a full traceback.
                LOGGER.error("skipping project %s: %s", repo.name, err)  # noqa: TRY400
                skipped.append(repo.name)
                continue
            processed.append(repo.name)
    build.write_dashboard(commits, targets.out_dir, template)
    open_in_browser(targets.out_dir / "dashboard.html", suppressed=args.no_open)
    summary = RunSummary(
        projects=processed,
        skipped=skipped,
        out_dir=targets.out_dir,
        commit_count=len(commits),
    )
    _log_summary(summary)
    return summary


def main(argv: Sequence[str] | None = None) -> None:
    """Configure logging, parse the command line, and run the report."""
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    run(_parse_args(argv))


__all__ = [
    "RunSummary",
    "Targets",
    "main",
    "open_in_browser",
    "resolve_targets",
    "run",
]


# eof
