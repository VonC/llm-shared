"""TDD contracts for typed, side-effect-free commit-plan validation."""

from __future__ import annotations

from tools.git_batch_commit_models import CommitBlock, CommitPlanSubjectRequirement
from tools.git_batch_commit_parsing import parse_clipboard_content
from tools.git_batch_commit_validation import validate_commit_plan

_UNSUPPORTED_COMMAND_COUNT = 4


def _block(title: str, *paths: str) -> CommitBlock:
    """Build one parsed-equivalent commit group."""
    message = f"{title}\n\nWhy:\n\nreason before\n\nreason after\n\nWhat:\n\n- change"
    return CommitBlock(
        git_adds=[f"git add -A -- {path}" for path in paths],
        commit_message=message,
        commit_title=title,
    )


def test_validate_commit_plan_preserves_group_order_and_exact_membership() -> None:
    """A valid plan returns typed groups in their original order."""
    result = validate_commit_plan(
        [
            _block("feat(evidence): add snapshots", "tools/evidence.py"),
            _block("test(evidence): cover snapshots", "tests/test_evidence.py"),
        ],
        ["tests/test_evidence.py", "tools/evidence.py"],
    )
    assert result.valid is True
    assert [group.position for group in result.groups] == [1, 2]
    assert [group.subject for group in result.groups] == [
        "feat(evidence): add snapshots",
        "test(evidence): cover snapshots",
    ]
    assert result.diagnostics == ()


def test_validate_commit_plan_reports_membership_duplicates_and_subjects() -> None:
    """Every staged path appears once and every group subject is conventional."""
    result = validate_commit_plan(
        [
            _block("feature: not conventional", "duplicate.py"),
            _block("fix(scope): valid", "duplicate.py", "planned-only.py"),
        ],
        ["duplicate.py", "staged-only.py"],
    )
    assert result.valid is False
    assert any("conventional" in item for item in result.diagnostics)
    assert any("multiple groups" in item for item in result.diagnostics)
    assert any("not staged" in item for item in result.diagnostics)
    assert any("missing from the plan" in item for item in result.diagnostics)


def test_non_interactive_parser_output_feeds_public_validator() -> None:
    """Reviewer parsing never prompts before the public validation boundary."""
    content = """## Group 1: evidence

git add -A -- tools/evidence.py

```log
feat(evidence): add snapshots

Why:

reason before

reason after

What:

- add snapshots
```
"""
    blocks = parse_clipboard_content(content, interactive=False)
    result = validate_commit_plan(blocks, ["tools/evidence.py"])
    assert result.valid is True
    assert result.groups[0].paths == ("tools/evidence.py",)


def test_validate_commit_plan_rejects_malformed_and_unsafe_git_adds() -> None:
    """Unsupported commands, quoting, path counts, and traversal are diagnostic."""
    block = CommitBlock(
        git_adds=[
            "git status file.py",
            'git add -A "unterminated',
            "git add -A one.py two.py",
            "git add -A ../outside.py",
        ],
        commit_message="fix(scope): title",
        commit_title="fix(scope): title",
    )
    result = validate_commit_plan([block], [])
    assert result.valid is False
    assert (
        sum("unsupported git add" in item for item in result.diagnostics)
        == _UNSUPPORTED_COMMAND_COUNT
    )


def test_validate_commit_plan_accepts_option_form_without_separator() -> None:
    """The established git-add form without `--` resolves its one path."""
    block = CommitBlock(
        git_adds=["git add -A tools/evidence.py"],
        commit_message="fix(scope): title",
        commit_title="fix(scope): title",
    )
    result = validate_commit_plan([block], ["tools/evidence.py"])
    assert result.valid is True


def test_validate_commit_plan_requires_exact_completed_validation_subject() -> None:
    """A completed validation path makes its pw marker a mechanical rule."""
    path = "docs/v0.11.0/plan.v0.11.0.topic.validation.md"
    requirement = CommitPlanSubjectRequirement(
        path=path,
        subject="docs(topic): record step 1 validation",
    )

    invalid = validate_commit_plan(
        [_block("docs(topic): update step 1 validation", path)],
        [path],
        (requirement,),
    )
    valid = validate_commit_plan(
        [_block(requirement.subject, path)],
        [path],
        (requirement,),
    )

    assert invalid.valid is False
    assert invalid.diagnostics == (
        "group 1 containing completed validation plan "
        f"{path} must use exact subject: {requirement.subject}",
    )
    assert valid.valid is True


def test_subject_requirement_defers_to_membership_diagnostics() -> None:
    """Missing or duplicated ownership is reported by exact membership checks."""
    requirement = CommitPlanSubjectRequirement(
        path="docs/plan.v1.0.topic.validation.md",
        subject="docs(topic): record step 1 validation",
    )

    result = validate_commit_plan(
        [_block("docs(topic): update validation", "other.md")],
        ["other.md"],
        (requirement,),
    )

    assert result.valid is True


# eof
