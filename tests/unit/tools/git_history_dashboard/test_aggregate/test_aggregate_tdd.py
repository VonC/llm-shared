"""Tests for the git-history dashboard commit aggregation.

Step 1 (v0.8.0): the aggregation assertions moved here verbatim from the build
test when ``classify``, ``aggregate`` and ``compute_highlights`` were extracted
into ``tools/git_history_dashboard/aggregate.py``. They cover the
conventional-commit classifier, the daily/weekly aggregation, the headline
numbers, and the unparseable-date and empty-history edges.
"""

from __future__ import annotations

import pytest

from tools.git_history_dashboard import aggregate

# Each conventional type (feat / fix / docs) appears exactly once.
EXPECTED_TYPE_OCCURRENCES = 1
# Two of the three calendar days in the span carry commits.
EXPECTED_ACTIVE_DAYS = 2
# The busiest single day holds two commits.
EXPECTED_PEAK_DAY_COMMITS = 2
# All three commits fall in the same Monday-anchored week.
EXPECTED_PEAK_WEEK_COMMITS = 3
# round(100 * 2 active days / 3 total days).
EXPECTED_ACTIVE_PCT = 67
# A three-day span rounds up to a single month subtitle.
EXPECTED_SPAN_MONTHS = 1
# Only the single parseable-date commit survives the skip test.
EXPECTED_COMMITS_AFTER_DATE_SKIP = 1

# Synthetic commit history, newest first, exactly as ``git log --date-order``
# would emit it: two commits on 2026-05-22 and one on 2026-05-20.
SAMPLE_COMMITS: list[tuple[str, str, str, str]] = [
    ("b2b2b2b", "2026-05-22 18:30:00 +0000", "Bob Dev", "fix(writer): patch the parser"),
    ("a1a1a1a", "2026-05-22 09:15:00 +0000", "Ann Dev", "feat(cli): add a flag"),
    ("c3c3c3c", "2026-05-20 11:00:00 +0000", "Ann Dev", "docs: update the readme"),
]


class TestClassify:
    """Cover the conventional-commit classifier."""

    def test_classify_extracts_conventional_type_and_scope(self) -> None:
        """Conventional subjects yield their type and scope; others collapse."""
        assert aggregate.classify("feat(cli): add flag") == ("feat", "cli")
        assert aggregate.classify("fix: quick patch") == ("fix", "")
        assert aggregate.classify("chore(ci)!: breaking change") == ("chore", "ci")
        assert aggregate.classify("random subject line") == ("other", "")
        assert aggregate.classify("wibble(scope): unknown type") == ("other", "scope")


class TestAggregation:
    """Cover the daily/weekly aggregation and the headline numbers."""

    def test_aggregate_reports_total_commits_and_date_span(self) -> None:
        """Aggregation echoes the input count and the inclusive date span."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        assert data["total_commits"] == len(SAMPLE_COMMITS)
        assert data["start"] == "2026-05-20"
        assert data["end"] == "2026-05-22"

    def test_aggregate_builds_a_contiguous_daily_series(self) -> None:
        """The daily series zero-fills the gap between the first and last days."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        assert data["dates"] == ["2026-05-20", "2026-05-21", "2026-05-22"]
        assert data["totals"] == [1, 0, 2]

    def test_aggregate_tallies_each_conventional_type_once(self) -> None:
        """``by_type`` counts feat, fix, and docs once each for the fixture."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        assert data["by_type"]["feat"] == EXPECTED_TYPE_OCCURRENCES
        assert data["by_type"]["fix"] == EXPECTED_TYPE_OCCURRENCES
        assert data["by_type"]["docs"] == EXPECTED_TYPE_OCCURRENCES

    def test_aggregate_tallies_scope_and_keeps_recent_head(self) -> None:
        """``by_scope`` counts the writer scope; ``recent`` head is newest first."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        assert data["by_scope"]["writer"] == EXPECTED_TYPE_OCCURRENCES
        assert data["recent"][0]["sha"] == SAMPLE_COMMITS[0][0][:7]

    def test_aggregate_skips_unparseable_dates(self) -> None:
        """A commit whose date will not parse is dropped, not fatal."""
        commits: list[tuple[str, str, str, str]] = [
            ("good123", "2026-05-20 11:00:00 +0000", "Dev", "feat: keep me"),
            ("bad456", "not-a-date", "Dev", "fix: drop me"),
        ]

        data = aggregate.aggregate(commits)

        assert data["total_commits"] == EXPECTED_COMMITS_AFTER_DATE_SKIP

    def test_aggregate_raises_system_exit_when_history_is_empty(self) -> None:
        """An empty history is a hard stop rather than an empty dashboard."""
        with pytest.raises(SystemExit, match="No commits found"):
            aggregate.aggregate([])

    def test_compute_highlights_reports_span_and_peaks(self) -> None:
        """Highlights expose the active-day ratio plus the peak day and week."""
        data = aggregate.aggregate(SAMPLE_COMMITS)

        highlights = aggregate.compute_highlights(data)

        assert highlights["total_commits"] == len(SAMPLE_COMMITS)
        assert highlights["total_days"] == len(data["dates"])
        assert highlights["active_days"] == EXPECTED_ACTIVE_DAYS
        assert highlights["peak_day_count"] == EXPECTED_PEAK_DAY_COMMITS
        assert highlights["peak_week_count"] == EXPECTED_PEAK_WEEK_COMMITS
        assert highlights["active_pct"] == EXPECTED_ACTIVE_PCT
        assert highlights["months"] == EXPECTED_SPAN_MONTHS
        assert "2026" in highlights["peak_day_date_fmt"]


# eof
