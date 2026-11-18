"""Pure exact-exchange observation boundary for resume-paused (design Q09=A).

Step 2 of v0.14.0 resume-paused observes the one review exchange that a saved
routing names, through the existing read-only pieces only: an already loaded
``ReviewArtifactConfiguration``, ``derive_artifact_paths``, the nonblocking
``observe_transition`` lock, ``ReviewExchangeObserver`` and the transcript
occurrence count. It never builds a ``ReviewExchangeCore``, prepares or
migrates an artifact home, claims a role or returns a capability.

Fix (code review round 1): absence is decided under the observation lock and
through the observer, so a held lock is busy even before a coordination record
exists, and orphan or interrupted request, answer and tombstone evidence keeps
its abandoned or interrupted state instead of reading as not live. Lock entry
and exit failures are damaged evidence. The snapshot reports the exact paths
and bytes read. The caller supplies the review configuration, loaded once per
checkout as the status collector does, so the observer reads only exchange
evidence.

Fix (code review round 2): the reused store reads through accounted exact
paths, which record the consumed bytes where they are read, before decoding or
parsing, so a malformed envelope, coordination record or transcript stays in
the account of the damaged snapshot; text is decoded from those bytes without
a second read.

A held lock and a record that changes during the read are busy; a different
occurrence, an earlier round or another document, umbrella or step is a
changed selection; unreadable, invalid or inconsistent evidence is damaged.
None of them is absence, and none selects another exchange. The snapshot
carries the ownership generation and role natures as non-secret claim
evidence, never the ownership token digest.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import io
from dataclasses import dataclass, field, replace
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self

from tools.resume_paused_profiles import ReadAccount
from tools.review_exchange_models import (
    ArtifactState,
    FamilyPolicy,
    ReviewContext,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_observer import ReviewExchangeObserver
from tools.review_exchange_ownership_store import observe_transition
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_exchange_transcript_identity import current_request_occurrence

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime
    from os import PathLike

    from tools.llm_nature import LlmNature
    from tools.resume_paused_routing import SavedExchange
    from tools.review_artifact_configuration import ReviewArtifactConfiguration
    from tools.review_exchange_models import Actor, ArtifactPaths, ReviewConfiguration
    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_observer import ExchangeObservation

# The observer compares a policy only against a coordination record; without
# one, this neutral registration is never consulted.
_RECORDLESS_POLICY: Final = FamilyPolicy("no-coordination-record", "Another round", "Continue")


class ExchangeObservationKind(StrEnum):
    """Outcome of observing one saved exchange; only ``OBSERVED`` carries live state."""

    NOT_LIVE = "not-live"
    BUSY = "busy"
    OBSERVED = "observed"
    SELECTION_CHANGED = "selection-changed"
    DAMAGED = "damaged"


@dataclass(frozen=True)
class ExchangeSnapshot:
    """Validated, non-secret state of one saved exchange, with the exact files read."""

    kind: ExchangeObservationKind
    identity: str
    diagnostic: str = ""
    state: ArtifactState | None = None
    round_number: int | None = None
    occurrence: int | None = None
    owner: Actor | None = None
    expected_next_actor: Actor | None = None
    ownership_generation: int | None = None
    requestor_nature: str | None = None
    reviewer_nature: str | None = None
    reads: tuple[Path, ...] = ()
    account: ReadAccount = field(default_factory=ReadAccount)


class _BusyError(Exception):
    """The coordination record changed while it was being read."""


class _SelectionChangedError(Exception):
    """The live exchange is not the saved occurrence, round, document or step."""


def _no_paths() -> list[Path]:
    """Start an empty list of exact paths read."""
    return []


@dataclass
class _Reads:
    """Exact paths read, in order, with the bytes each read consumed."""

    paths: list[Path] = field(default_factory=_no_paths)
    account: ReadAccount = field(default_factory=ReadAccount)

    def add(self, path: Path, consumed: int) -> None:
        """Account one read at its boundary, before anything parses its bytes."""
        self.paths.append(path)
        self.account = self.account.plus(consumed)


class _AccountedPath(Path):
    """One exact exchange path that accounts its whole-file reads where the bytes are read.

    The reused store and observer read through these paths, so a read stays
    accounted when decoding or parsing then rejects its bytes. ``read_text``
    decodes the bytes already read, with the same text-mode semantics as
    ``open``, rather than reading the file a second time.
    """

    _reads: _Reads

    @classmethod
    def bound(cls, reads: _Reads, *segments: str | PathLike[str]) -> Self:
        """Return the path of these segments, accounting its reads in ``reads``."""
        accounted = cls(*segments)
        accounted._reads = reads
        return accounted

    def with_segments(self, *segments: str | PathLike[str]) -> Self:
        """Keep derived paths, such as a resolved one, accounted."""
        return self.bound(self._reads, *segments)

    def resolve(self, strict: bool = False) -> Self:  # noqa: FBT001, FBT002 - pathlib signature
        """Resolve the path and keep it accounted."""
        return self.with_segments(super().resolve(strict=strict))

    def read_bytes(self) -> bytes:
        """Read the exact bytes and account for them at once."""
        data = super().read_bytes()
        self._reads.add(Path(self), len(data))
        return data

    def read_text(self, encoding: str | None = None, errors: str | None = None, newline: str | None = None) -> str:
        """Decode the accounted bytes as text mode would decode the file."""
        with io.TextIOWrapper(io.BytesIO(self.read_bytes()), encoding=encoding, errors=errors, newline=newline) as text:
            return text.read()


def _accounted_paths(paths: ArtifactPaths, reads: _Reads) -> ArtifactPaths:
    """Return the exact path set whose content reads are accounted."""
    return replace(
        paths,
        transcript=_AccountedPath.bound(reads, paths.transcript),
        request=_AccountedPath.bound(reads, paths.request),
        answer=_AccountedPath.bound(reads, paths.answer),
        coordination=_AccountedPath.bound(reads, paths.coordination),
        tombstone=_AccountedPath.bound(reads, paths.tombstone),
    )


@dataclass(frozen=True)
class _Selection:
    """One saved exchange bound to its exact paths and observation inputs."""

    review_configuration: ReviewConfiguration
    exchange: SavedExchange
    context: ReviewContext
    paths: ArtifactPaths
    evaluated_at: datetime
    read_bytes: Callable[[Path], bytes]
    reads: _Reads = field(default_factory=_Reads)

    def probe(self) -> bytes | None:
        """Read the coordination bytes, or ``None`` when no record exists."""
        path = self.paths.coordination
        if not path.exists():
            return None
        data = self.read_bytes(path)
        self.reads.add(path, len(data))
        return data

    def result(self, kind: ExchangeObservationKind, diagnostic: str) -> ExchangeSnapshot:
        """Return a snapshot that carries no live state."""
        return ExchangeSnapshot(
            kind, self.context.identity.key, diagnostic,
            reads=tuple(self.reads.paths), account=self.reads.account,
        )


@dataclass(frozen=True)
class _Evidence:
    """One stable observation of the saved exchange."""

    record: CoordinationRecord | None
    observation: ExchangeObservation
    round_number: int | None
    occurrence: int | None


def _read_file(path: Path) -> bytes:
    """Read one file's exact bytes."""
    return path.read_bytes()


