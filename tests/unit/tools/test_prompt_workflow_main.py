"""Tests for the orchestration and IO of prompt_workflow.

Fix: Cover logging setup, the clipboard wrapper and its fallback, topic choice
and ordering, the menu options, and the run/main entry points across the
no-topic, cancelled, mismatched-memory and happy paths. Also cover the cycle
introduction line shown above a non-terminal menu and skipped on a terminal one
(Q33, Q36, Q37).

Fix (branch lock): cover the auto-lock that skips the topic menu when the memory
still matches one detected topic on the branch, the ``--pick`` flag that reopens
the menu, and the flag threading through ``run`` and ``main`` (Q53).

Fix (menu order): the step menu lists its rows higher step number first, so the
next-step rows come above the repeat-current row; the menu-options scenarios
assert the descending order and the happy path picks the first row to advance
(Q54).

Fix (handoff dispatch): the parser now carries a ``handoff`` subcommand; this
file only asserts that ``main`` routes the subcommand to ``run_handoff`` with the
task and step, while the no-subcommand path still routes to ``run`` (Q56). The
``run_handoff`` orchestration itself is covered in
``test_prompt_workflow_handoff.py``.
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
from tools.prompt_workflow_plan import CycleAction, CycleState

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
        "plan": None,
        "validation_plan": None,
        "requirement_has_open_questions": False,
        "design_has_open_questions": False,
        "plan_has_open_questions": False,
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


def test_choose_topic_locks_to_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    """A memory matching one of several topics auto-selects it, no menu (Q53)."""
    record = MemoryRecord(branch="main", version="v9.8.0", topic="iso")
    messages: list[str] = []
    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda message, _options: messages.append(message),
    )

    # The locked topic is returned and the menu is never shown.
    assert prompt_workflow.choose_topic([_OTHER, _TOPIC], record, "main") == _TOPIC
    assert messages == []


def test_choose_topic_pick_forces_menu(monkeypatch: pytest.MonkeyPatch) -> None:
    """--pick reopens the menu even when the memory matches a topic (Q53)."""
    record = MemoryRecord(branch="main", version="v9.8.0", topic="iso")
    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda _message, options: options[0][1],
    )

    # With pick, the menu is shown; _order_topics floats the match to the front.
    chosen = prompt_workflow.choose_topic([_OTHER, _TOPIC], record, "main", pick=True)
    assert chosen == _TOPIC


def test_build_menu_options_with_and_without_current() -> None:
    """Menu options list the higher step first; the repeat row follows (Q54)."""
    current = StepAlternative(4, "write-design.md", "b", ("draft",))
    nxt = [StepAlternative(10, "implement-step.md", "b", ("plan",))]

    without = prompt_workflow.build_menu_options(None, nxt)
    assert [label for label, _ in without] == ["Step 10: implement-step.md"]

    with_current = prompt_workflow.build_menu_options(current, nxt)
    assert with_current[0][0] == "Step 10: implement-step.md"
    assert [label for label, _ in with_current] == [
        "Step 10: implement-step.md",
        "Repeat current step 4: write-design.md",
    ]


def test_build_menu_options_keeps_higher_current_first() -> None:
    """A current step above the next one stays first: higher step first (Q54)."""
    current = StepAlternative(7, "write-plans.md", "b", ("design",))
    nxt = [StepAlternative(3, "consolidate-then-review-ask-questions.md", "b", ("draft",))]

    labels = [label for label, _ in prompt_workflow.build_menu_options(current, nxt)]
    assert labels == [
        "Repeat current step 7: write-plans.md",
        "Step 3: consolidate-then-review-ask-questions.md",
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
    """A matching memory shows the repeat row and a chosen step is delivered.

    The next-step row sits first (Q54), so picking the first row advances to
    step 5 while the repeat row stays below it.
    """
    record = MemoryRecord(
        branch="main",
        version="v9.8.0",
        topic="iso",
        step=4,
        instruction="write-design.md",
    )

    def select(_message: str, options: list[tuple[str, object]]) -> object:
        return options[0][1]

    _wire_run(monkeypatch, tmp_path, topics=[_TOPIC], record=record, select=select)

    assert prompt_workflow.run(tmp_path) == 0
    written = (tmp_path / "a.prompt.txt").read_text(encoding="utf-8")
    assert "review-ask-questions.md" in written
    assert memory.read_memory(tmp_path) == MemoryRecord(
        branch="main",
        version="v9.8.0",
        topic="iso",
        step=5,
        instruction="review-ask-questions.md",
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


def test_run_locks_topic_to_memory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """With several topics, a matching memory skips the topic menu (Q53)."""
    record = MemoryRecord(
        branch="main",
        version="v9.8.0",
        topic="iso",
        step=4,
        instruction="write-design.md",
    )
    messages: list[str] = []

    def select(message: str, options: list[tuple[str, object]]) -> object:
        messages.append(message)
        return options[-1][1]

    _wire_run(monkeypatch, tmp_path, topics=[_TOPIC, _OTHER], record=record, select=select)

    assert prompt_workflow.run(tmp_path) == 0
    # Only the step menu is shown; the topic menu is skipped by the lock.
    assert all("Choose the general topic" not in message for message in messages)
    assert (tmp_path / "a.prompt.txt").exists()


_CYCLE = CycleState(
    x="2",
    verified=True,
    terminal=False,
    has_code_changes=True,
    cached=True,
    non_cached=False,
)


def _wire_cycle(
    monkeypatch: pytest.MonkeyPatch,
    *,
    cycle: CycleState | None,
    select: Callable[[str, list[tuple[str, object]]], object],
) -> None:
    monkeypatch.setattr(prompt_workflow.git, "current_branch", lambda _root: "main")
    monkeypatch.setattr(prompt_workflow.docs, "relevant_drafts", lambda _root, _cwd: [_TOPIC])
    monkeypatch.setattr(
        prompt_workflow.steps,
        "compute_state",
        # memory_step past the plan review round (>= 9) so the cycle gate fires.
        lambda _root, _topic, _step: _state(
            plan=Path("p"), validation_plan=Path("vp"), memory_step=10,
        ),
    )
    monkeypatch.setattr(prompt_workflow.git, "fork_point", lambda _root: "base")
    monkeypatch.setattr(prompt_workflow.plan, "compute_cycle", lambda _root, _state, _base: cycle)
    monkeypatch.setattr(prompt_workflow.plan, "build_cycle_options", lambda _cycle: [("Implement step 2", _CYCLE)])
    monkeypatch.setattr(prompt_workflow.menu, "select", select)
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)


def test_cycle_ready_line_labels() -> None:
    """The cycle ready line names the plan step, or the release notes."""
    implement = CycleAction(kind="implement", stage_all=False)
    release = CycleAction(kind="release", stage_all=False)
    assert "step 2 (implement)" in prompt_workflow._cycle_ready_line(_CYCLE, implement)
    assert "release notes" in prompt_workflow._cycle_ready_line(_CYCLE, release)


def test_run_implement_cycle_no_steps(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A plan with no validation steps exits the cycle without a prompt."""
    _wire_cycle(monkeypatch, cycle=None, select=lambda _m, _o: None)
    assert prompt_workflow.run(tmp_path) == 0
    assert not (tmp_path / "a.prompt.txt").exists()


