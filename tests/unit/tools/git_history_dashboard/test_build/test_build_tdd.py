"""Tests for the shared git-history dashboard builder hub.

Cover ``tools/git_history_dashboard/build.py``: the ``git log`` export
into ``git_history.csv``, the pipe-separated CSV parser, the ``run_build``
orchestration, and the ``main`` entry point in both its git-export and
pre-exported-CSV modes. A ``runpy`` test exercises the ``__main__`` script path
end to end.

The tool resolves the calling project's root through the shared
``find_project_root`` helper; these tests pin that resolution with
``monkeypatch`` (or ``PRJ_DIR``) so they never depend on the real checkout. The
export and git-mode tests build a throwaway repository under ``tmp_path`` with
real ``git`` commands.

Step 0 (v0.8.0): relocated verbatim from the flat
``tests/unit/tools/test_git_history_dashboard_build.py`` into the nested
``git_history_dashboard/test_build/`` subpackage (plan Q01).

Step 1 (v0.8.0): the classifier, aggregation and render assertions moved to
``test_aggregate`` and ``test_render`` when those functions were extracted from
``build.py``; this file keeps the export, the CSV parse, ``run_build`` and the
``main`` / ``__main__`` coverage that stay in the hub.

Step 1.1 (v0.8.0): ``run_build`` gains a ``project`` argument and tags the parsed
rows into ``Commit`` records, so the ``run_build`` test passes one and checks the
single project lands in the payload; the CSV-parse tests are unchanged because
``iter_commits_from_csv`` still yields raw rows.

Groundhog duration gate: the export unit test fakes the ``git log`` subprocess
at the ``subprocess.run`` boundary, asserting the exact argv and CSV behavior
without paying real repository setup in the call that only covers this module.
"""

from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.git_history_dashboard import build

if TYPE_CHECKING:
    from collections.abc import Callable

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

# The messy-CSV fixture yields two well-formed records.
EXPECTED_PARSED_FROM_MESSY_CSV = 2
# The export fixture writes one commit.
EXPECTED_EXPORTED_COMMITS = 1
# A full git object name is 40 hexadecimal characters.
GIT_SHA_LENGTH = 40
# Synthetic SHA emitted by the fake git-log subprocess.
PIPE_HISTORY_SHA = "a" * GIT_SHA_LENGTH

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


def _pipe_history_subprocess(
    captured: dict[str, object],
) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Return a fake ``subprocess.run`` that emits one pipe-bearing commit."""
    def fake_run(
        cmd: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
        encoding: str,
    ) -> subprocess.CompletedProcess[str]:
        """Record the subprocess contract and return the synthetic git output."""
        captured["cmd"] = cmd
        captured["options"] = (capture_output, text, check, encoding)
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=(
                PIPE_HISTORY_SHA
                + "|2026-05-22 10:00:00 +0000|Test Author|"
                + "fix(io): handle a|b edge case"
            ),
        )

    return fake_run


def _assert_pipe_history_export(
    captured: dict[str, object],
    repo_dir: Path,
    csv_path: Path,
    written: Path,
) -> None:
    """Assert the fake export wrote the expected CSV and subprocess contract."""
    assert written == csv_path
    assert captured["cmd"] == build.build_git_log_command(repo_dir)
    assert captured["options"] == (True, True, True, "utf-8")
    content = csv_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert len(content.splitlines()) == EXPECTED_EXPORTED_COMMITS
    assert list(build.iter_commits_from_csv(csv_path)) == [
        (
            PIPE_HISTORY_SHA,
            "2026-05-22 10:00:00 +0000",
            "Test Author",
            "fix(io): handle a|b edge case",
        ),
    ]


def _make_git_repo(repo_dir: Path, subjects: list[str]) -> None:
    """Create a git repo at repo_dir with one commit per subject line.

    The author identity comes from the GIT_AUTHOR_*/GIT_COMMITTER_* env vars and
    gpg signing is turned off inline on the commit, so no `git config`
    subprocess calls are needed. Empty commits are enough because the dashboard
    reads commit metadata, not tree contents.
    """
    repo_dir.mkdir(parents=True, exist_ok=True)
    _run_git(repo_dir, "init", "-q")
    for subject in subjects:
        _run_git(
            repo_dir,
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--allow-empty",
            "-m",
            subject,
        )


@pytest.fixture
def one_commit_repo(tmp_path: Path) -> Path:
    """Return a metadata-only repo with one commit for export tests."""
    repo_dir = tmp_path / "repo"
    _make_git_repo(repo_dir, ["docs: only commit"])
    return repo_dir


@pytest.fixture
def consumer_repo(tmp_path: Path) -> Path:
    """Return a consumer repo for the script-entry test."""
    repo_dir = tmp_path / "consumer"
    _make_git_repo(repo_dir, ["feat: only commit"])
    return repo_dir


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

    def test_export_writes_pipe_separated_history(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Exporting git output yields a parseable, newline-terminated CSV."""
        repo_dir = tmp_path / "sample_repo"
        csv_path = tmp_path / build.GIT_HISTORY_CSV_NAME
        captured: dict[str, object] = {}

        monkeypatch.setattr(build.subprocess, "run", _pipe_history_subprocess(captured))

        written = build.export_git_history_csv(repo_dir, csv_path)

        _assert_pipe_history_export(captured, repo_dir, csv_path, written)

    def test_export_creates_parent_directory(
        self,
        tmp_path: Path,
        one_commit_repo: Path,
    ) -> None:
        """A missing parent directory for the CSV is created on export."""
        csv_path = tmp_path / "nested" / "dir" / "git_history.csv"

        build.export_git_history_csv(one_commit_repo, csv_path)

        assert csv_path.is_file()

    def test_export_raises_for_a_non_git_directory(self, tmp_path: Path) -> None:
        """Running the export outside a repository surfaces the git failure."""
        plain_dir = tmp_path / "not_a_repo"
        plain_dir.mkdir()

        with pytest.raises(subprocess.CalledProcessError):
            build.export_git_history_csv(plain_dir, tmp_path / "out.csv")


class TestCsvParsing:
    """Cover the pipe-separated CSV reader."""

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

        build.run_build(csv_path, out_dir, template, "sample")

        data = json.loads((out_dir / "data.json").read_text(encoding="utf-8"))
        assert data["total_commits"] == len(SAMPLE_COMMITS)
        assert data["projects"] == ["sample"]
        assert (out_dir / "dashboard.html").is_file()

    def test_module_runs_as_a_script(
        self,
        consumer_repo: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Running build.py as ``__main__`` exports and renders end to end.

        ``PRJ_DIR`` points the shared root helper at the throwaway repo, so the
        default output lands under ``<repo>/docs/git_history_dashboard``;
        ``--no-open`` keeps the run from launching a browser (Step 2 delegates
        ``main`` to the CLI, which opens the report by default).
        """
        monkeypatch.setenv("PRJ_DIR", str(consumer_repo))
        monkeypatch.setattr(sys, "argv", ["build.py", "--no-open"])

        build_script = build.__file__
        assert build_script is not None
        runpy.run_path(build_script, run_name="__main__")

        dashboard_dir = consumer_repo.joinpath(*build.DASHBOARD_SUBDIR)
        assert (dashboard_dir / build.GIT_HISTORY_CSV_NAME).is_file()
        assert (dashboard_dir / "data.json").is_file()
        html = (dashboard_dir / "dashboard.html").read_text(encoding="utf-8")
        assert "__DATA__" not in html
        assert "__TOTAL_COMMITS__" not in html


# eof
