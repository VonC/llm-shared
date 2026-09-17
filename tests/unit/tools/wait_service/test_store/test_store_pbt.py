"""Generated retry, terminal and cancellation sequences over real SQLite."""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.wait_service.models import WaitError
from tools.wait_service.store import WaitStore

from .test_store_tdd import fault_store, intent, outcome

if TYPE_CHECKING:
    from tools.wait_service.models import Cancellation, Event


def act(store: WaitStore, wait_id: str, action: str) -> None:
    """Apply one generated operation without duplicating the expected state model."""
    if action == "cancel":
        store.cancel(wait_id, 2.0, "user")
    elif action != "retry":
        store.record_outcome(wait_id, outcome(action), 3.0)


class TestWaitStoreProperties:
    """Operation order cannot create a second wait or reopen a terminal event."""

    @settings(max_examples=12, deadline=None)
    @given(st.lists(st.sampled_from(["retry", "ready", "expired", "monitoring-failure", "cancel"]), min_size=1, max_size=6))
    def test_stable_identities_and_immutable_terminal_state(self, actions: list[str]) -> None:
        """Bounded sequences preserve the first terminal decision through reopen."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "wait.db"
            with WaitStore(path) as store:
                first = store.register(intent(), 1.0)
            event: Event | None = None
            cancellation: Cancellation | None = None
            for action in actions:
                with WaitStore(path) as store:
                    act(store, first.wait_id, action)
                    cancellation = cancellation or store.get_cancellation(first.wait_id)
                    event = event or store.get_event(first.wait_id)
                    assert store.register(intent(), 4.0).wait_id == first.wait_id
                    assert store.get_event(first.wait_id) == event
                    assert store.get_cancellation(first.wait_id) == cancellation

    @settings(max_examples=8, deadline=None)
    @given(st.lists(st.sampled_from(["before", "after"]), min_size=1, max_size=3))
    def test_failed_commit_sequences_never_acknowledge(self, faults: list[str]) -> None:
        """Repeated lost replies preserve the first event that actually committed."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "wait.db"
            with WaitStore(path) as store:
                registration = store.register(intent(), 1.0)
            event: Event | None = None
            for fault in faults:
                store, connection = fault_store(path)
                with store:
                    connection.fault = fault
                    with pytest.raises(WaitError, match="storage-unavailable"):
                        store.record_outcome(registration.wait_id, outcome(), 2.0)
                    if fault == "after":
                        event = event or store.get_event(registration.wait_id)
                    assert store.get_event(registration.wait_id) == event
            with WaitStore(path) as store:
                recovered = store.record_outcome(registration.wait_id, outcome(), 3.0)
                assert recovered == (event or recovered)
                assert store.record_outcome(registration.wait_id, outcome("expired"), 4.0) == recovered

# eof
