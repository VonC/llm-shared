"""Proof rules of the leveled groundhog walk: accumulate, cap, noop, upgrade.

v0.13.0 full_suite_levels, Step 1: the pure proof model the next steps wire
into the day walk, the direct full run and the review evidence. Nothing here
reads a file; the snapshot adapter hands its marker over through the
:class:`SavedProof` port.

- Each gate a walk judges guards one level (:class:`Gate`); a failed gate
  contradicts that level and every level above it.
- After a walk (:func:`accumulate`), the proof is the highest of what the walk
  fully established and the saved proof on the same digest, then capped just
  below the lowest level any gate of the walk contradicted (``None``, read as
  ``unproven``, when ``none`` itself was contradicted). A walk that judged no
  gate contradicts nothing and keeps the saved proof.
- Before a walk (:func:`decide`), valid saved proof at or above the requested
  level is a noop, below it an upgrade, and a stale digest, ``--force`` or no
  saved proof walk the whole chain. Only the duration verdict depends on the
  timing fingerprint, so a timing mismatch caps saved proof at ``cov``
  (:func:`cap_for_timing`).
- :func:`effective_saved` is the one rule that turns a marker into currently
  valid proof: scope, fingerprint and digest must all match, then the timing
  cap applies.
- :func:`earned_by_direct_full` is the proof of a direct ``ghog full`` run,
  which never reads or writes the marker.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Final, Protocol

from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


class Gate(Enum):
    """A gate a walk judges, valued by the lowest level its failure contradicts."""

    CHECK_OR_AFFECTED = FullLevel.NONE
    FULL_TESTS = FullLevel.PASS
    COVERAGE = FullLevel.COV
    DURATIONS = FullLevel.SPEED

    @property
    def contradicts(self) -> FullLevel:
        """Return the lowest level a failure of this gate contradicts."""
        return FullLevel(self.value)


class Decision(Enum):
    """What a walk does with its saved proof before running anything."""

    NOOP = "noop"
    UPGRADE = "upgrade"
    WALK = "walk"


class SavedProof(Protocol):
    """The port of a saved proof marker, read by :func:`effective_saved`."""

    @property
    def scope(self) -> str:
        """Return the scope key the proof was earned on."""
        ...

    @property
    def fingerprint(self) -> str:
        """Return the scope fingerprint the proof was earned on."""
        ...

    @property
    def timing(self) -> str:
        """Return the duration gate fingerprint the proof was earned on."""
        ...

    @property
    def digest(self) -> str:
        """Return the source digest the proof was earned on."""
        ...

    @property
    def proof(self) -> FullLevel:
        """Return the saved proof level."""
        ...


# The proof a direct full run still earns when only one gate failed: tests
# passed under a coverage gap; tests and coverage passed under outliers.
_EARNED_BELOW_FAILED_GATE: Final = {
    EXIT_COVERAGE_GAP: FullLevel.PASS,
    EXIT_DURATION_OUTLIERS: FullLevel.COV,
}


def accumulate(
    earned: FullLevel | None,
    saved: FullLevel | None,
    contradicted: Iterable[Gate],
) -> FullLevel | None:
    """Compute the proof after a walk, from what it established and contradicted.

    Args:
        earned: The level this walk fully established, reused steps
            included, or ``None`` when it established nothing.
        saved: The saved proof on the same digest, or ``None``.
        contradicted: The gates that failed anywhere in this walk.

    Returns:
        The highest of ``earned`` and ``saved``, capped just below the lowest
        contradicted level; ``None`` (``unproven``) when nothing is left.
    """
    candidates = [level for level in (earned, saved) if level is not None]
    proof = max(candidates) if candidates else None
    lowest = min((gate.contradicts for gate in contradicted), default=None)
    if proof is None or lowest is None:
        return proof
    if lowest is FullLevel.NONE:
        return None
    return min(proof, FullLevel(lowest - 1))


def cap_for_timing(saved: FullLevel | None, *, timing_matches: bool) -> FullLevel | None:
    """Cap saved proof at ``cov`` when the duration gate inputs changed.

    Args:
        saved: The saved proof, or ``None``.
        timing_matches: Whether the timing fingerprint still matches.

    Returns:
        The saved proof, at most ``cov`` on a timing mismatch.
    """
    if saved is None:
        return None
    return _timing_capped(saved, timing_matches=timing_matches)


def decide(
    saved: FullLevel | None,
    requested: FullLevel,
    *,
    digest_matches: bool,
    timing_matches: bool,
    force: bool,
) -> Decision:
    """Decide between a noop, an upgrade and a whole walk.

    Args:
        saved: The saved proof of the walk's scope, or ``None``.
        requested: The level the walk is asked to prove.
        digest_matches: Whether the saved proof is on the current digest.
        timing_matches: Whether the timing fingerprint still matches.
        force: Whether ``--force`` asks for the whole chain.

    Returns:
        ``NOOP`` when the valid saved proof meets the request, ``UPGRADE``
        when it is below it, ``WALK`` on ``--force``, a stale digest or no
        saved proof.
    """
    if force or not digest_matches or saved is None:
        return Decision.WALK
    if requested <= _timing_capped(saved, timing_matches=timing_matches):
        return Decision.NOOP
    return Decision.UPGRADE


def effective_saved(
    marker: SavedProof | None,
    *,
    scope_key: str,
    fingerprint: str,
    digest: str,
    timing: str,
) -> FullLevel | None:
    """Turn a saved marker into the proof valid for the current sources.

    Args:
        marker: The marker of the walk's scope, or ``None`` when unreadable.
        scope_key: The scope key of the walk, such as ``whole``.
        fingerprint: The current scope fingerprint.
        digest: The current source digest.
        timing: The current timing fingerprint.

    Returns:
        ``None`` unless scope, fingerprint and digest all match; otherwise the
        saved proof, capped at ``cov`` on a timing mismatch.
    """
    if marker is None:
        return None
    if (marker.scope, marker.fingerprint, marker.digest) != (scope_key, fingerprint, digest):
        return None
    return cap_for_timing(marker.proof, timing_matches=marker.timing == timing)


def earned_by_direct_full(level: FullLevel, exit_code: int, *, parallel: bool) -> FullLevel | None:
    """Return the proof a direct ``ghog full`` run earned.

    A parallel run at ``speed`` never measures durations, so it earns at most
    ``cov``. A failing run keeps the level below its one failed gate when that
    gate was judged at the run's level; any other failure earns nothing.

    Args:
        level: The level the run was asked for.
        exit_code: The contract exit code of the run.
        parallel: Whether the project runs its full suite on xdist workers.

    Returns:
        The earned proof, or ``None`` (``unproven``).
    """
    judged = FullLevel.COV if level is FullLevel.SPEED and parallel else level
    if judged is FullLevel.NONE:
        return None
    if exit_code == EXIT_OBJECTIVE_MET:
        return judged
    earned = _EARNED_BELOW_FAILED_GATE.get(exit_code)
    if earned is None or earned >= judged:
        return None
    return earned


def _timing_capped(saved: FullLevel, *, timing_matches: bool) -> FullLevel:
    """Cap one saved proof at ``cov`` on a timing mismatch.

    Args:
        saved: The saved proof.
        timing_matches: Whether the timing fingerprint still matches.

    Returns:
        ``saved``, or at most ``cov`` when the timing changed.
    """
    return saved if timing_matches else min(saved, FullLevel.COV)


# eof
