"""Tests for split git batch commit parsing and clipboard input.

Fix: Cover parser branches, clipboard and input helpers, and `__main__`
execution in the split `tools.git_batch_commit` modules.

Fix: Keep parser monkeypatches compatible with keyword-based
`interactive=` calls.

Fix: Cover the workflow missing-input branch and direct fatal-exit handling
without growing the process and root-workflow test files.

Fix: Cover `_ends_what_section` and the wrapped-continuation-line handling in
`_parse_list_items`, so a multi-line What item is parsed in full.

Fix: Patch `find_project_root` on the workflow module instead of the `tools`
package, so the root-workflow fatal test stays isolated from the real
repository `a.commit`.

Fix: Apply the same workflow-module patch to the dry-run `__main__` test,
which still patched only `tools.find_project_root` and therefore read the
real repository `a.commit`, failing whenever that file referenced files
already committed or deleted.

Fix: split for the repo line budget -- the workflow-helper and script
entry-point tests moved to `test_git_batch_commit_entry.py`, and the shared
commit-plan builders to `git_batch_commit_test_support.py`; this file keeps
the parser and clipboard coverage.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

from tests.unit.tools.git_batch_commit_test_support import (
    valid_commit_lines,
    valid_commit_message,
)
from tools import git_batch_commit_models as git_batch_models
from tools import git_batch_commit_parsing as git_batch_parsing

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

_EXPECTED_TWO = 2
_EXPECTED_THREE = 3
_EXPECTED_GIT_ADD_START = 2
_EXPECTED_NEXT_GIT_ADD_INDEX = 5
_EXPECTED_TITLE_INDEX = 6


def _raise_bad_split(_cmd: str, *, posix: bool) -> list[str]:
    del posix
    msg = "bad"
    raise ValueError(msg)


def _return_invalid_split(_cmd: str, *, posix: bool) -> list[str]:
    del posix
    return ["git", "commit"]


def _input_skip(_prompt: str) -> str:
    return "skip"


def _input_stop(_prompt: str) -> str:
    return "stop"


def _return_pwsh(_name: str) -> str:
    return "pwsh"


def test_commit_message_error_keeps_lines_and_faulty_line() -> None:
    """Commit-message errors should expose the parser context they captured."""
    error = git_batch_models.CommitMessageError("bad message", ["one", "two"], "bad")

    assert error.lines_read == ["one", "two"]
    assert error.faulty_line == "bad"
    assert str(error) == "bad message"


def test_commit_title_and_list_item_matchers_cover_true_and_false_cases() -> None:
    """Title and list-item matchers should accept valid lines and reject invalid ones."""
    assert git_batch_parsing._is_commit_title("fix(scope): title") is True
    assert git_batch_parsing._is_commit_title("not a commit title") is False
    assert (
        git_batch_parsing._is_probable_unscoped_commit_title("build: update lock")
        is True
    )
    assert (
        git_batch_parsing._is_probable_unscoped_commit_title("fix(scope): title")
        is False
    )
    assert git_batch_parsing._is_list_item("- item") is True
    assert git_batch_parsing._is_list_item("item") is False


def test_parse_title_raises_when_input_ends() -> None:
    """Title parsing should fail when the parser is already at EOF."""
    state = git_batch_models._ParseState(lines=[], idx=0, lines_read=[])

    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="Expected commit message title",
    ):
        git_batch_parsing._parse_title(state)


def test_parse_title_raises_for_invalid_commit_titles() -> None:
    """Title parsing should reject lines that do not match the conventional title form."""
    state = git_batch_models._ParseState(
        lines=["not a valid title"],
        idx=0,
        lines_read=[],
    )

    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="Invalid commit title format",
    ):
        git_batch_parsing._parse_title(state)


def test_expect_empty_line_raises_when_input_ends() -> None:
    """Empty-line parsing should fail when there is no line left to read."""
    state = git_batch_models._ParseState(lines=[], idx=0, lines_read=[])

    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="Expected empty line",
    ):
        git_batch_parsing._expect_empty_line(state, "after title")


def test_expect_empty_line_raises_when_the_line_is_not_empty() -> None:
    """Empty-line parsing should reject non-empty lines at the current position."""
    state = git_batch_models._ParseState(lines=["not empty"], idx=0, lines_read=[])

    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="Expected empty line",
    ):
        git_batch_parsing._expect_empty_line(state, "after title")


def test_expect_keyword_raises_when_input_ends() -> None:
    """Keyword parsing should fail when the parser is already at EOF."""
    state = git_batch_models._ParseState(lines=[], idx=0, lines_read=[])

    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="Expected 'Why:' section",
    ):
        git_batch_parsing._expect_keyword(state, "Why:")


def test_parse_non_empty_section_returns_lines_and_raises_when_empty() -> None:
    """Non-empty section parsing should stop at a marker and reject empty content."""
    state = git_batch_models._ParseState(
        lines=["reason", "What:", ""],
        idx=0,
        lines_read=[],
    )

    assert git_batch_parsing._parse_non_empty_section(
        state,
        "Why section",
        stop_at="What:",
    ) == ["reason"]
    assert state.idx == 1
    assert state.lines_read == ["reason"]

    empty_state = git_batch_models._ParseState(lines=[""], idx=0, lines_read=[])
    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="Expected non-empty lines",
    ):
        git_batch_parsing._parse_non_empty_section(empty_state, "Why section")


def test_parse_list_items_returns_items_and_raises_when_empty() -> None:
    """List-item parsing should collect `- item` lines and stop at the closing fence."""
    state = git_batch_models._ParseState(
        lines=["- one", "- two", "```"],
        idx=0,
        lines_read=[],
    )

    assert git_batch_parsing._parse_list_items(state) == ["- one", "- two"]
    assert state.idx == _EXPECTED_TWO

    empty_state = git_batch_models._ParseState(lines=["tail"], idx=0, lines_read=[])
    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="Expected at least one list item",
    ):
        git_batch_parsing._parse_list_items(empty_state)


def test_parse_list_items_keeps_wrapped_continuation_lines() -> None:
    """List-item parsing should keep continuation lines of wrapped What items."""
    state = git_batch_models._ParseState(
        lines=[
            "- first change that wraps onto",
            "a second physical line",
            "- second change",
            "```",
        ],
        idx=0,
        lines_read=[],
    )

    expected_items = [
        "- first change that wraps onto",
        "a second physical line",
        "- second change",
    ]
    assert git_batch_parsing._parse_list_items(state) == expected_items
    assert state.idx == _EXPECTED_THREE
    assert state.lines_read == expected_items


def test_ends_what_section_detects_section_boundaries() -> None:
    """The What-section terminator should flag boundaries and keep plain text."""
    assert git_batch_parsing._ends_what_section("") is True
    assert git_batch_parsing._ends_what_section("```") is True
    assert git_batch_parsing._ends_what_section("## Group 2: topic") is True
    assert git_batch_parsing._ends_what_section("git add -A file.py") is True
    assert git_batch_parsing._ends_what_section("fix(scope): title") is True
    assert git_batch_parsing._ends_what_section("a wrapped continuation line") is False


def test_parse_commit_message_returns_text_title_and_next_index() -> None:
    """Commit-message parsing should rebuild the message body and stop at the next line."""
    lines = [*valid_commit_lines(), "```"]

    commit_message, commit_title, next_idx = git_batch_parsing._parse_commit_message(
        lines,
        0,
    )

    assert commit_message == valid_commit_message()
    assert commit_title == "fix(scope): title"
    assert next_idx == len(valid_commit_lines())


def test_skip_helpers_and_parse_git_adds_handle_noise_and_clean_commands() -> None:
    """Git-add parsing should skip noise, ignore blanks, and strip `&&` fragments."""
    lines = [
        "intro",
        "```log",
        "git add -A src/one.py &&",
        "",
        'git add -A "src/two.py"',
        "not a title",
        "fix(scope): title",
    ]

    assert git_batch_parsing._skip_until_git_add(lines, 0) == _EXPECTED_GIT_ADD_START
    git_adds, next_idx = git_batch_parsing._parse_git_adds(
        lines,
        _EXPECTED_GIT_ADD_START,
    )
    assert git_adds == ["git add -A src/one.py", 'git add -A "src/two.py"']
    assert next_idx == _EXPECTED_NEXT_GIT_ADD_INDEX
    assert (
        git_batch_parsing._skip_until_commit_title(lines, next_idx)
        == _EXPECTED_TITLE_INDEX
    )


def test_skip_helpers_return_end_of_input_when_no_match_exists() -> None:
    """Skipping helpers should return the input length when no matching line exists."""
    lines = ["noise", "still noise"]

    assert git_batch_parsing._skip_until_git_add(lines, 0) == len(lines)
    assert git_batch_parsing._skip_until_commit_title(lines, 0) == len(lines)


def test_skip_until_commit_title_rejects_unscoped_title_before_later_block() -> None:
    """Unscoped titles should fail instead of binding paths to a later block."""
    lines = [
        "",
        "```log",
        "build: update pyright lock",
        "",
        "Why:",
        "",
        "reason before",
        "",
        "reason after",
        "",
        "What:",
        "",
        "- change",
        "```",
        "git add -A src/registry.py",
        "refactor(web): split shm recovery",
    ]

    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="Invalid commit title format after git add commands",
    ) as exc_info:
        git_batch_parsing._skip_until_commit_title(lines, 0)

    assert exc_info.value.faulty_line == "build: update pyright lock"


def test_parse_git_add_command_handles_split_errors_and_invalid_commands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Git-add command parsing should reject malformed or non-add commands."""
    monkeypatch.setattr(git_batch_parsing.shlex, "split", _raise_bad_split)
    assert git_batch_parsing._parse_git_add_command("git add -A broken") is None

    monkeypatch.setattr(git_batch_parsing.shlex, "split", _return_invalid_split)
    assert git_batch_parsing._parse_git_add_command("git commit") is None


