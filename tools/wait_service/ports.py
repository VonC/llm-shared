"""Provisional semantic ports, with source and host I/O outside transactions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.wait_service.models import (
        Capability,
        ConsumptionAttempt,
        Delivery,
        Event,
        HostBinding,
        Observation,
        Recipient,
        SourceIdentity,
    )


class SourcePort(Protocol):
    """Observe exact generations after subscribing to coalescible dirty hints."""

    def subscribe(self, source: SourceIdentity, dirty: Callable[[], None]) -> Callable[[], None]:
        """Return an unsubscribe callback; notifications confer no authority."""
        ...

    def read(self, source: SourceIdentity) -> Observation:
        """Read authoritative bounded evidence without holding a store lock."""
        ...


class HostPort(Protocol):
    """Verify exact recipients, arm routes and reconcile transport receipts."""

    def capability(self, recipient: Recipient) -> Capability:
        """Classify the exact installed host route and available evidence."""
        ...

    def validate(self, recipient: Recipient) -> bool:
        """Validate session and physical profile identity without inference."""
        ...

    def arm(self, recipient: Recipient) -> HostBinding:
        """Return verified incarnation, arming and normal-end gate evidence."""
        ...

    def normal_end(self, binding: HostBinding) -> bool:
        """Observe normal completion of the registering turn."""
        ...

    def deliver(self, event: Event, binding: HostBinding) -> Delivery:
        """Transmit typed fields with a stable event ID and fixed template."""
        ...

    def reconcile(self, delivery: Delivery) -> Delivery:
        """Recover transport acceptance without repeating useful work."""
        ...

    def rearm(self, binding: HostBinding) -> HostBinding:
        """Verify a new incarnation of the same exact recipient."""
        ...


class AuthorityPort(Protocol):
    """Workflow-owned authority, durable intent and receipt validation."""

    def prepare(self, event: Event, recipient: Recipient) -> ConsumptionAttempt:
        """Record intent under the workflow lock before contacting the service."""
        ...

    def validate(self, attempt: ConsumptionAttempt) -> bool:
        """Validate current authority and required authoritative result details."""
        ...

    def reconcile(self, attempt: ConsumptionAttempt) -> ConsumptionAttempt:
        """Reconcile workflow receipts, settlement and human abandonment."""
        ...


class ClockPort(Protocol):
    """Separate durable UTC evidence from process-local scheduling time."""

    def utc(self) -> float:
        """Return current UTC as Unix seconds."""
        ...

    def monotonic(self) -> float:
        """Return scheduling time that must never be persisted as a deadline."""
        ...


class IOPort(Protocol):
    """Bound blocking work independently from the number of registrations."""

    def submit(self, operation: Callable[[], None]) -> bool:
        """Admit ordinary work only when a bounded worker is available."""
        ...


# eof
