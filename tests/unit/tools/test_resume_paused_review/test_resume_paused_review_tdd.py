"""Exact-exchange observation tests over declared review artifacts.

Step 2 of v0.15.0 resume-paused: the saved exchange is observed through its
exact paths and the nonblocking observation lock, never through a review core
or a write. A busy lock, a changing record, another occurrence, round or step,
and damaged evidence are each reported as such, and the snapshot carries the
ownership generation but never the token digest. The prior writer's record,
envelopes and transcript footers are declared, not replayed.

Fix (code review round 1): absence is decided under the observation lock, so a
held lock without a record is busy and orphan or interrupted artifacts keep
their states; lock entry, acquisition and exit failures are damaged; and an
independent recorder of ``Path`` reads checks the snapshot's exact reads and
bytes, which include every read the reused store and observer make.

Fix (code review round 2): a malformed orphan answer, a malformed coordination
record and an undecodable transcript are each read once and stay in the
damaged snapshot's account, as the independent recorder confirms.

Fix (Step 7): a declared marked claim binding rides in the snapshot unchanged,
still without the ownership token digest.
"""

from __future__ import annotations

import errno
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    checkout,
    no_tracking,
    recorded_reads,
    sizes,
    tree,
    writes_forbidden,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    PLAN,
    REQUESTOR_PANE,
)
from tools import review_exchange_ownership_store as ownership_store
from tools.llm_nature import LlmNature
from tools.resume_paused_review import (
    ExchangeObservationKind,
    ExchangeSnapshot,
    observe_saved_exchange,
)
from tools.resume_paused_routing import SavedExchange
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import (
    CoordinationRecord,
    MarkedClaimEvidence,
)
from tools.review_exchange_models_envelope import (
    Envelope,
    render_envelope_markdown,
    render_json_markdown,
)
from tools.review_exchange_ownership import OwnershipService
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_role_nature import RoleNatureSnapshot

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.review_exchange_models import ArtifactPaths
    from tools.review_exchange_models_coordination import MarkedClaimBinding

LEASE = "2026-11-18T07:30:00+01:00"
ISSUED_CAPABILITY = "scenario-resume-paused-token-000000000"
GENERATION = 3
SAVED = SavedExchange(ReviewFamily.CODE, PLAN, "2", None, 1, 1)
POLICY = FamilyPolicy("commit-ready", "Another round", "Commit")
SETTINGS = ReviewConfiguration(enabled=True, wait_timeout_seconds=600)


def exchange_checkout(tmp_path: Path) -> tuple[ReviewArtifactConfiguration, ReviewContext, ArtifactPaths]:
    """Declare one checkout whose reviewed plan exists, with its read-only configuration and paths."""
    root = checkout(tmp_path)
    document = root / PLAN
    document.parent.mkdir(parents=True)
    document.write_text("# Plan\n", encoding="utf-8")
    identity = ExchangeIdentity(ReviewFamily.CODE, "code", "v0.15.0", "resume-paused")
    configuration = ReviewArtifactConfiguration.load(root, tracked_directory=no_tracking)
    context = ReviewContext(identity, document, None, "2")
    return configuration, context, derive_artifact_paths(root, context, configuration=configuration)


def declare_transcript(paths: ArtifactPaths, occurrences: int = 1) -> None:
    """Declare the request footers of the saved exchange's earlier occurrences."""
    footers = ["request-step-2-round-1", *(f"request-step-2-round-1-exchange-{number}" for number in range(2, occurrences + 1))]
    paths.transcript.write_text("".join(f"<!-- review-entry-id: {footer} -->\n" for footer in footers), encoding="utf-8")


def declare_exchange(
    context: ReviewContext, paths: ArtifactPaths, *, round_number: int = 1, occurrences: int = 1, marked: MarkedClaimBinding | None = None,
) -> None:
    """Declare the prior writer's coordination record, with an optional marked claim, and transcript footers."""
    record = CoordinationRecord(
        context, POLICY, CoordinationStatus.ACTIVE, Actor.REQUESTOR, Actor.REQUESTOR, round_number, LEASE,
        role_natures=RoleNatureSnapshot(LlmNature.CLAUDE, LlmNature.CODEX),
        ownership_generation=GENERATION, ownership_token_digest=OwnershipService.digest(ISSUED_CAPABILITY),
        marked_claim=marked,
    )
    title = f"Review exchange coordination for {context.identity.key}"
    paths.coordination.write_text(render_json_markdown(title, record.to_dict(), ""), encoding="utf-8")
    declare_transcript(paths, occurrences)


def request_text(context: ReviewContext) -> str:
    """Render one valid round-1 request envelope for the saved exchange."""
    envelope = Envelope(context.identity, None, context.document_path, "2", ReviewRole.REQUESTOR, 1, LEASE)
    return render_envelope_markdown(envelope, "Prepared request.\n")


def now() -> datetime:
    """Return the injected observation time, one second into the declared lease."""
    return datetime.fromisoformat(LEASE) + timedelta(seconds=1)


