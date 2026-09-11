"""Tests for review-exchange launcher isolation in consuming repositories."""

from pathlib import Path

_PROJECT_ROOT = Path(__file__).parents[3]


def test_launcher_prefers_shared_tools_and_the_consuming_git_root() -> None:
    """A consuming ``tools`` package or stale ``PRJ_DIR`` cannot redirect it."""
    launcher = (_PROJECT_ROOT / "bin" / "review_exchange.bat").read_text(
        encoding="utf-8",
    )

    assert 'set "PYTHONPATH=%LLM_SHARED_DIR%;%PYTHONPATH%"' in launcher
    assert 'set "PYTHONPATH=%LLM_SHARED_DIR%"' in launcher
    assert r'if exist "%CD%\.git" set "PRJ_DIR=%CD%"' in launcher


# eof
