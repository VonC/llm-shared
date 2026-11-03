"""Own one durable project operation through mutation, cleanup and handoffs.

Complete owner records are flushed before non-replacing Windows publication.
A short kernel mutex serializes every record transition, including stale-owner
recovery, so two recoverers cannot remove a newly published owner. Temporary
records never own the operation; unknown records and retained handoffs survive.
"""

from __future__ import annotations

import json
import os
import secrets
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from tools.release_workflow.managed_files import (
    ManagedWriteError,
    authorize_write,
    replace_bytes,
    temporary_bytes,
)
from tools.release_workflow.windows_process import (
    ProcessIdentity,
    ProcessState,
    current_identity,
    process_state,
    transition_mutex,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from tools.release_workflow.artifacts import PreparedArtifacts

_VERSION = 1
_NAME = "a.release-operation.lock"


class OperationLockError(ValueError):
    """A project operation cannot prove exclusive ownership or a safe transition."""


@dataclass(frozen=True)
class RetainedOwnership:
    """A private transfer capability, persisted only by the owning handoff domain.

    Item 5 must validate its handoff before using this capability. Possession
    permits exactly one transfer and is not a public recovery mechanism.
    """

    operation: str
    handoff: str
    secret: str


@dataclass(frozen=True)
class _Owner:
    """Strict version-one owner state; unknown shapes cannot prove abandonment."""

    process: ProcessIdentity
    operation: str
    handoff: str
    transfer_secret: str

    def encode(self) -> bytes:
        """Produce the complete record before creating any filesystem object."""
        return (json.dumps({
            "version": _VERSION, "pid": self.process.pid, "created": self.process.created,
            "operation": self.operation, "handoff": self.handoff, "transfer_secret": self.transfer_secret,
        }, ensure_ascii=True) + "\n").encode("utf-8")


def _unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous duplicate JSON owner fields instead of trusting the last."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            msg = f"Duplicate owner field: {key}"
            raise ValueError(msg)
        result[key] = value
    return result


def _record(content: bytes) -> dict[str, object]:
    """Decode an object without accepting arbitrary JSON values as lock records."""
    value: object = json.loads(content, object_pairs_hook=_unique_fields)
    if not isinstance(value, dict):
        msg = "Owner record is not an object"
        raise TypeError(msg)
    return cast("dict[str, object]", value)


def _integer(record: dict[str, object], key: str) -> int:
    """Accept positive integers, rejecting booleans and numeric strings."""
    value = record.get(key)
    if type(value) is not int or value <= 0:
        msg = f"Invalid owner {key}"
        raise ValueError(msg)
    return value


def _text(record: dict[str, object], key: str) -> str:
    """Require an explicitly present string even when an empty value is allowed."""
    value = record.get(key)
    if not isinstance(value, str):
        msg = f"Invalid owner {key}"
        raise TypeError(msg)
    return value


def _owner(record: dict[str, object]) -> _Owner:
    """Validate all fields, including retained-state consistency and exact types."""
    version, pid, created = (_integer(record, key) for key in ("version", "pid", "created"))
    operation, handoff, secret = (_text(record, key) for key in ("operation", "handoff", "transfer_secret"))
    keys = {"version", "pid", "created", "operation", "handoff", "transfer_secret"}
    if version != _VERSION or record.keys() != keys or not operation or bool(handoff) != bool(secret):
        msg = "Unverifiable owner record"
        raise ValueError(msg)
    return _Owner(ProcessIdentity(pid, created), operation, handoff, secret)


class OperationLock:
    """One prepared-project lock with conservative recovery and owned cleanup."""

    def __init__(self, artifacts: PreparedArtifacts, *, probe: Callable[[ProcessIdentity], ProcessState] = process_state) -> None:
        """Retain paths and injected process interrogation without acquiring yet."""
        self._artifacts = artifacts
        self._target = authorize_write(artifacts.project, artifacts.home / _NAME)
        self._probe = probe
        self._held: _Owner | None = None
        root = artifacts.project.root.stat()
        self._mutex = f"Global\\llm-shared-release-{root.st_dev:x}-{root.st_ino:x}"
        self._relative = self._target.path.relative_to(artifacts.project.root).as_posix()

    def _error(self, detail: str, record: dict[str, object] | None = None) -> OperationLockError:
        """Expose recovery context without printing the private transfer secret."""
        fields = record or {}
        context = ", ".join(f"{key}={fields.get(key, 'unknown')!r}" for key in ("version", "pid", "created", "operation", "handoff"))
        return OperationLockError(f"{self._relative}: {detail}; {context}")

    @contextmanager
    def _transition(self) -> Generator[None]:
        """Never read/check/remove outside serialization; recheck physical paths."""
        try:
            with transition_mutex(self._mutex):
                self._artifacts.destination.revalidate()
                self._target.revalidate()
                yield
        except (OSError, ManagedWriteError) as exc:
            raise self._error(str(exc)) from exc

    def _read(self) -> _Owner | None:
        """Absence permits publication; all unreadable/invalid owners fail closed."""
        record: dict[str, object] = {}
        try:
            content = self._target.revalidate().read_bytes()
        except FileNotFoundError:
            return None
        try:
            record = _record(content)
            return _owner(record)
        except (ValueError, TypeError) as exc:
            msg = "unverifiable owner; deliberate recovery required"
            raise self._error(msg, record) from exc

    def _require_owned(self) -> _Owner:
        """Reject stale handles, retained owners and a record replaced by others."""
        actual = self._read()
        if actual is None or self._held is None or actual != self._held or actual.handoff:
            msg = "operation is not owned by this handle"
            raise self._error(msg)
        return actual

    def acquire(self) -> OperationLock:
        """Publish without replacing, recovering only a positively dead owner."""
        with self._transition():
            actual = self._read()
            if actual is not None:
                record = _record(actual.encode())
                if actual.handoff:
                    msg = "retained owner requires validated transfer or deliberate recovery"
                    raise self._error(msg, record)
                if self._probe(actual.process) is not ProcessState.DEAD:
                    msg = "live or unverifiable owner"
                    raise self._error(msg, record)
            owner = _Owner(current_identity(), secrets.token_hex(32), "", "")
            # Prepare before removing a proven dead record: failed payload IO
            # leaves its recovery evidence intact. The mutex covers both steps.
            with temporary_bytes(self._target, owner.encode()) as temporary:
                if actual is not None:
                    self._target.revalidate().unlink()
                os.rename(temporary, self._target.revalidate())  # noqa: PTH104 - Windows non-replacing publication
            self._held = owner
        return self

    def release(self) -> None:
        """Remove only this handle's current non-retained record after cleanup."""
        with self._transition():
            self._require_owned()
            self._target.revalidate().unlink()
            self._held = None

    def retain(self, handoff: str) -> RetainedOwnership:
        """Persist operation ownership while the engine is absent during a build."""
        if not handoff:
            msg = "retention requires a handoff identity"
            raise self._error(msg)
        with self._transition():
            actual = self._require_owned()
            proof = RetainedOwnership(actual.operation, handoff, secrets.token_hex(32))
            owner = _Owner(actual.process, actual.operation, handoff, proof.secret)
            replace_bytes(self._target, owner.encode())
            self._held = None
            return proof

    def transfer(self, proof: RetainedOwnership) -> None:
        """Consume the exact retained capability and bind a fresh process owner."""
        with self._transition():
            actual = self._read()
            if actual is None or not actual.handoff or (
                actual.operation != proof.operation or actual.handoff != proof.handoff
                or not secrets.compare_digest(actual.transfer_secret.encode(), proof.secret.encode())
            ):
                msg = "retained ownership does not match the validated handoff"
                raise self._error(msg)
            owner = _Owner(current_identity(), actual.operation, "", "")
            replace_bytes(self._target, owner.encode())
            self._held = owner


# eof