def test_parse_clipboard_content_skips_invalid_block_on_user_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clipboard parsing should skip a broken block and continue to the next one."""
    content = "\n".join(
        [
            "git add -A src/one.py",
            "fix(scope): broken",
            "",
            "Why:",
            "",
            "reason before",
            "",
            "reason after",
            "git add -A src/two.py",
            *valid_commit_lines("fix(scope): second"),
        ],
    )
    monkeypatch.setattr("builtins.input", _input_skip)

    blocks = git_batch_parsing.parse_clipboard_content(content, interactive=True)

    assert blocks == [
        git_batch_models.CommitBlock(
            git_adds=["git add -A src/two.py"],
            commit_message=valid_commit_message("fix(scope): second"),
            commit_title="fix(scope): second",
        ),
    ]


def test_parse_clipboard_content_returns_valid_blocks_for_clean_input() -> None:
    """Clipboard parsing should build a commit block from a valid input chunk."""
    content = "\n".join(["git add -A src/one.py", *valid_commit_lines()])

    assert git_batch_parsing.parse_clipboard_content(content, interactive=False) == [
        git_batch_models.CommitBlock(
            git_adds=["git add -A src/one.py"],
            commit_message=valid_commit_message(),
            commit_title="fix(scope): title",
        ),
    ]


def test_parse_clipboard_content_raises_when_user_requests_stop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clipboard parsing should surface the commit error when the user stops."""
    content = "git add -A src/one.py\nfix(scope): broken\n\nWhy:\n"
    monkeypatch.setattr("builtins.input", _input_stop)

    with pytest.raises(git_batch_models.CommitMessageError):
        git_batch_parsing.parse_clipboard_content(content, interactive=True)


