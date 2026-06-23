"""Tests for the git-history dashboard HTML rendering.

Step 1 (v0.8.0): the render assertion moved here from the build test when
``render`` was extracted into ``tools/git_history_dashboard/render.py``. It
checks that every ``__PLACEHOLDER__`` token is substituted out of the template
and that the inlined payload carries the commit total.

Step 3 (v0.8.0): ``render`` gains the ``__TITLE__`` and ``__ANALYSIS__`` slots
and the bundled template is project-neutral; these tests check both slots fill,
the title names the one project or the project count, and that no pdfsplitter
string survives a render of the real template.
"""

from __future__ import annotations

from pathlib import Path

from tools.git_history_dashboard import aggregate
from tools.git_history_dashboard.render import render

# Synthetic commit history, newest first, all tagged with one project.
SAMPLE_COMMITS: list[aggregate.Commit] = [
    aggregate.Commit("b2b2b2b", "2026-05-22 18:30:00 +0000", "Bob Dev", "fix(writer): patch the parser", "demo"),
    aggregate.Commit("a1a1a1a", "2026-05-22 09:15:00 +0000", "Ann Dev", "feat(cli): add a flag", "demo"),
    aggregate.Commit("c3c3c3c", "2026-05-20 11:00:00 +0000", "Ann Dev", "docs: update the readme", "demo"),
]

# The real bundled template, alongside the package modules.
_TEMPLATE_DIR = Path(aggregate.__file__).resolve().parent if aggregate.__file__ else Path()
_REAL_TEMPLATE = _TEMPLATE_DIR / "template.html"

# A stand-in for the converted analysis HTML the caller would pass.
_ANALYSIS_HTML = '<div class="analysis"><h2>Observations</h2></div>'

# Every placeholder the HTML template carries for ``render`` to substitute.
TEMPLATE_PLACEHOLDERS: tuple[str, ...] = (
    "__DATA__",
    "__TITLE__",
    "__ANALYSIS__",
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
    """Cover HTML template substitution, the slots, and the project title."""

    def test_render_substitutes_every_placeholder(self, tmp_path: Path) -> None:
        """No ``__PLACEHOLDER__`` token survives a render of real data."""
        template = tmp_path / "template.html"
        _write_minimal_template(template)
        data = aggregate.aggregate(SAMPLE_COMMITS)

        html = render(data, template, _ANALYSIS_HTML)

        for placeholder in TEMPLATE_PLACEHOLDERS:
            assert placeholder not in html
        assert '"total_commits":' in html
        assert f"commits={len(SAMPLE_COMMITS)}" in html

    def test_render_fills_the_analysis_and_title_slots(self, tmp_path: Path) -> None:
        """The analysis HTML and the single-project title land in the output."""
        template = tmp_path / "template.html"
        _write_minimal_template(template)
        data = aggregate.aggregate(SAMPLE_COMMITS)

        html = render(data, template, _ANALYSIS_HTML)

        assert _ANALYSIS_HTML in html
        assert "demo" in html  # the one project name is the title

    def test_render_titles_a_combined_run_by_project_count(self, tmp_path: Path) -> None:
        """Several projects yield the project-count label as the title."""
        template = tmp_path / "template.html"
        template.write_text("<title>__TITLE__</title>\n__DATA__\n", encoding="utf-8")
        commits = [
            aggregate.Commit("s1", "2026-05-20 09:00:00 +0000", "Ann", "feat: a", "alpha"),
            aggregate.Commit("s2", "2026-05-21 09:00:00 +0000", "Bob", "fix: b", "beta"),
        ]
        data = aggregate.aggregate(commits)

        html = render(data, template, _ANALYSIS_HTML)

        assert "2 projects" in html

    def test_render_drops_the_pdfsplitter_strings(self) -> None:
        """The real bundled template renders with no pdfsplitter string or token."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        html = render(data, _REAL_TEMPLATE, _ANALYSIS_HTML)

        assert "pdfsplitter" not in html
        assert "__TITLE__" not in html
        assert "__ANALYSIS__" not in html
        assert _ANALYSIS_HTML in html


class TestFrontEndControls:
    """Cover the Step 4 front-end controls and recompute wiring.

    The recompute itself is client-side JavaScript with no Python harness in this
    repo, so these checks assert the controls and the payload-key wiring are
    present; the behavior is exercised by the Step 5 acceptance render.
    """

    def test_rendered_page_has_the_four_controls(self) -> None:
        """The project filter, contributor list, date range, and theme toggle render."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        html = render(data, _REAL_TEMPLATE, _ANALYSIS_HTML)

        assert 'id="project-filter"' in html
        assert 'id="contributors"' in html
        assert 'id="date-range"' in html
        assert 'id="theme-toggle"' in html

    def test_inline_script_wires_the_payload_keys(self) -> None:
        """The recompute references by_project, by_author, applyFilters and data-theme."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        html = render(data, _REAL_TEMPLATE, _ANALYSIS_HTML)

        assert "applyFilters" in html
        assert "D.by_project" in html
        assert "by_author" in html
        assert "data-theme" in html

    def test_single_project_payload_lists_one_project(self) -> None:
        """A single-project run carries one project for the filter to render."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        html = render(data, _REAL_TEMPLATE, _ANALYSIS_HTML)

        assert '"projects":["demo"]' in html
        assert 'id="project-filter"' in html


# eof
