"""Content contracts for the canonical implementation code reviewer.

Step 4 requires an independent read-only commit-plan check while keeping
mechanical readiness separate from assessment and human commit authority.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_INSTRUCTION = steps.llm_shared_dir() / "instructions" / "code-reviewer.md"
_MINIMUM_EVIDENCE_REFERENCES = 7


def _content() -> str:
    """Read the canonical policy once for one assertion phase."""
    return _INSTRUCTION.read_text(encoding="utf-8")


def _assert_contains_all(content: str, fragments: tuple[str, ...]) -> None:
    """Report every required fragment missing from one policy document."""
    missing = tuple(fragment for fragment in fragments if fragment not in content)
    assert not missing, f"missing policy fragments: {missing!r}"


def test_instruction_delegates_every_executable_boundary_to_launchers() -> None:
    """The instruction sequences launchers instead of cloning their behavior."""
    content = _content()
    evidence = "<LLM_SHARED_DIR>\\bin\\code_review_evidence.bat"
    for responsibility in (
        "baseline",
        "pre-repair blobs",
        "attribute-reviewer-patch",
        "validation-state",
        "manifest write",
        "manifest read",
        "manifest retire",
    ):
        assert responsibility in content
    assert content.count(evidence) >= _MINIMUM_EVIDENCE_REFERENCES
    assert "<LLM_SHARED_DIR>\\bin\\code_review_answer.bat" in content
    assert "<LLM_SHARED_DIR>\\bin\\review_exchange.bat" in content
    for forbidden_clone in ("git write-tree", "git hash-object", "git diff", "os.remove"):
        assert forbidden_clone not in content


def test_instruction_pins_policy_identity_and_reciprocal_bounded_waits() -> None:
    """Reviewer entry and later rounds use exact bounded counterpart waits."""
    content = _content()
    _assert_contains_all(
        content,
        (
            "--family code",
            "--convergence-signal commit-ready",
            '--another-round-label "Rework and review again"',
            '--continue-owning-workflow-label "Commit"',
            "--implementation-step <exact-plan-step>",
            "one bounded `wait-request` per round",
            "immediately run the next bounded `wait-request`",
            "same reviewer session",
            "continue at Step 3",
            "Read only the returned `paths.request`",
            "whether the expired request is first seen cold",
            "Require the reclaimed state to be",
        ),
    )
    assert "Do not read the versioned transcript" in " ".join(content.split())


def test_instruction_covers_assessment_repairs_validation_and_early_rejection() -> None:
    """The caller preserves every designed assessment and mutation boundary."""
    content = _content()
    for required in (
        "request-time index tree",
        "early rejection",
        "implementation-check",
        "umbrella digest",
        "pre-existing unstaged",
        "reviewer-authored",
        "tracked validation side effect",
        "a.commit",
        "Human guidance:",
        "changes-requested",
        "commit-ready",
    ):
        assert required in content


def test_reviewer_rejects_requestor_initiated_sessions_before_reading() -> None:
    """A pending artifact cannot legitimize a requestor-spawned reviewer."""
    content = " ".join(_content().split())

    for fragment in (
        "Before any command or repository read",
        "Refuse the task when an automated requestor",
        "parent agent acting as requestor",
        "does not prove valid reviewer provenance",
        "independently waiting reviewer",
    ):
        assert fragment in content


def test_reviewer_never_initiates_a_requestor_and_stays_in_waits() -> None:
    """Answer publication and missing requests cannot trigger role creation."""
    content = " ".join(_content().split())

    for fragment in (
        "must not spawn, start, delegate, invoke, or message a requestor",
        "`pw skill code-review-requestor`",
        "publishing an answer is its entire handoff",
        "Never start or contact a requestor to produce that next round",
        "The absence of a request never authorizes reviewer-to-requestor delegation",
        "Never spawn, start, delegate, invoke, or message a requestor",
        "substitute another model call for the round wait or artifact-home wait",
    ):
        assert fragment in content


def test_instruction_covers_manifest_recovery_and_both_publication_exits() -> None:
    """Retained evidence survives failures and retires on either published exit."""
    content = _content()
    assert "identity-and-step-derived" in content
    assert "exits `0`" in content
    assert "exit `3`" in content
    assert "outcome: published" in content
    assert "assessed index tree" in content
    assert "fresh assessment" in content
    assert "exchange_occurrence" in content


def test_instruction_forbids_writer_human_and_commit_authority() -> None:
    """The reviewer can wait again without crossing role authority."""
    content = _content()
    normalized = " ".join(content.split())
    for operation in (
        "consume-answer",
        "continue",
        "confirm",
        "complete",
        "escalate",
        "cancel",
        "resolve",
        "archive",
        "commit",
    ):
        assert f"`{operation}`" in content
    assert "never authorizes a commit" in content
    assert "Waiting does not transfer requestor authority" in normalized
    assert "ends the reviewer's rounds, not its session" in normalized


def test_instruction_requires_the_reviewer_to_always_wait() -> None:
    """A reviewer never ends its session; it waits for the next request."""
    content = _content()
    normalized = " ".join(content.split())

    assert "## A reviewer always waits" in content
    assert "publishing an answer never returns control to the user" in normalized
    for phrase in (
        "The round wait.",
        "The artifact-home wait.",
        "Do not restrict that wait to the exchange just finished",
        "Neither wait is optional and neither is a question for the user",
    ):
        assert phrase in normalized
    assert "GlobalReviewerWait" in content
    assert "it has not shipped" in normalized
    assert "hold the artifact-home wait open in words" in normalized


def test_instruction_requires_independent_commit_plan_readiness_evidence() -> None:
    """The reviewer reruns the checker without treating success as authority."""
    content = " ".join(_content().split())
    _assert_contains_all(
        content,
        (
            '`& "<LLM_SHARED_DIR>\\commit-plan-check.bat" --format json`',
            "independent",
            "status `3`",
            "status `2`",
            "mechanical",
            "does not prove implementation completeness",
            "never authorizes a commit",
            "six readiness-floor results",
        ),
    )
    assert content.index(
        '`& "<LLM_SHARED_DIR>\\commit-plan-check.bat" --format json`',
    ) < content.index(
        "six readiness-floor results",
    )


# eof
