"""Tests for the pw skill module: host prefix, rendering, and disk routing.

Step 1 covers the pure functions of tools/prompt_workflow_skill.py: detect_host
(host markers, Claude-wins, Claude default), host_prefix (an override
short-circuits the environment read), and render_command (a bare
``<prefix><name> on <document>`` line, ``.md`` dropped, no backticks). A small
property loop guards the render invariants.

Step 2 covers next_command: the next step read from disk (compute_state with no
memory step, next_step_numbers, the decisions-table override), mapped to an
instruction and a target document and rendered with the host prefix.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import prompt_workflow_skill as skill
from tools.prompt_workflow_models import Topic

if TYPE_CHECKING:
    from pathlib import Path


def test_detect_host_reads_the_markers_with_claude_first() -> None:
    """The Claude marker wins, then Codex, then the default host."""
    # Act and Assert: each marker, then both, then neither.
    assert skill.detect_host({"CLAUDECODE": "1"}) == skill.HOST_CLAUDE
    assert skill.detect_host({"CODEX_THREAD_ID": "abc"}) == skill.HOST_CODEX
    assert skill.detect_host({"CLAUDECODE": "1", "CODEX_THREAD_ID": "abc"}) == skill.HOST_CLAUDE
    assert skill.detect_host({}) == skill.DEFAULT_HOST


def test_detect_host_ignores_an_empty_marker() -> None:
    """An empty marker value is not a present host (truthiness, not membership)."""
    assert skill.detect_host({"CLAUDECODE": ""}) == skill.DEFAULT_HOST


def test_host_prefix_detects_from_the_environment() -> None:
    """With no override the prefix follows the detected host."""
    assert skill.host_prefix({"CLAUDECODE": "1"}) == "/"
    assert skill.host_prefix({"CODEX_THREAD_ID": "abc"}) == "$"
    assert skill.host_prefix({}) == "/"


def test_host_prefix_override_short_circuits_detection() -> None:
    """An override sets the prefix and the environment is not consulted."""
    # A Codex override wins even with the Claude marker set in the environment.
    assert skill.host_prefix({"CLAUDECODE": "1"}, override=skill.HOST_CODEX) == "$"
    assert skill.host_prefix({"CODEX_THREAD_ID": "abc"}, override=skill.HOST_CLAUDE) == "/"


def test_render_command_drops_the_md_suffix() -> None:
    """A bare command drops the ``.md`` suffix and uses no backticks."""
    command = skill.render_command(
        "/", "write-design.md", "docs/design.v0.9.0.handoff_automation.md",
    )
    assert command == "/write-design on docs/design.v0.9.0.handoff_automation.md"
    assert "`" not in command


def test_render_command_keeps_a_name_without_the_md_suffix() -> None:
    """An instruction name without a ``.md`` suffix is rendered unchanged."""
    assert skill.render_command("$", "write-plans", "docs/x.md") == "$write-plans on docs/x.md"


def test_render_command_property_invariants() -> None:
    """Every rendered command starts with the prefix, has no backtick, ends on the doc."""
    instructions = ["write-design.md", "review-ask-questions.md", "process-draft.md"]
    # Act: render across both prefixes and a spread of versions and slugs.
    for prefix in ("/", "$"):
        for version in ("v0.9.0", "v1.2.3", "v10.0"):
            for slug in ("handoff_automation", "duration_outliers", "x"):
                for instruction in instructions:
                    document = f"docs/design.{version}.{slug}.md"
                    command = skill.render_command(prefix, instruction, document)
                    # Assert: the render invariants hold for every combination.
                    assert command.startswith(prefix)
                    assert "`" not in command
                    assert " on " in command
                    assert command.endswith(document)


def _topic(tmp_path: Path) -> Topic:
    """Build a scratch docs tree with a draft and return its topic."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(exist_ok=True)
    draft = docs_dir / "draft.v0.9.0.handoff_automation.md"
    draft.write_text("draft", encoding="utf-8")
    return Topic(version="v0.9.0", slug="handoff_automation", draft_path=draft)


def _write(tmp_path: Path, name: str, body: str) -> None:
    """Write a document under the scratch docs folder."""
    (tmp_path / "docs" / name).write_text(body, encoding="utf-8")


# Bodies that put a document in a given state for the routing tests.
_OPEN = "# x\n\n## Open questions\n\n### Q1\n"
_FRESH = "# x\n\nbody only\n"
_SETTLED_REQ = "# x\n\n## Requirement clarifications\n\n| a | b |\n"
_SETTLED_DESIGN = "# x\n\n## Design decisions\n\n| a | b |\n"
_SETTLED_PLAN = "# x\n\n## Implementation decisions\n\n| a | b |\n"
_REQ = "feature-request.v0.9.0.handoff_automation.md"
_DESIGN = "design.v0.9.0.handoff_automation.md"
_PLAN = "plan.v0.9.0.handoff_automation.md"
_CLAUDE = {"CLAUDECODE": "1"}


def test_next_command_off_slug_branch_processes_the_draft(tmp_path: Path) -> None:
    """Off the slug branch a lone draft routes to process-draft."""
    topic = _topic(tmp_path)
    command = skill.next_command(tmp_path, topic, "main", _CLAUDE)
    assert command == "/process-draft on docs/draft.v0.9.0.handoff_automation.md"


def test_next_command_on_slug_branch_writes_the_requirement(tmp_path: Path) -> None:
    """On the slug branch a lone draft routes to write-requirement."""
    topic = _topic(tmp_path)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == (
        "/write-requirement on docs/feature-request.v0.9.0.handoff_automation.md"
    )


def test_next_command_open_questions_requirement_consolidates(tmp_path: Path) -> None:
    """A requirement still carrying open questions routes to consolidate."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _OPEN)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == (
        "/consolidate-then-review-ask-questions on "
        "docs/feature-request.v0.9.0.handoff_automation.md"
    )


def test_next_command_fresh_requirement_reviews(tmp_path: Path) -> None:
    """A fresh requirement (no markers) routes to review-ask-questions."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _FRESH)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == (
        "/review-ask-questions on docs/feature-request.v0.9.0.handoff_automation.md"
    )


def test_next_command_settled_requirement_writes_the_design(tmp_path: Path) -> None:
    """A requirement carrying a decisions table advances to write-design."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/write-design on docs/design.v0.9.0.handoff_automation.md"


def test_next_command_fresh_design_reviews(tmp_path: Path) -> None:
    """A settled requirement and a fresh design route to review-ask-questions."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _FRESH)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/review-ask-questions on docs/design.v0.9.0.handoff_automation.md"


def test_next_command_settled_design_writes_the_plans(tmp_path: Path) -> None:
    """A settled requirement and a settled design advance to write-plans."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/write-plans on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_fresh_plan_reviews(tmp_path: Path) -> None:
    """A fresh plan, the earlier docs settled, routes to review-ask-questions."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _FRESH)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/review-ask-questions on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_settled_plan_implements(tmp_path: Path) -> None:
    """A settled plan, the earlier docs settled, advances to implement-step."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _SETTLED_PLAN)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/implement-step on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_uses_the_codex_prefix(tmp_path: Path) -> None:
    """The host prefix follows the environment, here Codex."""
    topic = _topic(tmp_path)
    command = skill.next_command(tmp_path, topic, "main", {"CODEX_THREAD_ID": "x"})
    assert command == "$process-draft on docs/draft.v0.9.0.handoff_automation.md"


# eof
