"""Structure tests for thin review-status-command host adapters."""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_CANONICAL = _ROOT / "instructions" / "review-status-command.md"
_WORKFLOW = _ROOT / ".agent" / "workflows" / "review-status-command.md"
_LINK_ADAPTERS = (
    _ROOT / ".agents" / "llm-shared" / "instructions" / "review-status-command.md",
    _ROOT
    / ".agents"
    / "llm-shared"
    / "skills"
    / "review-status-command"
    / "SKILL.md",
    _ROOT / ".claude" / "skills" / "review-status-command" / "SKILL.md",
    _ROOT / ".github" / "skills" / "review-status-command" / "SKILL.md",
)
_ADAPTERS = (_WORKFLOW, *_LINK_ADAPTERS)
_MAX_ADAPTER_BODY_LINES = 8


def _body(content: str) -> str:
    """Return adapter content after optional YAML front matter."""
    if not content.startswith("---\n"):
        return content.strip()
    _front, separator, body = content[4:].partition("\n---\n")
    assert separator
    return body.strip()


def test_every_adapter_links_directly_to_the_canonical_instruction() -> None:
    """Provider discovery files never route through another adapter."""
    assert _CANONICAL.is_file()
    for path in _ADAPTERS:
        body = _body(path.read_text(encoding="utf-8"))
        assert "instructions/review-status-command.md" in body
        assert len(body.splitlines()) <= _MAX_ADAPTER_BODY_LINES


def test_skill_adapters_expose_the_review_status_command_name() -> None:
    """Installed skill wrappers expose the exact public discovery name."""
    for path in _LINK_ADAPTERS[1:]:
        content = path.read_text(encoding="utf-8")
        assert "name: review-status-command" in content
        assert "description:" in content
    for path in _LINK_ADAPTERS[2:]:
        assert "user-invocable: true" in path.read_text(encoding="utf-8")


def test_adapters_copy_no_status_or_mutation_policy() -> None:
    """Status behavior stays solely in the canonical instruction and command."""
    for path in _ADAPTERS:
        body = _body(path.read_text(encoding="utf-8"))
        for copied in (
            "owning-action-pending",
            "lease_renewed_at",
            "review_exchange.bat",
            "git add",
        ):
            assert copied not in body


# eof
