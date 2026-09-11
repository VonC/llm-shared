"""Pure host-detection and command-rendering tests for ``pw skill``."""

from tools import prompt_workflow_skill as skill


def test_detect_host_reads_one_marker_without_a_default() -> None:
    """Known single markers resolve while missing evidence stays unknown."""
    assert skill.detect_host({"CLAUDECODE": "1"}) == skill.HOST_CLAUDE
    assert skill.detect_host({"CODEX_THREAD_ID": "abc"}) == skill.HOST_CODEX
    assert skill.detect_host({}) == skill.DEFAULT_HOST


def test_detect_host_reports_conflicting_markers_as_unknown() -> None:
    """Contradictory environment evidence does not pick a host silently."""
    both = {"CLAUDECODE": "1", "CODEX_THREAD_ID": "abc"}
    assert skill.detect_host(both) == skill.HOST_UNKNOWN


def test_detect_host_ignores_an_empty_marker() -> None:
    """An empty marker value is not a present host."""
    assert skill.detect_host({"CLAUDECODE": ""}) == skill.DEFAULT_HOST


def test_host_prefix_detects_from_the_environment() -> None:
    """With no override the prefix follows the detected host."""
    assert skill.host_prefix({"CLAUDECODE": "1"}) == "/"
    assert skill.host_prefix({"CODEX_THREAD_ID": "abc"}) == "$"
    assert skill.host_prefix({}) == "<command-prefix>"


def test_host_prefix_override_short_circuits_detection() -> None:
    """An override sets the prefix and the environment is not consulted."""
    assert skill.host_prefix({"CLAUDECODE": "1"}, override=skill.HOST_CODEX) == "$"
    assert skill.host_prefix(
        {"CODEX_THREAD_ID": "abc"},
        override=skill.HOST_CLAUDE,
    ) == "/"
    assert skill.host_prefix({}, override=skill.HOST_GEMINI) == "/"


def test_render_command_drops_the_md_suffix() -> None:
    """A bare command drops the ``.md`` suffix and uses no backticks."""
    command = skill.render_command(
        "/",
        "write-design.md",
        "docs/design.v0.9.0.handoff_automation.md",
    )
    assert command == "/write-design on docs/design.v0.9.0.handoff_automation.md"
    assert "`" not in command


def test_render_command_keeps_a_name_without_the_md_suffix() -> None:
    """An instruction name without a ``.md`` suffix is rendered unchanged."""
    assert skill.render_command("$", "write-plans", "docs/x.md") == (
        "$llm-shared:write-plans on docs/x.md"
    )


def test_render_step_command_extends_both_hosts_without_changing_the_base() -> None:
    """A step-aware command is the ordinary command plus one literal suffix."""
    document = "docs/plan.v0.11.0.routing.md"
    for prefix, expected_name in (
        ("/", "code-review-requestor"),
        ("$", "llm-shared:code-review-requestor"),
    ):
        ordinary = skill.render_command(prefix, "code-review-requestor.md", document)
        step_aware = skill.render_step_command(
            prefix,
            "code-review-requestor.md",
            document,
            "4A",
        )
        assert ordinary == f"{prefix}{expected_name} on {document}"
        assert step_aware == f"{ordinary} step 4A"
        assert step_aware.startswith(ordinary)


def test_render_command_property_invariants() -> None:
    """Rendered commands preserve their prefix and target document."""
    instructions = ["write-design.md", "review-ask-questions.md", "process-draft.md"]
    for prefix in ("/", "$"):
        for version in ("v0.9.0", "v1.2.3", "v10.0"):
            for slug in ("handoff_automation", "duration_outliers", "x"):
                for instruction in instructions:
                    document = f"docs/design.{version}.{slug}.md"
                    command = skill.render_command(prefix, instruction, document)
                    assert command.startswith(prefix)
                    assert "`" not in command
                    assert " on " in command
                    assert command.endswith(document)


# eof
