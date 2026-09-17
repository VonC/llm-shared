"""Real SQLite persistence, lost replies and typed storage failure boundaries."""

# ruff: noqa: PLR2004 - Concrete persisted values are the test oracle.

from __future__ import annotations

import sqlite3
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools.wait_service.models import (
    Capability,
    Continuation,
    DeadlinePolicy,
    Delivery,
    HostBinding,
    NormalEnd,
    Observation,
    Outcome,
    Recipient,
    SourceIdentity,
    WaitError,
    WaitIntent,
)
from tools.wait_service.store import WaitStore

pytestmark = pytest.mark.timeout(10)

if TYPE_CHECKING:
    from pathlib import Path


def intent(key: str = "request-1") -> WaitIntent:
    """Supply exact synthetic identities without any production adapter."""
    return WaitIntent(
        key,
        SourceIdentity("synthetic", "repo-file-id", "worktree-file-id", "C:/repo/artifacts", "run-1", "round-1", "generation-1", "source-v1"),
        Recipient("synthetic", "host-v1", "thread-1", "profile-file-id"),
        DeadlinePolicy(indefinite=True),
        Continuation.RESUME,
        "same-user:fixture",
        "requestor",
    )


def binding() -> HostBinding:
    """Supply independently verified route evidence for durable arming."""
    return HostBinding(
        intent().recipient, "connection-1", Capability.FUNCTIONAL,
        NormalEnd.DIRECT, "route-v1", "armed-receipt", "turn-ended",
    )


def outcome(kind: str = "ready") -> Outcome:
    """Describe a bounded immutable source decision."""
    return Outcome(kind, Observation("ready", "generation-1", 10.0, 9.0, "result-1", "sha256:fixture"), "on-time", clock_uncertain=False)


class FaultConnection(sqlite3.Connection):
    """Inject commit loss before or after SQLite actually commits."""

    fault = ""

    def commit(self) -> None:
        """Leave the store to distinguish an error from a success acknowledgement."""
        if self.fault == "before":
            message = "database or disk is full"
            raise sqlite3.OperationalError(message)
        super().commit()
        if self.fault == "after":
            message = "reply lost after commit"
            raise sqlite3.OperationalError(message)


def fault_store(path: Path) -> tuple[WaitStore, FaultConnection]:
    """Open real SQLite with an injectable commit boundary."""
    connections: list[FaultConnection] = []

    def connect(location: str) -> sqlite3.Connection:
        connection = sqlite3.connect(location, uri=True, isolation_level=None, factory=FaultConnection)
        connections.append(connection)
        return connection

    return WaitStore(path, connect=connect), connections[0]


