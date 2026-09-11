"""Structure tests for thin implementation code-reviewer host adapters."""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_CANONICAL = _ROOT / "instructions" / "code-reviewer.md"
_WORKFLOW = _ROOT / ".agent" / "workflows" / "code-reviewer.md"
_LINK_ADAPTERS = (
    _ROOT / ".agents" / "llm-shared" / "instructions" / "code-reviewer.md",
    _ROOT / ".agents" / "llm-shared" / "skills" / "code-reviewer" / "SKILL.md",
    _ROOT / ".claude" / "skills" / "code-reviewer" / "SKILL.md",
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
        assert "instructions/code-reviewer.md" in body
        assert "../.agent" not in body
        assert "../.agents" not in body
        assert "../.claude" not in body


def test_adapter_bodies_copy_no_reviewer_policy_or_operations() -> None:
    """Metadata and one redirect are the only provider-specific content."""
    canonical = _CANONICAL.read_text(encoding="utf-8")
    for path in _ADAPTERS:
        body = _body(path.read_text(encoding="utf-8"))
        assert body not in canonical
        assert len(body.splitlines()) <= _MAX_ADAPTER_BODY_LINES
        for copied in (
            "commit-ready",
            "wait-request",
            "publish-answer",
            "code_review_evidence.bat",
        ):
            assert copied not in body


def test_skill_adapters_keep_only_discovery_metadata_and_one_redirect() -> None:
    """Codex and Claude wrappers expose the exact role without policy forks."""
    for path in _LINK_ADAPTERS[1:]:
        content = path.read_text(encoding="utf-8")
        assert "name: code-reviewer" in content
        assert "description:" in content
        assert "canonical instruction" in _body(content).lower()
    assert "user-invocable: true" in _LINK_ADAPTERS[-1].read_text(encoding="utf-8")


# eof
