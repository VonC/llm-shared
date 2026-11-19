r"""Read-only, agent-callable validation of one marked resume receiver.

Step 4 of v0.14.0 resume-paused gives both receiving workflows, resume-session
and review-resume, one validator to call immediately before each protected
write: receipt replacement, session journal write, backfill and ownership
claim (design Q11, Q13). It is separate from the human-only bulk command and
never consumes, prepares or migrates an artifact home, claims a role or
returns a capability. For one complete typed command it:

1. parses the single marker strictly;
2. reads the checkout's saved pause and requires resolved routing;
3. observes the saved exchange and takes its live round and occurrence;
4. rebuilds the assignment and requires the marker binding and receiver host;
5. checks the consumption stage: an unconsumed prompt or one consumed by this
   launch's schema 3 receipt, or for a reviewer the requestor's receipt;
6. proves the receiving pane from live discovery (full UUID, TUIOS session,
   checkout and host), never from an inherited ``TUIOS_PANE_ID``;
7. proves the marked command as the pane's latest complete typed input, at or
   after the pause snapshot, through the pinned host profile (Q14, Q15).

The result is typed non-secret JSON: validity, reason codes, launch id, pane,
role, host, consumption, live exchange, the Codex session identity to carry
into later calls, the compact failure line and the bytes read. Nothing is
cached between calls. ``main`` is the ``bin\resume_paused_validate.bat`` entry:
exit 0 when valid, 3 when refused, 2 on invalid arguments or an unexpected
failure.
"""

# ruff: noqa: EM101, EM102

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Final, NoReturn, Protocol, TextIO

from tools.resume_paused_artifacts import (
    PromptState,
    RoutingState,
    read_checkout_snapshot,
)
from tools.resume_paused_claim import consumed_by, requestor_consumed
from tools.resume_paused_claude import DirectoryTranscriptSource
from tools.resume_paused_codex import DirectorySessionStore
from tools.resume_paused_input import (
    CarriedIdentity,
    ClaudeInputProver,
    CodexInputProver,
    SubprocessRunner,
    TuiosDiscovery,
    UnpinnedCodexVersions,
    pane_host,
)
from tools.resume_paused_marker import (
    Assignment,
    LiveExchange,
    Marker,
    ResultLine,
    marker_in_command,
    resolve_assignment,
)
from tools.resume_paused_models import (
    ArtifactError,
    CanonicalRoot,
    SessionRole,
    timestamp_instant,
)
from tools.resume_paused_profiles import SUPPORTED_PROFILES, Host, ReadAccount
from tools.resume_paused_review import ExchangeObservationKind, observe_saved_exchange
from tools.resume_paused_routing import SavedExchange
from tools.resume_paused_windows import Win32Api
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_paths import load_review_configuration

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from tools.resume_paused_artifacts import CheckoutSnapshot, PromptMetadata
    from tools.resume_paused_input import InputProver, PaneDiscovery, PaneRecord
    from tools.resume_paused_routing import SavedRouting

OPERATION: Final = "resume-paused-validate"
_UNCONSUMED: Final = frozenset({PromptState.UNUSED, PromptState.NEW_SINCE_USE})
_CODEX_RESOLUTION_NS: Final = 100


@dataclass(frozen=True)
class ValidationRequest:
    """One receiver's checkout, complete typed command, own host and carried identity."""

    project_root: Path
    command: str
    host: Host
    carried: CarriedIdentity | None = None


@dataclass
class _Progress:
    """What one validation established so far, reported even when it stops."""

    marker: Marker | None = None
    consumed: bool = False
    live: LiveExchange | None = None
    carried_session: str | None = None
    account: ReadAccount = field(default_factory=ReadAccount)

    def charge(self, account: ReadAccount) -> None:
        """Add one evidence read account."""
        self.account = ReadAccount(self.account.files + account.files, self.account.bytes_read + account.bytes_read)


@dataclass(frozen=True)
class ValidationResult:
    """Typed non-secret outcome of one validation."""

    valid: bool
    reasons: tuple[str, ...]
    host: Host
    marker: Marker | None
    consumed: bool
    live: LiveExchange | None
    carried_session: str | None
    account: ReadAccount

    def to_json(self) -> dict[str, object]:
        """Return the JSON object the launcher prints; it holds no token, digest or content."""
        marker = self.marker
        carried = None
        if self.carried_session is not None and marker is not None:
            carried = {"session_id": self.carried_session, "launch_id": marker.launch_id}
        result = None if self.valid or marker is None else ResultLine(marker.launch_id, "failed").render()
        return {
            "operation": OPERATION,
            "valid": self.valid,
            "reasons": list(self.reasons),
            "host": self.host.value,
            "launch_id": None if marker is None else marker.launch_id,
            "pane_id": None if marker is None else marker.pane_id,
            "role": None if marker is None else marker.role.value,
            "consumed": self.consumed,
            "exchange": None if self.live is None else {"round": self.live.round_number, "occurrence": self.live.occurrence},
            "carried": carried,
            "result": result,
            "read": {"files": self.account.files, "bytes": self.account.bytes_read},
        }


