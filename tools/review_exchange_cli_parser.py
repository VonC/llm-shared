"""Argument and document-context parsing for the review-exchange CLI.

The command adapter imports this focused parser so JSON result rendering and
runtime dispatch stay separate from argparse construction and filename rules.
Known commands build only their own grammar. Full help and invalid command
diagnostics retain the complete grammar, using the same argument declarations.
"""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import NoReturn

from tools.review_exchange_cli_ownership import add_ownership_arguments
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)

_DOCUMENT_RE = re.compile(
    r"^(feature-request|issue|design|plan)\.(v\d+\.\d+\.\d+)\."
    r"([a-z0-9][a-z0-9_-]*)\.md$",
)
_PROTOCOL_OPERATIONS = (
    "activate", "status", "start", "continue", "pickup", "complete", "reclaim",
    "publish-request", "publish-answer", "repair-request-transcript",
    "wait-request", "wait-answer", "consume-answer", "escalate", "cancel",
    "resolve", "archive", "confirm",
)
_RESUME_OPERATIONS = (
    "migration-check", "migrate-artifacts", "resume-inspect", "claim", "wait-any-request",
)


class JsonArgumentParser(argparse.ArgumentParser):
    """Raise parse errors so main can emit the mandatory final JSON object."""

    def error(self, message: str) -> NoReturn:
        """Convert argparse diagnostics to typed fatal input."""
        raise ReviewExchangeError(message)


def positive_int(value: str) -> int:
    """Parse one positive integer command value."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def positive_float(value: str) -> float:
    """Parse one positive floating-point command value."""
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def parser() -> JsonArgumentParser:
    """Build the full grammar for help, diagnostics and direct parser callers."""
    return _build_parser((*_PROTOCOL_OPERATIONS, *_RESUME_OPERATIONS))


def parser_for(operation: str) -> JsonArgumentParser:
    """Build only a known command, preserving full help for other first tokens."""
    if operation not in (*_PROTOCOL_OPERATIONS, *_RESUME_OPERATIONS):
        return parser()
    return _build_parser((operation,))


def _common_arguments() -> JsonArgumentParser:
    """Declare the exact-context arguments shared by protocol operations."""
    common = JsonArgumentParser(add_help=False)
    common.add_argument("--family", choices=("specification", "code"), required=True)
    common.add_argument("--document", required=True)
    common.add_argument("--umbrella")
    common.add_argument("--implementation-step")
    common.add_argument("--convergence-signal", required=True)
    common.add_argument("--another-round-label", required=True)
    common.add_argument("--continue-owning-workflow-label", required=True)
    add_ownership_arguments(common)
    return common


def _build_parser(operations: tuple[str, ...]) -> JsonArgumentParser:
    """Construct selected commands from the single source of argument rules."""
    result = JsonArgumentParser(prog="review-exchange")
    subparsers = result.add_subparsers(dest="operation", required=True)
    common = [_common_arguments()] if any(name in _PROTOCOL_OPERATIONS for name in operations) else []
    for name in operations:
        if name in _PROTOCOL_OPERATIONS:
            command = subparsers.add_parser(name, parents=common)
            _add_protocol_arguments(command, name)
        else:
            command = subparsers.add_parser(name)
            _add_resume_arguments(command, name)
    return result


def _add_protocol_arguments(command: JsonArgumentParser, name: str) -> None:
    """Add operation-specific arguments after the shared protocol context."""
    if name in {"complete", "reclaim"}:
        command.add_argument("--force", action="store_true")
        command.add_argument("--summary-file")
    elif name in {"publish-request", "publish-answer"}:
        command.add_argument("--content-file", required=True)
        command.add_argument("--summary-file", required=True)
        if name == "publish-request":
            command.add_argument("--scope-capture-file")
    elif name in {"repair-request-transcript", "escalate", "cancel", "resolve", "archive"}:
        command.add_argument("--summary-file", required=True)
    elif name in {"wait-request", "wait-answer"}:
        command.add_argument("--timeout-seconds", type=positive_int)
        command.add_argument("--poll-interval", type=positive_float, default=1.0)
        command.add_argument("--progress-interval", type=positive_float, default=30.0)
    elif name == "consume-answer":
        command.add_argument("--reviewed-work-changed", choices=("true", "false"), required=True)
        command.add_argument("--disagreement", action="store_true")
    elif name == "confirm":
        command.add_argument("--choice-label", required=True)
        command.add_argument("--guidance-file")


def _add_resume_arguments(command: JsonArgumentParser, name: str) -> None:
    """Add support contracts without constructing unrelated protocol commands."""
    if name == "resume-inspect":
        command.add_argument("--role", choices=("requestor", "reviewer"))
        command.add_argument("--trusted-host-hint")
        command.add_argument("--document")
        command.add_argument("--implementation-step")
        command.add_argument("--override", action="store_true")
    elif name == "claim":
        command.add_argument("--document", required=True)
        command.add_argument("--implementation-step")
        command.add_argument("--role", choices=("requestor", "reviewer"), required=True)
        command.add_argument("--trusted-host-hint")
        command.add_argument("--round", dest="round_number", type=positive_int, required=True)
        command.add_argument("--occurrence", type=positive_int, required=True)
        command.add_argument("--override", action="store_true")
        add_ownership_arguments(command)
    elif name == "wait-any-request":
        command.add_argument("--poll-interval", type=positive_float, default=1.0)


def context_from_document(
    family_value: str,
    document_value: str | Path,
    umbrella_value: str | Path | None,
    implementation_step: str | None,
) -> ReviewContext:
    """Infer validated identity tokens from one exact reviewed document name."""
    document = Path(document_value).expanduser().resolve()
    match = _DOCUMENT_RE.fullmatch(document.name)
    if match is None:
        raise ReviewExchangeError("reviewed document has an unsupported file name")
    prefix, version, slug = match.groups()
    family = ReviewFamily(family_value)
    if family is ReviewFamily.CODE:
        if prefix != "plan":
            raise ReviewExchangeError("code review requires an exact plan document")
        type_token = "code"  # noqa: S105 - protocol token, not a credential
    else:
        type_token = "design-specification" if prefix == "design" else prefix
    identity = ExchangeIdentity(family, type_token, version, slug)
    umbrella = (
        None
        if umbrella_value is None
        else Path(umbrella_value).expanduser().resolve()
    )
    return ReviewContext(identity, document, umbrella, implementation_step)


# eof
