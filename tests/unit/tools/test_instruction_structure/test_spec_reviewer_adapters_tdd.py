"""Structure tests for specification reviewer host adapters.

Step 3 keeps reusable reviewer orchestration in the root instruction. The
workflow host retains the repository locate sequence, while packaged Codex and
Claude files use their loader-relative canonical links without copied policy.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_CANONICAL = _ROOT / "instructions" / "spec-reviewer.md"
_MAX_LINK_BODY_LINES = 2
_MAX_WORKFLOW_BODY_LINES = 8
_WORKFLOW = _ROOT / ".agent" / "workflows" / "spec-reviewer.md"
_SHARED_WORKFLOW = _ROOT / ".agent" / "workflows" / "spec-review-requestor.md"
_LINK_ADAPTERS = (
    _ROOT / ".agents" / "llm-shared" / "instructions" / "spec-reviewer.md",
    _ROOT / ".agents" / "llm-shared" / "skills" / "spec-reviewer" / "SKILL.md",
    _ROOT / ".claude" / "skills" / "spec-reviewer" / "SKILL.md",
)
_ADAPTERS = (_WORKFLOW, *_LINK_ADAPTERS)


def _body(content: str) -> str:
    """Return adapter content after optional YAML front matter."""
    if not content.startswith("---\n"):
        return content.strip()
    _front, separator, body = content[4:].partition("\n---\n")
    assert separator
    return body.strip()


def test_every_host_names_only_the_canonical_reviewer_instruction() -> None:
    """All requested hosts discover the role through canonical root prose."""
    assert _CANONICAL.is_file()
    for path in _ADAPTERS:
        body = _body(path.read_text(encoding="utf-8"))
        assert "instructions/spec-reviewer.md" in body
        assert "../.agent" not in body
        assert "../.agents" not in body
        assert "../.claude" not in body


def test_codex_and_claude_adapters_use_loader_relative_links() -> None:
    """Loader-relative hosts keep one direct link to the root instruction."""
    for path in _LINK_ADAPTERS:
        body = _body(path.read_text(encoding="utf-8"))
        assert "canonical instruction" in body.lower()
        assert len(body.splitlines()) <= _MAX_LINK_BODY_LINES


def test_codex_adapters_match_the_plugin_redirect_contract() -> None:
    """Codex redirects retain the exact forms used by packaged instructions."""
    packaged = _LINK_ADAPTERS[0].read_text(encoding="utf-8")
    assert packaged == (
        "Read and follow the canonical instruction at "
        "[`instructions/spec-reviewer.md`]"
        "(../../../../../../../git/llm-shared/instructions/spec-reviewer.md).\n"
    )
    skill = _LINK_ADAPTERS[1].read_text(encoding="utf-8")
    assert skill.rstrip().endswith(
        "Read and follow [the canonical instruction]"
        "(../../../../../../../../git/llm-shared/instructions/spec-reviewer.md)",
    )


def test_workflow_wrapper_reuses_the_repository_locate_steps() -> None:
    """The junctioned workflow host resolves the body outside this clone."""
    body = _body(_WORKFLOW.read_text(encoding="utf-8"))
    shared = _body(_SHARED_WORKFLOW.read_text(encoding="utf-8"))

    assert body == shared.replace(
        "instructions/spec-review-requestor.md",
        "instructions/spec-reviewer.md",
    )
    assert "sibling clone `../llm-shared`" in body
    assert "submodule folder" in body
    assert "../../instructions" not in body
    assert len(body.splitlines()) <= _MAX_WORKFLOW_BODY_LINES


def test_adapter_bodies_do_not_copy_reviewer_or_exchange_logic() -> None:
    """Metadata and one redirect are the only provider-specific content."""
    canonical = _CANONICAL.read_text(encoding="utf-8")
    for path in _ADAPTERS:
        body = _body(path.read_text(encoding="utf-8"))
        assert body not in canonical
        for copied_token in (
            "consolidation-ready",
            "wait-request",
            "publish-answer",
            "reclaim",
            "convergence-recommended",
        ):
            assert copied_token not in body


def test_skill_adapters_keep_discovery_metadata_only() -> None:
    """Skill front matter names the role while workflow metadata stays small."""
    for path in _ADAPTERS:
        content = path.read_text(encoding="utf-8")
        if path.name == "SKILL.md":
            assert "name: spec-reviewer" in content
            assert "description:" in content
        else:
            assert path.suffix == ".md"
    assert _WORKFLOW.read_text(encoding="utf-8").startswith("---\ndescription: ")
    claude = _LINK_ADAPTERS[-1].read_text(encoding="utf-8")
    assert "user-invocable: true" in claude


# eof
