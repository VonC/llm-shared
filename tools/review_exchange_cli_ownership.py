"""Ownership parsing and core boundary for the review-exchange CLI.

Step 3 keeps capability flags, token-safe failure rendering, and the lifecycle
port outside the risk-band command hub. Plaintext tokens remain in the parsed
command and successful machine result only.
"""

# ruff: noqa: ANN401, D102, EM101, TRY003

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Any, Protocol, cast

from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_ownership import (
    OwnershipCapability,
    OwnershipFailure,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from tools.review_exchange_human import ConfirmationDecision, ResolutionResult
    from tools.review_exchange_models import Actor, ArtifactState
    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_observer import ExchangeObservation
    from tools.review_exchange_ownership import OwnershipClaim
    from tools.review_exchange_wait import WaitProgress, WaitResult


class CorePort(Protocol):
    """Lifecycle and ownership operations used by the command adapter."""

    @property
    def ownership_capability(self) -> OwnershipCapability | None:
        """Return the capability held by this command invocation."""
        ...

    @property
    def ownership_capability_issued(self) -> bool:
        """Report whether this command invocation minted the capability."""
        ...

    def present_ownership(self, capability: OwnershipCapability | None) -> None:
        """Present the parsed session capability for one command."""
        ...

    def classify(self) -> ExchangeObservation: ...

    def start(self) -> CoordinationRecord: ...

    def publish_request(self, markdown: str, transcript_content: str) -> CoordinationRecord: ...

    def publish_answer(self, markdown: str, transcript_content: str) -> CoordinationRecord: ...

    def repair_current_request_transcript(self, transcript_content: str) -> CoordinationRecord: ...

    def wait_for_exact(
        self,
        expected: ArtifactState,
        *,
        timeout_seconds: int | None,
        poll_interval: float,
        progress_interval: float,
        progress_callback: Callable[[WaitProgress], None] | None,
    ) -> WaitResult: ...

    def consume_answer(
        self,
        *,
        reviewed_work_changed: bool,
        disagreement: bool = False,
    ) -> CoordinationRecord: ...

    def continue_round(self) -> CoordinationRecord: ...

    def reclaim(self) -> CoordinationRecord: ...

    def force_reclaim(self, summary: str) -> CoordinationRecord: ...

    def pickup_ownership(self, actor: Actor) -> OwnershipClaim: ...

    def escalate(self, reason: str) -> CoordinationRecord: ...

    def confirm(
        self,
        label: str,
        *,
        guidance: str | None = None,
    ) -> ConfirmationDecision: ...

    def cancel(self, reason: str) -> CoordinationRecord: ...

    def resolve_escalation(self, summary: str, *, archive: bool) -> ResolutionResult: ...

    def complete(self) -> bool: ...

    def force_complete(self, summary: str) -> bool: ...


class _SingleValueAction(argparse.Action):
    """Reject duplicate sensitive flags instead of accepting the last value."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        """Store one value or stop on a duplicated option."""
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} may be supplied only once")
        setattr(namespace, self.dest, values)


def _positive_generation(value: str) -> int:
    """Parse one positive generation without accepting booleans or signs."""
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("ownership generation must be positive") from error
    if parsed <= 0 or str(parsed) != value:
        raise argparse.ArgumentTypeError("ownership generation must be positive")
    return parsed


def _token(value: str) -> str:
    """Validate one secret without copying it into a parser diagnostic."""
    try:
        OwnershipCapability(1, value)
    except ReviewExchangeError as error:
        raise argparse.ArgumentTypeError("ownership token is invalid") from error
    return value


def add_ownership_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the paired generation and token flags to one command parser."""
    parser.add_argument(
        "--ownership-generation",
        type=_positive_generation,
        action=_SingleValueAction,
    )
    parser.add_argument(
        "--ownership-token",
        type=_token,
        action=_SingleValueAction,
    )


def capability_from_args(args: argparse.Namespace) -> OwnershipCapability | None:
    """Return the capability pair or reject a one-sided command."""
    generation = getattr(args, "ownership_generation", None)
    token = getattr(args, "ownership_token", None)
    if (generation is None) != (token is None):
        raise ReviewExchangeError(
            "ownership generation and token must be supplied together",
        )
    if generation is None:
        return None
    return OwnershipCapability(generation, cast("str", token))


def capability_payload(capability: OwnershipCapability) -> Mapping[str, Any]:
    """Render the session-held capability only in a successful machine result."""
    return {
        "ownership_generation": capability.generation,
        "ownership_token": capability.token,
    }


def failure_payload(failure: OwnershipFailure) -> Mapping[str, Any]:
    """Render a typed ownership stop from durable non-secret values."""
    return {
        "current_ownership_generation": failure.current_generation,
        "diagnostic": failure.diagnostic,
        "outcome": failure.code,
    }


__all__ = [
    "CorePort",
    "add_ownership_arguments",
    "capability_from_args",
    "capability_payload",
    "failure_payload",
]


# eof
