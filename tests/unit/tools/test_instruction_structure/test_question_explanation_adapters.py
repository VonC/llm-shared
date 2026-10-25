"""All hosts discover question discussion through one canonical instruction."""

from __future__ import annotations

import pytest

from tools import prompt_workflow_steps as steps

ROOT = steps.llm_shared_dir()
SKILL = "explain-undecided-questions"


@pytest.mark.parametrize(
    "folder",
    [".agents/llm-shared/skills", ".claude/skills", ".github/skills"],
)
def test_skill_discovery_and_direct_redirect(folder: str) -> None:
    """Each skill is discoverable and carries no independent workflow body."""
    path = ROOT / folder / SKILL / "SKILL.md"
    content = path.read_text(encoding="utf-8")
    metadata, body = content[4:].split("\n---\n", 1)
    assert f"name: {SKILL}" in metadata
    assert "description:" in metadata
    assert body.strip().startswith("Read and follow [the canonical instruction]")
    assert len(body.strip().splitlines()) == 1
    assert f"instructions/{SKILL}.md" in body
    if folder != ".agents/llm-shared/skills":
        assert "user-invocable: true" in metadata
        assert (
            (path.parent / "../../../instructions" / f"{SKILL}.md").resolve().is_file()
        )


@pytest.mark.parametrize(
    "folder",
    [".agent/workflows", ".grok/commands", ".agents/llm-shared/instructions"],
)
def test_command_redirect_matches_host_contract(folder: str) -> None:
    """Workflow and compatibility adapters retain each host's resolution form."""
    content = (ROOT / folder / f"{SKILL}.md").read_text(encoding="utf-8")
    existing = (ROOT / folder / "spec-review-requestor.md").read_text(encoding="utf-8")
    body = content.split("\n---\n", 1)[-1].strip()
    expected = existing.split("\n---\n", 1)[-1].strip()
    assert body == expected.replace("spec-review-requestor", SKILL)


# eof
