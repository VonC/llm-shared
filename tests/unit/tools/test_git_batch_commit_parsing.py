"""Tests for split git batch commit parsing, workflow helpers, and script entry points.

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
"""

from __future__ import annotations

import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

import tools
from tools import git_batch_commit as git_batch_commit_script
from tools import git_batch_commit_models as git_batch_models
from tools import git_batch_commit_parsing as git_batch_parsing
from tools import git_batch_commit_workflow as git_batch_workflow

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

if TYPE_CHECKING:
    from collections.abc import Callable

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


def _return_project_root(project_root: Path) -> Callable[[Path], Path]:
    def fake_find_project_root(_start_path: Path) -> Path:
        return project_root

    return fake_find_project_root


def _return_valid_message(_root: Path, _filename: str | None) -> str:
    return _valid_commit_message()


def _return_empty_message(_root: Path, _filename: str | None) -> str:
    return ""


def _valid_commit_lines(title: str = "fix(scope): title") -> list[str]:
    return [
        title,
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
        "- change two",
    ]


def _valid_commit_message(title: str = "fix(scope): title") -> str:
    return "\n".join(_valid_commit_lines(title))


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
    lines = [*_valid_commit_lines(), "```"]

    commit_message, commit_title, next_idx = git_batch_parsing._parse_commit_message(
        lines,
        0,
    )

    assert commit_message == _valid_commit_message()
    assert commit_title == "fix(scope): title"
    assert next_idx == len(_valid_commit_lines())


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
            *_valid_commit_lines("fix(scope): second"),
        ],
    )
    monkeypatch.setattr("builtins.input", _input_skip)

    blocks = git_batch_parsing.parse_clipboard_content(content, interactive=True)

    assert blocks == [
        git_batch_models.CommitBlock(
            git_adds=["git add -A src/two.py"],
            commit_message=_valid_commit_message("fix(scope): second"),
            commit_title="fix(scope): second",
        ),
    ]


def test_parse_clipboard_content_returns_valid_blocks_for_clean_input() -> None:
    """Clipboard parsing should build a commit block from a valid input chunk."""
    content = "\n".join(["git add -A src/one.py", *_valid_commit_lines()])

    assert git_batch_parsing.parse_clipboard_content(content, interactive=False) == [
        git_batch_models.CommitBlock(
            git_adds=["git add -A src/one.py"],
            commit_message=_valid_commit_message(),
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


def test_read_input_content_uses_clipboard_when_filename_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Input reading should delegate to the clipboard helper when no file is given."""

    def fake_get_clipboard_text() -> str:
        return "clipboard"

    monkeypatch.setattr(
        git_batch_workflow,
        "_get_clipboard_text",
        fake_get_clipboard_text,
    )

    assert git_batch_workflow._read_input_content(tmp_path, None) == "clipboard"


def test_read_input_content_wraps_file_read_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Input reading should convert file read errors into `GitBatchCommitError`."""
    input_file = tmp_path / "plan.txt"
    input_file.write_text("content", encoding="utf-8")
    path_type = type(input_file)
    original_read_text = path_type.read_text

    def fake_read_text(self: Path, *, encoding: str) -> str:
        if self == input_file:
            msg = "broken disk"
            raise OSError(msg)
        return original_read_text(self, encoding=encoding)

    monkeypatch.setattr(path_type, "read_text", fake_read_text)

    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match="Failed to read input file",
    ):
        git_batch_workflow._read_input_content(tmp_path, "plan.txt")


@pytest.mark.parametrize("filename", ["missing-plan.txt", "missing/nested-plan.txt"])
def test_read_input_content_raises_for_missing_input_files(
    filename: str,
    tmp_path: Path,
) -> None:
    """Input reading should reject missing file paths before trying to read them."""
    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match="Input file does not exist",
    ):
        git_batch_workflow._read_input_content(tmp_path, filename)


def test_read_and_parse_content_handles_empty_input_and_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Read-and-parse should reject empty input and return parsed commit blocks."""
    block = git_batch_models.CommitBlock(
        git_adds=["git add -A src/example.py"],
        commit_message=_valid_commit_message(),
        commit_title="fix(scope): title",
    )

    def fake_parse_clipboard_content(
        content: str,
        interactive: object,
    ) -> list[git_batch_models.CommitBlock]:
        del content, interactive
        return [block]

    monkeypatch.setattr(
        git_batch_workflow,
        "_read_input_content",
        _return_valid_message,
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "parse_clipboard_content",
        fake_parse_clipboard_content,
    )

    assert git_batch_workflow._read_and_parse_content(
        tmp_path,
        filename="plan.txt",
        interactive=False,
    ) == [block]

    monkeypatch.setattr(
        git_batch_workflow,
        "_read_input_content",
        _return_empty_message,
    )
    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match="Input content is empty",
    ):
        git_batch_workflow._read_and_parse_content(
            tmp_path,
            filename="plan.txt",
            interactive=False,
        )


def test_git_batch_commit_script_runs_as_main_and_exits_zero(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Running the script as `__main__` should insert paths and exit with code 0."""
    project_root = tmp_path
    script_path = Path(git_batch_commit_script.__file__)
    expected_root = str(script_path.parent.parent.resolve())
    expected_src = str((script_path.parent.parent.resolve() / "src").resolve())
    original_sys_path = list(sys.path)
    (project_root / "src").mkdir()
    (project_root / "src" / "example.py").write_text("print('hi')\n", encoding="utf-8")
    (project_root / "a.commit").write_text(
        "git add -A src/example.py\n" + _valid_commit_message(),
        encoding="utf-8",
    )

    monkeypatch.setattr(tools, "find_project_root", _return_project_root(project_root))
    monkeypatch.setattr(sys, "argv", [str(script_path), "a.commit", "--dry-run"])

    try:
        with pytest.raises(SystemExit) as excinfo:
            runpy.run_path(str(script_path), run_name="__main__")

        assert excinfo.value.code == 0
        assert expected_root in sys.path
        assert expected_src in sys.path
    finally:
        sys.path[:] = original_sys_path


def test_git_batch_commit_script_logs_fatal_for_root_workflow_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Script execution should translate root-workflow failures into exit code 2."""
    script_path = Path(git_batch_commit_script.__file__)

    # Patch the name the workflow module actually calls: it binds
    # find_project_root at import time, so patching tools.find_project_root
    # alone would leave the test reading the real repository a.commit.
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        _return_project_root(tmp_path),
    )
    monkeypatch.setattr(sys, "argv", [str(script_path), "--root-a-commit"])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(script_path), run_name="__main__")

    assert excinfo.value.code == _EXPECTED_TWO


def test_workflow_log_fatal_configures_logging_and_exits_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Workflow fatal handling should configure logging and exit with code 2."""
    with pytest.raises(SystemExit) as excinfo:
        git_batch_workflow._log_fatal(git_batch_models.GitBatchCommitError("boom"))

    captured = capsys.readouterr()

    assert excinfo.value.code == _EXPECTED_TWO
    assert "ERROR: boom" in captured.out


# eof
