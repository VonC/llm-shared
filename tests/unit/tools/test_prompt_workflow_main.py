"""Tests for the orchestration and IO of prompt_workflow.

Fix: Cover logging setup, the clipboard wrapper and its fallback, topic choice
and ordering, the menu options, and the run/main entry points across the
no-topic, cancelled, mismatched-memory and happy paths.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow
from tools import prompt_workflow_memory as memory
from tools.prompt_workflow_models import (
    MemoryRecord,
    StepAlternative,
    Topic,
    WorkflowState,
)

if TYPE_CHECKING:
    from collections.abc import Callable

# pyright: reportPrivateUsage=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false
# ruff: noqa: SLF001

_TOPIC = Topic(version="v9.8.0", slug="iso", draft_path=Path("docs/draft.v9.8.0.iso.md"))
_OTHER = Topic(version="v1.0.0", slug="other", draft_path=Path("docs/draft.v1.0.0.other.md"))


def _state(**overrides: object) -> WorkflowState:
    base: dict[str, object] = {
        "requirement": Path("r"),
        "design": Path("d"),
        "plan": Path("p"),
        "validation_plan": None,
        "requirement_has_open_questions": False,
        "design_has_open_questions": False,
        "memory_step": None,
    }
    base.update(overrides)
    return WorkflowState(**base)  # type: ignore[arg-type]


def _which_pwsh(_name: str) -> str:
    return "pwsh"


def test_configure_logging_levels() -> None:
    """Logging setup switches level and installs a single stdout handler."""
    root_logger = logging.getLogger()
    original = list(root_logger.handlers)
    try:
        prompt_workflow._configure_logging(debug=True)
        assert root_logger.level == logging.DEBUG
        prompt_workflow._configure_logging(debug=False)
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) == 1
    finally:
        root_logger.handlers.clear()
        for handler in original:
            root_logger.addHandler(handler)


def test_set_clipboard_text_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """A clipboard write runs PowerShell with the text on stdin."""
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(shutil, "which", _which_pwsh)
    monkeypatch.setattr(prompt_workflow.subprocess, "run", fake_run)

    prompt_workflow.set_clipboard_text("hello")

    assert captured["input"] == "hello"


def test_set_clipboard_text_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """A clipboard failure becomes a ClipboardError."""

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(shutil, "which", _which_pwsh)
    monkeypatch.setattr(prompt_workflow.subprocess, "run", fake_run)

    with pytest.raises(prompt_workflow.ClipboardError, match="Failed to write clipboard"):
        prompt_workflow.set_clipboard_text("hello")


def test_deliver_prompt_copies_to_clipboard(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Delivery writes the file and copies the prompt when the clipboard works."""
    copied: list[str] = []
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", copied.append)

    prompt_workflow.deliver_prompt(tmp_path, "PROMPT")

    assert (tmp_path / "a.prompt.txt").read_text(encoding="utf-8") == "PROMPT"
    assert copied == ["PROMPT"]


def test_deliver_prompt_falls_back_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """When the clipboard fails the prompt is logged and still written to file."""
    def boom(_text: str) -> None:
        message = "no clipboard"
        raise prompt_workflow.ClipboardError(message)

    infos: list[str] = []
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", boom)
    monkeypatch.setattr(prompt_workflow.LOGGER, "warning", lambda *_a: None)
    monkeypatch.setattr(prompt_workflow.LOGGER, "info", infos.append)

    prompt_workflow.deliver_prompt(tmp_path, "PROMPT")

    assert (tmp_path / "a.prompt.txt").read_text(encoding="utf-8") == "PROMPT"
    assert "PROMPT" in infos


def test_memory_matches_and_order() -> None:
    """Memory matching checks branch, version and slug; ordering puts it first."""
    record = MemoryRecord(branch="main", version="v9.8.0", topic="iso")
    assert prompt_workflow._memory_matches(None, _TOPIC, "main") is False
    assert prompt_workflow._memory_matches(record, _TOPIC, "other-branch") is False
    assert prompt_workflow._memory_matches(record, _TOPIC, "main") is True

    ordered = prompt_workflow._order_topics([_OTHER, _TOPIC], record, "main")
    assert ordered == [_TOPIC, _OTHER]


def test_choose_topic_single_and_menu(monkeypatch: pytest.MonkeyPatch) -> None:
    """A lone topic is used directly; several topics go through the menu."""
    assert prompt_workflow.choose_topic([_TOPIC], None, "main") == _TOPIC

    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda _message, options: options[0][1],
    )
    assert prompt_workflow.choose_topic([_OTHER, _TOPIC], None, "main") == _OTHER


