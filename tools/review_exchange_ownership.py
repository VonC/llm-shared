"""Session-held ownership capabilities for fenced review transitions.

Step 3 pairs a monotonic durable generation with a random plaintext token that
never enters coordination. Only its SHA-256 digest is stored, so a displaced
session can observe the newer generation without recovering its replacement
secret.
"""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from tools.review_exchange_models import Actor, ReviewExchangeError, positive_integer

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.review_exchange_models_coordination import CoordinationRecord

_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{31,255}$")


@dataclass(frozen=True, slots=True)
class OwnershipCapability:
    """One generation and plaintext secret held only by an acting session."""

    generation: int
    token: str

    def __post_init__(self) -> None:
        """Reject malformed capability values without echoing the secret."""
        positive_integer(self.generation, "ownership generation")
        if _TOKEN_RE.fullmatch(self.token) is None:
            raise ReviewExchangeError("invalid ownership token")


@dataclass(frozen=True, slots=True)
class OwnershipFailure:
    """Typed non-secret reason one ownership operation cannot continue."""

    code: str
    diagnostic: str
    current_generation: int


class OwnershipRejectedError(ReviewExchangeError):
    """Raise one typed ownership failure without retaining supplied secrets."""

    def __init__(self, failure: OwnershipFailure) -> None:
        """Keep only the non-secret failure record on the exception."""
        super().__init__(failure.diagnostic)
        self.failure = failure


@dataclass(frozen=True, slots=True)
class OwnershipClaim:
    """A persisted coordination replacement and its session-held capability."""

    record: CoordinationRecord
    capability: OwnershipCapability
    newly_issued: bool = True


class OwnershipService:
    """Issue and validate O(1) review-transition ownership capabilities."""

    def __init__(self, token_factory: Callable[[], str] | None = None) -> None:
        """Accept an injectable token source for deterministic focused tests."""
        self._token_factory = token_factory or (lambda: f"t{secrets.token_urlsafe(32)}")

    @staticmethod
    def digest(token: str) -> str:
        """Return the durable SHA-256 digest for one validated plaintext token."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def claim(
        self,
        record: CoordinationRecord,
        actor: Actor,
        *,
        presented: OwnershipCapability | None = None,
        force: bool = False,
    ) -> OwnershipClaim:
        """Return an ordinary idempotent claim or a generation-advancing pickup."""
        if record.ownership_generation > 0 and record.owner is actor and not force:
            if presented is None:
                raise OwnershipRejectedError(
                    self.already_claimed_failure(record),
                )
            self.require_valid(record, presented)
            return OwnershipClaim(record, presented, newly_issued=False)

        generation = record.ownership_generation + 1
        token = self._token_factory()
        capability = OwnershipCapability(generation, token)
        updated = replace(
            record,
            owner=actor,
            ownership_generation=generation,
            ownership_token_digest=self.digest(token),
        )
        return OwnershipClaim(updated, capability)

    def failure_for(
        self,
        record: CoordinationRecord,
        capability: OwnershipCapability | None,
    ) -> OwnershipFailure | None:
        """Return a non-secret failure for a presented capability, if any."""
        if capability is None:
            return self._failure(
                "ownership-missing",
                "ownership generation and token are required",
                record,
            )
        if capability.generation < record.ownership_generation:
            return self._failure(
                "ownership-superseded",
                "ownership capability was superseded",
                record,
            )
        if capability.generation != record.ownership_generation:
            return self._failure(
                "ownership-invalid",
                "ownership capability is invalid",
                record,
            )
        digest = record.ownership_token_digest
        if digest is None or not hmac.compare_digest(self.digest(capability.token), digest):
            return self._failure(
                "ownership-invalid",
                "ownership capability is invalid",
                record,
            )
        return None

    def already_claimed_failure(
        self,
        record: CoordinationRecord,
    ) -> OwnershipFailure:
        """Return the typed failure for a claim held by another session."""
        return self._failure(
            "already-claimed",
            "review transition is already claimed",
            record,
        )

    def require_valid(
        self,
        record: CoordinationRecord,
        capability: OwnershipCapability | None,
    ) -> None:
        """Raise the typed rejection for any missing, stale, or invalid value."""
        failure = self.failure_for(record, capability)
        if failure is not None:
            raise OwnershipRejectedError(failure)

    @staticmethod
    def _failure(
        code: str,
        diagnostic: str,
        record: CoordinationRecord,
    ) -> OwnershipFailure:
        """Build one failure from durable non-secret coordination state."""
        return OwnershipFailure(code, diagnostic, record.ownership_generation)


__all__ = [
    "OwnershipCapability",
    "OwnershipClaim",
    "OwnershipFailure",
    "OwnershipRejectedError",
    "OwnershipService",
]


# eof
