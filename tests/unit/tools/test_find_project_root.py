"""Tests for shared project-root resolution across the tools package.

Fix: Verify `PRJ_DIR` takes priority when it already points at a Git root.

Fix: Verify the shared helper falls back to the upward `.git` scan when
`PRJ_DIR` is set but does not point at a Git root.

Fix: Verify tools such as the grouped commit prompt resolve their default root
through the shared helper when no explicit override is provided.

Fix: Add explicit pytest fixture types so Ruff accepts the new test coverage.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tools import group_commit_message_prompt
from tools._models import find_project_root

if TYPE_CHECKING:
    import pytest


def test_find_project_root_prefers_prj_dir_git_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """`PRJ_DIR` should win when it already points at a Git-rooted project."""
    prj_dir_root = tmp_path / "consumer-project"
    (prj_dir_root / ".git").mkdir(parents=True)

    fallback_root = tmp_path / "copilot-shared"
    (fallback_root / ".git").mkdir(parents=True)
    nested_start = fallback_root / "tools" / "nested"
    nested_start.mkdir(parents=True)

    monkeypatch.setenv("PRJ_DIR", str(prj_dir_root))

    assert find_project_root(nested_start) == prj_dir_root.resolve()


def test_find_project_root_falls_back_when_prj_dir_has_no_git(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The upward scan should run when `PRJ_DIR` is not itself a Git root."""
    invalid_prj_dir = tmp_path / "not-a-root"
    invalid_prj_dir.mkdir()

    fallback_root = tmp_path / "copilot-shared"
    (fallback_root / ".git").mkdir(parents=True)
    nested_start = fallback_root / "tools" / "nested"
    nested_start.mkdir(parents=True)

    monkeypatch.setenv("PRJ_DIR", str(invalid_prj_dir))

    assert find_project_root(nested_start) == fallback_root.resolve()


def test_group_commit_prompt_main_uses_shared_root_helper_without_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The prompt tool should resolve its default root through `find_project_root`."""
    captured_messages: list[str] = []
    captured_clipboard: list[str] = []
    ready_line = "ready"
    prompt = "prompt"
    root_calls: list[Path] = []

    def fake_configure_logging(*, debug: bool) -> None:
        assert debug is False

    def fake_find_project_root(start: Path) -> Path:
        root_calls.append(start)
        return tmp_path

    def fake_prepare_group_commit_prompt(root: Path) -> tuple[str, str]:
        assert root == tmp_path
        return ready_line, prompt

    monkeypatch.setattr(
        group_commit_message_prompt,
        "_configure_logging",
        fake_configure_logging,
    )
    monkeypatch.setattr(
        group_commit_message_prompt,
        "find_project_root",
        fake_find_project_root,
    )
    monkeypatch.setattr(
        group_commit_message_prompt,
        "_prepare_group_commit_prompt",
        fake_prepare_group_commit_prompt,
    )
    monkeypatch.setattr(
        group_commit_message_prompt,
        "_set_clipboard_text",
        captured_clipboard.append,
    )
    monkeypatch.setattr(
        group_commit_message_prompt.LOGGER,
        "info",
        captured_messages.append,
    )

    assert group_commit_message_prompt.main([]) == 0
    assert root_calls == [Path.cwd()]
    assert captured_messages == [ready_line]
    assert captured_clipboard == [prompt]


# eof
