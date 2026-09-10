"""Stable input diagnostics shared by the normal and resume command adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tools.review_exchange_cli_ownership import capability_payload

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.review_exchange_cli_ownership import CorePort


_EXIT_STOP = 3


def fatal_payload(operation: str, diagnostic: str) -> dict[str, Any]:
    """Build the stable schema for invalid input or unexpected failure."""
    return {
        "diagnostic": diagnostic,
        "candidates": [],
        "identity": None,
        "operation": operation,
        "outcome": "fatal-input",
        "paths": {},
        "round": None,
        "state": "fatal",
    }


def operation_name(argv: Sequence[str]) -> str:
    """Return the first token for parse-failure reporting."""
    return argv[0] if argv and not argv[0].startswith("-") else "unknown"


def add_issued_capability(
    payload: dict[str, Any], core: CorePort, operation: str, exit_code: int | None,
) -> None:
    """Expose a newly issued session capability only on a successful actor operation."""
    capability = core.ownership_capability
    if (
        capability is not None
        and core.ownership_capability_issued
        and exit_code != _EXIT_STOP
        and operation not in {"activate", "status"}
    ):
        payload.update(capability_payload(capability))


# eof
