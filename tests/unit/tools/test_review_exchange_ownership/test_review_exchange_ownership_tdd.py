"""Focused examples for Step 3 ownership capabilities and persistence.

The tests pin digest-only coordination, ordinary and forced claims, strict
capability validation, legacy parsing, and transition-lock persistence without
placing a plaintext token in durable evidence.
"""

# ruff: noqa: S105

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier

import pytest

from tools import review_exchange_ownership_store as ownership_store_module
from tools.review_exchange_models import (
    Actor,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewContext,
    ReviewFamily,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import render_json_markdown
from tools.review_exchange_ownership import (
    OwnershipCapability,
    OwnershipClaim,
    OwnershipRejectedError,
    OwnershipService,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

_TOKEN_A = "a" * 43
_TOKEN_B = "b" * 43
_SECOND_GENERATION = 2
_COMMIT_FAILURE = "injected coordination replacement failure"
_SYNC_FAILURE = "injected synchronization failure"
_SHARING_VIOLATION = "injected sharing violation"
_REPLACE_RETRY_DELAYS = 4


def _record(tmp_path: Path) -> CoordinationRecord:
    """Build one legacy-compatible active coordination record."""
    document = tmp_path / "docs" / "plan.v0.11.0.topic.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# Plan\n", encoding="utf-8")
    context = ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", "topic"),
        document,
        None,
        "3",
    )
    return CoordinationRecord(
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        CoordinationStatus.ACTIVE,
        Actor.REQUESTOR,
        Actor.REVIEWER,
        1,
        "2026-09-04T09:00:00+02:00",
    )


def _claimed_twice(
    tmp_path: Path,
) -> tuple[OwnershipService, OwnershipClaim, OwnershipClaim]:
    """Return successive claims with stable capabilities for rejection tests."""
    tokens = iter((_TOKEN_A, _TOKEN_B))
    service = OwnershipService(token_factory=lambda: next(tokens))
    first = service.claim(_record(tmp_path), Actor.REQUESTOR)
    second = service.claim(
        first.record,
        Actor.REQUESTOR,
        presented=first.capability,
        force=True,
    )
    return service, first, second


def test_claim_persists_only_digest_and_matching_capability_validates(
    tmp_path: Path,
) -> None:
    """A claim advances generation while plaintext remains session-held."""
    service = OwnershipService(token_factory=lambda: _TOKEN_A)

    claim = service.claim(_record(tmp_path), Actor.REQUESTOR)

    assert claim.capability == OwnershipCapability(1, _TOKEN_A)
    assert claim.record.ownership_generation == 1
    assert claim.record.ownership_token_digest is not None
    assert _TOKEN_A not in claim.record.ownership_token_digest
    assert _TOKEN_A not in str(claim.record.to_dict())
    assert service.failure_for(claim.record, claim.capability) is None


def test_missing_wrong_and_stale_capabilities_return_typed_failures(
    tmp_path: Path,
) -> None:
    """Missing and wrong capabilities report stable typed failures."""
    service, _first, second = _claimed_twice(tmp_path)

    missing = service.failure_for(second.record, None)
    wrong = service.failure_for(second.record, OwnershipCapability(2, _TOKEN_A))

    assert missing is not None
    assert missing.code == "ownership-missing"
    assert wrong is not None
    assert wrong.code == "ownership-invalid"


def test_stale_and_future_capabilities_return_typed_failures(tmp_path: Path) -> None:
    """Past generations are superseded while future generations are invalid."""
    service, first, second = _claimed_twice(tmp_path)

    stale = service.failure_for(second.record, first.capability)
    future = service.failure_for(second.record, OwnershipCapability(3, _TOKEN_A))

    assert stale is not None
    assert stale.code == "ownership-superseded"
    assert stale.current_generation == _SECOND_GENERATION
    assert future is not None
    assert future.code == "ownership-invalid"


def test_require_valid_raises_typed_stale_failure(tmp_path: Path) -> None:
    """Strict validation raises the same typed superseded result."""
    service, first, second = _claimed_twice(tmp_path)
    stale = service.failure_for(second.record, first.capability)

    with pytest.raises(OwnershipRejectedError) as raised:
        service.require_valid(second.record, first.capability)
    assert raised.value.failure == stale
    assert _TOKEN_A not in str(raised.value)


