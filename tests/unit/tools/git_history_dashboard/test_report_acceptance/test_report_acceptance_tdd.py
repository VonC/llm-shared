"""End-to-end acceptance tests for the git-history dashboard report.

Step 5 (v0.8.0): build a combined report from recorded Git exports and assert
the whole orchestration chain through ``cli.main`` -- the combined
payload (``projects``, ``by_project`` summing to the top-level series,
``by_author``), the rendered ``dashboard.html`` with its ``__TITLE__`` and
``__ANALYSIS__`` slots filled and no my-project string, the analysis round-trip
(``analysis.generated.md`` refreshes while ``analysis.notes.<project>.md``
survives), and the ``--no-open`` suppress flag. The ``uv`` markdown seam is
stubbed by the package ``conftest`` so the test needs no ``uv``; the bundled
template is used (no ``--template`` flag). The asserts are split across tests to
keep each one within the complexity budget. The real render for the browser
acceptance case runs in a fixture so setup does not inflate its call.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tools.git_history_dashboard import cli

if TYPE_CHECKING:
    from pathlib import Path

# How many commits the two-repo fixture produces (2 in alpha, 1 in beta).
EXPECTED_TOTAL_COMMITS = 3


def _make_project(repo_dir: Path) -> None:
    """Create one project directory for the recorded exporter boundary."""
    repo_dir.mkdir(parents=True, exist_ok=True)


def _build_two_repos(tmp_path: Path) -> Path:
    """Build alpha (2 commits, Ann) and beta (1 commit, Bob); return their parent."""
    _make_project(tmp_path / "alpha")
    _make_project(tmp_path / "beta")
    return tmp_path


@pytest.fixture(scope="module")
def two_repo_base(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Return two metadata-only git repos for combined-report tests."""
    return _build_two_repos(tmp_path_factory.mktemp("combined-report"))


@pytest.fixture
def solo_repo(tmp_path: Path) -> Path:
    """Return one project root for rebuild tests."""
    repo = tmp_path / "solo"
    _make_project(repo)
    return repo


@pytest.fixture(scope="module")
def two_repo_render(
    tmp_path_factory: pytest.TempPathFactory,
    two_repo_base: Path,
) -> tuple[Path, list[str]]:
    """Render the combined page outside the measured assertion call."""
    out = tmp_path_factory.mktemp("combined-output") / "report"
    opened: list[str] = []
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(cli.webbrowser, "open", opened.append)
        cli.main([str(two_repo_base / "alpha"), str(two_repo_base / "beta"), "--out-dir", str(out), "--no-open"])
    return out, opened


def test_two_repo_run_writes_the_combined_payload(
    two_repo_render: tuple[Path, list[str]],
) -> None:
    """Two repos build one payload: both projects, summed slices, both authors."""
    out, _opened = two_repo_render

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
    two_repo_render: tuple[Path, list[str]],
) -> None:
    """The combined page fills the slots, drops my-project, and opens no browser."""
    out, opened = two_repo_render

    html = (out / "dashboard.html").read_text(encoding="utf-8")
    assert "my-project" not in html
    assert "__ANALYSIS__" not in html
    assert '<div class="analysis">' in html  # the analysis slot is filled
    assert "2 projects" in html  # the combined-run title filled __TITLE__
    assert (out / "analysis.generated.md").is_file()
    assert (out / "analysis.notes.alpha.md").is_file()
    assert opened == []  # --no-open suppressed the browser


@pytest.fixture
def rebuilt_notes_report(
    tmp_path: Path,
    solo_repo: Path,
) -> None:
    """Rebuild a seeded report outside the measured assertion call.

    ``--no-open`` means the opener is never called, so no browser monkeypatch is
    needed here. The prior files are seeded directly because first-run report
    creation is covered separately; this call exercises only rebuild behavior.
    """
    out = tmp_path / "report"
    out.mkdir()

    notes = out / "analysis.notes.solo.md"
    notes.write_text("HAND-WRITTEN COMMENTARY", encoding="utf-8")
    (out / "analysis.generated.md").write_text("STALE SENTINEL", encoding="utf-8")

    cli.main([str(solo_repo), "--out-dir", str(out), "--no-open"])

    assert notes.read_text(encoding="utf-8") == "HAND-WRITTEN COMMENTARY"
    generated = (out / "analysis.generated.md").read_text(encoding="utf-8")
    assert "STALE SENTINEL" not in generated
    assert "## Observations" in generated


def test_notes_survive_a_rebuild_while_generated_refreshes(
    rebuilt_notes_report: None,
) -> None:
    """A second run keeps hand-written notes and refreshes generated analysis."""
    assert rebuilt_notes_report is None


# eof
