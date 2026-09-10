"""Portability contracts for utilities named by canonical instructions."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
_INSTRUCTIONS = _ROOT / "instructions"


def _instruction(name: str) -> str:
    """Read one canonical instruction as UTF-8."""
    return (_INSTRUCTIONS / name).read_text(encoding="utf-8")


def test_instructions_do_not_execute_shared_utilities_through_stale_locations() -> None:
    """Executable examples never depend on caller layout or inherited variables."""
    bad_invocations = (
        'cmd /d /v:on /c "..\\llm-shared\\bin\\',
        "bash ../llm-shared/scripts/",
        '& "$env:LLM_SHARED_DIR\\bin\\',
        '"%LLM_SHARED_DIR%\\bin\\',
        'bash -c "%LLM_SHARED_DIR_UNIX%/',
    )

    offenders = {
        path.name: tuple(token for token in bad_invocations if token in content)
        for path in _INSTRUCTIONS.glob("*.md")
        if (content := path.read_text(encoding="utf-8"))
        and any(token in content for token in bad_invocations)
    }

    assert not offenders, f"stale shared utility invocations: {offenders!r}"


def test_review_commands_use_resolved_full_paths_without_senv() -> None:
    """Both review roles inherit one explicit cross-repository command boundary."""
    common = _instruction("review-requestor.md")
    reviewer = _instruction("code-reviewer.md")

    assert "absolute parent of the `instructions` folder" in common
    assert '& "<LLM_SHARED_DIR>\\bin\\review_exchange.bat"' in common
    assert "do not run either repository's `senv.bat` first" in common
    assert '& "<LLM_SHARED_DIR>\\bin\\code_review_evidence.bat"' in reviewer
    assert '& "<LLM_SHARED_DIR>\\commit-plan-check.bat" --format json' in reviewer


def test_question_and_handoff_commands_use_resolved_full_paths() -> None:
    """Frequently cross-repository oqm and pw calls show executable commands."""
    questions = _instruction("review-ask-questions.md")
    handoff = _instruction("run-pw.md")

    assert '& "<LLM_SHARED_DIR>\\bin\\oqm.bat" <document-path>' in questions
    assert '& "<LLM_SHARED_DIR>\\bin\\prompt_workflow.bat" skill' in handoff
    assert "do not pass the placeholder literally" in handoff


# eof
