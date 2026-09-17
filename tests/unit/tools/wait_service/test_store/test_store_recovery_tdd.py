"""Store recovery edges, schema evidence and non-armed retry behavior."""

# ruff: noqa: PLR2004 - Assertions name exact schema and recovery facts.

from __future__ import annotations

import sqlite3
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools.wait_service.models import Capability, NormalEnd, WaitError
from tools.wait_service.store import HISTORY_LIMIT, WaitStore

from .test_store_tdd import FaultConnection, binding, fault_store, intent, outcome

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.timeout(10)


class TestStoreRecovery:
    """Durable evidence survives rejected routes, storage errors and cleanup."""

    def test_explicit_retained_and_failed_arming_retry(self, tmp_path: Path) -> None:
        """Only usable automatic routes report armed; failed preparation can resume."""
        with WaitStore(tmp_path / "wait.db") as store:
            registration = store.register(intent(), 1.0)
            event = store.record_outcome(registration.wait_id, outcome(), 2.0)
            unavailable = replace(binding(), capability=Capability.UNAVAILABLE, normal_end=NormalEnd.UNAVAILABLE)
            failed = store.arm(registration.wait_id, unavailable)
            assert failed.state == "preparing"
            assert failed.diagnostic == Capability.UNAVAILABLE
            assert store.register(intent(), 3.0) == failed
            assert store.arm(registration.wait_id, binding()).state == "armed"
            assert store.get_event(registration.wait_id) == event
            manual = store.register(intent("manual"), 4.0)
            assert store.arm(manual.wait_id, replace(unavailable, capability=Capability.RETAINED)).state == "retained"

    def test_arming_and_cancellation_do_not_acknowledge_failed_commits(self, tmp_path: Path) -> None:
        """Rollback retains preparing and uncancelled state on storage failure."""
        store, connection = fault_store(tmp_path / "wait.db")
        with store:
            registration = store.register(intent(), 1.0)
            connection.fault = "before"
            with pytest.raises(WaitError, match="storage-unavailable"):
                store.arm(registration.wait_id, binding())
            assert store.get_binding(registration.wait_id) is None
            assert store.get_registration(registration.wait_id).state == "preparing"
            with pytest.raises(WaitError, match="storage-unavailable"):
                store.cancel(registration.wait_id, 2.0, "user")
            assert store.get_cancellation(registration.wait_id) is None

    def test_shared_observation_isolated_by_exact_source(self, tmp_path: Path) -> None:
        """Two subscribers share one source record without crossing generations."""
        with WaitStore(tmp_path / "wait.db") as store:
            first = store.register(intent(), 1.0)
            other_recipient = replace(intent("second"), recipient=replace(intent().recipient, thread_id="other"))
            second = store.register(other_recipient, 1.0)
            third = store.register(replace(intent("third"), source=replace(intent().source, generation="new")), 1.0)
            assert store.get_observation(first.wait_id) is None
            assert store.get_delivery("missing") is None
            store.observe(first.wait_id, outcome().observation)
            assert store.get_observation(second.wait_id) == outcome().observation
            assert store.get_observation(third.wait_id) is None
            with pytest.raises(WaitError, match="generation mismatch"):
                store.observe(third.wait_id, outcome().observation)
            with pytest.raises(WaitError, match="recipient mismatch"):
                store.arm(second.wait_id, binding())
            with pytest.raises(WaitError, match="wait-not-found"):
                store.get_registration("missing")

    def test_schema_shape_and_unavailable_storage_are_typed(self, tmp_path: Path) -> None:
        """A claimed version with the wrong schema cannot enter service."""
        path = tmp_path / "wait.db"
        with sqlite3.connect(path) as connection:
            connection.execute("PRAGMA user_version = 1")
        with pytest.raises(WaitError, match="schema-incompatible"):
            WaitStore(path)
        with pytest.raises(WaitError, match="storage-unavailable"):
            WaitStore(tmp_path / "absent-parent" / "wait.db")
        with pytest.raises(WaitError, match="durable journal"):
            WaitStore(tmp_path / "memory.db", connect=lambda _: sqlite3.connect(":memory:"))

    def test_nested_transaction_and_sqlite_read_failures(self, tmp_path: Path) -> None:
        """An inner operation cannot commit a caller's outer transaction."""
        store, connection = fault_store(tmp_path / "wait.db")
        with store:
            with store.transaction(), pytest.raises(WaitError, match="transaction-active"):
                store.register(intent(), 1.0)
            connection.close()
            with pytest.raises(WaitError, match="storage-unavailable"):
                store.get_event("missing")
        with pytest.raises(WaitError, match="store closed"):
            store.register(intent(), 1.0)

    def test_rollback_failure_poisoned_connection_is_closed(self, tmp_path: Path) -> None:
        """A failed rollback cannot leave later requests using an uncertain writer."""
        class RollbackFailure(FaultConnection):
            """A failed device cannot complete rollback after a failed commit."""

            def rollback(self) -> None:
                """Surface device failure for the adapter to close safely."""
                message = "device unavailable"
                raise sqlite3.OperationalError(message)

        def connect(location: str) -> sqlite3.Connection:
            return sqlite3.connect(location, uri=True, isolation_level=None, factory=RollbackFailure)

        with WaitStore(tmp_path / "wait.db", connect=connect) as store:
            with pytest.raises(WaitError, match="storage-unavailable"), store.transaction() as transaction:
                transaction.execute("INSERT INTO absent_table VALUES (1)")
            with pytest.raises(WaitError, match="store closed"):
                store.register(intent(), 1.0)

    def test_history_is_bounded_without_deleting_outcome(self, tmp_path: Path) -> None:
        """Diagnostic truncation preserves the stable unconsumed event."""
        with WaitStore(tmp_path / "wait.db") as store:
            registration = store.register(intent(), 1.0)
            event = store.record_outcome(registration.wait_id, outcome(), 2.0)
            for index in range(HISTORY_LIMIT + 2):
                store.add_history(registration.wait_id, float(index), "busy", "bounded detail")
            with store.transaction() as transaction:
                count, oldest = transaction.execute("SELECT count(*), min(recorded_utc) FROM history").fetchone()
            assert count == HISTORY_LIMIT
            assert oldest == 2.0
            assert store.get_event(registration.wait_id) == event

    def test_settlement_abandonment_and_tombstone_schema_survive_reopen(self, tmp_path: Path) -> None:
        """Step 6/7 facts are durable already, without implementing their workflow."""
        path = tmp_path / "wait.db"
        with WaitStore(path) as store:
            registration = store.register(intent(), 1.0)
            event = store.record_outcome(registration.wait_id, outcome(), 2.0)
            with store.transaction() as transaction:
                transaction.execute(
                    "INSERT INTO consumption_attempts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    ("attempt", event.event_id, '{"thread_id":"thread-1"}', "authority-v1", "authorized", "consumption", "receipt", "execution-unresolved", 3.0, "human-abandoned", 4.0, 1, 0),
                )
            assert store.cancel(registration.wait_id, 5.0, "user").decision == "already-consumed"
            with store.transaction() as transaction:
                transaction.execute("INSERT INTO tombstones VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ("old-wait", "old-event", "old-key", replace(intent(), idempotency_key="old-key").digest(), "armed", 0.0, "suppressed", "old-consumption", "cancelled"))
        with WaitStore(path) as store:
            with store.transaction() as transaction:
                attempt = transaction.execute("SELECT * FROM consumption_attempts WHERE attempt_id = 'attempt'").fetchone()
            assert attempt["workflow_receipt"] == "receipt"
            assert attempt["abandonment_reason"] == "human-abandoned"
            assert attempt["reconciliation_pending"] == 1
            assert attempt["execution_state"] == "execution-unresolved"
            retry = store.register(replace(intent(), idempotency_key="old-key"), 6.0)
            assert retry.wait_id == "old-wait"
            assert retry.state == "armed"
            with pytest.raises(WaitError, match="idempotency-conflict"):
                store.register(replace(intent(), idempotency_key="old-key", role="reviewer"), 7.0)

# eof
