"""A decision no blocking picker holds still shows the agent as waiting.

Fix: Codex in Default mode has no blocking picker, so a turn ending on a
question looked finished in tuios and Windows Terminal. ``rules/interactive_menu.md``
now keeps the choices visible, reports the wait with OSC 7501
(``state=blocked``, ``kind=question``) through ``bin/program_status.bat``,
forbids deciding for the user, and closes the record once the answer comes.
The decision workflows and the session-level instructions send their
questions through that one rule instead of repeating it.
"""

from __future__ import annotations

import pytest

from tools import prompt_workflow_steps as steps

ROOT = steps.llm_shared_dir()


def _text(relative: str) -> str:
    """Read a canonical file with its line breaks folded into spaces."""
    return " ".join((ROOT / relative).read_text(encoding="utf-8").split())


def _section(relative: str, heading: str) -> str:
    content = (ROOT / relative).read_text(encoding="utf-8")
    return " ".join(content.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0].split())


def test_rule_reports_a_pending_decision_to_the_terminal() -> None:
    """Without a blocking picker, the choices stay visible and blocked/question is reported last."""
    section = _section("rules/interactive_menu.md", "Signal a decision that no blocking picker holds")

    for required in (
        "Codex in Default mode",
        "(https://www.superlogical.com/rex/docs/build/program-status)",
        "Present the choices",
        'program_status.bat" blocked --kind question --id question --app <app> --msg',
        "`--id question` keeps the wait in a record of its own",
        "while any of its records is `blocked`",
        "as the turn's last command",
        "no sleep, no polling, no watcher",
        "| Codex | `codex` |",
        "| Claude Code | `claude` |",
        "not to the captured command output",
        "Exit 3 means no terminal could be reached",
        "Never print the escape sequence yourself",
        "The helper then exits 3 rather than signal the pane of the session that started the daemon",
    ):
        assert required in section


def test_rule_never_decides_for_the_user() -> None:
    """Silence, the recommendation and an unanswered question never count as a decision."""
    section = _section("rules/interactive_menu.md", "Keep the decision open until the user answers")

    assert "Never infer a decision from silence" in section
    assert "select the recommended option on the user's behalf" in section
    assert "record an unanswered question as decided" in section
    assert "Do not continue work that depends on the answer" in section


@pytest.mark.parametrize(
    "row",
    [
        "| The user answers and the work resumes | `working`, as the turn's first command |",
        "| The user cancels or postpones the decision | `idle` |",
        "| The turn ends on another pending decision | `blocked --kind question` |",
        "| The turn ends with the work finished | `done` |",
        "| The turn ends on a failure that stops the work | `error` |",
        "| The turn ends after a cancellation, with nothing to report | `clear` |",
    ],
)
def test_rule_closes_the_record_after_the_answer(row: str) -> None:
    """Each step after the wait has its report, with the same app and id."""
    section = _section("rules/interactive_menu.md", "Report the end of the wait")

    assert "keep the same `--app` and `--id question`" in section
    assert row in section


@pytest.mark.parametrize(
    ("relative", "pointer"),
    [
        ("instructions/explain-undecided-questions.md", "report the question as `blocked` first"),
        ("instructions/resume-session.md", "yes or no choice under [interactive_menu.md](../rules/interactive_menu.md)"),
        ("instructions/pause-session.md", "Ask it as a choice under [interactive_menu.md](../rules/interactive_menu.md)"),
        ("instructions/review-requestor.md", "the labels as a choice under [interactive_menu.md](../rules/interactive_menu.md)"),
        ("rules/chat.md", "otherwise the choices plus a `blocked` report to the terminal"),
        ("AGENTS.md", "rules/interactive_menu.md ``` In Default mode, Codex has no blocking picker"),
    ],
)
def test_decision_points_use_the_one_rule(relative: str, pointer: str) -> None:
    """Workflows and session rules point to the rule rather than copy it."""
    text = _text(relative)

    assert pointer in text
    assert "program_status.bat" not in text


def test_launcher_runs_the_status_tool_with_llm_shared_python() -> None:
    """The launcher self-locates and runs the tool file with the llm-shared venv."""
    launcher = (ROOT / "bin/program_status.bat").read_text(encoding="utf-8")

    assert 'if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."' in launcher
    assert r'"%LLM_SHARED_DIR%\tools\program_status.py" %*' in launcher
    assert "exit /b %ERRORLEVEL%" in launcher


# eof