def _routing(snapshot: CheckoutSnapshot) -> tuple[PromptMetadata, SavedRouting]:
    """Return a readable prompt and its resolved saved routing, or refuse."""
    if snapshot.state is PromptState.ERROR:
        raise ArtifactError("checkout-unreadable")
    prompt, reading = snapshot.prompt, snapshot.routing
    if prompt is None or reading is None:
        raise ArtifactError("prompt-unavailable")
    if reading.state is not RoutingState.RESOLVED or reading.routing is None:
        raise ArtifactError(f"routing-{reading.state.value}")
    return prompt, reading.routing


def _stage(snapshot: CheckoutSnapshot, marker: Marker, assignment: Assignment) -> bool:
    """Return whether this launch already consumed the prompt; refuse any other consumption."""
    if marker.role is SessionRole.REVIEWER and assignment.pair is not None:
        if not requestor_consumed(snapshot, assignment):
            raise ArtifactError("requestor-receipt-missing")
        return False
    if consumed_by(snapshot, marker):
        return True
    if snapshot.state in _UNCONSUMED:
        return False
    raise ArtifactError("prompt-already-used")


class Validator(Protocol):
    """Anything that validates one receiver request, as ``main`` needs it."""

    def validate(self, request: ValidationRequest) -> ValidationResult:
        """Return the validation result of one request."""
        ...


class BuildReader(Protocol):
    """The one Windows observation the default composition needs: the OS build."""

    def os_build(self) -> int | None:
        """Return the OS build number, or ``None`` when it cannot be read."""
        ...


class ReceiverValidator:
    """Validate one marked receiver from fresh evidence on every call."""

    def __init__(
        self, discovery: PaneDiscovery, provers: Mapping[Host, InputProver], wall_clock: Callable[[], datetime],
    ) -> None:
        """Keep the live discovery, the host input provers and the clock."""
        self.discovery = discovery
        self.provers = provers
        self._wall_clock = wall_clock

    def validate(self, request: ValidationRequest) -> ValidationResult:
        """Return a valid result, or the first reason the receiver must stop before its write."""
        progress = _Progress()
        try:
            self._validate(request, progress)
        except ArtifactError as error:
            return self._result(request, progress, (str(error),))
        return self._result(request, progress, ())

    @staticmethod
    def _result(request: ValidationRequest, progress: _Progress, reasons: tuple[str, ...]) -> ValidationResult:
        """Assemble the result from what the validation established."""
        return ValidationResult(
            not reasons, reasons, request.host, progress.marker, progress.consumed,
            progress.live, progress.carried_session if not reasons else None, progress.account,
        )

    def _validate(self, request: ValidationRequest, progress: _Progress) -> None:
        """Run every check in order; the first refusal raises its reason."""
        marker = progress.marker = marker_in_command(request.command)
        carried = request.carried
        if carried is not None and carried.launch_id != marker.launch_id:
            raise ArtifactError("carried-launch-id-mismatch")
        snapshot = read_checkout_snapshot(request.project_root)
        progress.charge(snapshot.account)
        prompt, routing = _routing(snapshot)
        progress.live = self._live(request.project_root, routing, progress)
        assignment = resolve_assignment(routing, prompt.digest, marker.pane_id, marker.role, progress.live)
        if assignment.digest() != marker.binding:
            raise ArtifactError("binding-mismatch")
        if assignment.receiver.host is not request.host:
            raise ArtifactError("host-mismatch")
        progress.consumed = _stage(snapshot, marker, assignment)
        pane = self._pane(assignment, routing.pause.checkout, request.host)
        prover = self.provers.get(request.host)
        if prover is None:
            raise ArtifactError("host-profile-unsupported")
        evidence = prover.prove(pane, request.command, timestamp_instant(prompt.snapshot), carried)
        progress.charge(evidence.account)
        if not evidence.proved:
            raise ArtifactError(evidence.reasons[0] if evidence.reasons else "input-unproved")
        progress.carried_session = evidence.session_id

    def _live(self, root: Path, routing: SavedRouting, progress: _Progress) -> LiveExchange | None:
        """Observe the saved exchange read-only and return its live occurrence and round."""
        exchange = routing.exchange
        if not isinstance(exchange, SavedExchange):
            return None
        try:
            configuration = ReviewArtifactConfiguration.load(root)
            review = load_review_configuration(root, configuration=configuration)
        except (OSError, ReviewExchangeError) as error:
            raise ArtifactError("exchange-unreadable") from error
        observed = observe_saved_exchange(configuration, review, exchange, self._wall_clock)
        progress.charge(observed.account)
        if observed.kind is not ExchangeObservationKind.OBSERVED or observed.occurrence is None or observed.round_number is None:
            raise ArtifactError(f"exchange-{observed.kind.value}")
        return LiveExchange(observed.occurrence, observed.round_number)

    def _pane(self, assignment: Assignment, checkout: CanonicalRoot, host: Host) -> PaneRecord:
        """Find the receiving pane in live discovery and check its session, checkout and host."""
        agents = self.discovery.agents()
        if agents is None:
            raise ArtifactError("discovery-failed")
        matches = [agent for agent in agents if agent.pane_id == assignment.receiver.pane_id]
        if len(matches) != 1:
            raise ArtifactError("pane-ambiguous" if matches else "pane-absent")
        pane = matches[0]
        if pane.session != assignment.receiver.session:
            raise ArtifactError("session-mismatch")
        try:
            same_checkout = CanonicalRoot.parse(pane.cwd, "pane checkout") == checkout
        except ArtifactError:
            same_checkout = False
        if not same_checkout:
            raise ArtifactError("checkout-mismatch")
        if pane_host(pane) is not host:
            raise ArtifactError("pane-host-mismatch")
        return pane


