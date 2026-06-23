"""Tests for the git-history dashboard multi-repo CLI orchestration.

Step 2 (v0.8.0): cover ``tools/git_history_dashboard/cli.py`` -- target
resolution (none, one, several, and the multi-project out-dir rule), the
combined run that aggregates several projects into one report, the ``--no-open``
suppress flag, the per-repo skip on a failing export, and the run summary. The
export is faked so the run tests need no real ``git``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from tools.git_history_dashboard import cli

if TYPE_CHECKING:
    from pathlib import Path

# How many commits the two-repo combined run aggregates (one per repo).
EXPECTED_COMBINED_COMMITS = 2

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


def _args(
    *,
    repos: tuple[str, ...] = (),
    csv: str | None = None,
    out_dir: str | None = None,
    template: str = "ignored.html",
    no_open: bool = False,
) -> argparse.Namespace:
    """Build a parsed-args namespace the CLI functions read."""
    return argparse.Namespace(
        repos=list(repos),
        csv=csv,
        out_dir=out_dir,
        template=template,
        no_open=no_open,
    )


def _write_minimal_template(path: Path) -> None:
    """Write a minimal HTML template that carries every dashboard placeholder."""
    body = "\n".join(f"<div>{name}</div>" for name in TEMPLATE_PLACEHOLDERS)
    path.write_text(
        f"<html><body>\n{body}\n<p>commits=__TOTAL_COMMITS__</p>\n</body></html>\n",
        encoding="utf-8",
    )


def _fake_export(repo: Path, csv_path: Path) -> Path:
    """Write a one-commit CSV for `repo` instead of running real ``git log``."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.write_text(
        f"sha{repo.name}|2026-05-20 10:00:00 +0000|Dev|feat: from {repo.name}\n",
        encoding="utf-8",
    )
    return csv_path


def _swallow_open(_url: str) -> None:
    """A no-op stand-in for ``webbrowser.open`` when the call is not tracked."""


