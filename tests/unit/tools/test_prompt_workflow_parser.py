"""Contracts for the `pw` argument parser, split out of `tools.prompt_workflow`.

`--root` and `--debug` parse on either side of every subcommand (Q01), the
`handoff` step stays a plain string (Q04, Q56), and `skill` and `progress`
share the same `--host` choices.
"""

from __future__ import annotations

import pytest

from tools import prompt_workflow_parser as parser_module
from tools import prompt_workflow_skill as skill


def _parse(*argv: str) -> dict[str, object]:
    """Parse `argv` with a fresh parser and return the namespace as a dict."""
    return vars(parser_module.build_arg_parser().parse_args(list(argv)))


def test_common_options_parse_on_the_top_level_and_after_a_subcommand() -> None:
    """`--root` and `--debug` parse on the bare call and after a subcommand."""
    top = _parse("--root", "r", "--debug")
    after = _parse("handoff", "check", "4A", "--root", "r", "--debug")

    for args in (top, after):
        assert args["root"] == "r"
        assert args["debug"] is True
    assert (after["command"], after["task"], after["step"]) == ("handoff", "check", "4A")


def test_a_subcommand_default_overrides_a_common_option_given_before_it() -> None:
    """Argparse lets the subparser's own `--root` default win over an earlier value.

    This pins the behavior the parser had before it moved out of
    `tools.prompt_workflow`; the Q01 promise that the options parse on either
    side of the subcommand does not hold before the subcommand.
    """
    args = _parse("--root", "r", "--debug", "handoff", "check", "4A")
    assert args["root"] is None
    assert args["debug"] is False


def test_the_bare_menu_call_keeps_pick_and_no_subcommand() -> None:
    """No subcommand runs the menu; `--pick` reopens it."""
    assert _parse() == {"root": None, "debug": False, "pick": False, "command": None}
    assert _parse("--pick")["pick"] is True


def test_skill_options_and_host_choices() -> None:
    """`skill` carries its optional name and the post-write, -commit and -merge options."""
    args = _parse(
        "skill",
        "spec-review-requestor",
        "--host",
        skill.HOST_CODEX,
        "--after-commit",
        "3",
        "--after-merge",
        "docs/draft.md",
    )
    assert args["skill_name"] == "spec-review-requestor"
    assert args["host_override"] == skill.HOST_CODEX
    assert args["after_commit"] == "3"
    assert args["after_merge"] == "docs/draft.md"
    assert args["after_write"] is None
    assert _parse("skill", "--after-write", skill.AFTER_WRITE_ROLES[0])["after_write"] == (
        skill.AFTER_WRITE_ROLES[0]
    )
    with pytest.raises(SystemExit):
        _parse("skill", "--host", "unknown")


def test_report_and_document_subcommands() -> None:
    """`progress`, `step-journal`, `document` and `code-review-commit` parse their arguments."""
    assert _parse("progress", "--host", skill.HOST_CLAUDE)["host_override"] == skill.HOST_CLAUDE
    assert _parse("step-journal", "2")["step"] == "2"
    document = _parse("document", "v1.2.3", "topic", parser_module.docs.DOCUMENT_TYPES[0])
    assert (document["version"], document["slug"]) == ("v1.2.3", "topic")
    assert _parse("code-review-commit", "--residual")["residual"] is True
    assert _parse("code-review-commit")["residual"] is False


# eof
