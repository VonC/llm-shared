"""Tests for the shared git-history dashboard builder tool.

Cover ``tools/git_history_dashboard/build.py``: the ``git log`` export
into ``git_history.csv``, the pipe-separated CSV parser, the commit
aggregation and rendering, and the ``main`` entry point in both its
git-export and pre-exported-CSV modes. A ``runpy`` test exercises the
``__main__`` script path end to end.

The tool resolves the calling project's root through the shared
``find_project_root`` helper; these tests pin that resolution with
``monkeypatch`` (or ``PRJ_DIR``) so they never depend on the real
checkout. The aggregation and rendering tests run on synthetic commit
tuples; the export and git-mode tests build a throwaway repository under
``tmp_path`` with real ``git`` commands.

Fix: Supply the commit identity through the GIT_AUTHOR_*/GIT_COMMITTER_*
env vars on every git call and drop the three ``git config`` subprocess
calls from ``_make_git_repo``. Each git spawn costs a few hundred
milliseconds on Windows, so removing the redundant config processes cuts
the throwaway-repo setup wall time.

Step 0 (v0.8.0): relocated verbatim from the flat
``tests/unit/tools/test_git_history_dashboard_build.py`` into the nested
``git_history_dashboard/test_build/`` subpackage, adopting the
per-test-folder convention (plan Q01). The assertions are unchanged; only
the path moved.
"""

from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from tools.git_history_dashboard import build

# Identity through the environment so the repo setup needs no `git config`
# subprocess calls; merged onto os.environ to keep PATH and the Windows
# system variables git relies on.
_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test Author",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test Author",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}

# --- Expectations for the synthetic SAMPLE_COMMITS fixture ------------------

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
# The messy-CSV fixture yields two well-formed records.
EXPECTED_PARSED_FROM_MESSY_CSV = 2
# Only the single parseable-date commit survives the skip test.
EXPECTED_COMMITS_AFTER_DATE_SKIP = 1
# A full git object name is 40 hexadecimal characters.
GIT_SHA_LENGTH = 40

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


def _sample_csv_text() -> str:
    """Return the pipe-separated CSV text for the SAMPLE_COMMITS fixture."""
    lines = [
        f"{sha}|{iso_date}|{author}|{subject}"
        for sha, iso_date, author, subject in SAMPLE_COMMITS
    ]
    return "\n".join(lines) + "\n"


def _write_minimal_template(path: Path) -> None:
    """Write a minimal HTML template that carries every dashboard placeholder."""
    body = "\n".join(f"<div>{name}</div>" for name in TEMPLATE_PLACEHOLDERS)
    path.write_text(
        f"<html><body>\n{body}\n<p>commits=__TOTAL_COMMITS__</p>\n</body></html>\n",
        encoding="utf-8",
    )


def _run_git(repo_dir: Path, *args: str) -> None:
    """Run a git subcommand inside repo_dir for throwaway-repository setup."""
    subprocess.run(  # noqa: S603
        ["git", "-C", str(repo_dir), *args],  # noqa: S607
        capture_output=True,
        check=True,
        text=True,
        encoding="utf-8",
        env=_GIT_ENV,
    )


def _make_git_repo(repo_dir: Path, subjects: list[str]) -> None:
    """Create a git repo at repo_dir with one commit per subject line.

    The author identity comes from the GIT_AUTHOR_*/GIT_COMMITTER_* env vars and
    gpg signing is turned off inline on the commit, so no `git config`
    subprocess calls are needed.
    """
    repo_dir.mkdir(parents=True, exist_ok=True)
    _run_git(repo_dir, "init")
    for index, subject in enumerate(subjects):
        (repo_dir / f"file_{index}.txt").write_text(subject, encoding="utf-8")
        _run_git(repo_dir, "add", "-A")
        _run_git(repo_dir, "-c", "commit.gpgsign=false", "commit", "-m", subject)


class TestGitHistoryExport:
    """Cover the ``git log`` command and the ``git_history.csv`` export."""

    def test_build_git_log_command_matches_documented_one_liner(self) -> None:
        """The argv mirrors the documented ``git log`` pipe-format one-liner."""
        repo_dir = Path("some") / "repo"

        command = build.build_git_log_command(repo_dir)

        assert command == [
            "git",
            "-C",
            str(repo_dir),
            "log",
            "--all",
            "--pretty=format:%H|%ai|%an|%s",
            "--date-order",
        ]

    def test_export_writes_pipe_separated_history(self, tmp_path: Path) -> None:
        """Exporting a real repo yields a parseable, newline-terminated CSV."""
        repo_dir = tmp_path / "sample_repo"
        subjects = ["feat(cli): first commit", "fix(io): handle a|b edge case"]
        _make_git_repo(repo_dir, subjects)
        csv_path = tmp_path / build.GIT_HISTORY_CSV_NAME

        written = build.export_git_history_csv(repo_dir, csv_path)

        assert written == csv_path
        content = csv_path.read_text(encoding="utf-8")
        assert content.endswith("\n")
        assert len(content.splitlines()) == len(subjects)

        parsed = list(build.iter_commits_from_csv(csv_path))
        assert len(parsed) == len(subjects)
        assert {commit[3] for commit in parsed} == set(subjects)
        for sha, iso_date, author, _subject in parsed:
            assert len(sha) == GIT_SHA_LENGTH
            assert iso_date[:4].isdigit()
            assert author == "Test Author"

    def test_export_creates_parent_directory(self, tmp_path: Path) -> None:
        """A missing parent directory for the CSV is created on export."""
        repo_dir = tmp_path / "repo"
        _make_git_repo(repo_dir, ["docs: only commit"])
        csv_path = tmp_path / "nested" / "dir" / "git_history.csv"

        build.export_git_history_csv(repo_dir, csv_path)

        assert csv_path.is_file()

    def test_export_raises_for_a_non_git_directory(self, tmp_path: Path) -> None:
        """Running the export outside a repository surfaces the git failure."""
        plain_dir = tmp_path / "not_a_repo"
        plain_dir.mkdir()

        with pytest.raises(subprocess.CalledProcessError):
            build.export_git_history_csv(plain_dir, tmp_path / "out.csv")


