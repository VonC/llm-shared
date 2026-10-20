"""Contract tests for question-workflow specification review delegation.

Question count cannot bypass independent review of an authored specification.
"""

from pathlib import Path

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_INSTRUCTIONS = (
    _ROOT / "instructions/review-ask-questions.md",
    _ROOT / "instructions/consolidate-then-review-ask-questions.md",
)


def _content(path: Path) -> str:
    """Read one canonical question workflow."""
    return path.read_text(encoding="utf-8")


def test_both_question_workflows_delegate_to_the_specialized_role_once() -> None:
    """Each writer keeps one thin marker-gated forced pw handoff."""
    for path in _INSTRUCTIONS:
        content = _content(path)
        assert content.count("pw skill spec-review-requestor") == 1
        assert "specification-review-gate.md" in content
        assert "pw skill spec-review-requestor" in content


def test_question_delegation_preserves_holds_without_no_question_bypass() -> None:
    """Both entrypoints apply one shared gate even for settled author decisions."""
    for path in _INSTRUCTIONS:
        content = _content(path)
        delegation = content.index("pw skill spec-review-requestor")
        assert "stop here" in content[:delegation].lower()
        assert "no-question" in content.lower()
        assert "review mode" in content.lower()
        assert "A no-question pass skips this block" not in content


def test_review_gate_distinguishes_independent_evidence_and_author_decisions() -> None:
    """Absent review mode and settled rows cannot silently authorize advancement."""
    content = " ".join(
        _content(_ROOT / "rules/specification-review-gate.md").split(),
    )
    assert "including a pass that raises no new questions" in content
    assert "With review mode disabled" in content
    assert "stop before the next phase" in content
    assert "invoking consolidation is not a waiver" in content
    assert "owning-action-pending" in content
    assert "do not start a duplicate exchange" in content
    assert "A no-question pass must never bypass this gate" in content


def test_review_preserves_existing_answered_questions() -> None:
    """A review refresh retains prior questions instead of silently stripping them."""
    content = " ".join(_content(_ROOT / "instructions/review-ask-questions.md").split())
    assert "Do not run `--strip` during review" in content
    assert "copy every existing question and answer into it unchanged" in content
    assert "all prior question IDs, options, and human answers remain present" in content
    assert "Do not replace them with a settled decision marker" in content


# eof
