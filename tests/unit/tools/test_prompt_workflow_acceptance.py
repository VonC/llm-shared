"""Acceptance tests running prompt_workflow as a script via its __main__ guard.

Fix: Cover the ``__main__`` entry point for both the success path (a prompt is
written and memory is recorded) and the fatal path (a workflow error exits with
code 2 through ``_log_fatal``).
"""

from __future__ import annotations

import runpy
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow
from tools import prompt_workflow_git as git
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_menu as menu
from tools.prompt_workflow_models import PromptWorkflowError

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

_FATAL_EXIT_CODE = 2


def _which_identity(name: str) -> str:
    return name


def _fake_subprocess_run(
    command: list[str],
    **kwargs: object,
) -> subprocess.CompletedProcess[str]:
    del kwargs
    return subprocess.CompletedProcess(command, 0, stdout="")


def test_script_runs_as_main_and_writes_prompt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Running as __main__ resolves a topic, writes the prompt, records memory."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("# Draft\n", encoding="utf-8")

    monkeypatch.setattr(git, "current_branch", lambda _cwd: "main")
    monkeypatch.setattr(
        git,
        "working_tree_changed_files",
        lambda _cwd: ["docs/draft.v9.8.0.iso.md"],
    )
    monkeypatch.setattr(git, "fork_point", lambda _cwd: None)
    monkeypatch.setattr(menu, "select", lambda _message, options: options[0][1])
    monkeypatch.setattr(shutil, "which", _which_identity)
    monkeypatch.setattr(subprocess, "run", _fake_subprocess_run)

    script_path = prompt_workflow.__file__
    monkeypatch.setattr(sys, "argv", [script_path, "--root", str(tmp_path)])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(script_path, run_name="__main__")

    assert excinfo.value.code == 0
    assert (tmp_path / "a.prompt.txt").is_file()
    record = memory.read_memory(tmp_path)
    assert record is not None
    assert record.step == 1


def test_script_logs_fatal_on_workflow_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A workflow error during the run exits with the fatal code via __main__."""
    def boom(_cwd: object) -> str:
        message = "no branch"
        raise PromptWorkflowError(message)

    monkeypatch.setattr(git, "current_branch", boom)

    script_path = prompt_workflow.__file__
    monkeypatch.setattr(sys, "argv", [script_path, "--root", str(tmp_path)])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(script_path, run_name="__main__")

    assert excinfo.value.code == _FATAL_EXIT_CODE


# eof
