"""Contract tests for question-workflow specification review delegation.

Step 3 keeps trigger detection in both canonical question workflows and routes
only marker-enabled, question-present work to the specialized requestor.
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
        assert content.count("spec-review-requestor") == 1
        assert "a.review-mode" in content
        assert "pw skill spec-review-requestor" in content


def test_question_delegation_preserves_holds_and_non_review_handoffs() -> None:
    """Explicit holds, no-question passes, and marker absence stay unchanged."""
    for path in _INSTRUCTIONS:
        content = _content(path)
        delegation = content.index("pw skill spec-review-requestor")
        assert "stop here" in content[:delegation].lower()
        assert "no new" in content.lower() or "no question" in content.lower()
        assert "review mode" in content.lower()
        assert "existing" in content.lower()


# eof
