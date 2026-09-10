"""Structure contracts for Step 2 code-review requestor host adapters.

Provider files retain discovery metadata and point directly to the canonical
root instruction. Policy and lifecycle prose must never be copied into them.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_CANONICAL = _ROOT / "instructions" / "code-review-requestor.md"
_WORKFLOW = _ROOT / ".agent" / "workflows" / "code-review-requestor.md"
_SHARED_WORKFLOW = _ROOT / ".agent" / "workflows" / "review-requestor.md"
_LINK_ADAPTERS = (
    _ROOT / ".agents" / "llm-shared" / "instructions" / "code-review-requestor.md",
    _ROOT / ".agents" / "llm-shared" / "skills" / "code-review-requestor" / "SKILL.md",
    _ROOT / ".claude" / "skills" / "code-review-requestor" / "SKILL.md",
)
_ADAPTERS = (_WORKFLOW, *_LINK_ADAPTERS)
_MAX_LINK_BODY_LINES = 2
_MAX_WORKFLOW_BODY_LINES = 8


def _body(content: str) -> str:
    """Return adapter content after optional YAML front matter."""
    if not content.startswith("---\n"):
        return content.strip()
    _front, separator, body = content[4:].partition("\n---\n")
    assert separator
    return body.strip()


def test_every_adapter_names_only_the_direct_canonical_instruction() -> None:
    """All hosts discover the specialized role through the root source."""
    assert _CANONICAL.is_file()
    for path in _ADAPTERS:
        body = _body(path.read_text(encoding="utf-8"))
        assert "instructions/code-review-requestor.md" in body
        assert "../.agent" not in body
        assert "../.agents" not in body
        assert "../.claude" not in body


def test_link_adapters_keep_metadata_plus_one_redirect() -> None:
    """Codex and Claude loader files retain their established redirect shape."""
    for path in _LINK_ADAPTERS:
        content = path.read_text(encoding="utf-8")
        body = _body(content)
        assert "canonical instruction" in body.lower()
        assert len(body.splitlines()) <= _MAX_LINK_BODY_LINES
        if path.name == "SKILL.md":
            assert "name: code-review-requestor" in content
            assert "description:" in content


def test_codex_redirects_match_direct_plugin_paths() -> None:
    """Packaged instruction and skill paths resolve straight to root prose."""
    packaged = _LINK_ADAPTERS[0].read_text(encoding="utf-8")
    assert packaged == (
        "Read and follow the canonical instruction at "
        "[`instructions/code-review-requestor.md`]"
        "(../../../../../../../git/llm-shared/instructions/code-review-requestor.md).\n"
    )
    skill = _LINK_ADAPTERS[1].read_text(encoding="utf-8")
    assert skill.rstrip().endswith(
        "Read and follow [the canonical instruction]"
        "(../../../../../../../../git/llm-shared/instructions/code-review-requestor.md)",
    )


def test_workflow_reuses_repository_location_steps() -> None:
    """The junctioned workflow resolves the canonical body outside this clone."""
    body = _body(_WORKFLOW.read_text(encoding="utf-8"))
    shared = _body(_SHARED_WORKFLOW.read_text(encoding="utf-8"))
    assert body == shared.replace(
        "instructions/review-requestor.md",
        "instructions/code-review-requestor.md",
    )
    assert "sibling clone `../llm-shared`" in body
    assert "submodule folder" in body
    assert len(body.splitlines()) <= _MAX_WORKFLOW_BODY_LINES


def test_adapters_copy_no_policy_or_lifecycle_logic() -> None:
    """Only the canonical file contains specialized behavior tokens."""
    canonical = _CANONICAL.read_text(encoding="utf-8")
    for path in _ADAPTERS:
        body = _body(path.read_text(encoding="utf-8"))
        assert body not in canonical
        for token in (
            "commit-ready",
            "Rework and review again",
            "reviewed-work-changed",
            "owning-action-pending",
        ):
            assert token not in body


def test_claude_and_workflow_discovery_metadata_is_minimal() -> None:
    """Claude stays invocable and workflow metadata remains descriptive only."""
    assert _WORKFLOW.read_text(encoding="utf-8").startswith("---\ndescription: ")
    claude = _LINK_ADAPTERS[-1].read_text(encoding="utf-8")
    assert "user-invocable: true" in claude


# eof