class TestCsvParsing:
    """Cover the pipe-separated CSV reader and the commit classifier."""

    def test_keeps_pipes_in_subject_and_skips_bad_lines(
        self,
        tmp_path: Path,
    ) -> None:
        """A ``|`` in the subject survives; blank and short lines are dropped."""
        csv_path = tmp_path / "messy.csv"
        csv_path.write_text(
            "sha1|2026-05-22 10:00:00 +0000|Dev One|feat: handle a | b | c\n"
            "\n"
            "sha2|2026-05-21 09:00:00 +0000|Dev Two|docs: tidy up\n"
            "this line is malformed\n",
            encoding="utf-8",
        )

        parsed = list(build.iter_commits_from_csv(csv_path))

        assert len(parsed) == EXPECTED_PARSED_FROM_MESSY_CSV
        assert parsed[0] == (
            "sha1",
            "2026-05-22 10:00:00 +0000",
            "Dev One",
            "feat: handle a | b | c",
        )
        assert parsed[1][3] == "docs: tidy up"

    def test_classify_extracts_conventional_type_and_scope(self) -> None:
        """Conventional subjects yield their type and scope; others collapse."""
        assert build.classify("feat(cli): add flag") == ("feat", "cli")
        assert build.classify("fix: quick patch") == ("fix", "")
        assert build.classify("chore(ci)!: breaking change") == ("chore", "ci")
        assert build.classify("random subject line") == ("other", "")
        assert build.classify("wibble(scope): unknown type") == ("other", "scope")


class TestAggregation:
    """Cover the daily/weekly aggregation and the headline numbers."""

    def test_aggregate_reports_total_commits_and_date_span(self) -> None:
        """Aggregation echoes the input count and the inclusive date span."""
        data = build.aggregate(SAMPLE_COMMITS)

        assert data["total_commits"] == len(SAMPLE_COMMITS)
        assert data["start"] == "2026-05-20"
        assert data["end"] == "2026-05-22"

    def test_aggregate_builds_a_contiguous_daily_series(self) -> None:
        """The daily series zero-fills the gap between the first and last days."""
        data = build.aggregate(SAMPLE_COMMITS)

        assert data["dates"] == ["2026-05-20", "2026-05-21", "2026-05-22"]
        assert data["totals"] == [1, 0, 2]

    def test_aggregate_tallies_each_conventional_type_once(self) -> None:
        """``by_type`` counts feat, fix, and docs once each for the fixture."""
        data = build.aggregate(SAMPLE_COMMITS)

        assert data["by_type"]["feat"] == EXPECTED_TYPE_OCCURRENCES
        assert data["by_type"]["fix"] == EXPECTED_TYPE_OCCURRENCES
        assert data["by_type"]["docs"] == EXPECTED_TYPE_OCCURRENCES

    def test_aggregate_tallies_scope_and_keeps_recent_head(self) -> None:
        """``by_scope`` counts the writer scope; ``recent`` head is newest first."""
        data = build.aggregate(SAMPLE_COMMITS)

        assert data["by_scope"]["writer"] == EXPECTED_TYPE_OCCURRENCES
        assert data["recent"][0]["sha"] == SAMPLE_COMMITS[0][0][:7]

    def test_aggregate_skips_unparseable_dates(self) -> None:
        """A commit whose date will not parse is dropped, not fatal."""
        commits: list[tuple[str, str, str, str]] = [
            ("good123", "2026-05-20 11:00:00 +0000", "Dev", "feat: keep me"),
            ("bad456", "not-a-date", "Dev", "fix: drop me"),
        ]

        data = build.aggregate(commits)

        assert data["total_commits"] == EXPECTED_COMMITS_AFTER_DATE_SKIP

    def test_aggregate_raises_system_exit_when_history_is_empty(self) -> None:
        """An empty history is a hard stop rather than an empty dashboard."""
        with pytest.raises(SystemExit, match="No commits found"):
            build.aggregate([])

    def test_compute_highlights_reports_span_and_peaks(self) -> None:
        """Highlights expose the active-day ratio plus the peak day and week."""
        data = build.aggregate(SAMPLE_COMMITS)

        highlights = build.compute_highlights(data)

        assert highlights["total_commits"] == len(SAMPLE_COMMITS)
        assert highlights["total_days"] == len(data["dates"])
        assert highlights["active_days"] == EXPECTED_ACTIVE_DAYS
        assert highlights["peak_day_count"] == EXPECTED_PEAK_DAY_COMMITS
        assert highlights["peak_week_count"] == EXPECTED_PEAK_WEEK_COMMITS
        assert highlights["active_pct"] == EXPECTED_ACTIVE_PCT
        assert highlights["months"] == EXPECTED_SPAN_MONTHS
        assert "2026" in highlights["peak_day_date_fmt"]


