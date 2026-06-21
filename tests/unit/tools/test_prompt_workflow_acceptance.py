"""Acceptance tests running prompt_workflow end to end through its entry points.

Fix: Cover the ``__main__`` entry point for both the success path (a prompt is
written and memory is recorded) and the fatal path (a workflow error exits with
code 2 through ``_log_fatal``).

Fix (handoff chain, Step 4): drive ``main(["handoff", ...])`` against a temp
project (draft, plan, validation plan) for the three forward transitions of the
implement cycle -- ``check`` to the check prompt, ``after-check`` to the
implement-missing prompt on a ``No`` step and to the commit prompt on a ``Yes``
step, and the direct ``commit`` -- and assert the delivered ``a.prompt.txt`` names
the expected instruction and the recorded memory carries the expected step. The
real ``build_cycle_prompt`` runs; only the git reads and the clipboard are
monkeypatched (Q05), since the git helpers have their own tests.
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
from tools.prompt_workflow_models import MemoryRecord, PromptWorkflowError

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

_FATAL_EXIT_CODE = 2

# The plan step the handoff chain works on in these scenarios, and its title as
# written in the temp plan's ``### Step 2.`` heading (read by read_step_title).
_STEP = "2"
_STEP_TITLE = "The handoff subcommand and its orchestration"

# Validation-plan bodies for the named step, one per status the check can write.
_PLACEHOLDER = (
    "### Analysis of Step 2 implementation state\n\nNot started yet.\n"
)
_NO = (
    "### Analysis of Step 2 implementation state\n\nNo. Step 2 is not fully implemented.\n"
)
_YES = (
    "### Analysis of Step 2 implementation state\n\nYes. Step 2 is fully implemented.\n"
)

# The staged set the commit prompt lists; the validation plan is among it, so the
# prompt is completed with the ``record step <x> validation`` final-commit line.
_VALIDATION_RELPATH = "docs/plan.v0.1.0.pw_handoff.validation.md"
_STATUS_ENTRIES = [
    ("M ", _VALIDATION_RELPATH),
    ("A ", "tools/prompt_workflow_handoff.py"),
]
_STAGED_FILES = [entry[1] for entry in _STATUS_ENTRIES]


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


def _build_project(tmp_path: Path, validation_text: str) -> None:
    """Create the draft, plan and validation plan a handoff resolves against.

    The single draft makes the topic resolve with no menu, the plan carries the
    ``### Step 2.`` heading ``read_step_title`` reads, and the validation plan
    carries the ``Analysis of Step 2`` status line the after-check routing reads.
    """
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v0.1.0.pw_handoff.md").write_text("# Draft\n", encoding="utf-8")
    (docs_dir / "plan.v0.1.0.pw_handoff.md").write_text(
        f"## Numbered steps\n\n### Step {_STEP}. {_STEP_TITLE}\n",
        encoding="utf-8",
    )
    (docs_dir / "plan.v0.1.0.pw_handoff.validation.md").write_text(
        validation_text,
        encoding="utf-8",
    )


def _wire_handoff(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Monkeypatch the git reads and the clipboard; return the stage-all log.

    The single draft and a None fork point resolve the topic without a menu; the
    status entries and staged files feed the real commit-prompt build; the
    clipboard is a no-op so no PowerShell runs. The returned list records each
    ``git add -A`` the commit and after-check-Yes handoffs make (Q61).
    """
    staged_calls: list[str] = []
    monkeypatch.setattr(git, "current_branch", lambda _cwd: "main")
    monkeypatch.setattr(
        git,
        "working_tree_changed_files",
        lambda _cwd: ["docs/draft.v0.1.0.pw_handoff.md"],
    )
    monkeypatch.setattr(git, "fork_point", lambda _cwd: None)
    monkeypatch.setattr(git, "has_step_commit", lambda _cwd, _step, _base: False)
    monkeypatch.setattr(git, "status_entries", lambda _cwd: _STATUS_ENTRIES)
    monkeypatch.setattr(git, "staged_files", lambda _cwd: _STAGED_FILES)
    monkeypatch.setattr(git, "stage_all", lambda _cwd: staged_calls.append("add -A"))
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)
    return staged_calls


def _delivered_prompt(tmp_path: Path) -> str:
    """Return the prompt text the handoff wrote to ``a.prompt.txt``."""
    return (tmp_path / "a.prompt.txt").read_text(encoding="utf-8")


