"""The recoverable version transition behind `versions set` and item 5.

Step 4 of v0.14.0 version-sources. A standalone call first plans without any
side effect, so a well-formed target that fails source validation (status 2)
leaves no artifact home, lock record or evidence. It then prepares the
artifact home and takes the operation lock (a held lock: status 1). Under the
lock it removes completed standalone residue with a warning and stops, with
status 2, on interrupted, unreadable or another transaction's evidence, even
when nothing would change. It plans again in a fresh view; only this plan is
authoritative, and an empty one reports `unchanged`. Otherwise it writes
recovery evidence (a failure there: status 1, no source written), compares
each file with its captured original just before replacing it, replaces the
files in path order with `version.txt` last, verifies every source in a fresh
view and durably marks the evidence `complete`. Before that marker any failure
restores the replaced files and verifies them: status 1 when every file is
back, status 3 with each unrestored source and its retained copy otherwise.
After it, a failed cleanup or lock release keeps the new versions and only
adds a diagnostic. The outcome is fixed before cleanup and release run, except
that an `unchanged` run whose lock release fails stops with status 1: its lock
record remains, so it cannot report success (code review, step 4 round 1).

A lifecycle caller (design decision Q07) supplies its held lock and its
transaction identity: the lock is verified before any read and is neither
acquired nor released, the evidence is owned by the transaction and kept
`complete`, and a restore handle reapplies the same restoration later. Every
side effect goes through the injected `TransitionPorts` (plan decision Q07),
which also opens each phase's file view.
"""

from __future__ import annotations

import contextlib
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

from tools.release_workflow.artifacts import prepare_artifacts
from tools.release_workflow.managed_files import (
    ManagedWriteError,
    authorize_write,
    replace_bytes,
)
from tools.release_workflow.operation_lock import OperationLock, OperationLockError
from tools.release_workflow.sources import anchor
from tools.release_workflow.sources.detection import detect, plan_edits
from tools.release_workflow.sources.model import FileView, Plan, SourceError
from tools.release_workflow.version_evidence import (
    STANDALONE,
    EvidenceError,
    EvidenceKind,
    EvidenceManifest,
    EvidenceState,
    allocate,
    evidence_files,
    find_evidence,
    remove_managed,
    write_evidence,
)
from tools.release_workflow.windows_process import process_state

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from tools.release_workflow.artifacts import PreparedArtifacts
    from tools.release_workflow.managed_files import ManagedTarget
    from tools.release_workflow.sources.model import (
        FileCapture,
        FileEdit,
        SourceChange,
        VersionInputs,
        VersionToken,
    )
    from tools.release_workflow.version_evidence import EvidenceDirectory
    from tools.release_workflow.windows_process import ProcessIdentity, ProcessState


class TransitionOutcome(StrEnum):
    """The five results a transition reports, each with its public status."""

    APPLIED = "applied"
    UNCHANGED = "unchanged"
    RESTORED = "restored"
    RESTORATION_INCOMPLETE = "restoration incomplete"
    APPLIED_CLEANUP_FAILED = "applied with cleanup failed"

    @property
    def status(self) -> int:
        """Return 0 for applied or unchanged, 3 for an incomplete restoration, 1 otherwise."""
        return _STATUSES[self]


_STATUSES = {
    TransitionOutcome.APPLIED: 0, TransitionOutcome.UNCHANGED: 0, TransitionOutcome.RESTORED: 1,
    TransitionOutcome.RESTORATION_INCOMPLETE: 3, TransitionOutcome.APPLIED_CLEANUP_FAILED: 1,
}
_APPLIED = frozenset({TransitionOutcome.APPLIED, TransitionOutcome.APPLIED_CLEANUP_FAILED})


class TransitionError(ValueError):
    """A transition that stops before writing a source, with its public status."""

    def __init__(self, message: str, *, exit_code: int) -> None:
        """Keep the status for the handler that renders the failure."""
        self.exit_code = exit_code
        super().__init__(message)


