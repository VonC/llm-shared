#!/usr/bin/env python3
"""Analysis files and markdown conversion for git_history_dashboard (Step 3).

Writes a regenerated ``analysis.generated.md`` from the aggregated figures on
every run, keeps one hand-editable ``analysis.notes.<project>.md`` per project
(created once, never overwritten), concatenates the generated file then the
per-project notes in project order, and converts the whole to HTML through a
single ``uv run --with markdown`` seam (``convert_markdown``) that the unit tests
monkeypatch so they need no ``markdown`` install (Q03). ``build.write_dashboard``
injects the resulting HTML into the template's ``__ANALYSIS__`` slot.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from tools.git_history_dashboard.aggregate import compute_highlights

if TYPE_CHECKING:
    from pathlib import Path

    from tools.git_history_dashboard.aggregate import DashboardData

# How many commit types and scopes the generated story names.
_TOP_TYPES_SHOWN = 3
_TOP_SCOPES_SHOWN = 5

# Weekday index (Monday == 0) to name, for the busiest-weekday figure.
_WEEKDAYS = (
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
)

# The stub written into a fresh per-project notes file; never overwrites one.
_NOTES_STUB = (
    "## Notes for {project}\n\n"
    "Hand-written commentary for {project} goes here. This file is created once\n"
    "and is never overwritten by a dashboard rebuild.\n"
)


def _peak_index(series: list[int]) -> tuple[int, int]:
    """Return the ``(index, value)`` of the largest entry of a non-empty series.

    ``by_hour`` and ``by_weekday`` always carry 24 and 7 entries with at least
    one commit, so the series is never empty here.
    """
    idx = max(range(len(series)), key=lambda i: series[i])
    return idx, series[idx]


def _generated_markdown(data: DashboardData) -> str:
    """Build the auto-generated observations as one short markdown story."""
    h = compute_highlights(data)
    type_items = list(data["by_type"].items())[:_TOP_TYPES_SHOWN]
    leaders = ", ".join(f"**{ctype}** ({count:,})" for ctype, count in type_items)
    hour, hour_count = _peak_index(data["by_hour"])
    weekday, weekday_count = _peak_index(data["by_weekday"])
    scopes = ", ".join(f"`{scope}`" for scope in list(data["by_scope"])[:_TOP_SCOPES_SHOWN])
    lines = [
        "## Observations",
        "",
        f"- **{h['total_commits_fmt']} commits** from **{h['start_fmt']}** to "
        f"**{h['end_fmt']}**, active on **{h['active_days_fmt']} of "
        f"{h['total_days_fmt']} days** ({h['active_pct']}%).",
        f"- Commit mix led by {leaders}.",
        f"- Busiest hour **{hour:02d}:00** ({hour_count:,}); "
        f"busiest weekday **{_WEEKDAYS[weekday]}** ({weekday_count:,}).",
        f"- Top scopes: {scopes}." if scopes else "- No scopes recorded.",
        "",
    ]
    return "\n".join(lines)


def write_generated_analysis(data: DashboardData, path: Path) -> Path:
    """Rewrite ``path`` with the figures-driven observations and return it.

    Overwritten on every run so the generated story always reflects the latest
    aggregation; the hand-written per-project notes live in separate files.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_generated_markdown(data), encoding="utf-8")
    return path


def ensure_notes(project: str, directory: Path) -> Path:
    """Return the per-project notes path, creating it once with a stub if absent.

    An existing notes file is left byte-for-byte unchanged (Q06): the rebuild
    never clobbers hand-written commentary.
    """
    path = directory / f"analysis.notes.{project}.md"
    if not path.exists():
        directory.mkdir(parents=True, exist_ok=True)
        path.write_text(_NOTES_STUB.format(project=project), encoding="utf-8")
    return path


def convert_markdown(md: str) -> str:
    """Convert markdown to HTML through ``uv run --with markdown``, the one seam.

    Shelling to ``uv`` keeps the tool itself free of a ``markdown`` dependency;
    the unit tests monkeypatch this function so they need neither ``uv`` nor the
    package (Q03).
    """
    cmd = [
        "uv", "run", "--with", "markdown",
        "python", "-c",
        "import sys, markdown; sys.stdout.write(markdown.markdown(sys.stdin.read()))",
    ]
    # A fixed `uv` invocation feeding the markdown on stdin; no shell is used.
    proc = subprocess.run(  # noqa: S603
        cmd,
        input=md,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    return proc.stdout


def analysis_html(generated_path: Path, notes_paths: list[Path]) -> str:
    """Concatenate the generated file then the notes, and convert to HTML.

    The generated observations come first, then each per-project notes file in
    project order, joined by blank lines and converted through ``convert_markdown``.
    """
    parts = [generated_path.read_text(encoding="utf-8")]
    parts.extend(path.read_text(encoding="utf-8") for path in notes_paths)
    return convert_markdown("\n\n".join(parts))


__all__ = [
    "analysis_html",
    "convert_markdown",
    "ensure_notes",
    "write_generated_analysis",
]


# eof