def test_run_implement_cycle_cancelled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Pressing ESC in the cycle menu exits without a prompt."""
    _wire_cycle(monkeypatch, cycle=_CYCLE, select=lambda _m, _o: None)
    assert prompt_workflow.run(tmp_path) == 0
    assert not (tmp_path / "a.prompt.txt").exists()


def test_run_implement_cycle_delivers(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An implement action writes the prompt and records the plan step."""
    action = CycleAction(kind="implement", stage_all=False)
    staged_calls: list[str] = []

    def build(*_args: object) -> tuple[str, int, str]:
        return ("PROMPT-BODY", 10, "implement-step.md")

    monkeypatch.setattr(prompt_workflow.git, "stage_all", lambda _root: staged_calls.append("x"))
    monkeypatch.setattr(prompt_workflow.plan, "build_cycle_prompt", build)
    _wire_cycle(monkeypatch, cycle=_CYCLE, select=lambda _m, opts: opts[0][1])
    monkeypatch.setattr(prompt_workflow.plan, "build_cycle_options", lambda _cycle: [("Implement step 2", action)])

    assert prompt_workflow.run(tmp_path) == 0
    assert (tmp_path / "a.prompt.txt").read_text(encoding="utf-8") == "PROMPT-BODY"
    assert staged_calls == []
    assert memory.read_memory(tmp_path) == MemoryRecord(
        branch="main",
        version="v9.8.0",
        topic="iso",
        step=10,
        instruction="implement-step.md",
        plan_step="2",
    )


