"""Tests for the git-history dashboard analysis files and markdown seam.

Step 3 (v0.8.0): cover ``tools/git_history_dashboard/analysis.py`` -- the
regenerated generated file, the per-project notes kept byte-for-byte, the
generated-then-notes concatenation order, and the ``uv``-backed
``convert_markdown`` seam (with ``subprocess`` mocked so the test needs neither
``uv`` nor the ``markdown`` package).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

from tools.git_history_dashboard import aggregate, analysis

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# A small tagged history whose figures are easy to assert: feat leads (2 vs 1),
# the busiest hour is 21:00, and ``cli`` is the top scope.
SAMPLE_COMMITS: list[aggregate.Commit] = [
    aggregate.Commit("1", "2026-05-20 21:00:00 +0000", "Ann", "feat(cli): one", "demo"),
    aggregate.Commit("2", "2026-05-20 21:30:00 +0000", "Bob", "feat(cli): two", "demo"),
    aggregate.Commit("3", "2026-05-21 09:00:00 +0000", "Ann", "fix(io): three", "demo"),
]


def _sample_data() -> aggregate.DashboardData:
    """Aggregate the sample commits into a dashboard payload for the figures."""
    return aggregate.aggregate(SAMPLE_COMMITS)


class TestGeneratedAnalysis:
    """Cover the regenerated analysis.generated.md."""

    def test_generated_file_is_rewritten_from_the_figures(self, tmp_path: Path) -> None:
        """A rebuild overwrites the generated file with the current figures."""
        path = tmp_path / "analysis.generated.md"
        path.write_text("STALE", encoding="utf-8")

        result = analysis.write_generated_analysis(_sample_data(), path)

        text = result.read_text(encoding="utf-8")
        assert "STALE" not in text
        assert "## Observations" in text
        assert "**feat** (2)" in text
        assert "21:00" in text
        assert "`cli`" in text
        assert "3 commits" in text

    def test_generated_notes_no_scopes_when_absent(self, tmp_path: Path) -> None:
        """A history with no scoped commits says so instead of an empty list."""
        commits = [
            aggregate.Commit("1", "2026-05-20 21:00:00 +0000", "Ann", "feat: no scope", "demo"),
        ]
        path = tmp_path / "analysis.generated.md"

        analysis.write_generated_analysis(aggregate.aggregate(commits), path)

        assert "No scopes recorded" in path.read_text(encoding="utf-8")


class TestPerProjectNotes:
    """Cover the per-project notes kept across runs."""

    def test_notes_created_once_with_a_stub(self, tmp_path: Path) -> None:
        """A missing notes file is created once with a project stub."""
        path = analysis.ensure_notes("demo", tmp_path)

        assert path == tmp_path / "analysis.notes.demo.md"
        assert "Notes for demo" in path.read_text(encoding="utf-8")

    def test_existing_notes_are_never_overwritten(self, tmp_path: Path) -> None:
        """A hand-written notes file is left byte-for-byte unchanged."""
        notes = tmp_path / "analysis.notes.demo.md"
        notes.write_text("MY HAND-WRITTEN NOTES", encoding="utf-8")

        result = analysis.ensure_notes("demo", tmp_path)

        assert result.read_text(encoding="utf-8") == "MY HAND-WRITTEN NOTES"


class TestAnalysisHtml:
    """Cover the concatenation order and the conversion seam."""

    def test_generated_then_notes_in_order(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The generated file precedes the per-project notes, in project order."""
        seen: list[str] = []

        def _capture(markdown_text: str) -> str:
            seen.append(markdown_text)
            return "<html>"

        monkeypatch.setattr(analysis, "convert_markdown", _capture)
        generated = tmp_path / "analysis.generated.md"
        generated.write_text("GENERATED", encoding="utf-8")
        first = tmp_path / "analysis.notes.alpha.md"
        first.write_text("ALPHA-NOTES", encoding="utf-8")
        second = tmp_path / "analysis.notes.beta.md"
        second.write_text("BETA-NOTES", encoding="utf-8")

        html = analysis.analysis_html(generated, [first, second])

        assert html == "<html>"
        combined = seen[0]
        assert combined.index("GENERATED") < combined.index("ALPHA-NOTES") < combined.index("BETA-NOTES")

    def test_convert_markdown_shells_to_uv(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The seam shells to ``uv run --with markdown`` and feeds the markdown on stdin."""
        calls: list[list[str]] = []
        inputs: list[str | None] = []

        def _fake_run(cmd: list[str], **kwargs: object) -> SimpleNamespace:
            calls.append(cmd)
            raw = kwargs.get("input")
            inputs.append(raw if isinstance(raw, str) else None)
            return SimpleNamespace(stdout="<p>hi</p>")

        monkeypatch.setattr(analysis.subprocess, "run", _fake_run)

        html = analysis.convert_markdown("# hi")

        assert html == "<p>hi</p>"
        assert "uv" in calls[0]
        assert "markdown" in " ".join(calls[0])
        assert inputs[0] == "# hi"


# eof
