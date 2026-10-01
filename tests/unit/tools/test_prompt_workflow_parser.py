"""Contracts for the `pw` argument parser, split out of `tools.prompt_workflow`.

`--root` and `--debug` parse on either side of every subcommand (Q01), the
`handoff` step stays a plain string (Q04, Q56), and `skill` and `progress`
share the same `--host` choices.

Fix: the options given before the subcommand are no longer reset by the
subparser defaults; the test that pinned the lost values now asserts that they
are kept, and that a value given after the subcommand still wins.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow
from tools import prompt_workflow_parser as parser_module
from tools import prompt_workflow_skill as skill

if TYPE_CHECKING:
    from pathlib import Path


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


@pytest.mark.parametrize(
    "subcommand",
    [
        ("handoff", "check", "4A"),
        ("skill",),
        ("progress",),
        ("step-journal", "2"),
        ("code-review-commit",),
    ],
)
def test_common_options_given_before_a_subcommand_are_kept(subcommand: tuple[str, ...]) -> None:
    """A subparser default no longer resets `--root` or `--debug` given before it.

    Before the fix, `pw --root r handoff check 4A` came back with `root=None`
    and `debug=False`, breaking the Q01 promise on that side of the subcommand.
    """
    args = _parse("--root", "r", "--debug", *subcommand)
    assert args["root"] == "r"
    assert args["debug"] is True


def test_a_common_option_after_the_subcommand_wins_over_one_before_it() -> None:
    """The later `--root` wins, and an absent option keeps its top-level default."""
    args = _parse("--root", "before", "handoff", "check", "4A", "--root", "after")
    assert args["root"] == "after"
    assert args["debug"] is False
    assert _parse("handoff", "check", "4A")["root"] is None


def test_main_dispatches_with_the_root_given_before_the_subcommand(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """`pw --root <dir> code-review-commit` reaches its command with that root.

    The subparser defaults used to reset it, so the command ran against the
    project root scanned upward from the working directory instead.
    """
    roots: list[Path] = []

    def _continuation(root: Path, **_kwargs: object) -> int:
        roots.append(root)
        return 0

    monkeypatch.setattr(skill, "run_authorized_code_review_commit", _continuation)

    assert prompt_workflow.main(["--root", str(tmp_path), "code-review-commit"]) == 0
    assert roots == [tmp_path.resolve()]


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
