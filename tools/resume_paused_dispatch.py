"""Durable dispatch reservations shared by the human launcher and marked receivers."""

# ruff: noqa: EM101

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.resume_paused_artifacts import PromptState, read_checkout_snapshot
from tools.resume_paused_delivery_model import Phase
from tools.resume_paused_evidence import ObservedCommand
from tools.resume_paused_marker import (
    LiveExchange,
    marker_in_command,
    resolve_assignment,
)
from tools.resume_paused_models import ArtifactError
from tools.resume_paused_plan_model import ActionKind
from tools.resume_paused_profiles import as_mapping, loads_strict
from tools.resume_paused_takeover_proof import (
    Durable,
    ProofState,
    consumption,
    read_exchange,
    takeover,
)
from tools.resume_paused_terminal import COMMANDS
from tools.review_exchange_models import Actor

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.resume_paused_artifacts import CheckoutSnapshot
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_marker import Marker
    from tools.resume_paused_models import PromptDigest
    from tools.resume_paused_plan_model import PlannedAction
    from tools.resume_paused_planner import ExchangeObserver
    from tools.resume_paused_profiles import Host
    from tools.resume_paused_review import ExchangeSnapshot


def _path(snapshot: CheckoutSnapshot, phase: Phase) -> Path:
    """Restrict names to the validated artifact home, prompt digest and operation."""
    if snapshot.state is PromptState.ERROR or snapshot.prompt is None or snapshot.home is None:
        raise ArtifactError("dispatch-checkout-unreadable")
    return snapshot.home / f"a.resume-paused.{snapshot.prompt.digest.value}.{phase.value}.local.json"


@dataclass(frozen=True)
class Dispatch:
    """One exact command and the ownership generation immediately preceding it."""

    command: str
    generation: int | None

    def save(self, path: Path) -> None:
        """Reserve before input, preserving even an interrupted write as a retry fence."""
        try:
            with path.open("x", encoding="utf-8") as stream:
                json.dump({"command": self.command, "generation": self.generation}, stream)
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError as error:
            raise ArtifactError("dispatch-already-reserved") from error
        except OSError as error:
            raise ArtifactError("dispatch-write-failed") from error


def _parse_dispatch(text: str) -> Dispatch:
    """Reject partial writes, duplicate keys, malformed markers and invalid generations."""
    raw = as_mapping(loads_strict(text))
    command, generation = raw.get("command"), raw.get("generation")
    if set(raw) != {"command", "generation"} or not isinstance(command, str):
        raise ArtifactError("dispatch-unreadable")
    if generation is not None and (type(generation) is not int or generation < 0):
        raise ArtifactError("dispatch-unreadable")
    marker_in_command(command)
    return Dispatch(command, generation)


def read_dispatch(snapshot: CheckoutSnapshot, phase: Phase) -> Dispatch | None:
    """A missing record is distinct from an unreadable or incomplete reservation."""
    try:
        return _parse_dispatch(_path(snapshot, phase).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError, RecursionError) as error:
        raise ArtifactError("dispatch-unreadable") from error


def command_phase(command: str, host: Host) -> Phase:
    """Distinguish consumption of the saved prompt from counterpart activation."""
    return Phase.REVIEWER if command.split(maxsplit=1)[0] == COMMANDS[host].reviewer else Phase.RESUME


def authorized(snapshot: CheckoutSnapshot, command: str, host: Host, environ: Mapping[str, str]) -> Dispatch:
    """Require the receiving terminal identity and the exact non-preview command."""
    marker = marker_in_command(command)
    if environ.get("TUIOS_PANE_ID", "").lower() != marker.pane_id:
        raise ArtifactError("receiver-pane-mismatch")
    dispatch = read_dispatch(snapshot, command_phase(command, host))
    if dispatch is None or dispatch.command != command:
        raise ArtifactError("dispatch-mismatch")
    return dispatch


@dataclass(frozen=True)
class DispatchHistory:
    """Read only this pause's shared reservations. An interrupted send suppresses a second launch."""

    own_command: str | None = None

    def commands(self, pane: PaneRecord) -> tuple[ObservedCommand, ...] | None:
        """Refresh the waiter's history for a reviewer decision."""
        return self.for_snapshot(read_checkout_snapshot(Path(pane.cwd))).entries

    def for_snapshot(self, snapshot: CheckoutSnapshot) -> _CheckoutHistory:
        """Read reservations once per checkout observation, including reservations for vanished panes."""
        try:
            records = [read_dispatch(snapshot, phase) for phase in (Phase.RESUME, Phase.CLEAR, Phase.REVIEWER)]
        except ArtifactError:
            return _CheckoutHistory(None)
        return _CheckoutHistory(tuple(ObservedCommand(record.command, None) for record in records if record is not None and record.command != self.own_command))