def test_ordinary_duplicate_claim_is_idempotent_only_for_holder(
    tmp_path: Path,
) -> None:
    """The holder can repeat a claim while another session is already claimed."""
    service = OwnershipService(token_factory=lambda: _TOKEN_A)
    first = service.claim(_record(tmp_path), Actor.REQUESTOR)

    repeated = service.claim(
        first.record,
        Actor.REQUESTOR,
        presented=first.capability,
    )

    assert repeated.newly_issued is False
    assert repeated.capability == first.capability
    with pytest.raises(OwnershipRejectedError) as raised:
        service.claim(first.record, Actor.REQUESTOR)
    assert raised.value.failure.code == "already-claimed"


def test_forced_pickup_advances_generation_and_displaces_old_holder(
    tmp_path: Path,
) -> None:
    """Direct human-invoked pickup advances even while the prior claim is live."""
    tokens = iter((_TOKEN_A, _TOKEN_B))
    service = OwnershipService(token_factory=lambda: next(tokens))
    first = service.claim(_record(tmp_path), Actor.REQUESTOR)

    second = service.claim(first.record, Actor.REVIEWER, force=True)

    assert second.record.owner is Actor.REVIEWER
    assert second.capability.generation == _SECOND_GENERATION
    failure = service.failure_for(second.record, first.capability)
    assert failure is not None
    assert failure.code == "ownership-superseded"


def test_coordination_accepts_legacy_absence_but_rejects_partial_ownership(
    tmp_path: Path,
) -> None:
    """The ownership pair is optional only when both legacy fields are absent."""
    record = _record(tmp_path)
    legacy = record.to_dict()
    assert "ownership_generation" not in legacy
    assert CoordinationRecord.from_dict(legacy) == record

    partial = dict(legacy)
    partial["ownership_generation"] = 1
    with pytest.raises(ValueError, match="ownership fields"):
        CoordinationRecord.from_dict(partial)
    with pytest.raises(ValueError, match="ownership fields"):
        replace(record, ownership_generation=1)


def test_store_claim_is_persisted_inside_transition_lock(tmp_path: Path) -> None:
    """The focused ownership store commits the compare-and-swap result."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    service = OwnershipService(token_factory=lambda: _TOKEN_A)
    with store.transition_lock():
        store.write_coordination(record)
        claim = store.claim_ownership(record, service, Actor.REQUESTOR)

    assert store.read_coordination(required=True) == claim.record
    assert claim.record.ownership_token_digest is not None
    assert _TOKEN_A not in store.paths.coordination.read_text(encoding="utf-8")


def test_transition_lock_allows_only_one_competing_ordinary_claim(
    tmp_path: Path,
) -> None:
    """Two simultaneous reviewers produce one owner and one typed loser."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    store.write_coordination(record)
    barrier = Barrier(2)

    def compete(token: str) -> str:
        service = OwnershipService(token_factory=lambda: token)
        barrier.wait(timeout=2)
        try:
            with store.transition_lock():
                current = store.read_coordination(required=True)
                assert current is not None
                store.claim_ownership(current, service, Actor.REVIEWER)
        except OwnershipRejectedError as error:
            return error.failure.code
        return "claimed"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(compete, (_TOKEN_A, _TOKEN_B), timeout=5))

    assert sorted(results) == ["already-claimed", "claimed"]


def test_stale_record_claim_reports_explicit_already_claimed_failure(
    tmp_path: Path,
) -> None:
    """A stale caller gets the stored holder's typed duplicate-claim result."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    first_service = OwnershipService(token_factory=lambda: _TOKEN_A)
    second_service = OwnershipService(token_factory=lambda: _TOKEN_B)
    with store.transition_lock():
        store.write_coordination(record)
        claimed = store.claim_ownership(record, first_service, Actor.REQUESTOR)
        with pytest.raises(OwnershipRejectedError) as raised:
            store.claim_ownership(record, second_service, Actor.REQUESTOR)

    assert raised.value.failure.code == "already-claimed"
    assert raised.value.failure.current_generation == claimed.capability.generation


def test_store_does_not_publish_a_claim_when_persistence_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A failed capability write leaves the prior coordination bytes intact."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    service = OwnershipService(token_factory=lambda: _TOKEN_A)
    store.write_coordination(record)
    before = store.paths.coordination.read_bytes()

    def fail_write(_record: CoordinationRecord) -> None:
        message = "injected ownership persistence failure"
        raise OSError(message)

    monkeypatch.setattr(store.ownership_store, "write_coordination", fail_write)
    with store.transition_lock(), pytest.raises(OSError, match="injected"):
        store.claim_ownership(record, service, Actor.REQUESTOR)

    assert store.paths.coordination.read_bytes() == before


def test_stale_claim_for_another_actor_fails_without_replacement(tmp_path: Path) -> None:
    """A stale compare-and-swap cannot overwrite a different durable owner."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    service = OwnershipService(token_factory=lambda: _TOKEN_A)
    store.write_coordination(record)
    with store.transition_lock():
        store.claim_ownership(record, service, Actor.REQUESTOR)
        with pytest.raises(ValueError, match="stale coordination"):
            store.claim_ownership(record, service, Actor.REVIEWER)


