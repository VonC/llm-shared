"""Tests for the git-history dashboard HTML rendering.

Step 1 (v0.8.0): the render assertion moved here from the build test when
``render`` was extracted into ``tools/git_history_dashboard/render.py``. It
checks that every ``__PLACEHOLDER__`` token is substituted out of the template
and that the inlined payload carries the commit total.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.git_history_dashboard import aggregate
from tools.git_history_dashboard.render import render

if TYPE_CHECKING:
    from pathlib import Path

# Synthetic commit history, newest first, exactly as ``git log --date-order``
# would emit it: two commits on 2026-05-22 and one on 2026-05-20.
SAMPLE_COMMITS: list[tuple[str, str, str, str]] = [
    ("b2b2b2b", "2026-05-22 18:30:00 +0000", "Bob Dev", "fix(writer): patch the parser"),
    ("a1a1a1a", "2026-05-22 09:15:00 +0000", "Ann Dev", "feat(cli): add a flag"),
    ("c3c3c3c", "2026-05-20 11:00:00 +0000", "Ann Dev", "docs: update the readme"),
]

# Every placeholder the HTML template carries for ``render`` to substitute.
TEMPLATE_PLACEHOLDERS: tuple[str, ...] = (
    "__DATA__",
    "__TOTAL_COMMITS__",
    "__START__",
    "__END__",
    "__MONTHS__",
    "__ACTIVE_DAYS__",
    "__TOTAL_DAYS__",
    "__ACTIVE_PCT__",
    "__PEAK_DAY_COUNT__",
    "__PEAK_DAY_DATE__",
    "__PEAK_WEEK_COUNT__",
    "__PEAK_WEEK_START__",
)


def _write_minimal_template(path: Path) -> None:
    """Write a minimal HTML template that carries every dashboard placeholder."""
    body = "\n".join(f"<div>{name}</div>" for name in TEMPLATE_PLACEHOLDERS)
    path.write_text(
        f"<html><body>\n{body}\n<p>commits=__TOTAL_COMMITS__</p>\n</body></html>\n",
        encoding="utf-8",
    )


class TestRendering:
    """Cover HTML template substitution."""

    def test_render_substitutes_every_placeholder(self, tmp_path: Path) -> None:
        """No ``__PLACEHOLDER__`` token survives a render of real data."""
        template = tmp_path / "template.html"
        _write_minimal_template(template)
        data = aggregate.aggregate(SAMPLE_COMMITS)

        html = render(data, template)

        for placeholder in TEMPLATE_PLACEHOLDERS:
            assert placeholder not in html
        assert '"total_commits":' in html
        assert f"commits={len(SAMPLE_COMMITS)}" in html


# eof