def _assert_commit_prompt(tmp_path: Path, prompt: str, staged_calls: list[str]) -> None:
    """Assert the commit prompt, the emptied a.commit, and the recorded memory."""
    # Every fragment of the real commit body, the staged log block, and the
    # ``record step <x> validation`` final-commit line the staged validation plan
    # triggers (Q16); checked as one membership scan to keep the branch count low.
    expected = (
        "group-commits-msg.md and do the following:",
        "for those 2 files, per step 2",
        f'("{_STEP_TITLE}")',
        'of the implementation plan "docs/plan.v0.1.0.pw_handoff.md"',
        "```log",
        f"M  {_VALIDATION_RELPATH}",
        "A  tools/prompt_workflow_handoff.py",
        "docs(pw_handoff): record step 2 validation",
    )
    missing = [fragment for fragment in expected if fragment not in prompt]
    assert not missing, f"missing from commit prompt: {missing}"
    # a.commit is emptied for the commit prompt so the grouping starts clean (Q25).
    assert (tmp_path / "a.commit").read_text(encoding="utf-8") == ""
    # git add -A ran once before the prompt was built (Q61).
    assert staged_calls == ["add -A"]
    assert memory.read_memory(tmp_path) == MemoryRecord(
        branch="main",
        version="v0.1.0",
        topic="pw_handoff",
        step=12,
        instruction="group-commits-msg.md",
        plan_step="2",
    )


def test_handoff_check_delivers_check_prompt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Check hands off to the implementation-check prompt for the named step."""
    _build_project(tmp_path, _PLACEHOLDER)
    staged_calls = _wire_handoff(monkeypatch)

    assert prompt_workflow.main(["handoff", "check", _STEP, "--root", str(tmp_path)]) == 0

    prompt = _delivered_prompt(tmp_path)
    assert "implementation-check.md and do the following:" in prompt
    assert f'Check step 2 "{_STEP_TITLE}" implementation' in prompt
    assert staged_calls == []
    assert memory.read_memory(tmp_path) == MemoryRecord(
        branch="main",
        version="v0.1.0",
        topic="pw_handoff",
        step=11,
        instruction="implementation-check.md",
        plan_step="2",
    )


def test_handoff_after_check_no_delivers_implement_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """after-check on a No step hands off to the implement-missing prompt (Q58)."""
    _build_project(tmp_path, _NO)
    staged_calls = _wire_handoff(monkeypatch)

    assert (
        prompt_workflow.main(["handoff", "after-check", _STEP, "--root", str(tmp_path)])
        == 0
    )

    prompt = _delivered_prompt(tmp_path)
    assert "implement-missing-step.md and do the following:" in prompt
    assert f'Implement the missing work of step 2 "{_STEP_TITLE}"' in prompt
    assert '"Missing work for Step 2" section' in prompt
    # The split-large-file reminder resolves its {prefix} to a real path (Q50).
    assert "instructions/split-large-file.md" in prompt
    assert staged_calls == []
    assert memory.read_memory(tmp_path) == MemoryRecord(
        branch="main",
        version="v0.1.0",
        topic="pw_handoff",
        step=10,
        instruction="implement-missing-step.md",
        plan_step="2",
    )


def test_handoff_after_check_yes_delivers_commit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """after-check on a Yes step hands off to the commit prompt and stages all."""
    _build_project(tmp_path, _YES)
    (tmp_path / "a.commit").write_text("stale group\n", encoding="utf-8")
    staged_calls = _wire_handoff(monkeypatch)

    assert (
        prompt_workflow.main(["handoff", "after-check", _STEP, "--root", str(tmp_path)])
        == 0
    )

    _assert_commit_prompt(tmp_path, _delivered_prompt(tmp_path), staged_calls)


def test_handoff_commit_delivers_commit_prompt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The direct commit token writes the commit prompt and empties a.commit (Q62)."""
    _build_project(tmp_path, _YES)
    (tmp_path / "a.commit").write_text("stale group\n", encoding="utf-8")
    staged_calls = _wire_handoff(monkeypatch)

    assert prompt_workflow.main(["handoff", "commit", _STEP, "--root", str(tmp_path)]) == 0

    _assert_commit_prompt(tmp_path, _delivered_prompt(tmp_path), staged_calls)


# eof