def test_build_menu_options_with_and_without_current() -> None:
    """Menu options prepend the repeat row only when a current step exists."""
    current = StepAlternative(4, "write-design.md", "b", ("draft",))
    nxt = [StepAlternative(8, "implement-step.md", "b", ("plan",))]

    without = prompt_workflow.build_menu_options(None, nxt)
    assert [label for label, _ in without] == ["Step 8: implement-step.md"]

    with_current = prompt_workflow.build_menu_options(current, nxt)
    assert with_current[0][0] == "Repeat current step 4: write-design.md"
    assert [label for label, _ in with_current] == [
        "Repeat current step 4: write-design.md",
        "Step 8: implement-step.md",
    ]


def _wire_run(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    *,
    topics: list[Topic],
    record: MemoryRecord | None,
    select: Callable[[str, list[tuple[str, object]]], object],
) -> None:
    if record is not None:
        memory.write_memory(root, record)
    monkeypatch.setattr(prompt_workflow.git, "current_branch", lambda _root: "main")
    monkeypatch.setattr(prompt_workflow.docs, "relevant_drafts", lambda _root, _cwd: topics)
    monkeypatch.setattr(
        prompt_workflow.steps,
        "compute_state",
        lambda _root, _topic, memory_step: _state(memory_step=memory_step),
    )
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)
    monkeypatch.setattr(prompt_workflow.menu, "select", select)


def test_run_without_topics(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """No relevant topic exits cleanly without writing a prompt."""
    _wire_run(monkeypatch, tmp_path, topics=[], record=None, select=lambda _m, _o: None)
    assert prompt_workflow.run(tmp_path) == 0
    assert not (tmp_path / "a.prompt.txt").exists()


def test_run_topic_cancelled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Pressing ESC on the topic menu exits without a prompt."""
    _wire_run(
        monkeypatch,
        tmp_path,
        topics=[_TOPIC, _OTHER],
        record=None,
        select=lambda _m, _o: None,
    )
    assert prompt_workflow.run(tmp_path) == 0
    assert not (tmp_path / "a.prompt.txt").exists()


def test_run_step_cancelled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Pressing ESC on the step menu exits without a prompt."""
    _wire_run(monkeypatch, tmp_path, topics=[_TOPIC], record=None, select=lambda _m, _o: None)
    assert prompt_workflow.run(tmp_path) == 0
    assert not (tmp_path / "a.prompt.txt").exists()


def test_run_happy_path_with_matching_memory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A matching memory shows the repeat row and a chosen step is delivered."""
    record = MemoryRecord(
        branch="main",
        version="v9.8.0",
        topic="iso",
        step=4,
        instruction="write-design.md",
    )

    def select(_message: str, options: list[tuple[str, object]]) -> object:
        return options[-1][1]

    _wire_run(monkeypatch, tmp_path, topics=[_TOPIC], record=record, select=select)

    assert prompt_workflow.run(tmp_path) == 0
    written = (tmp_path / "a.prompt.txt").read_text(encoding="utf-8")
    assert "implement-step.md" in written
    assert memory.read_memory(tmp_path) == MemoryRecord(
        branch="main",
        version="v9.8.0",
        topic="iso",
        step=8,
        instruction="implement-step.md",
    )


def test_run_with_mismatched_memory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A memory from another branch is ignored, so no repeat row is shown."""
    record = MemoryRecord(branch="old", version="v9.8.0", topic="iso", step=4)
    labels: list[str] = []

    def select(_message: str, options: list[tuple[str, object]]) -> object:
        labels.extend(label for label, _ in options)
        return options[0][1]

    _wire_run(monkeypatch, tmp_path, topics=[_TOPIC], record=record, select=select)

    assert prompt_workflow.run(tmp_path) == 0
    assert all("Repeat" not in label for label in labels)


def test_main_uses_root_argument(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The --root argument is passed through to run."""
    seen: dict[str, Path] = {}

    def fake_run(root: Path) -> int:
        seen["root"] = root
        return 0

    monkeypatch.setattr(prompt_workflow, "run", fake_run)
    assert prompt_workflow.main(["--root", str(tmp_path), "--debug"]) == 0
    assert seen["root"] == tmp_path.resolve()


def test_main_defaults_to_found_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Without --root the project root is discovered."""
    monkeypatch.setattr(prompt_workflow, "find_project_root", lambda _start: tmp_path)
    monkeypatch.setattr(prompt_workflow, "run", lambda _root: 0)
    assert prompt_workflow.main([]) == 0


def test_log_fatal_exits_with_code(monkeypatch: pytest.MonkeyPatch) -> None:
    """The fatal helper logs and raises SystemExit with the fatal code."""
    monkeypatch.setattr(sys, "argv", ["prompt_workflow"])
    with pytest.raises(SystemExit) as excinfo:
        prompt_workflow._log_fatal(prompt_workflow.ClipboardError("boom"))
    assert excinfo.value.code == prompt_workflow.EXIT_FATAL


# eof
