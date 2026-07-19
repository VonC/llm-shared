"""Render deterministic, accessible SVG Git-history diagrams."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.git_history_diagrams.models import Commit, Edge, Lane, Scenario

WIDTH = 1120
TOP = 62
BOTTOM = 94
NODE_RADIUS = 12


def _commit_map(scenario: Scenario) -> dict[str, tuple[Commit, Lane]]:
    lanes = {lane.key: lane for lane in scenario.lanes}
    if len(lanes) != len(scenario.lanes):
        msg = "lane keys must be unique"
        raise ValueError(msg)
    commits: dict[str, tuple[Commit, Lane]] = {}
    for commit in scenario.commits:
        if commit.key in commits:
            msg = "commit keys must be unique"
            raise ValueError(msg)
        if commit.lane not in lanes:
            msg = f"unknown lane for commit {commit.key}: {commit.lane}"
            raise ValueError(msg)
        commits[commit.key] = (commit, lanes[commit.lane])
    return commits


def _line(edge: Edge, commits: dict[str, tuple[Commit, Lane]]) -> str:
    try:
        start, start_lane = commits[edge.start]
        end, end_lane = commits[edge.end]
    except KeyError as error:
        msg = f"edge references unknown commit: {error.args[0]}"
        raise ValueError(msg) from error
    css_class = escape(edge.kind)
    marker = ' marker-end="url(#arrow)"' if edge.kind in {"merge", "rebase"} else ""
    color = end_lane.color if edge.kind != "history" else start_lane.color
    line = (
        f'<line class="edge {css_class}" x1="{start.x}" y1="{start_lane.y}" '
        f'x2="{end.x}" y2="{end_lane.y}" stroke="{color}"{marker}/>'
    )
    if not edge.label:
        return line
    x = (start.x + end.x) // 2
    y = (start_lane.y + end_lane.y) // 2 - 10
    label = escape(edge.label)
    return f'{line}<text class="edge-label" x="{x}" y="{y}">{label}</text>'


def _lane(lane: Lane) -> str:
    label = escape(lane.label)
    return (
        f'<text class="lane-label" x="18" y="{lane.y + 5}" fill="{lane.color}">'
        f"{label}</text>"
    )


def _commit(commit: Commit, lane: Lane) -> str:
    label = escape(commit.label)
    return (
        f'<circle class="commit" cx="{commit.x}" cy="{lane.y}" r="{NODE_RADIUS}" '
        f'fill="{lane.color}"/><text class="commit-label" x="{commit.x}" '
        f'y="{lane.y - 19}">{label}</text>'
    )


def render_svg(scenario: Scenario) -> str:
    """Render one scenario as standalone SVG markup."""
    commits = _commit_map(scenario)
    max_y = max(lane.y for lane in scenario.lanes)
    height = max_y + BOTTOM
    edges = "".join(_line(edge, commits) for edge in scenario.edges)
    lanes = "".join(_lane(lane) for lane in scenario.lanes)
    nodes = "".join(_commit(*commits[commit.key]) for commit in scenario.commits)
    title = escape(scenario.title)
    caption = escape(scenario.caption)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" viewBox="0 0 {WIDTH} {height}">
<title id="title">{title}</title><desc id="desc">{caption}</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="context-stroke"/></marker></defs>
<style>
  text {{ font-family: Inter, Segoe UI, sans-serif; }}
  .title {{ font-size: 21px; font-weight: 700; fill: #172033; }}
  .lane-label {{ font-size: 14px; font-weight: 700; }}
  .edge {{ fill: none; stroke-width: 3; opacity: .88; }}
  .edge.merge {{ stroke-width: 5; }}
  .edge.rebase {{ stroke-width: 4; stroke-dasharray: 9 7; }}
  .edge-label {{ font-size: 12px; text-anchor: middle; fill: #374151; }}
  .commit {{ stroke: #fff; stroke-width: 3; }}
  .commit-label {{ font-size: 12px; font-weight: 700; text-anchor: middle; fill: #172033; }}
  .caption {{ font-size: 13px; fill: #4b5563; }}
  .legend {{ font-size: 12px; fill: #374151; }}
</style>
<rect width="100%" height="100%" rx="12" fill="#f8fafc" stroke="#d7deea"/>
<text class="title" x="18" y="32">{title}</text>
{lanes}{edges}{nodes}
<line class="edge rebase" x1="20" y1="{height - 58}" x2="82" y2="{height - 58}" stroke="#7c3aed" marker-end="url(#arrow)"/>
<text class="legend" x="94" y="{height - 53}">dashed = rebase/replay (new commit identities)</text>
<line class="edge merge" x1="440" y1="{height - 58}" x2="502" y2="{height - 58}" stroke="#2563eb" marker-end="url(#arrow)"/>
<text class="legend" x="514" y="{height - 53}">solid arrow = merge --no-ff</text>
<text class="caption" x="18" y="{height - 22}">{caption}</text>
</svg>
"""


# eof
