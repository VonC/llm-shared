"""Argument and document-context parsing for the review-exchange CLI.

The command adapter imports this focused parser so JSON result rendering and
runtime dispatch stay separate from argparse construction and filename rules.
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
    """Build the command parser with shared exact-context arguments."""
    common = JsonArgumentParser(add_help=False)
    common.add_argument("--family", choices=("specification", "code"), required=True)
    common.add_argument("--document", required=True)
    common.add_argument("--umbrella")
    common.add_argument("--implementation-step")
    common.add_argument("--convergence-signal", required=True)
    common.add_argument("--another-round-label", required=True)
    common.add_argument("--continue-owning-workflow-label", required=True)
    add_ownership_arguments(common)

    result = JsonArgumentParser(prog="review-exchange")
    subparsers = result.add_subparsers(dest="operation", required=True)
    for name in ("activate", "status", "start", "continue", "pickup"):
        subparsers.add_parser(name, parents=[common])
    complete = subparsers.add_parser("complete", parents=[common])
    complete.add_argument("--force", action="store_true")
    complete.add_argument("--summary-file")
    reclaim = subparsers.add_parser("reclaim", parents=[common])
    reclaim.add_argument("--force", action="store_true")
    reclaim.add_argument("--summary-file")
    for name in ("publish-request", "publish-answer"):
        command = subparsers.add_parser(name, parents=[common])
        command.add_argument("--content-file", required=True)
        command.add_argument("--summary-file", required=True)
    repair_request = subparsers.add_parser(
        "repair-request-transcript",
        parents=[common],
    )
    repair_request.add_argument("--summary-file", required=True)
    for name in ("wait-request", "wait-answer"):
        command = subparsers.add_parser(name, parents=[common])
        command.add_argument("--timeout-seconds", type=positive_int)
        command.add_argument("--poll-interval", type=positive_float, default=1.0)
        command.add_argument("--progress-interval", type=positive_float, default=30.0)
    consume = subparsers.add_parser("consume-answer", parents=[common])
    consume.add_argument(
        "--reviewed-work-changed",
        choices=("true", "false"),
        required=True,
    )
    consume.add_argument("--disagreement", action="store_true")
    for name in ("escalate", "cancel", "resolve", "archive"):
        command = subparsers.add_parser(name, parents=[common])
        command.add_argument("--summary-file", required=True)
    confirm = subparsers.add_parser("confirm", parents=[common])
    confirm.add_argument("--choice-label", required=True)
    confirm.add_argument("--guidance-file")
    _add_resume_arguments(subparsers)
    return result


def _add_resume_arguments(subparsers: argparse._SubParsersAction[JsonArgumentParser]) -> None:  # pyright: ignore[reportPrivateUsage]
    """Add the focused support contracts without growing normal protocol parsing."""
    for name in ("migration-check", "migrate-artifacts"):
        subparsers.add_parser(name)
    inspect = subparsers.add_parser("resume-inspect")
    inspect.add_argument("--role", choices=("requestor", "reviewer"))
    inspect.add_argument("--trusted-host-hint")
    inspect.add_argument("--document")
    inspect.add_argument("--implementation-step")
    inspect.add_argument("--override", action="store_true")
    claim = subparsers.add_parser("claim")
    claim.add_argument("--document", required=True)
    claim.add_argument("--implementation-step")
    claim.add_argument("--role", choices=("requestor", "reviewer"), required=True)
    claim.add_argument("--trusted-host-hint")
    claim.add_argument("--round", dest="round_number", type=positive_int, required=True)
    claim.add_argument("--occurrence", type=positive_int, required=True)
    claim.add_argument("--override", action="store_true")
    add_ownership_arguments(claim)
    wait_any = subparsers.add_parser("wait-any-request")
    wait_any.add_argument("--poll-interval", type=positive_float, default=1.0)


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
