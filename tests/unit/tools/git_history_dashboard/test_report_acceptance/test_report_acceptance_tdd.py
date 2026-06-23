"""End-to-end acceptance tests for the git-history dashboard report.

Step 5 (v0.8.0): build a combined report from throwaway git repositories with
real ``git`` and assert the whole chain through ``cli.main`` -- the combined
payload (``projects``, ``by_project`` summing to the top-level series,
``by_author``), the rendered ``dashboard.html`` with its ``__TITLE__`` and
``__ANALYSIS__`` slots filled and no my-project string, the analysis round-trip
(``analysis.generated.md`` refreshes while ``analysis.notes.<project>.md``
survives), and the ``--no-open`` suppress flag. The ``uv`` markdown seam is
stubbed by the package ``conftest`` so the test needs no ``uv``; the bundled
template is used (no ``--template`` flag). The asserts are split across tests to
keep each one within the complexity budget.
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import TYPE_CHECKING

from tools.git_history_dashboard import cli

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# How many commits the two-repo fixture produces (2 in alpha, 1 in beta).
EXPECTED_TOTAL_COMMITS = 3


def _git_env(author: str) -> dict[str, str]:
    """Return an env that fixes the commit identity, so no ``git config`` is needed."""
    return {
        **os.environ,
        "GIT_AUTHOR_NAME": author,
        "GIT_AUTHOR_EMAIL": f"{author.replace(' ', '.').lower()}@test",
        "GIT_COMMITTER_NAME": author,
        "GIT_COMMITTER_EMAIL": f"{author.replace(' ', '.').lower()}@test",
    }


def _run_git(repo_dir: Path, env: dict[str, str], *args: str) -> None:
    """Run a git subcommand inside repo_dir for throwaway-repository setup."""
    subprocess.run(  # noqa: S603
        ["git", "-C", str(repo_dir), *args],  # noqa: S607
        capture_output=True,
        check=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def _make_git_repo(repo_dir: Path, subjects: list[str], author: str) -> None:
    """Create a git repo at repo_dir with one commit per subject, by `author`.

    The author identity comes from the GIT_AUTHOR_*/GIT_COMMITTER_* env vars and
    gpg signing is turned off inline on the commit, so no `git config`
    subprocess calls are needed.
    """
    env = _git_env(author)
    repo_dir.mkdir(parents=True, exist_ok=True)
    _run_git(repo_dir, env, "init")
    for index, subject in enumerate(subjects):
        (repo_dir / f"file_{index}.txt").write_text(subject, encoding="utf-8")
        _run_git(repo_dir, env, "add", "-A")
        _run_git(repo_dir, env, "-c", "commit.gpgsign=false", "commit", "-m", subject)


def _build_two_repos(tmp_path: Path) -> Path:
    """Build alpha (2 commits, Ann) and beta (1 commit, Bob); return their parent."""
    _make_git_repo(tmp_path / "alpha", ["feat(cli): start alpha", "fix(io): patch alpha"], "Ann Dev")
    _make_git_repo(tmp_path / "beta", ["docs: describe beta"], "Bob Dev")
    return tmp_path


def test_two_repo_run_writes_the_combined_payload(tmp_path: Path) -> None:
    """Two repos build one payload: both projects, summed slices, both authors."""
    base = _build_two_repos(tmp_path)
    out = tmp_path / "report"

    cli.main([str(base / "alpha"), str(base / "beta"), "--out-dir", str(out), "--no-open"])

    data = json.loads((out / "data.json").read_text(encoding="utf-8"))
    assert data["projects"] == ["alpha", "beta"]
    assert data["total_commits"] == EXPECTED_TOTAL_COMMITS
    combined = [
        a + b
        for a, b in zip(
            data["by_project"]["alpha"]["totals"],
            data["by_project"]["beta"]["totals"],
            strict=True,
        )
    ]
    assert combined == data["totals"]
    assert "Ann Dev" in data["by_author"]
    assert "Bob Dev" in data["by_author"]


def test_two_repo_render_fills_slots_and_suppresses_browser(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The combined page fills the slots, drops my-project, and opens no browser."""
    base = _build_two_repos(tmp_path)
    out = tmp_path / "report"
    opened: list[str] = []
    monkeypatch.setattr(cli.webbrowser, "open", opened.append)

    cli.main([str(base / "alpha"), str(base / "beta"), "--out-dir", str(out), "--no-open"])

    html = (out / "dashboard.html").read_text(encoding="utf-8")
    assert "my-project" not in html
    assert "__ANALYSIS__" not in html
    assert '<div class="analysis">' in html  # the analysis slot is filled
    assert "2 projects" in html  # the combined-run title filled __TITLE__
    assert (out / "analysis.generated.md").is_file()
    assert (out / "analysis.notes.alpha.md").is_file()
    assert opened == []  # --no-open suppressed the browser


def test_notes_survive_a_rebuild_while_generated_refreshes(tmp_path: Path) -> None:
    """A second run keeps the hand-written notes and rewrites the generated file.

    ``--no-open`` means the opener is never called, so no browser monkeypatch is
    needed here.
    """
    repo = tmp_path / "solo"
    _make_git_repo(repo, ["feat: only commit"], "Ann Dev")
    out = tmp_path / "report"

    cli.main([str(repo), "--out-dir", str(out), "--no-open"])

    notes = out / "analysis.notes.solo.md"
    notes.write_text("HAND-WRITTEN COMMENTARY", encoding="utf-8")
    (out / "analysis.generated.md").write_text("STALE SENTINEL", encoding="utf-8")

    cli.main([str(repo), "--out-dir", str(out), "--no-open"])

    assert notes.read_text(encoding="utf-8") == "HAND-WRITTEN COMMENTARY"
    generated = (out / "analysis.generated.md").read_text(encoding="utf-8")
    assert "STALE SENTINEL" not in generated
    assert "## Observations" in generated


# eof
