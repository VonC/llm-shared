"""Tests for grouped commit prompt preparation.

Fix: Verify the staged-diff prompt tool writes `a.diff`, clears `a.commit`,
formats the staged porcelain lines inside a fenced `log` block, and copies one
ready-to-paste grouped commit message prompt with a trailing `Context: ` line.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import group_commit_message_prompt

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


class TestGroupCommitMessagePromptTDD:
    """Validate fenced prompt assembly and entry-point dispatch."""

    def test_filter_staged_porcelain_lines_keeps_only_indexed_entries(self) -> None:
        """Only staged porcelain lines should be kept in the prompt body."""
        status_text = (
            "M  src/example.py\n"
            " M src/unstaged_only.py\n"
            "?? src/untracked.py\n"
            "A  src/new_file.py\n"
            "R  old.py -> new.py"
        )

        result = group_commit_message_prompt._filter_staged_porcelain_lines(
            status_text,
        )

        assert result == [
            "M  src/example.py",
            "A  src/new_file.py",
            "R  old.py -> new.py",
        ]

    def test_build_group_commit_prompt_includes_status_lines_and_blank_tail(
        self,
    ) -> None:
        """The prompt should contain the header, fenced log lines, and context."""
        result = group_commit_message_prompt.build_group_commit_prompt(
            2,
            [
                "M  src/example.py",
                "A  src/new_file.py",
            ],
        )

        assert result == (
            "/group-commits-msg for those 2 files:\n\n"
            "```log\n"
            "M  src/example.py\n"
            "A  src/new_file.py\n"
            "```\n\n"
            "Context: "
        )

    def test_prepare_group_commit_prompt_writes_diff_and_clears_a_commit(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Preparing the prompt should write `a.diff` and empty `a.commit`."""
        (tmp_path / "a.commit").write_text(
            "existing grouped commit text",
            encoding="utf-8",
        )

        diff_text = (
            "diff --git a/one.py b/one.py\n"
            "@@ -1 +1 @@\n"
            "diff --git a/two.py b/two.py"
        )
        status_text = "M  src/one.py\n M src/not_staged.py\nA  src/two.py"

        def fake_run_git_text(args: list[str], *, cwd: Path) -> str:
            assert cwd == tmp_path
            if args == ["diff", "--cached"]:
                return diff_text
            if args == ["status", "--porcelain"]:
                return status_text
            msg = f"Unexpected git args: {args}"
            raise AssertionError(msg)

        monkeypatch.setattr(
            group_commit_message_prompt,
            "_run_git_text",
            fake_run_git_text,
        )

        ready_line, prompt = group_commit_message_prompt._prepare_group_commit_prompt(
            tmp_path,
        )

        assert ready_line == (
            "/group-commits-msg for those 2 files: Ready to paste from clipboard into the LLM prompt."
        )
        assert prompt == (
            "/group-commits-msg for those 2 files:\n\n"
            "```log\n"
            "M  src/one.py\n"
            "A  src/two.py\n"
            "```\n\n"
            "Context: "
        )
        assert (tmp_path / "a.diff").read_text(encoding="utf-8") == diff_text
        assert (tmp_path / "a.commit").read_text(encoding="utf-8") == ""

    def test_main_logs_ready_line_and_copies_prompt(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """The entry point should log one ready line and copy the full prompt."""
        captured_messages: list[str] = []
        captured_clipboard: list[str] = []
        ready_line = (
            "/group-commits-msg for those 3 files: Ready to paste from "
            "clipboard into the LLM prompt."
        )
        prompt = (
            "/group-commits-msg for those 3 files:\n\n"
            "```log\n"
            "M  src/one.py\n"
            "```\n\n"
            "Context: "
        )

        def fake_configure_logging(*, debug: bool) -> None:
            del debug

        def fake_prepare_group_commit_prompt(root: Path) -> tuple[str, str]:
            del root
            return ready_line, prompt

        monkeypatch.setattr(
            group_commit_message_prompt,
            "_configure_logging",
            fake_configure_logging,
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

        result = group_commit_message_prompt.main(["--root", str(tmp_path)])

        assert result == 0
        assert captured_messages == [ready_line]
        assert captured_clipboard == [prompt]


# eof
