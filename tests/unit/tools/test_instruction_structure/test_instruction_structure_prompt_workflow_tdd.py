"""Structural checks for prompt-workflow instructions and their wiki pages.

Split from the v0.9.0 instruction-structure test: keeps pw launch, question,
writer-review, document-layout, and wrapper guarantees in one focused leaf.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_INSTRUCTIONS = steps.llm_shared_dir() / "instructions"


def _read(name: str) -> str:
    """Return the text of an instruction file."""
    return (_INSTRUCTIONS / name).read_text(encoding="utf-8")


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
    """Review and consolidate present the standard three-column question table."""
    for name in ("review-ask-questions.md", "consolidate-then-review-ask-questions.md"):
        assert "| Q0x | Title | Recommended Answer |" in _read(name)


def test_question_skills_use_the_oqm_wrapper() -> None:
    """Review and consolidate use oqm.bat instead of direct Python fallback."""
    for name in ("review-ask-questions.md", "consolidate-then-review-ask-questions.md"):
        content = _read(name)
        assert "run_commands.md" in content
        assert "oqm.bat" in content
        assert "python <LLM_SHARED_DIR>\\tools\\open_questions_md.py" not in content


def test_writer_handoffs_review_the_artifact_that_was_just_written() -> None:
    """Each writer uses explicit post-write routing instead of disk inference."""
    writers = (
        ("write-requirement.md", "requirement"),
        ("write-design.md", "design"),
        ("write-plans.md", "plan"),
    )
    for name, role in writers:
        assert f"pw skill --after-write {role}" in _read(name)


def test_wiki_covers_umbrella_topics_and_explicit_post_write_review() -> None:
    """Every Diataxis purpose reflects both prompt-workflow routing fixes."""
    root = steps.llm_shared_dir() / "wiki"
    pages = {
        "explanation": root / "explanation" / "one-launcher-three-modes.md",
        "tutorial": root / "tutorials" / "02-from-draft-to-settled-requirement.md",
        "how_to": root / "how-to" / "split-a-mixed-draft.md",
        "reference": root / "reference" / "pw-launcher.md",
    }
    content = {role: path.read_text(encoding="utf-8") for role, path in pages.items()}
    assert all("umbrella" in text for text in content.values())
    assert all("after-write" in text for text in content.values())
    tutorial = content["tutorial"]
    assert "draft.v10.0.0.sentinel.md" in tutorial
    assert "- Draft role: umbrella" in tutorial
    assert "based on route-cleanup" in tutorial
    assert "`completed`" in tutorial
    reference = content["reference"]
    assert "$llm-shared:skill" in reference
    assert "Missing and ambiguous relationships return no topic" in reference


def test_wiki_covers_shared_menu_less_umbrella_resolution() -> None:
    """Diataxis pages state that skill and handoff share topic resolution."""
    root = steps.llm_shared_dir() / "wiki"
    pages = (
        root / "explanation" / "one-launcher-three-modes.md",
        root / "tutorials" / "04-run-the-implement-chain.md",
        root / "how-to" / "run-pw-from-any-shell.md",
        root / "how-to" / "split-a-mixed-draft.md",
        root / "reference" / "artifact-files.md",
        root / "reference" / "pw-launcher.md",
    )
    for path in pages:
        content = path.read_text(encoding="utf-8")
        assert "pw skill" in content
        assert "pw handoff" in content
        assert "umbrella" in content
    for path in pages[1:4]:
        assert "temporary" in path.read_text(encoding="utf-8")


def test_wiki_covers_document_layouts_and_stateless_lookup() -> None:
    """Every Diataxis purpose covers its part of document organization."""
    root = steps.llm_shared_dir() / "wiki"
    explanation = (
        root / "explanation" / "where-the-human-stays-in-the-loop.md"
    ).read_text(encoding="utf-8")
    tutorial = (
        root / "tutorials" / "02-from-draft-to-settled-requirement.md"
    ).read_text(encoding="utf-8")
    how_to = (root / "how-to" / "run-pw-from-any-shell.md").read_text(
        encoding="utf-8",
    )
    reference = (root / "reference" / "artifact-files.md").read_text(
        encoding="utf-8",
    )
    assert "five menus" in explanation
    assert "documentation-layout choice" in explanation
    for layout in ("docs/", "docs/vX.Y/", "docs/vX.Y.Z/", "docs/vX.Y/vX.Y.Z/"):
        assert layout in tutorial
        assert layout in reference
    assert "pw document <version> <slug> <type>" in how_to
    assert "without knowing its folder" in how_to
    assert "version, slug, and document type" in reference
    assert "same selector exists in more than one supported layout" in reference


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
