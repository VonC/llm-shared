"""Tests for the pw skill foundation: host prefix and command rendering.

Step 1 of docs/plan.v0.9.0.handoff_automation.md covers the pure functions of
tools/prompt_workflow_skill.py: detect_host (read the host markers with the
Claude-wins precedence and the Claude default), host_prefix (an override
short-circuits the environment read), and render_command (a bare
``<prefix><name> on <document>`` line with the ``.md`` suffix dropped and no
backticks). A small property loop guards the render invariants.
"""

from __future__ import annotations

from tools import prompt_workflow_skill as skill


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


# eof
