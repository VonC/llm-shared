"""Tests for the git batch commit workflow helpers and script entry points.

Cover the input-reading workflow helpers (`_read_input_content` and
`_read_and_parse_content`), direct fatal-exit handling, and `__main__`
execution of the `tools.git_batch_commit` script hub.

Fix: split for the repo line budget -- these tests moved out of
`test_git_batch_commit_parsing.py` (which keeps the parser and clipboard
coverage and the full fix history), with the shared commit-plan builders
in `git_batch_commit_test_support.py`. The workflow-module
`find_project_root` patches are kept so the `__main__` tests stay
isolated from the real repository `a.commit`.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

import tools
from tests.unit.tools.git_batch_commit_test_support import (
    return_project_root,
    valid_commit_message,
)
from tools import git_batch_commit as git_batch_commit_script
from tools import git_batch_commit_models as git_batch_models
from tools import git_batch_commit_workflow as git_batch_workflow

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

_EXPECTED_TWO = 2


def _return_valid_message(_root: Path, _filename: str | None) -> str:
    return valid_commit_message()


def _return_empty_message(_root: Path, _filename: str | None) -> str:
    return ""


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
        commit_message=valid_commit_message(),
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
        "git add -A src/example.py\n" + valid_commit_message(),
        encoding="utf-8",
    )

    monkeypatch.setattr(tools, "find_project_root", return_project_root(project_root))
    # The workflow module binds find_project_root at import time, so the
    # tools-level patch alone would leave the run reading the real a.commit.
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        return_project_root(project_root),
    )
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
        return_project_root(tmp_path),
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