def saved_context(root: Path, exchange: SavedExchange) -> ReviewContext:
    """Rebuild the exact review context that a saved exchange names."""
    umbrella = root / exchange.umbrella if exchange.umbrella is not None else None
    return ReviewContext(exchange.identity(), root / exchange.document, umbrella, exchange.implementation_step)


def _nature(nature: LlmNature | None) -> str | None:
    """Return one recorded role nature's value."""
    return None if nature is None else nature.value


def _live_round(record: CoordinationRecord | None, observation: ExchangeObservation) -> int | None:
    """Return the round of the record, or of an orphan request or answer."""
    if record is not None:
        return record.round_number
    envelope = observation.request_envelope or observation.answer_envelope
    return None if envelope is None else envelope.round_number


def _require_saved_selection(exchange: SavedExchange, round_number: int, occurrence: int) -> None:
    """Refuse a live occurrence or round that cannot be the saved one."""
    if occurrence != exchange.occurrence:
        raise _SelectionChangedError(f"live occurrence {occurrence} differs from saved occurrence {exchange.occurrence}")
    if exchange.round_number is not None and round_number < exchange.round_number:
        raise _SelectionChangedError(f"live round {round_number} precedes saved round {exchange.round_number}")


def _read_evidence(selection: _Selection) -> _Evidence:
    """Observe the exact paths between two coordination probes."""
    context = selection.context
    before = selection.probe()
    store = ReviewExchangeStore(_accounted_paths(selection.paths, selection.reads))
    record = store.read_coordination()
    policy = record.policy if record is not None else _RECORDLESS_POLICY
    observation = ReviewExchangeObserver(
        store, context, policy, selection.review_configuration, lambda: selection.evaluated_at,
    ).classify()
    round_number = _live_round(record, observation)
    same_context = record is None or record.context == context
    occurrence = (
        current_request_occurrence(store, context, round_number)
        if round_number is not None and same_context else None
    )
    if selection.probe() != before:
        raise _BusyError
    if not same_context:
        raise _SelectionChangedError("the live exchange names another document, umbrella or implementation step")
    if round_number is not None and occurrence is not None:
        _require_saved_selection(selection.exchange, round_number, occurrence)
    return _Evidence(record, observation, round_number, occurrence)