class TransitionLock(Protocol):
    """The operation lock as a standalone transition uses it."""

    def acquire(self) -> TransitionLock:
        """Take the lock or fail with `OperationLockError`."""
        ...

    def release(self) -> None:
        """Release the lock or fail with `OperationLockError`."""
        ...


class LockFactory(Protocol):
    """Build a lock for prepared artifacts with an explicit process probe."""

    def __call__(self, artifacts: PreparedArtifacts, *, probe: Callable[[ProcessIdentity], ProcessState]) -> TransitionLock:
        """Return an unacquired lock."""
        ...


def _local_now() -> datetime:
    """Return the local time with its offset."""
    return datetime.now(UTC).astimezone()


@dataclass(frozen=True)
class TransitionPorts:
    """Every side effect of a transition, with its production default."""

    replace: Callable[[ManagedTarget, bytes], None] = replace_bytes
    remove: Callable[[ManagedTarget], None] = remove_managed
    lock_factory: LockFactory = OperationLock
    probe: Callable[[ProcessIdentity], ProcessState] = process_state
    clock: Callable[[], datetime] = _local_now
    pid: Callable[[], int] = os.getpid
    view: Callable[[], FileView] = FileView


DEFAULT_PORTS = TransitionPorts()


@dataclass(frozen=True)
class LifecycleOwnership:
    """The held operation lock and transaction identity a lifecycle caller supplies."""

    lock: OperationLock
    transaction: str


@dataclass(frozen=True)
class _Context:
    """What every phase of one call needs."""

    inputs: VersionInputs
    target: VersionToken
    owner: str
    ports: TransitionPorts

    @property
    def standalone(self) -> bool:
        """Tell whether this call owns its lock and its evidence."""
        return self.owner == STANDALONE


@dataclass(frozen=True)
class _Replaced:
    """A replaced file and the original bytes it held just before."""

    edit: FileEdit
    original: bytes


@dataclass(frozen=True)
class RestoreHandle:
    """Item 5's later restoration of a lifecycle transition, with the same routine."""

    context: _Context
    evidence: EvidenceDirectory
    replaced: tuple[_Replaced, ...]

    def restore(self) -> TransitionResult:
        """Restore every replaced source and verify it; the evidence stays for item 5."""
        return _restore(self.context, self.evidence, self.replaced, ())

    def discard(self) -> None:
        """Delete the transaction's evidence once item 5 no longer needs it."""
        self.evidence.delete(self.context.ports.remove)


@dataclass(frozen=True)
class TransitionResult:
    """The outcome, the changed fields, diagnostics and, for a lifecycle call, the restore handle."""

    outcome: TransitionOutcome
    changes: tuple[SourceChange, ...] = ()
    diagnostics: tuple[str, ...] = ()
    restore: RestoreHandle | None = None

    @property
    def status(self) -> int:
        """Return the public status of the outcome."""
        return self.outcome.status


def plan_transition(inputs: VersionInputs, target: VersionToken, view: FileView | None = None) -> Plan:
    """Detect every participating source and plan the edits, without any side effect."""
    inventory = detect(inputs, FileView() if view is None else view)
    return Plan(target, inventory, plan_edits(inventory, target))