def test_run_implement_cycle_stage_all(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A git-add-A commit action stages everything before building the prompt."""
    action = CycleAction(kind="commit", stage_all=True)
    staged_calls: list[str] = []

    def build(*_args: object) -> tuple[str, int, str]:
        return ("COMMIT-PROMPT", 12, "group-commits-msg.md")

    monkeypatch.setattr(prompt_workflow.git, "stage_all", lambda _root: staged_calls.append("x"))
    monkeypatch.setattr(prompt_workflow.plan, "build_cycle_prompt", build)
    _wire_cycle(monkeypatch, cycle=_CYCLE, select=lambda _m, opts: opts[0][1])
    monkeypatch.setattr(prompt_workflow.plan, "build_cycle_options", lambda _cycle: [("Commit", action)])

    assert prompt_workflow.run(tmp_path) == 0
    assert staged_calls == ["x"]
    assert memory.read_memory(tmp_path) == MemoryRecord(
        branch="main",
        version="v9.8.0",
        topic="iso",
        step=12,
        instruction="group-commits-msg.md",
        plan_step="2",
    )


def test_run_implement_cycle_prints_intro(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A non-terminal cycle prints the 'Regarding step' introduction (Q33, Q36)."""
    action = CycleAction(kind="implement", stage_all=False)
    infos: list[str] = []

    def build(*_args: object) -> tuple[str, int, str]:
        return ("PROMPT-BODY", 8, "implement-step.md")

    monkeypatch.setattr(prompt_workflow.plan, "build_cycle_prompt", build)
    _wire_cycle(monkeypatch, cycle=_CYCLE, select=lambda _m, opts: opts[0][1])
    monkeypatch.setattr(
        prompt_workflow.plan,
        "build_cycle_options",
        lambda _cycle: [("Implement step 2", action)],
    )
    monkeypatch.setattr(prompt_workflow.LOGGER, "info", infos.append)

    assert prompt_workflow.run(tmp_path) == 0
    assert any("Regarding step 2" in message for message in infos)


def test_run_implement_cycle_terminal_skips_intro(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A terminal cycle shows no 'Regarding step' introduction (Q37)."""
    action = CycleAction(kind="release", stage_all=False)
    terminal = CycleState(
        x="2",
        verified=True,
        terminal=True,
        has_code_changes=False,
        cached=False,
        non_cached=False,
    )
    infos: list[str] = []

    def build(*_args: object) -> tuple[str, int, str]:
        return ("RELEASE-PROMPT", 13, "prepare-release-notes.md")

    monkeypatch.setattr(prompt_workflow.plan, "build_cycle_prompt", build)
    _wire_cycle(monkeypatch, cycle=terminal, select=lambda _m, opts: opts[0][1])
    monkeypatch.setattr(
        prompt_workflow.plan,
        "build_cycle_options",
        lambda _cycle: [("Prepare release notes", action)],
    )
    monkeypatch.setattr(prompt_workflow.LOGGER, "info", infos.append)

    assert prompt_workflow.run(tmp_path) == 0
    assert all("Regarding step" not in message for message in infos)


def test_main_uses_root_argument(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The --root argument is passed through to run; pick defaults to False."""
    seen: dict[str, object] = {}

    def fake_run(root: Path, *, pick: bool = False) -> int:
        seen["root"] = root
        seen["pick"] = pick
        return 0

    monkeypatch.setattr(prompt_workflow, "run", fake_run)
    assert prompt_workflow.main(["--root", str(tmp_path), "--debug"]) == 0
    assert seen["root"] == tmp_path.resolve()
    assert seen["pick"] is False


def test_main_pick_flag(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The --pick flag is forwarded to run as pick=True (Q53)."""
    seen: dict[str, object] = {}

    def fake_run(root: Path, *, pick: bool = False) -> int:
        seen["root"] = root
        seen["pick"] = pick
        return 0

    monkeypatch.setattr(prompt_workflow, "run", fake_run)
    assert prompt_workflow.main(["--root", str(tmp_path), "--pick"]) == 0
    assert seen["pick"] is True


def test_main_dispatches_handoff(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The handoff subcommand routes to run_handoff with the task and step (Q56)."""
    seen: dict[str, object] = {}

    def fake_handoff(root: Path, task: str, step: str) -> int:
        seen["root"] = root
        seen["task"] = task
        seen["step"] = step
        return 0

    monkeypatch.setattr(prompt_workflow, "run_handoff", fake_handoff)
    assert prompt_workflow.main(["handoff", "check", "2", "--root", str(tmp_path)]) == 0
    assert seen == {"root": tmp_path.resolve(), "task": "check", "step": "2"}


def test_main_defaults_to_found_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Without --root the project root is discovered."""
    monkeypatch.setattr(prompt_workflow, "find_project_root", lambda _start: tmp_path)
    monkeypatch.setattr(prompt_workflow, "run", lambda _root, *, pick=False: 0)  # noqa: ARG005
    assert prompt_workflow.main([]) == 0


def test_log_fatal_exits_with_code(monkeypatch: pytest.MonkeyPatch) -> None:
    """The fatal helper logs and raises SystemExit with the fatal code."""
    monkeypatch.setattr(sys, "argv", ["prompt_workflow"])
    with pytest.raises(SystemExit) as excinfo:
        prompt_workflow._log_fatal(prompt_workflow.ClipboardError("boom"))
    assert excinfo.value.code == prompt_workflow.EXIT_FATAL


# eof