def test_parse_clipboard_content_re_raises_invalid_messages_in_noninteractive_mode() -> (
    None
):
    """Non-interactive parsing should re-raise invalid commit-message errors."""
    content = "git add -A src/one.py\nfix(scope): broken\n\nWhy:"

    with pytest.raises(git_batch_models.CommitMessageError):
        git_batch_parsing.parse_clipboard_content(content, interactive=False)


def test_parse_clipboard_content_rejects_unscoped_title_before_next_commit() -> None:
    """Root plan validation should fail before a git-add block drifts forward."""
    content = "\n".join(
        [
            "git add -A uv.lock",
            "",
            "```log",
            "build: update pyright lock",
            "",
            "Why:",
            "",
            "reason before",
            "",
            "reason after",
            "",
            "What:",
            "",
            "- change one",
            "```",
            "",
            "git add -A src/registry.py",
            *valid_commit_lines("refactor(web): split shm recovery"),
        ],
    )

    with pytest.raises(
        git_batch_models.CommitMessageError,
        match="expected 'type\\(scope\\): subject'",
    ) as exc_info:
        git_batch_parsing.parse_clipboard_content(content, interactive=False)

    assert exc_info.value.faulty_line == "build: update pyright lock"


def test_parse_clipboard_content_warns_when_commit_message_is_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Clipboard parsing should warn and stop when a git-add block has no title."""
    caplog.set_level("WARNING")

    assert (
        git_batch_parsing.parse_clipboard_content(
            "git add -A src/one.py\nnoise",
            interactive=False,
        )
        == []
    )
    assert "Found git add commands but no commit message" in caplog.text


def test_parse_clipboard_content_handles_empty_git_add_parse_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clipboard parsing should advance safely when git-add parsing returns no commands."""
    calls = {"count": 0}

    def fake_skip_until_git_add(lines: list[str], start_idx: int) -> int:
        del lines, start_idx
        calls["count"] += 1
        return 0 if calls["count"] == 1 else 1

    def fake_parse_git_adds(
        _lines: list[str],
        _start_idx: int,
    ) -> tuple[list[str], int]:
        return [], 0

    monkeypatch.setattr(
        git_batch_parsing,
        "_skip_until_git_add",
        fake_skip_until_git_add,
    )
    monkeypatch.setattr(git_batch_parsing, "_parse_git_adds", fake_parse_git_adds)

    assert (
        git_batch_parsing.parse_clipboard_content(
            "git add -A src/one.py",
            interactive=False,
        )
        == []
    )


def test_parse_clipboard_content_returns_empty_when_no_git_add_is_present() -> None:
    """Clipboard parsing should return no blocks when the input has no git-add command."""
    assert (
        git_batch_parsing.parse_clipboard_content("noise only", interactive=False) == []
    )


def test_get_clipboard_text_reads_stdout_and_wraps_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clipboard reads should trim stdout and wrap subprocess failures."""

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        return subprocess.CompletedProcess(command, 0, stdout="text from clipboard\n")

    monkeypatch.setattr(shutil, "which", _return_pwsh)
    monkeypatch.setattr(git_batch_parsing.subprocess, "run", fake_run)

    assert git_batch_parsing._get_clipboard_text() == "text from clipboard"

    def failing_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(git_batch_parsing.subprocess, "run", failing_run)
    with pytest.raises(
        git_batch_models.ClipboardError,
        match="Failed to read clipboard",
    ):
        git_batch_parsing._get_clipboard_text()


# eof
