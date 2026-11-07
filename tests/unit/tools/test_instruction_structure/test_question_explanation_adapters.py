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

Fix: without a blocking choice (Codex Default mode), the chat list now comes
with a ``blocked`` report to the terminal, and the answer with ``working``
before it is recorded, both under ``rules/interactive_menu.md``.

Fix: a user reading one question at a time lost the bigger picture. After its
status, every explanation now describes the project around the question,
umbrella first, then the topic draft and the effort's documents, with an
end-to-end walkthrough and a flow diagram marking the question's step, before
the question itself. Two tests pin that order in the instruction, the template
and the state note, and its recomposition on resume.

Fix: a flow diagram past the limits of Codex's terminal renderer showed as
source under "This Mermaid diagram exceeds the terminal renderer's size
limits.". The flow diagram part now links the Mermaid rules of
``rules/markdown.md``. A test pins those limits, the link, and the template
diagram within them.

Fix: a notion the user asks about was explained in the chat only. It is now
introduced in the umbrella draft, the topic draft and the effort's documents
up to the one under review, without changing any decision, recorded in the
note, and explained again in more detail by every later question involving
it. The last test pins those rules, the template part and the note section.
"""

from __future__ import annotations

import re

import pytest

from tools import prompt_workflow_steps as steps

ROOT = steps.llm_shared_dir()
SKILL = "explain-undecided-questions"
# Codex's terminal Mermaid renderer refuses a wider label line (MAX_LABEL).
MERMAID_LABEL_COLUMNS = 40


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
        "`request_user_input` in Codex (Plan mode, or Default mode with its\nfeature on)",
        "`(Recommended)`",
        "Without a blocking choice, as in Codex Default mode",
        "report the question as `blocked` first",
        "A typed reply",
        "report `working` before recording the answer",
    ):
        assert required in section
    resume = instruction.split("- `awaiting-user-decision`:", 1)[1].split("\n- ", 1)[0]
    assert "ask the choice again" in resume
    assert "`blocked` report" in resume
    template = (ROOT / "templates/question-explanation.template.md").read_text(encoding="utf-8")
    decision = template.split("## Decision prompt", 1)[1]
    for required in (
        "Do not write this section as text",
        "`rules/interactive_menu.md`",
        "as `blocked` to the\nterminal",
        "`(Recommended)`",
        "Never pre-record the recommended option",
    ):
        assert required in decision


def _ordered(text: str, *markers: str) -> list[int]:
    """Return each marker's first index in ``text``, failing on a missing one."""
    return [text.index(marker) for marker in markers]


def test_every_explanation_places_the_question_in_the_big_picture() -> None:
    """The instruction composes the umbrella, draft and flow picture shown before every question."""
    instruction = (ROOT / "instructions" / f"{SKILL}.md").read_text(encoding="utf-8")
    section = instruction.split("## Compose the big picture shown before every question", 1)[1].split("\n## ", 1)[0]
    sources = _ordered(section, "1. The umbrella draft", "2. The topic draft", "3. The effort's other documents")
    assert sources == sorted(sources)
    parts = _ordered(section, "- Purpose:", "- Today and after:", "- Terms:", "- Walkthrough:", "- Flow diagram:", "- Close-up:", "- The question:")
    assert parts == sorted(parts)
    for required in ("before every question", "`not resolved`", "never fill a gap", "`Q01=A3`", "big-picture section"):
        assert required in section
    step = instruction.split("2. Explain it with", 1)[1].split("\n3. ", 1)[0]
    assert "the big picture with this question's step marked" in step
    assert "Keep the decision within the document's scope" in step
    resume = instruction.split("## Pause and resume", 1)[1]
    assert "recomposes the big picture" in resume


def test_the_templates_render_and_save_the_big_picture() -> None:
    """The template shows the picture after the status; the state note saves it."""
    template = (ROOT / "templates/question-explanation.template.md").read_text(encoding="utf-8")
    order = _ordered(
        template,
        "## Where this question sits",
        "Status: awaiting your decision.",
        "## The bigger picture around this question",
        "{For an umbrella item",
        "This is the part involved in **{question-id}**",
        "```mermaid",
        "### What {question-id} is asking",
        "### Example",
        "### Where the choice lands",
        "## Decision prompt",
    )
    assert order == sorted(order)
    state = (ROOT / "templates/question-explanation-state.template.md").read_text(encoding="utf-8")
    picture = state.split("## Big picture shown before each question", 1)[1].split("\n## ", 1)[0]
    for field in ("- Sources and refresh:", "- Purpose:", "- Walkthrough steps:", "- Step of each batch question:"):
        assert field in picture


def test_flow_diagrams_stay_within_what_codex_can_draw() -> None:
    """The Mermaid rules give Codex's limits; the instruction and the template diagram follow them."""
    rules = (ROOT / "rules/markdown.md").read_text(encoding="utf-8")
    section = rules.split("## Mermaid diagrams that Codex can draw", 1)[1].split("\n## ", 1)[0]
    for required in (
        "at most 40 columns",
        "with `<br>`",
        "At most 16 nodes and 24 edges",
        "No `subgraph`",
        "Prefer `flowchart TD`",
        "under 80 columns",
    ):
        assert required in section
    instruction = (ROOT / "instructions" / f"{SKILL}.md").read_text(encoding="utf-8")
    part = instruction.split("- Flow diagram:", 1)[1].split("\n- ", 1)[0]
    assert "(../rules/markdown.md#mermaid-diagrams-that-codex-can-draw)" in part
    template = (ROOT / "templates/question-explanation.template.md").read_text(encoding="utf-8")
    diagram = template.split("```mermaid\n", 1)[1].split("```", 1)[0]
    assert diagram.startswith("flowchart TD")
    assert "subgraph" not in diagram
    labels = re.findall(r'\["([^"]*)"\]', diagram)
    assert labels
    assert all(len(line) <= MERMAID_LABEL_COLUMNS for label in labels for line in re.split(r"<br\s*/?>", label))


def test_an_asked_notion_reaches_every_document_and_returns_in_more_detail() -> None:
    """A notion the user asks about is written into the effort's documents and re-explained later."""
    instruction = (ROOT / "instructions" / f"{SKILL}.md").read_text(encoding="utf-8")
    section = instruction.split("## Explain a notion the user asks about", 1)[1].split("\n## ", 1)[0]
    documents = _ordered(section, "the umbrella draft when", "the topic draft", "the requirement", "the design", "the\n   plan")
    assert documents == sorted(documents)
    for required in (
        "up to and including the document under review",
        "Do not create a\n   document the effort has not reached yet",
        "Keep every\n   decision, question ID, option, recommendation and recorded answer",
        "notions section",
        "the follow-up review examines them",
        "in more detail than the previous time",
    ):
        assert required in section
    assert "introducing the notions the user asks\nabout" in instruction
    step = instruction.split("3. Save `awaiting-user-decision`", 1)[1].split("\n4. ", 1)[0]
    assert "(#explain-a-notion-the-user-asks-about)" in step
    assert "including the notion introductions" in instruction.split("## Finish with a fresh independent review", 1)[1]
    template = (ROOT / "templates/question-explanation.template.md").read_text(encoding="utf-8")
    order = _ordered(template, "### What {question-id} is asking", "### Notions you asked about, in more detail", "### Example")
    assert order == sorted(order)
    state = (ROOT / "templates/question-explanation-state.template.md").read_text(encoding="utf-8")
    notions = state.split("## Notions explained to the user", 1)[1].split("\n## ", 1)[0]
    assert "raised at {question ID}; introduced in" in notions


# eof