def observe(configuration: ReviewArtifactConfiguration, exchange: SavedExchange = SAVED, read_bytes: Callable[[Path], bytes] | None = None) -> ExchangeSnapshot:
    """Observe one saved exchange with the declared review settings and clock."""
    if read_bytes is None:
        return observe_saved_exchange(configuration, SETTINGS, exchange, now)
    return observe_saved_exchange(configuration, SETTINGS, exchange, now, read_bytes=read_bytes)


def held_by_a_publisher(_stream: object) -> bool:
    """Declare native contention: a publication holds the transition lock byte."""
    return False


def failing_lock(_stream: object) -> bool:
    """Declare a native lock call that fails with an input/output error."""
    raise OSError(errno.EIO, "lock device failed")


def test_observed_exchange_accounts_every_read_and_exposes_no_secret(tmp_path: Path) -> None:
    """A populated exchange is observed through exact paths, with every read accounted."""
    configuration, context, paths = exchange_checkout(tmp_path)
    declare_exchange(context, paths)
    paths.request.write_text(request_text(context), encoding="utf-8")
    before = tree(configuration.project_root)
    with writes_forbidden(), recorded_reads() as seen:
        snapshot = observe(configuration)
    assert tree(configuration.project_root) == before
    coordination = paths.coordination
    assert snapshot.reads == (coordination, coordination, paths.request, coordination, paths.transcript, coordination) == tuple(seen)
    assert (snapshot.account.files, snapshot.account.bytes_read) == (len(seen), sizes(snapshot.reads))
    assert (snapshot.kind, snapshot.state, snapshot.round_number, snapshot.occurrence) == (ExchangeObservationKind.OBSERVED, ArtifactState.REQUEST_PENDING, 1, 1)
    assert (snapshot.owner, snapshot.expected_next_actor, snapshot.ownership_generation) == (Actor.REQUESTOR, Actor.REQUESTOR, GENERATION)
    assert (snapshot.requestor_nature, snapshot.reviewer_nature, snapshot.identity) == ("claude", "codex", context.identity.key)
    assert snapshot.marked_claim is None
    assert OwnershipService.digest(ISSUED_CAPABILITY) not in repr(snapshot)


def test_observed_exchange_carries_the_marked_claim_binding(tmp_path: Path) -> None:
    """The current marked claim's non-secret binding rides in the snapshot, never the token digest (Step 7)."""
    configuration, context, paths = exchange_checkout(tmp_path)
    marked = MarkedClaimEvidence("a1" * 16, REQUESTOR_PANE, "claude", "b" * 64, 1, 1).issued(GENERATION)
    declare_exchange(context, paths, marked=marked)
    paths.request.write_text(request_text(context), encoding="utf-8")
    snapshot = observe(configuration)
    assert (snapshot.kind, snapshot.marked_claim) == (ExchangeObservationKind.OBSERVED, marked)
    assert OwnershipService.digest(ISSUED_CAPABILITY) not in repr(snapshot)


def test_genuinely_absent_exchange_is_not_live(tmp_path: Path) -> None:
    """No record and no artifact at all is the only not-live outcome, and reads nothing."""
    configuration, _context, _paths = exchange_checkout(tmp_path)
    snapshot = observe(configuration)
    assert (snapshot.kind, snapshot.reads) == (ExchangeObservationKind.NOT_LIVE, ())


def test_orphan_artifacts_keep_their_states(tmp_path: Path) -> None:
    """A request or tombstone without a record is abandoned or interrupted, not absent."""
    configuration, context, paths = exchange_checkout(tmp_path)
    declare_transcript(paths)
    paths.request.write_text(request_text(context), encoding="utf-8")
    orphan = observe(configuration)
    assert (orphan.kind, orphan.state, orphan.round_number, orphan.occurrence) == (ExchangeObservationKind.OBSERVED, ArtifactState.ABANDONED_REQUEST, 1, 1)
    assert (orphan.owner, orphan.ownership_generation, orphan.requestor_nature) == (None, None, None)
    paths.request.replace(paths.tombstone)
    interrupted = observe(configuration)
    assert (interrupted.kind, interrupted.state, interrupted.round_number) == (ExchangeObservationKind.OBSERVED, ArtifactState.INTERRUPTED_ANSWER_PUBLICATION, None)


def test_malformed_orphan_artifact_is_damaged(tmp_path: Path) -> None:
    """An invalid answer without a record is damaged evidence, never absence."""
    configuration, _context, paths = exchange_checkout(tmp_path)
    paths.answer.write_text("not an envelope\n", encoding="utf-8")
    assert observe(configuration).kind is ExchangeObservationKind.DAMAGED


