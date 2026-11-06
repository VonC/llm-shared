"""All hosts discover question discussion through one canonical instruction.

Fix: every explained question now opens with its full context (umbrella and
item position, topic, phase, draft, document, batch position and review), so
the user knows what is being decided. The tests below pin that the template
opens with that table, that the state note saves it, and that the instruction
gathers it from ``pw progress`` with the drafts as fallback, never a guess.

Fix: every explanation now ends with a host-native choice instead of options
written as text, so the host shows the agent waiting for a reply rather than
done. The last test pins that decision step in the instruction, its resume
path and the template.
"""

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


CONTEXT_ROWS = ("Umbrella", "Topic", "Phase", "Draft", "Document", "Questions", "Review")


def test_every_explanation_opens_with_its_full_context() -> None:
    """The context table comes before the progress line and names every field."""
    template = (ROOT / "templates/question-explanation.template.md").read_text(encoding="utf-8")
    context = template.index("## Where this question sits")
    assert context < template.index("{question-id}/{last-question-id} {percentage}%")
    section = template[context:].split("\n## ", 1)[0]
    rows = [line.split("|")[1].strip() for line in section.splitlines() if line.startswith("| ")]
    assert tuple(rows[2:]) == CONTEXT_ROWS
    assert "item {x}/{N}" in template
    assert "`none, standalone topic`" in template
    assert "`not resolved`" in template


def test_context_is_saved_and_gathered_without_guessing() -> None:
    """The note keeps the context; the instruction reads pw progress, then the drafts."""
    state = (ROOT / "templates/question-explanation-state.template.md").read_text(encoding="utf-8")
    for field in ("- Document type:", "- Topic and phase:", "- Umbrella:", "- Topic draft:", "- Context source and refresh:"):
        assert field in state
    instruction = (ROOT / "instructions" / f"{SKILL}.md").read_text(encoding="utf-8")
    section = instruction.split("## Gather the context shown with every question", 1)[1].split("\n## ", 1)[0]
    assert 'prompt_workflow.bat" progress' in section
    assert "`- Umbrella:`" in section
    assert "never guess" in section
    assert "gathers the\nquestion context again" in instruction


def test_every_explanation_ends_with_a_native_choice() -> None:
    """The decision goes through interactive_menu.md as a host choice, never as text only."""
    instruction = (ROOT / "instructions" / f"{SKILL}.md").read_text(encoding="utf-8")
    step = instruction.split("3. Save `awaiting-user-decision`", 1)[1].split("\n4. ", 1)[0]
    assert "(#ask-for-the-decision-as-a-choice)" in step
    section = instruction.split("## Ask for the decision as a choice", 1)[1].split("\n## ", 1)[0]
    for required in (
        "(../rules/interactive_menu.md)",
        "`AskUserQuestion`",
        "`request_user_input`",
        "`(Recommended)`",
        "Only when the host has no native choice",
        "A typed reply",
    ):
        assert required in section
    resume = instruction.split("- `awaiting-user-decision`:", 1)[1].split("\n- ", 1)[0]
    assert "ask the choice again" in resume
    template = (ROOT / "templates/question-explanation.template.md").read_text(encoding="utf-8")
    decision = template.split("## Decision prompt", 1)[1]
    for required in (
        "Do not write this section as text",
        "`rules/interactive_menu.md`",
        "`(Recommended)`",
        "Never pre-record the recommended option",
    ):
        assert required in decision


# eof
