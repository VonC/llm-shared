"""Prepare exact waits and acknowledge arming only after durable route evidence.

The caller receives preparing while ordinary I/O is pending. Repeating the exact
intent observes its committed acknowledgement or retries failed route arming.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.wait_service.models import (
    Capability,
    HostBinding,
    WaitError,
)

if TYPE_CHECKING:
    from tools.wait_service.models import Recipient, Registration, WaitIntent
    from tools.wait_service.monitoring import SourceMonitor
    from tools.wait_service.ports import HostPort
    from tools.wait_service.store import WaitStore
    from tools.wait_service.work import WorkResult


class RegistrationService:
    """An independently authenticated role registers only its own exact recipient."""

    def __init__(self, store: WaitStore, monitor: SourceMonitor, host: HostPort, registrant: Recipient, role: str) -> None:
        """Receive verified caller context from the local authenticated boundary."""
        self.store, self.monitor, self.host = store, monitor, host
        self.registrant, self.role = registrant, role

    def register(self, intent: WaitIntent) -> Registration:
        """Persist one preparation; source sharing never grants counterpart authority."""
        intent.validate()
        if intent.recipient != self.registrant or intent.role != self.role or intent.provenance != "same-session":
            code = "registration-authority"
            raise WaitError(code, "recipient, role or provenance differs")
        policy = self.monitor.policy(intent.source)
        registration = self.store.register(intent, self.monitor.clock.utc())
        self.monitor.attach(registration, lambda: self._schedule_arm(registration, policy.observation_seconds))
        return registration

    def _schedule_arm(self, registration: Registration, budget: float) -> None:
        if registration.state == "preparing":
            self.monitor.work.submit(
                f"arm:{registration.wait_id}",
                lambda: self._arm(registration.intent),
                lambda result: self._armed(registration, result),
                budget,
            )

    def _arm(self, intent: WaitIntent) -> HostBinding:
        if not self.host.validate(intent.recipient):
            code = "recipient-unavailable"
            raise WaitError(code)
        capability = self.host.capability(intent.recipient)
        if capability not in {Capability.STRICT, Capability.FUNCTIONAL, Capability.RETAINED}:
            code = "route-unavailable"
            raise WaitError(code, capability.value)
        binding = self.host.arm(intent.recipient)
        binding.validate()
        if binding.recipient != intent.recipient or binding.capability != capability:
            code = "route-identity-mismatch"
            raise WaitError(code)
        return binding

    def _armed(self, registration: Registration, result: WorkResult) -> None:
        if isinstance(result.value, HostBinding):
            self.store.arm(registration.wait_id, result.value)
        else:
            code = result.value.code if isinstance(result.value, WaitError) else "invalid-host-result"
            self.store.preparation_failed(registration.wait_id, code)


# eof
