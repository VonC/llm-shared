"""TDD contracts for the Step 2 code-review requestor instruction.

The tests pin required policy tokens and ordering while leaving prose free to
improve. Shared lifecycle mechanics remain owned by review-requestor.md.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_INSTRUCTION = _ROOT / "instructions" / "code-review-requestor.md"


def _content() -> str:
    """Read the canonical specialized instruction."""
    return _INSTRUCTION.read_text(encoding="utf-8")


def _assert_in_order(content: str, tokens: tuple[str, ...]) -> None:
    """Assert each contract token follows the preceding token."""
    cursor = -1
    for token in tokens:
        position = content.find(token, cursor + 1)
        assert position > cursor, token
        cursor = position


def test_instruction_registers_exact_code_policy_and_identity() -> None:
    """Every exchange command receives fixed code policy and exact context."""
    content = _content()

    for token in (
        "--family code",
        "--convergence-signal commit-ready",
        '--another-round-label "Rework and review again"',
        '--continue-owning-workflow-label "Commit"',
        "--document <exact-implementation-plan>",
        "--implementation-step <exact-step>",
    ):
        assert token in content
    assert "Pass this unchanged policy" in content


def test_instruction_delegates_renderer_and_shared_lifecycle_in_order() -> None:
    """Specialized assessment joins paired output to shared transitions."""
    content = _content()

    assert "instructions/review-requestor.md" in content
    assert "<LLM_SHARED_DIR>\\bin\\code_review_request.bat" in content
    assert "<LLM_SHARED_DIR>\\bin\\review_exchange.bat" in content
    _assert_in_order(
        content,
        (
            "`status`",
            "`activate`",
            "`start`",
            "`publish-request`",
            "`wait-answer`",
            "`consume-answer`",
            "`continue`",
            "`confirm`",
            "`complete`",
        ),
    )


def test_instruction_captures_and_publishes_typed_request_evidence() -> None:
    """The requestor delegates immutable tree capture and additive validation resolution."""
    content = _content()

    for token in (
        "capture_index_tree",
        "resolve_code_review_validation",
        "--plan-validation-command",
        "--request-validation-command",
        "request_index_tree",
        "resolved_validation_set",
        "## Code review evidence",
    ):
        assert token in content
    assert "cannot remove the `ghog day` project default" in content
    _assert_in_order(
        content,
        ("capture_index_tree", "resolve_code_review_validation", "render", "publish-request"),
    )


def test_requestor_cannot_initiate_the_reviewer() -> None:
    """Publication hands off through artifacts, never through agent creation."""
    normalized = " ".join(_content().split())

    for fragment in (
        "Do not start, spawn, delegate, invoke, or message a reviewer",
        "wait-answer` immediately in this same requestor session",
        "never runs `pw skill code-reviewer`",
        "uses an agent or subagent tool to create the counterpart",
        "Publishing the request is the whole handoff",
    ):
        assert fragment in normalized


def test_requestor_rejects_reviewer_initiated_continuation() -> None:
    """Answer publication cannot create a new requestor session."""
    normalized = " ".join(_content().split())

    assert "Reject this requestor task if an automated reviewer" in normalized
    assert "parent agent acting as reviewer" in normalized
    assert "it never creates the requestor continuation" in normalized


def test_instruction_handles_every_resumable_state_without_manual_edits() -> None:
    """Every durable state maps to shared recovery or a fail-closed stop."""
    content = _content()

    for state in (
        "disabled",
        "idle",
        "round-in-progress",
        "request-pending",
        "answer-pending",
        "abandoned-request",
        "abandoned-answer",
        "abandoned-mid-round",
        "convergence-gate",
        "owning-action-pending",
        "escalated",
    ):
        assert f"`{state}`" in content
    assert "Never create, overwrite, rename, or delete a protocol artifact by hand" in content
    assert "read only the exact `paths.answer` file" in content
    assert "Never read the versioned transcript as working context" in content


def test_instruction_advances_ownership_for_a_new_requestor_session() -> None:
    """A fresh session picks up a new capability before its first mutation."""
    content = _content()
    section = content[content.index("## New-session ownership pickup") :]

    for token in (
        "This is a new session",
        "force requestor ownership pickup",
        "`pickup`",
        "ownership generation",
        "`--ownership-generation`",
        "`--ownership-token`",
        "not a reset",
        "`reclaim`",
    ):
        assert token in section
    _assert_in_order(section, ("`pickup`", "`confirm`"))


def test_repair_assessment_uses_all_required_evidence() -> None:
    """Writer authority is grounded in exact step and staged repair evidence."""
    content = _content()

    _assert_in_order(
        content,
        (
            "exact plan step",
            "repaired-path inventory",
            "staged diff",
            "implementation-check",
        ),
    )
    assert "leave each repair staged" in content
    assert "name every repaired path" in content
    assert "membership, grouping, order, scope, or subject accuracy" in content
    assert "`a.commit`" in content


def test_intermediate_rounds_record_change_and_reversal_disagreement() -> None:
    """Intermediate feedback reports change truthfully and bounds reversals."""
    content = _content()

    assert "reviewed-work-changed" in content
    assert "disagreement" in content
    assert "explicit disagreement" in content
    assert "requestor reverses" in content
    assert "Do not call `consume-answer` for a commit-ready recommendation" in content
    _assert_in_order(content, ("`consume-answer`", "`continue`", "replacement round"))


def test_substantive_repairs_and_convergence_use_the_human_gate() -> None:
    """Four substantive categories force re-review or an override recommendation."""
    content = _content()

    for token in ("code", "tests", "acceptance behavior", "commit grouping"):
        assert token in content
    assert "polishing-only" in content
    assert "recommend `Rework and review again`" in content
    assert "The reviewer recommendation never authorizes a commit" in content
    assert "owning_action_authorized: true" in content
    assert "do not ask the human again" in content


def test_authorized_commit_replays_owner_action_before_completion() -> None:
    """Durable commit authority remains with the existing owning continuation."""
    content = _content()

    _assert_in_order(
        content,
        (
            "owning_action_authorized: true",
            "canonical commit continuation",
            "action succeeds",
            "`complete`",
        ),
    )
    assert "reviewer never commits" in content.lower()


# eof