def _observed(selection: _Selection, evidence: _Evidence) -> ExchangeSnapshot:
    """Return the live state and non-secret claim evidence of a stable observation."""
    record, observation = evidence.record, evidence.observation
    natures = record.role_natures if record is not None else None
    return ExchangeSnapshot(
        ExchangeObservationKind.OBSERVED,
        selection.context.identity.key,
        observation.diagnostic,
        observation.state,
        evidence.round_number,
        evidence.occurrence,
        record.owner if record is not None else None,
        record.expected_next_actor if record is not None else None,
        record.ownership_generation if record is not None else None,
        _nature(natures.for_role(ReviewRole.REQUESTOR)) if natures is not None else None,
        _nature(natures.for_role(ReviewRole.REVIEWER)) if natures is not None else None,
        tuple(selection.reads.paths),
        selection.reads.account,
    )


def _observe_settled(selection: _Selection) -> ExchangeSnapshot:
    """Classify the saved exchange once no publication holds its transition lock."""
    try:
        evidence = _read_evidence(selection)
    except _BusyError:
        return selection.result(ExchangeObservationKind.BUSY, "coordination changed during the read")
    except _SelectionChangedError as change:
        return selection.result(ExchangeObservationKind.SELECTION_CHANGED, str(change))
    except (OSError, UnicodeError, ReviewExchangeError) as error:
        return selection.result(ExchangeObservationKind.DAMAGED, f"saved exchange evidence is invalid: {error}")
    if evidence.observation.state is ArtifactState.IDLE:
        return selection.result(ExchangeObservationKind.NOT_LIVE, "no live artifact for the saved exchange")
    if evidence.observation.state is ArtifactState.INCONSISTENT:
        return selection.result(ExchangeObservationKind.DAMAGED, evidence.observation.diagnostic)
    return _observed(selection, evidence)


def observe_saved_exchange(
    configuration: ReviewArtifactConfiguration,
    review_configuration: ReviewConfiguration,
    exchange: SavedExchange,
    wall_clock: Callable[[], datetime],
    *,
    read_bytes: Callable[[Path], bytes] = _read_file,
) -> ExchangeSnapshot:
    """Observe one saved exchange read-only under its nonblocking observation lock."""
    root = configuration.project_root
    try:
        context = saved_context(root, exchange)
        paths = derive_artifact_paths(root, context, configuration=configuration)
    except ReviewExchangeError as error:
        return ExchangeSnapshot(ExchangeObservationKind.DAMAGED, exchange.identity().key, f"saved exchange cannot be located: {error}")
    selection = _Selection(review_configuration, exchange, context, paths, wall_clock(), read_bytes)
    try:
        with observe_transition(paths.transition_lock) as available:
            if not available:
                return selection.result(ExchangeObservationKind.BUSY, "a publication holds the transition lock")
            return _observe_settled(selection)
    except OSError as error:
        return selection.result(ExchangeObservationKind.DAMAGED, f"observation lock failed: {error}")


__all__ = [
    "ExchangeObservationKind",
    "ExchangeSnapshot",
    "observe_saved_exchange",
    "saved_context",
]


# eof
