"""Commit, readiness, and clean-tree contracts for question consolidation."""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_MINIMUM_STATUS_CHECK_COUNT = 4


def _instruction(name: str) -> str:
    """Read one canonical workflow instruction."""
    path = steps.llm_shared_dir() / "instructions" / name
    return path.read_text(encoding="utf-8")


def test_settled_consolidation_commits_every_change_before_handoff() -> None:
    """The final grouped commit gate runs after folding and before pw routing."""
    content = _instruction("consolidate-then-review-ask-questions.md")
    snapshot = content.index("## Pre-consolidation question snapshot")
    integration = content.index("You need to remove `Qxx:` sections")
    grouped = content.index("## Post-consolidation grouped commits and clean-tree gate")
    handoff = content.index("## Handoff")
    gate = " ".join(content[grouped:handoff].split())

    assert snapshot < integration < grouped < handoff
    for fragment in (
        "git add -A",
        "with no path restriction",
        "git diff --cached --name-only",
        "git diff --name-only",
        "git ls-files --others --exclude-standard",
        "$llm-shared:group-commits-msg for all staged changes",
        "--root-a-commit --non-interactive",
        "skip the normal group-commit menu",
    ):
        assert fragment in gate


def test_question_snapshot_uses_a_parser_compatible_scope() -> None:
    """The snapshot title derives a bounded scope instead of using bare docs."""
    content = _instruction("consolidate-then-review-ask-questions.md")
    snapshot = content.index("## Pre-consolidation question snapshot")
    integration = content.index("You need to remove `Qxx:` sections")
    contract = " ".join(content[snapshot:integration].split())

    assert "prefer its topic slug" in contract
    assert "normalized document-type scope" in contract
    assert "docs(<scope>): record pre-consolidation questions" in contract
    assert "52-character" in contract


def test_pw_handoff_requires_an_empty_porcelain_status() -> None:
    """Dirty post-commit state receives one recovery pass and can never route."""
    content = _instruction("consolidate-then-review-ask-questions.md")
    grouped = content.index("## Post-consolidation grouped commits and clean-tree gate")
    handoff = content.index("## Handoff")
    gate = " ".join(content[grouped:handoff].split())
    handoff_text = " ".join(content[handoff:].split())

    assert gate.count("git status --porcelain") >= _MINIMUM_STATUS_CHECK_COUNT
    assert "do not run `pw skill`" in gate
    assert "repeat the same `group-commits-msg`" in gate
    assert "once as a recovery pass" in gate
    assert "still nonempty afterward, stop" in gate
    assert "Only a successful grouped-commit pass" in gate
    assert "`git status --porcelain` empty" in handoff_text


def test_grouping_skill_has_the_authorized_consolidation_continuation() -> None:
    """Consolidation reuses canonical grouping without a second human menu."""
    content = _instruction("group-commits-msg.md")
    continuation = content.split("## Authorized consolidation continuation", 1)[1]

    assert "consolidate-then-review-ask-questions.md" in continuation
    assert "Steps 1 through 7" in continuation
    assert "do not present the Step 8 menu" in continuation
    assert "--root-a-commit --non-interactive" in continuation
    assert "consolidation verifies" in continuation
