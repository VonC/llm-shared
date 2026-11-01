"""Keep selected-command construction equivalent to the complete CLI grammar.

Cold construction remains measured. Each command checks accepted arguments,
rejected arguments and help against the full parser from the same declarations.
The cache must never retain parsed values or duplicate-option bookkeeping.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.review_exchange_cli_parser import JsonArgumentParser, parser, parser_for
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from argparse import Namespace

_COMMON = (
    "--family", "code", "--document", "plan.v0.11.0.topic.md",
    "--convergence-signal", "ready", "--another-round-label", "repeat",
    "--continue-owning-workflow-label", "done",
)
_COMMANDS = {
    "activate": _COMMON,
    "status": _COMMON,
    "start": _COMMON,
    "continue": _COMMON,
    "pickup": _COMMON,
    "complete": (*_COMMON, "--force", "--summary-file", "summary.md"),
    "reclaim": (*_COMMON, "--force", "--summary-file", "summary.md"),
    "publish-request": (*_COMMON, "--content-file", "request.md", "--summary-file", "summary.md",
                        "--scope-capture-file", "scope.json"),
    "publish-answer": (*_COMMON, "--content-file", "answer.md", "--summary-file", "summary.md"),
    "repair-request-transcript": (*_COMMON, "--summary-file", "summary.md"),
    "wait-request": (*_COMMON, "--timeout-seconds", "2", "--poll-interval", "0.5", "--progress-interval", "3"),
    "wait-answer": _COMMON,
    "consume-answer": (*_COMMON, "--reviewed-work-changed", "false", "--disagreement"),
    "escalate": (*_COMMON, "--summary-file", "summary.md"),
    "cancel": (*_COMMON, "--summary-file", "summary.md"),
    "resolve": (*_COMMON, "--summary-file", "summary.md"),
    "archive": (*_COMMON, "--summary-file", "summary.md"),
    "confirm": (*_COMMON, "--choice-label", "done", "--guidance-file", "guidance.md"),
    "migration-check": (),
    "migrate-artifacts": (),
    "resume-inspect": ("--role", "reviewer", "--trusted-host-hint", "codex",
                       "--document", "plan.v0.11.0.topic.md", "--implementation-step", "5", "--override"),
    "claim": ("--document", "plan.v0.11.0.topic.md", "--role", "reviewer", "--round", "1",
              "--occurrence", "1", "--ownership-generation", "1", "--ownership-token", "t" * 32),
    "wait-any-request": (),
}


@pytest.fixture(scope="module")
def complete_grammar() -> JsonArgumentParser:
    """Construct the reference grammar inside its first consumer's lifecycle."""
    return parser()


@pytest.mark.parametrize("operation", _COMMANDS)
def test_selected_command_matches_complete_grammar(
    operation: str, complete_grammar: JsonArgumentParser, capsys: pytest.CaptureFixture[str],
) -> None:
    """Every command retains accepted values, rejection diagnostics and help."""
    selected = parser_for(operation)
    arguments = [operation, *_COMMANDS[operation]]
    assert vars(selected.parse_args(arguments)) == vars(complete_grammar.parse_args(arguments))
    for invalid in ([*arguments, "--no-such-argument"], [operation, "--document"]):
        with pytest.raises(ReviewExchangeError) as expected:
            complete_grammar.parse_args(invalid)
        with pytest.raises(ReviewExchangeError) as actual:
            selected.parse_args(invalid)
        assert str(actual.value) == str(expected.value)
    with pytest.raises(SystemExit) as full_exit:
        complete_grammar.parse_args([operation, "--help"])
    full_help = capsys.readouterr()
    with pytest.raises(SystemExit) as selected_exit:
        selected.parse_args([operation, "--help"])
    assert selected_exit.value.code == full_exit.value.code == 0
    assert capsys.readouterr() == full_help


@pytest.mark.parametrize("first", ["unknown", "--help", "--invalid", ""])
def test_unselected_command_retains_complete_help_and_diagnostics(
    first: str, complete_grammar: JsonArgumentParser,
) -> None:
    """Unknown, option-first and missing command shapes keep the full grammar."""
    selected = parser_for(first)
    assert selected.format_help() == complete_grammar.format_help()
    arguments = [first] if first != "--help" else []
    with pytest.raises(ReviewExchangeError) as expected:
        complete_grammar.parse_args(arguments)
    with pytest.raises(ReviewExchangeError) as actual:
        selected.parse_args(arguments)
    assert str(actual.value) == str(expected.value)


@pytest.mark.parametrize("extra", [
    ("--round", "0"), ("--occurrence", "bad"), ("--role", "unknown"),
    ("--ownership-generation", "2"), ("--ownership-token", "u" * 32),
])
def test_selected_claim_preserves_validation_and_fresh_namespaces(
    extra: tuple[str, ...], complete_grammar: JsonArgumentParser,
) -> None:
    """Typed errors and duplicate capability options do not leak across parses."""
    selected = parser_for("claim")
    arguments = ["claim", *_COMMANDS["claim"]]
    first: Namespace = selected.parse_args(arguments)
    with pytest.raises(ReviewExchangeError) as expected:
        complete_grammar.parse_args([*arguments, *extra])
    with pytest.raises(ReviewExchangeError) as actual:
        selected.parse_args([*arguments, *extra])
    assert str(actual.value) == str(expected.value)
    second = selected.parse_args(arguments)
    assert second is not first
    assert vars(first) == vars(second)


# eof