def _read_file(path: str) -> bytes | None:
    """Read one host evidence file completely, or ``None`` when unreadable."""
    try:
        return Path(path).read_bytes()
    except OSError:
        return None


def default_validator(
    environ: Mapping[str, str], wall_clock: Callable[[], datetime], *, api_factory: Callable[[], BuildReader] = Win32Api,
) -> ReceiverValidator:
    """Compose the validator over TUIOS, the user's host evidence folders and the pinned registry."""
    home = Path(environ.get("USERPROFILE", ""))
    discovery = TuiosDiscovery(SubprocessRunner())

    def os_build() -> int | None:
        """Read the OS build only when a Claude proof reaches profile selection."""
        return api_factory().os_build()

    claude = ClaudeInputProver(DirectoryTranscriptSource(str(home / ".claude" / "projects"), _read_file), SUPPORTED_PROFILES, os_build)
    codex = CodexInputProver(
        DirectorySessionStore(str(home / ".codex" / "sessions"), _read_file), discovery, UnpinnedCodexVersions(), _CODEX_RESOLUTION_NS,
    )
    return ReceiverValidator(discovery, {Host.CLAUDE: claude, Host.CODEX: codex}, wall_clock)


class _ArgumentParser(argparse.ArgumentParser):
    """Raise usage errors so ``main`` can still print one JSON object."""

    def error(self, message: str) -> NoReturn:
        """Convert an argparse diagnostic into a typed failure."""
        raise ArtifactError(message)


def _parser() -> argparse.ArgumentParser:
    """Build the validator's argument grammar."""
    parser = _ArgumentParser(prog="resume_paused_validate", add_help=False)
    parser.add_argument("--command", required=True)
    parser.add_argument("--host", choices=[host.value for host in Host], required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--carried-session")
    parser.add_argument("--carried-launch-id")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    factory: Callable[[], Validator] | None = None,
) -> int:
    """Validate one receiver and print one JSON object: exit 0 valid, 3 refused, 2 invalid input."""
    out = stdout or sys.stdout
    try:
        args = _parser().parse_args(list(sys.argv[1:] if argv is None else argv))
        session, launch = args.carried_session, args.carried_launch_id
        carried = None if session is None and launch is None else CarriedIdentity(session or "", launch or "")
        request = ValidationRequest(Path(args.project_root).absolute(), args.command, Host(args.host), carried)
        validator = factory() if factory is not None else default_validator(os.environ, _now)
        result = validator.validate(request)
        payload, code = result.to_json(), 0 if result.valid else 3
    except Exception as error:  # noqa: BLE001 - every failure still prints one JSON object
        payload, code = {"operation": OPERATION, "valid": False, "reasons": ["invalid-input"], "diagnostic": str(error)}, 2
    out.write(f"{json.dumps(payload, ensure_ascii=True, sort_keys=True)}\n")
    return code


def _now() -> datetime:
    """Return the current timezone-aware instant."""
    return datetime.now(UTC)


__all__ = [
    "OPERATION",
    "BuildReader",
    "ReceiverValidator",
    "ValidationRequest",
    "ValidationResult",
    "Validator",
    "default_validator",
    "main",
]


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