class TestRendering:
    """Cover HTML template substitution."""

    def test_render_substitutes_every_placeholder(self, tmp_path: Path) -> None:
        """No ``__PLACEHOLDER__`` token survives a render of real data."""
        template = tmp_path / "template.html"
        _write_minimal_template(template)
        data = build.aggregate(SAMPLE_COMMITS)

        html = build.render(data, template)

        for placeholder in TEMPLATE_PLACEHOLDERS:
            assert placeholder not in html
        assert '"total_commits":' in html
        assert f"commits={len(SAMPLE_COMMITS)}" in html


class TestEndToEnd:
    """Cover ``run_build`` and ``main`` in both history-source modes."""

    def test_run_build_writes_data_json_and_dashboard_html(
        self,
        tmp_path: Path,
    ) -> None:
        """``run_build`` turns a CSV into ``data.json`` and ``dashboard.html``."""
        csv_path = tmp_path / "history.csv"
        csv_path.write_text(_sample_csv_text(), encoding="utf-8")
        template = tmp_path / "template.html"
        _write_minimal_template(template)
        out_dir = tmp_path / "out"

        build.run_build(csv_path, out_dir, template)

        data = json.loads((out_dir / "data.json").read_text(encoding="utf-8"))
        assert data["total_commits"] == len(SAMPLE_COMMITS)
        assert (out_dir / "dashboard.html").is_file()

    def test_main_csv_mode_builds_dashboard_without_git(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """``--csv`` skips ``git log`` and renders straight from the file."""
        csv_path = tmp_path / "history.csv"
        csv_path.write_text(_sample_csv_text(), encoding="utf-8")
        out_dir = tmp_path / "out"
        template = tmp_path / "template.html"
        _write_minimal_template(template)

        def _fake_project_root(_start: Path) -> Path:
            """Return tmp_path as the discovered project root."""
            return tmp_path

        monkeypatch.setattr(build, "find_project_root", _fake_project_root)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "build.py",
                "--csv",
                str(csv_path),
                "--out-dir",
                str(out_dir),
                "--template",
                str(template),
            ],
        )

        build.main()

        assert (out_dir / "data.json").is_file()
        dashboard = (out_dir / "dashboard.html").read_text(encoding="utf-8")
        assert f"commits={len(SAMPLE_COMMITS)}" in dashboard

    def test_main_exports_history_from_the_calling_project(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """With no source flag, ``main`` exports the CSV then builds the page."""
        repo_dir = tmp_path / "project"
        subjects = ["feat(core): seed commit", "docs: describe it"]
        _make_git_repo(repo_dir, subjects)
        out_dir = tmp_path / "out"
        template = tmp_path / "template.html"
        _write_minimal_template(template)

        def _fake_project_root(_start: Path) -> Path:
            """Return the throwaway repo as the discovered project root."""
            return repo_dir

        monkeypatch.setattr(build, "find_project_root", _fake_project_root)
        monkeypatch.setattr(
            sys,
            "argv",
            ["build.py", "--out-dir", str(out_dir), "--template", str(template)],
        )

        build.main()

        exported_csv = repo_dir.joinpath(*build.DASHBOARD_SUBDIR) / build.GIT_HISTORY_CSV_NAME
        assert exported_csv.is_file()
        dashboard = (out_dir / "dashboard.html").read_text(encoding="utf-8")
        assert f"commits={len(subjects)}" in dashboard

    def test_module_runs_as_a_script(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Running build.py as ``__main__`` exports and renders end to end.

        ``PRJ_DIR`` points the shared root helper at the throwaway repo, so
        the default output lands under ``<repo>/docs/git_history_dashboard``.
        """
        repo_dir = tmp_path / "consumer"
        _make_git_repo(repo_dir, ["feat: only commit"])
        monkeypatch.setenv("PRJ_DIR", str(repo_dir))
        monkeypatch.setattr(sys, "argv", ["build.py"])

        build_script = build.__file__
        assert build_script is not None
        runpy.run_path(build_script, run_name="__main__")

        dashboard_dir = repo_dir.joinpath(*build.DASHBOARD_SUBDIR)
        assert (dashboard_dir / build.GIT_HISTORY_CSV_NAME).is_file()
        assert (dashboard_dir / "data.json").is_file()
        html = (dashboard_dir / "dashboard.html").read_text(encoding="utf-8")
        assert "__DATA__" not in html
        assert "__TOTAL_COMMITS__" not in html


# eof
