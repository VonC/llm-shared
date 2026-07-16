"""Structural check that the workflow instructions carry their handoff, hint, or list.

Step 5 of docs/plan.v0.9.0.handoff_automation.md guards the markdown sections
added in Steps 4 and 5: the writing and consolidation instructions carry a
``## Handoff`` that runs ``pw skill``, the review instruction leaves the
consolidation hint, and the splitting instructions present a multi-choice list
with a free-text entry. The check runs on every walk, so a later edit that drops
one fails fast (Q06).
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_INSTRUCTIONS = steps.llm_shared_dir() / "instructions"


def _read(name: str) -> str:
    """Return the text of an instruction file."""
    return (_INSTRUCTIONS / name).read_text(encoding="utf-8")


def test_writing_and_consolidate_instructions_carry_a_handoff() -> None:
    """The four writing and consolidation instructions run pw skill in a ## Handoff."""
    for name in (
        "write-requirement.md",
        "write-design.md",
        "write-plans.md",
        "consolidate-then-review-ask-questions.md",
    ):
        content = _read(name)
        assert "## Handoff" in content
        assert "pw skill" in content


def test_review_instruction_leaves_the_consolidation_hint() -> None:
    """review-ask-questions hints the consolidation step on the reviewed document."""
    assert "consolidate-then-review-ask-questions" in _read("review-ask-questions.md")


def test_splitting_instructions_present_the_multi_choice() -> None:
    """process-draft and split-and-define list the next steps with a free-text entry."""
    for name in ("process-draft.md", "split-and-define.md"):
        content = _read(name)
        assert "write-requirement" in content
        assert "Type something else" in content


def test_group_commits_carries_the_commit_gate_multi_choice() -> None:
    """group-commits-msg presents the commit-gate multi-choice via pw skill."""
    content = _read("group-commits-msg.md")
    assert "pw skill --after-commit" in content
    assert "Go ahead, and implement step" in content
    assert "Go ahead, and prepare-release" in content
    assert "Never present the contextual option as only the printed command" in content
    assert "Type something else" in content


def test_run_pw_note_documents_the_launcher() -> None:
    """run-pw.md references the command rules and the launcher, not the bare alias."""
    content = _read("run-pw.md")
    assert "run_commands.md" in content
    assert "prompt_workflow.bat" in content
    assert "C:\\Users\\" not in content


def test_run_commands_documents_python_script_invocation() -> None:
    """run_commands.md gives the guard-clearing shape for direct Python scripts."""
    content = (steps.llm_shared_dir() / "rules" / "run_commands.md").read_text(
        encoding="utf-8",
    )
    assert "Python scripts use wrappers" in content
    assert "set NO_MORE_SENV_%PRJ_DIR_NAME%=& senv.bat && python" in content


def test_codex_plugin_packages_every_instruction() -> None:
    """Every shared instruction has a matching, self-contained Codex skill."""
    root = steps.llm_shared_dir()
    plugin = root / ".agents" / "llm-shared"
    instruction_names = {path.name for path in _INSTRUCTIONS.glob("*.md")}
    expected_skill_names = {
        name.removesuffix(".md").replace("_", "-") for name in instruction_names
    }
    packaged_skill_names = {
        path.name for path in (plugin / "skills").iterdir() if path.is_dir()
    }

    assert packaged_skill_names == expected_skill_names
    for instruction_name in instruction_names:
        skill_name = instruction_name.removesuffix(".md").replace("_", "-")
        skill = (plugin / "skills" / skill_name / "SKILL.md").read_text(
            encoding="utf-8",
        )
        packaged = plugin / "instructions" / instruction_name

        assert f"[Instruction](../../instructions/{instruction_name})" in skill
        assert packaged.read_bytes() == (_INSTRUCTIONS / instruction_name).read_bytes()


def test_pw_running_instructions_link_to_the_run_pw_note() -> None:
    """Each instruction that runs a pw command points at run-pw.md."""
    for name in (
        "write-requirement.md",
        "write-design.md",
        "write-plans.md",
        "consolidate-then-review-ask-questions.md",
        "process-draft.md",
        "group-commits-msg.md",
        "implement-step.md",
        "implement-missing-step.md",
        "implementation-check.md",
    ):
        assert "run-pw.md" in _read(name)


def test_question_skills_show_the_three_column_table() -> None:
    """Review and consolidate present open questions as a Q0x / Title / Recommended table."""
    for name in ("review-ask-questions.md", "consolidate-then-review-ask-questions.md"):
        assert "| Q0x | Title | Recommended Answer |" in _read(name)


def test_question_skills_use_the_oqm_wrapper() -> None:
    """Review and consolidate use oqm.bat instead of direct Python fallback."""
    for name in ("review-ask-questions.md", "consolidate-then-review-ask-questions.md"):
        content = _read(name)
        assert "run_commands.md" in content
        assert "oqm.bat" in content
        assert "python <LLM_SHARED_DIR>\\tools\\open_questions_md.py" not in content


def test_oqm_wrapper_clears_the_project_senv_guard() -> None:
    """oqm.bat clears the project guard before calling senv.bat."""
    content = (steps.llm_shared_dir() / "bin" / "oqm.bat").read_text(
        encoding="utf-8",
    )
    assert "NO_MORE_SENV_!LLM_SHARED_PRJ_DIR_NAME!=" in content
    assert "%PRJ_DIR%\\senv.bat" in content
    assert "open_questions_md.py" in content


def test_python_tool_instructions_use_wrappers() -> None:
    """Instructions should avoid direct Python script calls when wrappers exist."""
    for name in (
        "group-commits-msg.md",
        "update-merge-commit-msg.md",
        "git-history-report.md",
    ):
        content = _read(name)
        assert "run_commands.md" in content
        assert 'python "%LLM_SHARED_DIR%\\tools\\' not in content
        assert "python <llm-shared>/tools/" not in content


# eof
