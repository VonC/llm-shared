"""Shared fixtures for the git-history dashboard acceptance tests.

Step 5 (v0.8.0): the acceptance run goes through ``write_dashboard``. This
fixture records the Git export and Markdown conversion boundaries so the tests
exercise parse -> aggregate -> analysis-files -> render without repeated child
processes. Focused build and analysis tests retain both real seams.
"""
# pytest invokes the autouse fixture, which pyright cannot see as used.
# pyright: reportUnusedFunction=false

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.git_history_dashboard import analysis, build

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

_HISTORY_BY_PROJECT = {
    "alpha": (
        "a1|2026-01-02 10:00:00 +0000|Ann Dev|feat(cli): start alpha\n"
        "a2|2026-01-03 11:00:00 +0000|Ann Dev|fix(io): patch alpha\n"
    ),
    "beta": "b1|2026-01-04 12:00:00 +0000|Bob Dev|docs: describe beta\n",
    "solo": "s1|2026-01-05 13:00:00 +0000|Ann Dev|feat: only commit\n",
}


def _fake_convert(markdown_text: str) -> str:
    """Return the markdown wrapped in a div, standing in for the uv seam."""
    return f'<div class="analysis">{markdown_text}</div>'


def _recorded_export(repo_dir: Path, csv_path: Path) -> Path:
    """Write recorded Git output; build tests own the real subprocess seam."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.write_text(_HISTORY_BY_PROJECT[repo_dir.name], encoding="utf-8")
    return csv_path


@pytest.fixture(scope="module", autouse=True)
def _stub_markdown_conversion() -> Generator[None]:
    """Replace external conversion and Git duration with recorded boundaries."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(analysis, "convert_markdown", _fake_convert)
        monkeypatch.setattr(build, "export_git_history_csv", _recorded_export)
        yield


# eof