def set_versions(inputs: VersionInputs, target: VersionToken, *, lifecycle: LifecycleOwnership | None = None,
                 ports: TransitionPorts = DEFAULT_PORTS) -> TransitionResult:
    """Run one transition, standalone under its own lock or inside a lifecycle caller's lock."""
    if lifecycle is not None:
        context = _Context(inputs, target, _transaction(lifecycle), ports)
        try:
            prepared = lifecycle.lock.verify_held(inputs.artifacts)
        except OperationLockError as exc:
            msg = f"the lifecycle lock cannot be used for this project: {exc}"
            raise TransitionError(msg, exit_code=1) from exc
        return _transition(context, prepared)
    plan_transition(inputs, target, ports.view())
    prepared = prepare_artifacts(inputs.artifacts, inputs.git)
    try:
        lock = ports.lock_factory(prepared, probe=ports.probe).acquire()
    except OperationLockError as exc:
        msg = f"another operation holds this project: {exc}"
        raise TransitionError(msg, exit_code=1) from exc
    try:
        result = _transition(_Context(inputs, target, STANDALONE, ports), prepared)
    except BaseException:
        with contextlib.suppress(OperationLockError):
            lock.release()
        raise
    try:
        lock.release()
    except OperationLockError as exc:
        problem = f"releasing the operation lock failed and its record remains until this process ends: {exc}"
        if result.outcome is TransitionOutcome.UNCHANGED:
            msg = f"no source changed; {problem}"
            raise TransitionError(msg, exit_code=1) from exc
        return _secondary(result, problem)
    return result


def _transaction(lifecycle: LifecycleOwnership) -> str:
    """Require a transaction identity distinct from standalone evidence."""
    if not lifecycle.transaction or lifecycle.transaction == STANDALONE:
        msg = f"a lifecycle transaction needs its own identity, not {lifecycle.transaction!r}"
        raise TransitionError(msg, exit_code=2)
    return lifecycle.transaction


def _secondary(result: TransitionResult, problem: str) -> TransitionResult:
    """Add a cleanup or release failure; applied versions stay applied, with status 1."""
    if result.outcome in _APPLIED:
        diagnostic = f"the new versions are applied; {problem}"
        return TransitionResult(TransitionOutcome.APPLIED_CLEANUP_FAILED, result.changes, (*result.diagnostics, diagnostic), result.restore)
    return TransitionResult(result.outcome, result.changes, (*result.diagnostics, problem), result.restore)


def _transition(context: _Context, prepared: PreparedArtifacts) -> TransitionResult:
    """Check evidence, plan under the lock, then write evidence and apply the edits."""
    warnings = _check_evidence(context)
    plan = plan_transition(context.inputs, context.target, context.ports.view())
    if not plan.edits:
        return TransitionResult(TransitionOutcome.UNCHANGED, (), warnings)
    now = context.ports.clock()
    directory = allocate(prepared, now, context.ports.pid())
    captures: Sequence[FileCapture] = plan.inventory.captures
    manifest = EvidenceManifest.of(context.owner, str(context.target), now, evidence_files(context.inputs.project.root, captures))
    evidence = write_evidence(directory, manifest, captures, replace=context.ports.replace, remove=context.ports.remove)
    return _apply(context, plan, evidence, warnings)


def _check_evidence(context: _Context) -> tuple[str, ...]:
    """Remove completed standalone residue; stop on any evidence this call does not own."""
    warnings: list[str] = []
    for entry in find_evidence(context.inputs.artifacts):
        kind = entry.kind
        if kind is EvidenceKind.RESIDUE:
            entry.delete(context.inputs.project, context.ports.remove)
            warnings.append(f"removed {kind} {entry.path}")
        elif not (kind is EvidenceKind.LIFECYCLE and entry.owner == context.owner):
            recorded = "" if entry.manifest is None else f" (owner {entry.owner}, state {entry.manifest.state})"
            msg = (f"{entry.path}: {kind} version-transition evidence{recorded} stops this transition; "
                   "inspect it, restore what is needed and remove it")
            raise TransitionError(msg, exit_code=2)
    return tuple(warnings)


def _ordered(edits: Sequence[FileEdit]) -> list[FileEdit]:
    """Order the files by path, the anchor last, so it changes after every other source."""
    return sorted(edits, key=lambda edit: (any(change.adapter == anchor.ADAPTER.name for change in edit.changes), str(edit.capture.path)))