class TestWaitStore:
    """Acknowledgements and immutable events survive reopen and exact retries."""

    def test_reopen_retains_preparation_arming_and_early_outcome(self, tmp_path: Path) -> None:
        """An early event and a lost registration reply keep their identities."""
        path = tmp_path / "wait.db"
        with WaitStore(path) as store:
            first = store.register(intent(), 1.0)
            assert first.state == "preparing"
            assert store.register(intent(), 2.0) == first
            event = store.record_outcome(first.wait_id, outcome(), 10.0)
            assert store.record_outcome(first.wait_id, outcome("expired"), 11.0) == event
            armed = store.arm(first.wait_id, binding())
            assert armed.state == "armed"
        with WaitStore(path) as store:
            assert store.register(intent(), 20.0) == armed
            assert store.get_event(first.wait_id) == event
            assert store.get_binding(first.wait_id) == binding()
            assert store.get_registration(first.wait_id).intent == intent()
            assert store.get_event("missing") is None

    def test_conflicting_key_never_mutates_existing_intent(self, tmp_path: Path) -> None:
        """Physical identities and continuation policy participate in equality."""
        with WaitStore(tmp_path / "wait.db") as store:
            original = intent()
            first = store.register(original, 1.0)
            changes = [
                replace(original, source=replace(original.source, worktree_id="replaced")),
                replace(original, source=replace(original.source, generation="reused-label")),
                replace(original, recipient=replace(original.recipient, thread_id="other")),
                replace(original, deadline=DeadlinePolicy(20.0)),
                replace(original, continuation=Continuation.INSPECT),
            ]
            for changed in changes:
                with pytest.raises(WaitError, match="idempotency-conflict") as error:
                    store.register(changed, 2.0)
                assert error.value.wait_id == first.wait_id
            assert store.get_registration(first.wait_id).intent == original
            second = store.register(replace(changes[0], idempotency_key="other"), 3.0)
            assert second.wait_id != first.wait_id

    @pytest.mark.parametrize("fault", ["before", "after"])
    def test_failed_commit_never_returns_an_acknowledgement(self, tmp_path: Path, fault: str) -> None:
        """A lost commit reply remains unknown and an exact retry resolves it."""
        path = tmp_path / "wait.db"
        store, connection = fault_store(path)
        connection.fault = fault
        with pytest.raises(WaitError, match="storage-unavailable"):
            store.register(intent(), 1.0)
        store.close()
        with WaitStore(path) as recovered:
            registration = recovered.register(intent(), 2.0)
            assert registration.created_utc == (1.0 if fault == "after" else 2.0)
            assert recovered.register(intent(), 3.0) == registration

    def test_outcome_and_event_rollback_together(self, tmp_path: Path) -> None:
        """Failed terminal commits cannot leave an outcome without its event."""
        store, connection = fault_store(tmp_path / "wait.db")
        with store:
            registration = store.register(intent(), 1.0)
            connection.fault = "before"
            with pytest.raises(WaitError, match="storage-unavailable"):
                store.record_outcome(registration.wait_id, outcome(), 10.0)
            assert store.get_event(registration.wait_id) is None
            connection.fault = ""
            event = store.record_outcome(registration.wait_id, outcome(), 11.0)
            assert event.outcome == outcome()

    @pytest.mark.parametrize("contents", [b"", b"not a database"])
    def test_existing_unknown_or_corrupt_store_is_never_replaced(self, tmp_path: Path, contents: bytes) -> None:
        """Initialization is permitted only for a previously absent store."""
        path = tmp_path / "wait.db"
        path.write_bytes(contents)
        with pytest.raises(WaitError, match=r"schema-incompatible|storage-unavailable"):
            WaitStore(path)
        assert path.read_bytes() == contents

    def test_unknown_version_is_refused_without_migration(self, tmp_path: Path) -> None:
        """The store cannot silently reset or downgrade a future schema."""
        path = tmp_path / "wait.db"
        with sqlite3.connect(path) as connection:
            connection.execute("PRAGMA user_version = 42")
        original = path.read_bytes()
        with pytest.raises(WaitError, match="schema-incompatible"):
            WaitStore(path)
        assert path.read_bytes() == original

    def test_recovery_records_preserve_cancellation_and_delivery_evidence(self, tmp_path: Path) -> None:
        """Restart retains access-loss start, accepted receipt and retry epoch."""
        path = tmp_path / "wait.db"
        observation = Observation("unknown", "generation-1", 5.0, access_loss_utc=4.0)
        with WaitStore(path) as store:
            registration = store.register(intent(), 1.0)
            store.observe(registration.wait_id, observation)
            event = store.record_outcome(registration.wait_id, outcome(), 10.0)
            delivery = Delivery(event.event_id, "connection-1", "accepted", 2, 1, 15.0, "receipt-1", "busy", "route-v1")
            store.save_delivery(delivery)
            cancellation = store.cancel(registration.wait_id, 12.0, "local-user")
            assert store.cancel(registration.wait_id, 13.0, "retry") == cancellation
        with WaitStore(path) as store:
            assert store.get_observation(registration.wait_id) == observation
            assert store.get_delivery(event.event_id) == delivery
            assert store.get_cancellation(registration.wait_id) == cancellation
            assert store.get_event(registration.wait_id) == event
            assert store.register(intent(), 20.0).wait_id == registration.wait_id

    def test_arming_retry_does_not_replace_connection(self, tmp_path: Path) -> None:
        """Only a later explicit rearm operation may change an incarnation."""
        with WaitStore(tmp_path / "wait.db") as store:
            registration = store.register(intent(), 1.0)
            store.arm(registration.wait_id, binding())
            with pytest.raises(WaitError, match="rearm-required"):
                store.arm(registration.wait_id, replace(binding(), incarnation="new"))
            assert store.get_binding(registration.wait_id) == binding()

def test_recovery_preserves_early_preparation_but_skips_completed_routes(tmp_path: Path) -> None:
    """Startup includes a result awaiting arming and excludes a settled armed result."""
    with WaitStore(tmp_path / "wait.db") as store:
        registration = store.register(intent(), 1)
        event = store.record_outcome(registration.wait_id, outcome(), 2)
        store.preparation_failed(registration.wait_id, "route-unavailable")
        recovered = list(store.recover_registrations())
        assert [item.wait_id for item in recovered] == [registration.wait_id]
        assert recovered[0].diagnostic == "route-unavailable"
        armed = store.arm(registration.wait_id, binding())
        store.preparation_failed(registration.wait_id, "stale-error")
        assert store.get_registration(registration.wait_id) == armed
        assert store.get_event(registration.wait_id) == event
        assert list(store.recover_registrations()) == []
        with pytest.raises(WaitError, match="bounded preparation diagnostic"):
            store.preparation_failed(registration.wait_id, "")


def test_recovery_query_failure_retains_database(tmp_path: Path) -> None:
    """A broken SQLite handle reports unavailable rather than an empty recovery set."""
    path = tmp_path / "wait.db"
    store, connection = fault_store(path)
    with store:
        connection.close()
        with pytest.raises(WaitError, match="storage-unavailable"):
            list(store.recover_registrations())
    assert path.exists()


# eof
