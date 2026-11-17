"""Resolve the download budget override once per provisioning caller.

`LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` sets the download budget D,
both attempts together (design "The download budget override", Q18). Unset,
D is 300 s. A set value is an ASCII decimal integer of seconds from 300
through 3600; any other form is refused, never clamped and never replaced by
the default. The caller's lock wait is W = D + 60 s. The socket, probe,
metadata and retry delay budgets are engine constants.

Step 1 of v0.14.0 git-cliff-provisioning ships the policy. Provisioning and
the evidence harness call `resolve_budget` once, before any reuse probe,
child, network access or cache change, and hand the policy to workers and the
lock wait; no other module reads the variable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

DOWNLOAD_BUDGET_VARIABLE = "LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS"
DEFAULT_DOWNLOAD_SECONDS = 300
MAXIMUM_DOWNLOAD_SECONDS = 3600
WAIT_MARGIN_SECONDS = 60
_MAXIMUM_DIGITS = len(str(MAXIMUM_DOWNLOAD_SECONDS))


class BudgetSettingError(ValueError):
    """The budget variable holds a refused form: a setup failure, status 2."""

    exit_code = 2


@dataclass(frozen=True, kw_only=True)
class BudgetPolicy:
    """Stage budgets in seconds for one caller, resolved once and handed on.

    `download` is D, both attempts together; `wait` is the caller's own
    finite lock wait W = D + 60; `source` tells messages where D came from,
    `default` or the variable with its text.
    """

    download: int
    wait: int
    socket: int = 30
    probe: int = 15
    metadata: int = 60
    retry_delay: int = 5
    source: str


def _lookup(environment: Mapping[str, str]) -> str | None:
    """Find the variable whatever its case, as Windows names are, in one pass."""
    return next((value for name, value in environment.items() if name.upper() == DOWNLOAD_BUDGET_VARIABLE), None)


def resolve_budget(environment: Mapping[str, str]) -> BudgetPolicy:
    """Validate the override once and give the caller its stage budgets.

    Args:
        environment: The caller's environment mapping, read once.

    Returns:
        The default policy when the variable is unset, otherwise the exact
        raised download budget and its wait.

    Raises:
        BudgetSettingError: The value is not an ASCII decimal integer from
            300 through 3600.
    """
    raw = _lookup(environment)
    if raw is None:
        return BudgetPolicy(download=DEFAULT_DOWNLOAD_SECONDS, wait=DEFAULT_DOWNLOAD_SECONDS + WAIT_MARGIN_SECONDS, source="default")
    # Leading zeros are allowed; stripping them first bounds the conversion.
    digits = raw.lstrip("0") if raw.isascii() and raw.isdigit() else ""
    seconds = int(digits) if 0 < len(digits) <= _MAXIMUM_DIGITS else 0
    if not DEFAULT_DOWNLOAD_SECONDS <= seconds <= MAXIMUM_DOWNLOAD_SECONDS:
        msg = (
            f"{DOWNLOAD_BUDGET_VARIABLE}={raw!r}: expected a whole number of seconds"
            f" from {DEFAULT_DOWNLOAD_SECONDS} through {MAXIMUM_DOWNLOAD_SECONDS}, or unset it"
        )
        raise BudgetSettingError(msg)
    return BudgetPolicy(download=seconds, wait=seconds + WAIT_MARGIN_SECONDS, source=f"{DOWNLOAD_BUDGET_VARIABLE}={raw}")


# eof
