"""Controllable source, host, clock and worker ports with no workflow side effects."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tools.wait_service.models import (
    Capability,
    Delivery,
    HostBinding,
    NormalEnd,
    Observation,
    Recipient,
    SourceIdentity,
    WaitError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.wait_service.models import Event


class SyntheticClock:
    """Advance UTC, process time, suspension and corrections independently."""

    def __init__(self, now: float = 0.0) -> None:
        """A fresh instance gives restart a new monotonic origin."""
        self.now, self.elapsed = now, 0.0

    def utc(self) -> float:
        """Return the fixture's absolute wall clock."""
        return self.now

    def monotonic(self) -> float:
        """Return only the current process's scheduling epoch."""
        return self.elapsed

    def advance(self, seconds: float, *, monotonic: float | None = None) -> None:
        """Use a distinct monotonic delta for suspend or wall-clock corrections."""
        self.now += seconds
        self.elapsed += seconds if monotonic is None else monotonic


class ControlledIO:
    """Hold a fixed number of operations until a deterministic test releases them."""

    def __init__(self, capacity: int = 4) -> None:
        """No pending operation allocates a thread or sleeps."""
        self.capacity = capacity
        self.pending: list[Callable[[], None]] = []
        self.maximum = 0

    def submit(self, operation: Callable[[], None]) -> bool:
        """Refuse excess work using the same port as the real bounded pool."""
        if len(self.pending) >= self.capacity:
            return False
        self.pending.append(operation)
        self.maximum = max(self.maximum, len(self.pending))
        return True

    def run_all(self) -> None:
        """Complete the currently admitted batch, without admitting its successors."""
        pending, self.pending = self.pending, []
        for operation in pending:
            operation()


class SyntheticSource:
    """Exact generation observations and controllable duplicate or missing hints."""

    def __init__(self, clock: SyntheticClock) -> None:
        """Retain source identity separately from callbacks and fault injection."""
        self.clock = clock
        self.observations: dict[SourceIdentity, Observation] = {}
        self.callbacks: dict[SourceIdentity, Callable[[], None]] = {}
        self.error: OSError | WaitError | None = None
        self.subscribe_error: OSError | None = None
        self.on_subscribe: Callable[[SourceIdentity], None] | None = None
        self.on_read: Callable[[SourceIdentity], None] | None = None
        self.subscriptions = 0
        self.reads = 0
        self.trace: list[str] = []

    def subscribe(self, source: SourceIdentity, dirty: Callable[[], None]) -> Callable[[], None]:
        """Install the hint before injecting completion during observer startup."""
        self.trace.append("subscribe")
        if self.subscribe_error is not None:
            raise self.subscribe_error
        self.callbacks[source] = dirty
        self.subscriptions += 1
        if self.on_subscribe is not None:
            self.on_subscribe(source)

        def unsubscribe() -> None:
            self.callbacks.pop(source, None)

        return unsubscribe

    def read(self, source: SourceIdentity) -> Observation:
        """Return authoritative fixture state, with explicit failure injection."""
        self.trace.append("read")
        self.reads += 1
        if self.on_read is not None:
            self.on_read(source)
        if self.error is not None:
            raise self.error
        return self.observations.get(source, Observation("pending", source.generation, self.clock.utc()))

    def ready(self, source: SourceIdentity, *, completed_utc: float | None = None, notify: bool = True) -> None:
        """Publish a typed result; its text is never an executable continuation."""
        self.observations[source] = Observation("ready", source.generation, self.clock.utc(), completed_utc, "synthetic-result", "digest", "fixture")
        if notify:
            self.notify(source)

    def notify(self, source: SourceIdentity) -> None:
        """Duplicate hints carry no result and cannot confer authority."""
        callback = self.callbacks.get(source)
        if callback is not None:
            callback()


class SyntheticHost:
    """Expose declared route capabilities without waking or consuming workflow work."""

    def __init__(self) -> None:
        """Keep failed arming, exact-recipient validation and busy turns controllable."""
        self.support = Capability.STRICT
        self.gate = NormalEnd.DIRECT
        self.valid = True
        self.ended = False
        self.error: WaitError | None = None
        self.arm_calls = 0

    def capability(self, recipient: Recipient) -> Capability:
        """Return the configured route class without inferring production support."""
        return self.support if recipient.host == "synthetic" else Capability.UNAVAILABLE

    def validate(self, recipient: Recipient) -> bool:
        """Return independently controlled exact-recipient evidence."""
        return self.valid and recipient.host == "synthetic"

    def arm(self, recipient: Recipient) -> HostBinding:
        """Supply a usable synthetic binding or a typed non-armed failure."""
        self.arm_calls += 1
        if self.error is not None:
            raise self.error
        return HostBinding(recipient, "synthetic-incarnation", self.support, self.gate, "v1", "fixture-armed")

    def normal_end(self, binding: HostBinding) -> bool:
        """Read the exact turn's completion without starting another session."""
        binding.validate()
        return self.ended

    def deliver(self, event: Event, binding: HostBinding) -> Delivery:
        """Record transport acceptance separately from later workflow consumption."""
        return Delivery(event.event_id, binding.incarnation, "accepted", 1, 0, None, "synthetic-receipt", "", binding.policy_version)

    def reconcile(self, delivery: Delivery) -> Delivery:
        """Preserve receipt and stable event identity on transport recovery."""
        return delivery

    def rearm(self, binding: HostBinding) -> HostBinding:
        """Only an explicit rearm changes the existing recipient's incarnation."""
        return replace(binding, incarnation="synthetic-rearmed")


# eof