def test_ownership_store_rejects_wrong_identity_and_document_parent(
    tmp_path: Path,
) -> None:
    """Focused coordination storage remains bound to its exact context."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    other_document = record.context.document_path.with_name("plan.v0.11.0.other.md")
    other_document.write_text("# Other\n", encoding="utf-8")
    wrong_identity = ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", "other"),
        other_document,
        None,
        "3",
    )
    wrong_parent_document = tmp_path / "elsewhere" / record.context.document_path.name
    wrong_parent_document.parent.mkdir()
    wrong_parent_document.write_text("# Elsewhere\n", encoding="utf-8")
    wrong_parent = ReviewContext(
        record.context.identity,
        wrong_parent_document,
        None,
        "3",
    )

    with pytest.raises(ValueError, match="identity"):
        store.ownership_store._validate_context(wrong_identity)
    with pytest.raises(ValueError, match="document"):
        store.ownership_store._validate_context(wrong_parent)


def test_ownership_store_wraps_write_failure_and_rejects_trailing_content(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Atomic publication failures and extra coordination content fail closed."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    store.write_coordination(record)
    path = store.paths.coordination
    path.write_text(path.read_text(encoding="utf-8") + "trailing\n", encoding="utf-8")
    with pytest.raises(ValueError, match="trailing content"):
        store.read_coordination(required=True)

    def fail_commit(_prepared: Path, _target: Path) -> None:
        raise OSError(_COMMIT_FAILURE)

    monkeypatch.setattr(store.ownership_store, "_commit_prepared", fail_commit)
    with pytest.raises(ValueError, match="coordination publication failed"):
        store.write_coordination(record)


def test_ownership_atomic_prepare_cleans_up_after_sync_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A failed prepared write leaves no ownership temporary behind."""
    target = tmp_path / "coordination.md"

    def fail_sync(_descriptor: int) -> None:
        raise OSError(_SYNC_FAILURE)

    monkeypatch.setattr(ownership_store_module.os, "fsync", fail_sync)
    with pytest.raises(OSError, match="synchronization"):
        ownership_store_module.ReviewExchangeOwnershipStore._prepare_atomic(
            target,
            b"content",
        )
    assert tuple(tmp_path.glob(".tmp-review-ownership-*")) == ()


def test_ownership_atomic_replace_exhausts_bounded_permission_retries(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Persistent sharing violations stop after the bounded retry count."""
    prepared = tmp_path / "prepared.tmp"
    prepared.write_bytes(b"content")
    delays: list[float] = []

    def deny_replace(_self: Path, _target: Path) -> Path:
        raise PermissionError(_SHARING_VIOLATION)

    monkeypatch.setattr(Path, "replace", deny_replace)
    monkeypatch.setattr(ownership_store_module.time, "sleep", delays.append)
    with pytest.raises(PermissionError, match="sharing violation"):
        ownership_store_module.ReviewExchangeOwnershipStore._commit_prepared(
            prepared,
            tmp_path / "target.md",
        )
    assert len(delays) == _REPLACE_RETRY_DELAYS


def test_generic_store_validates_coordination_content_before_publication(
    tmp_path: Path,
) -> None:
    """The retained generic fixed-path API still validates coordination JSON."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    content = render_json_markdown("Coordination", record.to_dict(), "")

    store.publish_atomic(store.paths.coordination, content)

    assert store.read_coordination(required=True) == record


def test_capability_validation_rejects_invalid_record_digest(tmp_path: Path) -> None:
    """Malformed durable digest data is rejected by the coordination model."""
    record = _record(tmp_path)
    with pytest.raises(ValueError, match="digest"):
        replace(
            record,
            ownership_generation=1,
            ownership_token_digest="not-a-sha256-digest",  # noqa: S106
        )


# eof