@dataclass(frozen=True)
class _CheckoutHistory:
    """Checkout-wide reservations scoped to a single fresh planning decision."""

    entries: tuple[ObservedCommand, ...] | None

    def commands(self, pane: PaneRecord) -> tuple[ObservedCommand, ...] | None:
        """Return checkout-wide evidence even when the original pane no longer exists."""
        del pane
        return self.entries


def _position(exchange: ExchangeSnapshot | None) -> tuple[LiveExchange | None, int | None]:
    """Identify the live round and generation of a paired pause."""
    if exchange is None:
        return None, None
    if exchange.round_number is None or exchange.occurrence is None or exchange.ownership_generation is None:
        raise ArtifactError("dispatch-exchange-unavailable")
    return LiveExchange(exchange.occurrence, exchange.round_number), exchange.ownership_generation


def _require_stage(durable: Durable, phase: Phase, pane_id: str, intended: PromptDigest | None) -> None:
    """Check consumption or takeover immediately before reserving input."""
    if phase is Phase.REVIEWER:
        proof = takeover(durable, intended=intended)
        if proof.state is not ProofState.PROVED or proof.counterpart != pane_id:
            raise ArtifactError("dispatch-takeover-changed")
    elif durable.snapshot.state not in {PromptState.UNUSED, PromptState.NEW_SINCE_USE}:
        raise ArtifactError("dispatch-prompt-consumed")


def _save(snapshot: CheckoutSnapshot, reservation: Dispatch, phase: Phase) -> None:
    """A clear and its following resume must belong to the same launch."""
    clear = read_dispatch(snapshot, Phase.CLEAR)
    if clear is not None and phase is Phase.RESUME and clear != reservation:
        raise ArtifactError("clear-already-reserved")
    if phase is Phase.CLEAR and read_dispatch(snapshot, Phase.RESUME) is not None:
        raise ArtifactError("dispatch-already-reserved")
    reservation.save(_path(snapshot, phase))


def _claimed(exchange: ExchangeSnapshot | None, marker: Marker, host: Host) -> bool:
    """Match the marked claim to the currently owned reviewer generation."""
    if not exchange or exchange.owner is not Actor.REVIEWER or not exchange.marked_claim:
        return False
    binding = exchange.marked_claim
    claim = binding.evidence
    return (
        binding.issued_generation, claim.host, claim.occurrence, claim.round_number,
        claim.launch_id, claim.pane_id, claim.assignment_binding,
    ) == (
        exchange.ownership_generation, host.value, exchange.occurrence, exchange.round_number,
        marker.launch_id, marker.pane_id, marker.binding,
    )


@dataclass(frozen=True)
class SharedDelivery:
    """Refresh exact assignment and ownership when reserving, then observe receipt or claim."""

    exchanges: ExchangeObserver

    def check(self, pane: PaneRecord, action: PlannedAction, phase: Phase, intended: PromptDigest | None, *, recovery: bool = False) -> None:
        """Reserve the first send or require its unchanged reservation for a recovery Enter."""
        snapshot = read_checkout_snapshot(Path(pane.cwd))
        prompt, routing = snapshot.prompt, snapshot.routing
        if not action.command or not prompt or prompt.digest != intended or not routing or not routing.routing:
            raise ArtifactError("dispatch-prompt-changed")
        marker = marker_in_command(action.command)
        durable = read_exchange(snapshot.root, snapshot, self.exchanges)
        live, generation = _position(durable.exchange)
        assignment = resolve_assignment(routing.routing, prompt.digest, pane.pane_id, action.role, live)
        if assignment.digest() != marker.binding:
            raise ArtifactError("dispatch-binding-changed")
        _require_stage(durable, phase, pane.pane_id, intended)
        reservation = Dispatch(action.command, generation)
        if recovery:
            if read_dispatch(snapshot, phase) != reservation:
                raise ArtifactError("dispatch-changed")
        else:
            _save(snapshot, reservation, phase)

    def accepted(self, pane: PaneRecord, action: PlannedAction, intended: PromptDigest | None) -> bool:
        """Observe consumption of this launch or its currently owned counterpart claim."""
        if action.command is None:
            return False
        marker = marker_in_command(action.command)
        snapshot = read_checkout_snapshot(Path(pane.cwd))
        if action.kind is ActionKind.RESUME:
            return consumption(Durable(snapshot), marker, action.host, intended).state is ProofState.PROVED
        if snapshot.state is not PromptState.USED or snapshot.prompt is None or snapshot.prompt.digest != intended:
            return False
        exchange = read_exchange(snapshot.root, snapshot, self.exchanges).exchange
        return _claimed(exchange, marker, action.host)


# eof