class TestResolveTargets:
    """Cover target resolution and the multi-project out-dir rule."""

    def test_no_path_resolves_to_the_current_project(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """With no path the run targets the current project and its default folder."""
        def _project_root(_start: Path) -> Path:
            return tmp_path

        monkeypatch.setattr(cli, "find_project_root", _project_root)

        targets = cli.resolve_targets(_args())

        assert targets.repos == [tmp_path]
        assert targets.out_dir == tmp_path.joinpath(*cli.build.DASHBOARD_SUBDIR)
        assert targets.csv is None

    def test_one_path_keeps_its_default_out_dir(self, tmp_path: Path) -> None:
        """A single repo keeps the dashboard folder under that repo."""
        repo = tmp_path / "alpha"

        targets = cli.resolve_targets(_args(repos=(str(repo),)))

        assert targets.repos == [repo.resolve()]
        assert targets.out_dir == repo.resolve().joinpath(*cli.build.DASHBOARD_SUBDIR)

    def test_two_paths_without_out_dir_error(self, tmp_path: Path) -> None:
        """A multi-project run with no ``--out-dir`` is rejected."""
        repos = (str(tmp_path / "alpha"), str(tmp_path / "beta"))

        with pytest.raises(SystemExit, match="--out-dir"):
            cli.resolve_targets(_args(repos=repos))

    def test_two_paths_with_out_dir_keep_both(self, tmp_path: Path) -> None:
        """A multi-project run with ``--out-dir`` keeps both repos and the folder."""
        alpha = tmp_path / "alpha"
        beta = tmp_path / "beta"
        out = tmp_path / "report"

        targets = cli.resolve_targets(
            _args(repos=(str(alpha), str(beta)), out_dir=str(out)),
        )

        assert targets.repos == [alpha.resolve(), beta.resolve()]
        assert targets.out_dir == out.resolve()


class TestRun:
    """Cover the combined run, the suppress flag, the skip, and the summary."""

    def test_run_combines_projects_into_one_report(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Two repos aggregate into one report and the browser opens by default."""
        opened: list[str] = []
        monkeypatch.setattr(cli.build, "export_git_history_csv", _fake_export)
        monkeypatch.setattr(cli.webbrowser, "open", opened.append)
        out = tmp_path / "report"
        template = tmp_path / "template.html"
        _write_minimal_template(template)

        summary = cli.run(
            _args(
                repos=(str(tmp_path / "alpha"), str(tmp_path / "beta")),
                out_dir=str(out),
                template=str(template),
            ),
        )

        data = json.loads((out / "data.json").read_text(encoding="utf-8"))
        assert data["projects"] == ["alpha", "beta"]
        assert (out / "dashboard.html").is_file()
        assert summary.projects == ["alpha", "beta"]
        assert summary.commit_count == EXPECTED_COMBINED_COMMITS
        assert summary.out_dir == out.resolve()
        assert len(opened) == 1

    def test_run_no_open_suppresses_the_browser(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """``--no-open`` writes the report without opening the browser."""
        opened: list[str] = []
        monkeypatch.setattr(cli.build, "export_git_history_csv", _fake_export)
        monkeypatch.setattr(cli.webbrowser, "open", opened.append)
        out = tmp_path / "report"
        template = tmp_path / "template.html"
        _write_minimal_template(template)

        cli.run(
            _args(
                repos=(str(tmp_path / "alpha"),),
                out_dir=str(out),
                template=str(template),
                no_open=True,
            ),
        )

        assert opened == []
        assert (out / "data.json").is_file()

    def test_run_skips_a_failing_repo(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A repo whose export fails is logged, skipped, and named in the summary."""
        def _flaky_export(repo: Path, csv_path: Path) -> Path:
            if repo.name == "broken":
                raise subprocess.CalledProcessError(1, ["git"])
            return _fake_export(repo, csv_path)

        monkeypatch.setattr(cli.build, "export_git_history_csv", _flaky_export)
        out = tmp_path / "report"
        template = tmp_path / "template.html"
        _write_minimal_template(template)

        summary = cli.run(
            _args(
                repos=(str(tmp_path / "good"), str(tmp_path / "broken")),
                out_dir=str(out),
                template=str(template),
                no_open=True,
            ),
        )

        assert summary.projects == ["good"]
        assert summary.skipped == ["broken"]
        data = json.loads((out / "data.json").read_text(encoding="utf-8"))
        assert data["projects"] == ["good"]

    def test_run_csv_mode_tags_the_current_project(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The ``--csv`` path builds one report tagged with the calling project."""
        def _project_root(_start: Path) -> Path:
            return tmp_path / "myproj"

        monkeypatch.setattr(cli, "find_project_root", _project_root)
        monkeypatch.setattr(cli.webbrowser, "open", _swallow_open)
        csv_path = tmp_path / "history.csv"
        csv_path.write_text(
            "sha1|2026-05-20 10:00:00 +0000|Dev|feat: one\n",
            encoding="utf-8",
        )
        out = tmp_path / "report"
        template = tmp_path / "template.html"
        _write_minimal_template(template)

        summary = cli.run(
            _args(csv=str(csv_path), out_dir=str(out), template=str(template)),
        )

        data = json.loads((out / "data.json").read_text(encoding="utf-8"))
        assert data["projects"] == ["myproj"]
        assert summary.projects == ["myproj"]


def test_main_parses_and_runs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``main`` parses the command line and runs the report."""
    monkeypatch.setattr(cli.build, "export_git_history_csv", _fake_export)
    out = tmp_path / "report"
    template = tmp_path / "template.html"
    _write_minimal_template(template)

    cli.main(
        [
            str(tmp_path / "alpha"),
            "--out-dir",
            str(out),
            "--template",
            str(template),
            "--no-open",
        ],
    )

    assert (out / "data.json").is_file()


# eof