def _write(context: _Context, edits: Sequence[FileEdit], replaced: list[_Replaced]) -> None:
    """Replace each file after checking that it still holds its captured bytes."""
    view = context.ports.view()
    for edit in edits:
        path = edit.capture.path
        current = view.read(path)
        if current is None or current != edit.capture.original:
            msg = f"{path} changed since it was captured; it keeps the other writer's content"
            raise SourceError(msg)
        try:
            context.ports.replace(authorize_write(context.inputs.project, path), edit.new)
        except (ManagedWriteError, OSError) as exc:
            msg = f"writing {path} failed: {exc}"
            raise ManagedWriteError(msg) from exc
        replaced.append(_Replaced(edit, current))


def _verify(context: _Context) -> None:
    """Read every participating source in a fresh view; each must hold its expected value."""
    for source in detect(context.inputs, context.ports.view()).sources:
        expected = source.form.expected(context.target)
        if source.value != expected:
            msg = f"verification failed: {source.path} {source.field} holds {source.value}, expected {expected}"
            raise SourceError(msg)


def _apply(context: _Context, plan: Plan, evidence: EvidenceDirectory, warnings: tuple[str, ...]) -> TransitionResult:
    """Write, verify and mark complete; restore on any failure before that marker."""
    edits = _ordered(plan.edits)
    replaced: list[_Replaced] = []
    try:
        _write(context, edits, replaced)
        _verify(context)
        evidence = evidence.mark(EvidenceState.COMPLETE, context.ports.replace)
    except (SourceError, ManagedWriteError, OSError, EvidenceError) as exc:
        return _restore(context, evidence, tuple(replaced), (*warnings, str(exc)))
    changes = tuple(change for edit in edits for change in edit.changes)
    if not context.standalone:
        return TransitionResult(TransitionOutcome.APPLIED, changes, warnings, RestoreHandle(context, evidence, tuple(replaced)))
    applied = TransitionResult(TransitionOutcome.APPLIED, changes, warnings)
    try:
        evidence.delete(context.ports.remove)
    except EvidenceError as exc:
        return _secondary(applied, f"cleanup failed: {exc}")
    return applied


def _holds(view: FileView, path: Path, content: bytes) -> bool:
    """Tell whether a file reads back as the given bytes; an unreadable file does not."""
    try:
        return view.read(path) == content
    except OSError:
        return False


def _restore(context: _Context, evidence: EvidenceDirectory, replaced: tuple[_Replaced, ...], diagnostics: tuple[str, ...]) -> TransitionResult:
    """Write back every replaced file, verify it, then delete or keep the evidence."""
    project, ports = context.inputs.project, context.ports
    for item in reversed(replaced):
        with contextlib.suppress(ManagedWriteError, OSError):
            ports.replace(authorize_write(project, item.edit.capture.path), item.original)
    view = ports.view()
    unrestored = [item.edit.capture.path for item in replaced if not _holds(view, item.edit.capture.path, item.original)]
    if not unrestored:
        restored = TransitionResult(TransitionOutcome.RESTORED, (), (
            *diagnostics, f"every replaced source was restored and verified ({len(replaced)} files); no version changed"))
        if not context.standalone:
            return restored
        try:
            evidence.delete(ports.remove)
        except EvidenceError as exc:
            return _secondary(restored, f"the restored evidence {evidence.path} could not be deleted: {exc}; inspect it and remove it")
        return restored
    details = tuple(f"{path} was not restored; its original is retained at {evidence.copy_path(path.relative_to(project.root).as_posix())}"
                    for path in unrestored)
    incomplete = TransitionResult(TransitionOutcome.RESTORATION_INCOMPLETE, (), (*diagnostics, *details))
    try:
        evidence.mark(EvidenceState.RESTORATION_INCOMPLETE, ports.replace)
    except EvidenceError as exc:
        return _secondary(incomplete, f"the evidence manifest still says writing: {exc}")
    return incomplete


# eof
