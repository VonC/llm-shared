#!/usr/bin/env python3
"""HTML template rendering for git_history_dashboard.

Step 1 (v0.8.0): extracted verbatim from ``build.py``. ``render`` substitutes
the aggregated payload and the headline numbers into the placeholder tokens of
``template.html``. ``compute_highlights`` is imported from the sibling
``aggregate`` module.

Step 3 (v0.8.0): two project-neutral slots join the table. ``__TITLE__`` names
the project (or the project count for a combined run), and ``__ANALYSIS__``
carries the analysis HTML the caller builds; the template's hardcoded
pdfsplitter strings and inline observations are gone.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tools.git_history_dashboard.aggregate import compute_highlights

if TYPE_CHECKING:
    from pathlib import Path

    from tools.git_history_dashboard.aggregate import DashboardData


def _report_title(projects: list[str]) -> str:
    """Return the page title: the one project's name, or the project count."""
    if len(projects) == 1:
        return projects[0]
    return f"{len(projects)} projects"


def render(data: DashboardData, template_path: Path, analysis_html: str) -> str:
    """Substitute aggregated data, highlights, title and analysis into the template.

    Args:
        data: The aggregated payload, whose ``projects`` drive the title.
        template_path: The HTML template carrying the ``__TOKEN__`` slots.
        analysis_html: The analysis HTML for the ``__ANALYSIS__`` slot, built by
            the caller from the generated figures and the per-project notes.

    Returns:
        The rendered HTML with every token substituted.
    """
    template = template_path.read_text(encoding="utf-8")
    h = compute_highlights(data)
    payload = json.dumps(data, separators=(",", ":"))
    replacements: dict[str, str] = {
        "__DATA__": payload,
        "__TITLE__": _report_title(data["projects"]),
        "__ANALYSIS__": analysis_html,
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


__all__ = ["render"]


# eof
