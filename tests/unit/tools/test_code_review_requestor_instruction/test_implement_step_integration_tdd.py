"""Contract tests for Step 3 and Step 4 instruction integration.

The checks pin only required trigger, delegation, and continuation tokens plus
their order, including the Step 4 readiness gate before authorized batches.
"""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]


def _content(name: str) -> str:
    """Read one canonical instruction as normalized text."""
    return (_ROOT / "instructions" / name).read_text(encoding="utf-8")


def test_implement_step_samples_review_mode_after_grouping_and_delegates() -> None:
    """The normal stop is replaced only after successful grouping."""
    content = _content("implement-step.md")
    grouping = content.index("group-commits-msg")
    marker = content.index("a.review-mode", grouping)
    requestor = content.index("code-review-requestor", marker)
    workflow = content.index("pw skill", marker)
    assert grouping < marker < requestor
    assert marker < workflow
    assert "exact plan" in content[marker:]
    assert "implementation step" in content[marker:]
    assert "run the printed command verbatim" in content[marker:]
    assert "versioned review transcript" in content[marker:]
    assert "starts no reviewer agent or session" in content[marker:]
    assert "immediately waits for the answer" in " ".join(content[marker:].split())


def test_agents_md_applies_shared_review_role_isolation() -> None:
    """Codex receives the role boundary before any specialized skill runs."""
    content = (_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "## Review role isolation" in content
    assert "instructions/review-requestor.md" in content
    assert "must never spawn, start, delegate, invoke, or message a reviewer" in content
    assert "must never spawn, start, delegate," in content
    assert "invoke, or message a requestor agent or session" in content
    assert "Each role rejects a task" in content


def test_grouping_instruction_has_a_dedicated_authorized_entry() -> None:
    """Authorization covers reviewed and residual batches up to a clean tree."""
    content = _content("group-commits-msg.md")
    start = content.index("Authorized code-review continuation")
    block = content[start:]
    ordered = [
        "owning-action-pending",
        "owning_action_authorized: true",
        "pw",
        "--root-a-commit",
        "complete",
    ]
    positions = [block.index(token) for token in ordered]
    assert positions == sorted(positions)
    assert "do not present" in block
    assert "authorization remains pending" in block
    normalized = " ".join(block.split())
    for token in (
        "git add -A",
        "Steps 1 through 7",
        "pw code-review-commit --residual",
        "git status --porcelain",
        "clean working tree",
        "do not run `pw skill`",
    ):
        assert token in normalized


def test_code_review_requestor_requires_clean_residual_completion() -> None:
    """The convergence Commit choice retains authority through cleanup."""
    content = _content("code-review-requestor.md")
    start = content.index("Authorized commit replay")
    block = content[start:]
    for token in (
        "reviewed root `a.commit`",
        "git add -A",
        "group-commits-msg",
        "pw code-review-commit --residual",
        "git status --porcelain",
        "Never proceed to `pw skill`",
    ):
        assert token in block