@pytest.mark.parametrize("damage", ["answer", "coordination", "transcript"])
def test_rejected_reads_stay_accounted(tmp_path: Path, damage: str) -> None:
    """Bytes read and then rejected by parsing or decoding stay in the damaged account."""
    configuration, context, paths = exchange_checkout(tmp_path)
    coordination = paths.coordination
    if damage == "answer":
        paths.answer.write_text("not an envelope\n", encoding="utf-8")
        expected = (paths.answer,)
    elif damage == "coordination":
        declare_exchange(context, paths)
        coordination.write_text("# Broken\n", encoding="utf-8")
        expected = (coordination, coordination)
    else:
        declare_exchange(context, paths)
        paths.transcript.write_bytes(b"\xff\xfe not UTF-8\n")
        expected = (coordination, coordination, coordination, paths.transcript)
    with recorded_reads() as seen:
        snapshot = observe(configuration)
    assert snapshot.kind is ExchangeObservationKind.DAMAGED
    assert snapshot.reads == expected == tuple(seen)
    assert (snapshot.account.files, snapshot.account.bytes_read) == (len(seen), sizes(snapshot.reads))


@pytest.mark.parametrize(
    ("saved", "round_number", "occurrences", "diagnostic"),
    [
        (SAVED, 1, 2, "live occurrence 2 differs from saved occurrence 1"),
        (SavedExchange(ReviewFamily.CODE, PLAN, "2", None, 1, 2), 1, 1, "live round 1 precedes saved round 2"),
        (SavedExchange(ReviewFamily.CODE, PLAN, "3", None, 1, 1), 1, 1, "the live exchange names another document, umbrella or implementation step"),
    ],
)
def test_changed_selection_is_never_another_exchange(tmp_path: Path, saved: SavedExchange, round_number: int, occurrences: int, diagnostic: str) -> None:
    """A different occurrence, an earlier round or another step is a changed selection."""
    configuration, context, paths = exchange_checkout(tmp_path)
    declare_exchange(context, paths, round_number=round_number, occurrences=occurrences)
    snapshot = observe(configuration, saved)
    assert (snapshot.kind, snapshot.diagnostic) == (ExchangeObservationKind.SELECTION_CHANGED, diagnostic)


def test_held_lock_is_busy_with_or_without_a_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A publisher holding the lock is busy, even before its coordination record exists."""
    configuration, context, paths = exchange_checkout(tmp_path)
    paths.transition_lock.write_bytes(b"\0")
    with monkeypatch.context() as patch:
        patch.setattr(ownership_store, "_try_observation_lock", held_by_a_publisher)
        early = observe(configuration)
        declare_exchange(context, paths)
        late = observe(configuration)
    for busy in (early, late):
        assert (busy.kind, busy.diagnostic, busy.reads) == (ExchangeObservationKind.BUSY, "a publication holds the transition lock", ())


def test_changing_record_is_busy(tmp_path: Path) -> None:
    """A record whose bytes differ between the two probes is busy, not absent."""
    configuration, context, paths = exchange_checkout(tmp_path)
    declare_exchange(context, paths)
    versions = iter((b"first", b"second"))
    changing = observe(configuration, read_bytes=lambda _path: next(versions))
    assert (changing.kind, changing.diagnostic) == (ExchangeObservationKind.BUSY, "coordination changed during the read")


def raise_on_unlock(_stream: object) -> None:
    """Declare a native unlock that fails after the observation."""
    raise OSError(errno.EIO, "unlock failed")


@pytest.mark.parametrize("failure", ["directory", "acquire", "release"])
def test_lock_failures_are_damaged_not_raised(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    """Opening, acquiring or releasing the observation lock fails into a damaged result."""
    configuration, context, paths = exchange_checkout(tmp_path)
    declare_exchange(context, paths)
    if failure == "directory":
        paths.transition_lock.mkdir()
    else:
        paths.transition_lock.write_bytes(b"\0")
    with monkeypatch.context() as patch:
        if failure == "acquire":
            patch.setattr(ownership_store, "_try_observation_lock", failing_lock)
        if failure == "release":
            patch.setattr(ownership_store, "_unlock_stream", raise_on_unlock)
        snapshot = observe(configuration)
    assert snapshot.kind is ExchangeObservationKind.DAMAGED
    assert snapshot.diagnostic.startswith("observation lock failed")


def test_damaged_evidence_is_reported_as_damaged(tmp_path: Path) -> None:
    """Invalid coordination, an inconsistent artifact set or a missing document is damaged."""
    configuration, context, paths = exchange_checkout(tmp_path)
    declare_exchange(context, paths)
    paths.request.write_text("not an envelope\n", encoding="utf-8")
    assert observe(configuration).kind is ExchangeObservationKind.DAMAGED
    paths.request.unlink()
    paths.coordination.write_text("# Broken\n", encoding="utf-8")
    assert observe(configuration).kind is ExchangeObservationKind.DAMAGED
    missing = SavedExchange(ReviewFamily.CODE, "docs/v0.14.0/plan.v0.14.0.missing.md", "2", None, 1, None)
    located = observe(configuration, missing)
    assert (located.kind, located.diagnostic.startswith("saved exchange cannot be located")) == (ExchangeObservationKind.DAMAGED, True)


# eof
