"""Command-line parser of the prompt workflow tool (`pw`).

Split out of ``prompt_workflow.py`` so that module stays under the repository
line budget: this module builds the argument parser only, while
``prompt_workflow.main`` keeps the dispatch to each subcommand.

``--root`` and ``--debug`` live on a shared parent parser passed to both the
top-level parser and every subparser, so they parse on either side of the
subcommand (Q01); ``--pick`` stays top-level only. The ``handoff`` subcommand
carries a ``task`` word and a plain-string ``step`` positional, so a sub-step id
such as ``4A`` is accepted and validated by the resolver, not the parser (Q04,
Q56).
The ``scope`` subcommand carries remaining ghog arguments unchanged, so their
level options belong to groundhog rather than this parser.

Fix: ``--root`` and ``--debug`` given before the subcommand were lost. Argparse
applies each subparser's own defaults to the shared namespace after the
top-level parser has filled it, so ``pw --root <dir> handoff check 4A`` came
back with ``root=None`` and ``debug=False``. Only the top-level copy of the
common options now carries the ``None`` and ``False`` defaults; the subparser
copy suppresses its defaults, so it sets ``root`` or ``debug`` only when the
option is given after the subcommand, where the later value wins.
"""

from __future__ import annotations

import argparse

from tools import prompt_workflow_docs as docs
from tools import prompt_workflow_handoff as handoff
from tools import prompt_workflow_skill as skill


def build_arg_parser() -> argparse.ArgumentParser:
    """Create and return the `pw` argument parser.

    Returns:
        The top-level parser with its ``handoff``, ``skill``, ``progress``,
        ``scope``, ``document``, ``step-journal`` and ``code-review-commit`` subparsers;
        ``--root`` and ``--debug`` keep the value given on either side of the
        subcommand.
    """
    common = _common_parser(suppress_defaults=True)
    parser = argparse.ArgumentParser(
        parents=[_common_parser(suppress_defaults=False)],
        description="Generate and copy the next-step LLM prompt for the current topic.",
    )
    parser.add_argument(
        "--pick",
        action="store_true",
        help="Reopen the topic menu even when a topic is locked to the branch.",
    )
    subparsers = parser.add_subparsers(dest="command")
    handoff_parser = subparsers.add_parser(
        "handoff",
        parents=[common],
        help="Write the prompt for one named step without the menu.",
    )
    handoff_parser.add_argument(
        "task",
        help=f"The handoff task, one of: {', '.join(handoff.TASK_TOKENS)}.",
    )
    handoff_parser.add_argument(
        "step",
        help="The plan step id the prompt is for, such as 2 or 4A.",
    )
    _add_skill_parser(subparsers, common)
    progress_parser = subparsers.add_parser(
        "progress",
        parents=[common],
        help="Print where the current topic stands, then its next command.",
    )
    _add_host_option(progress_parser)
    scope_parser = subparsers.add_parser(
        "scope",
        parents=[common],
        help="Print the effort selector or complete a ghog command with it.",
    )
    scope_parser.add_argument("ghog_args", nargs=argparse.REMAINDER, help="Arguments for ghog, starting with its command.")
    document_parser = subparsers.add_parser(
        "document",
        parents=[common],
        help="Find one document from its version, slug, and type.",
    )
    document_parser.add_argument("version", help="Document version, such as v1.2.3.")
    document_parser.add_argument("slug", help="Document topic slug.")
    document_parser.add_argument(
        "document_type",
        choices=docs.DOCUMENT_TYPES,
        help="Document type to resolve.",
    )
    step_journal_parser = subparsers.add_parser(
        "step-journal",
        parents=[common],
        help="Print the start or resume state and private note paths of one plan step.",
    )
    step_journal_parser.add_argument(
        "step",
        help="The plan step id being implemented, such as 2 or 4A.",
    )
    code_review_commit_parser = subparsers.add_parser(
        "code-review-commit",
        parents=[common],
        help="Resume one durably authorized clean code-review commit flow.",
    )
    code_review_commit_parser.add_argument(
        "--residual",
        action="store_true",
        help="Execute the grouped residual commit plan and require a clean tree.",
    )
    return parser


def _common_parser(*, suppress_defaults: bool) -> argparse.ArgumentParser:
    """Return the parent parser carrying ``--root`` and ``--debug`` (Q01).

    Args:
        suppress_defaults: True for the copy shared by the subparsers, whose
            defaults would otherwise overwrite a value parsed before the
            subcommand; False for the top-level copy, which owns the
            ``None`` and ``False`` defaults.

    Returns:
        The parent parser, without its own help option.
    """
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        default=argparse.SUPPRESS if suppress_defaults else None,
        help="Project root override. If not provided, scan upward for the root.",
    )
    common.add_argument(
        "--debug",
        action="store_true",
        default=argparse.SUPPRESS if suppress_defaults else False,
        help="Enable debug logging.",
    )
    return common


def _add_host_option(parser: argparse.ArgumentParser) -> None:
    """Add the ``--host`` prefix override shared by ``skill`` and ``progress``."""
    parser.add_argument(
        "--host",
        dest="host_override",
        default=None,
        choices=[skill.HOST_CLAUDE, skill.HOST_CODEX],
        help="Force the command prefix host instead of detecting it.",
    )


def _add_skill_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],  # pyright: ignore[reportPrivateUsage]
    common: argparse.ArgumentParser,
) -> None:
    """Add the ``skill`` subcommand and its post-write, -commit and -merge options."""
    skill_parser = subparsers.add_parser(
        "skill",
        parents=[common],
        help="Print the bare next-step command for the current topic (skill mode).",
    )
    skill_parser.add_argument(
        "skill_name",
        nargs="?",
        default=None,
        help="Force this skill's command when its document exists, not the next step.",
    )
    _add_host_option(skill_parser)
    skill_parser.add_argument(
        "--after-commit",
        dest="after_commit",
        default=None,
        help="Print the post-commit next action for the named just-committed plan step.",
    )
    skill_parser.add_argument(
        "--after-write",
        dest="after_write",
        default=None,
        choices=skill.AFTER_WRITE_ROLES,
        help="Review the named artifact role that was just written.",
    )
    skill_parser.add_argument(
        "--after-merge",
        dest="after_merge",
        default=None,
        help="Print the next ordered item from the named umbrella draft.",
    )


# eof
