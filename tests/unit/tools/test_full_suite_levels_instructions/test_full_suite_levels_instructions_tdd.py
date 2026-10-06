"""Pin workflow level and scope boundaries without prescribing all prose.

Fix: development follows the requirement scope, review proves speed, and
release proves whole-suite coverage. Review-off changes return through check.
These are text policy contracts; no runtime algorithm requires property tests.
"""

from __future__ import annotations

import pytest

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_EXPECTED_SENV_CALLS = 2
_REQUIREMENT_TEMPLATE_SHAPES = 2


def _read(path: str) -> str:
    """Normalize whitespace so wrapping does not alter policy assertions."""
    return " ".join((_ROOT / path).read_text(encoding="utf-8").split())


def _contains(path: str, *tokens: str) -> str:
    """Require independently meaningful policy fragments in one document."""
    content = _read(path)
    for token in tokens:
        assert token in content, (path, token)
    return content


@pytest.mark.parametrize("name", ["implement-step", "implement-missing-step", "split-large-file"])
def test_development_resolves_scope_and_skips_default_full(name: str) -> None:
    """A current requirement choice is resolved when the command runs."""
    content = _contains(
        f"instructions/{name}.md", "pw scope day", "check.bat", "affected tests",
        "full stage is deliberately skipped", "printed repair and restart",
    )
    assert "full coverage pass" not in content


def test_review_off_compares_tree_and_exclusions_before_menu() -> None:
    """Changed or unverified evidence goes back through implementation-check."""
    content = _read("instructions/implement-step.md")
    sample = content.index("sample review mode exactly once")
    gate = content.index("### Review-off speed pass")
    assert sample < gate
    section = content[gate:]
    cursor = -1
    for token in (
        "git add -A", "git write-tree", "ghog exclude --list",
        "a.<slug>.step<x>.tmp.exclusions.txt", "pw scope day --full=speed",
        "--since=", "exclusions=unchanged", "exclusions=changed",
        "exclusions=unverified", "pw handoff check <x>", "commit menu",
    ):
        position = section.find(token, cursor + 1)
        assert position > cursor, token
        cursor = position
    for token in ("measured seconds", "attempted improvement", "reason",
                  "journal", "handoff", "No test-only exemption", "new reference"):
        assert token in section
    _contains("instructions/group-commits-msg.md", "review-off speed pass", "accepted exclusion")


def test_loop_retains_resolved_objective_and_printed_commands() -> None:
    """Repairs must never silently downgrade the requested evidence."""
    content = _contains(
        "instructions/groundhog.md", "starting level and scope", "GHOG_FULL",
        "GHOG_GROUP", "full stage is deliberately skipped", "printed repair and restart",
        "only at `speed`", "proof=pending", "--scope-file",
    )
    assert content.count(".\\senv.bat &&") == _EXPECTED_SENV_CALLS
    _contains("instructions/fix_slow_test.md", "ghog day --full=speed", "same scope")


def test_plan_and_handoff_keep_scope_live_and_record_actual_gate() -> None:
    """Plans resolve scope at execution; notes preserve the command executed."""
    for path in ("instructions/write-plans.md", "templates/write-plans.template.md"):
        _contains(path, "pw scope day", "selector", "affected tests")
    _contains("templates/step-handoff.template.md", "Last gate:", "command with its selector")
    _contains("instructions/step-journal.md", "command with its selector")


def test_scope_menu_follows_branch_choice_and_handles_children() -> None:
    """Only a focused effort gets a scope; new groups are validated first."""
    content = _contains(
        "instructions/process-draft.md", "Whole suite", "ghog groups", "New group",
        "Type something else", "ghog groups <name>", "- Test group:",
        "tests", "sources", "umbrella draft", "child",
    )
    assert content.index("the branch-layout choices") < content.index("### Test-scope menu")
    _contains(
        "instructions/write-requirement.md", "only when the draft records no choice",
        "requirement is authoritative", "ghog groups <name>", "- Test group:",
    )
    template = _read("templates/write-requirement.template.md")
    assert template.count("- Test group:") == _REQUIREMENT_TEMPLATE_SHAPES


def test_release_requires_coverage_of_whole_suite() -> None:
    """Ambient or effort groups cannot weaken release validation."""
    _contains("instructions/prepare-release.md", "ghog day --full=cov --whole-suite")
    for path in (".claude/skills/prepare-release/SKILL.md", ".github/skills/prepare-release/SKILL.md"):
        _contains(path, "ghog day --full=cov --whole-suite")


@pytest.mark.parametrize("path", [
    ".claude/skills/prepare-release/SKILL.md", ".github/skills/prepare-release/SKILL.md",
    ".agents/llm-shared/skills/fix-slow-test/SKILL.md", ".agent/workflows/fix-slow-test.md",
])
def test_changed_adapters_keep_only_redirect_bodies(path: str) -> None:
    """Descriptions may carry triggers; canonical instructions own behavior."""
    raw = (_ROOT / path).read_text(encoding="utf-8")
    body = raw.split("---", 2)[-1].strip() if raw.startswith("---") else raw.strip()
    assert len(body.splitlines()) == 1
    assert "instructions/" in body
    assert "Read" in body or "Follow" in body
    if "fix-slow-test" in path:
        assert "speed" in raw


@pytest.mark.parametrize("path", ["GROUNDHOG.md", "tools/Pytest reset specs.md", "DEVELOPMENT.md"])
def test_manuals_explain_levels_proof_scopes_and_migration(path: str) -> None:
    """Public reference covers weaker defaults and bounded group evidence."""
    _contains(
        path, "GHOG_FULL", "GHOG_GROUP", "--full=pass", "--full=cov", "--full=speed",
        "pw scope", ".ghog-groups", "python_files", "100%", "fingerprint",
        "proof", "reused", "--scope-file", "ghog exclude --list", "--since",
        "exclusions=unverified", ".review-validation", "whole suite", "timings",
    )


def test_spec_adds_decisions_and_acceptance_cases() -> None:
    """New policy has decision identifiers and observable acceptance cases."""
    _contains("tools/Pytest reset specs.md", "Q71", "Q72", "Q73", "AT20", "AT21", "AT22")


# eof
