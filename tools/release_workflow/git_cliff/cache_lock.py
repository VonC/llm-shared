r"""Serialize provisioning of one version and platform with a bounded wait, owned records and owner-aware recovery.

Step 3 of v0.14.0 git-cliff-provisioning (design "Provisioning lock,
contention and recovery", from its lock record and transition mutex to the
recovery of a dead holder and its partial state; design decisions Q03 and
Q04; requirement clarifications Q06 and Q14; plan decision Q02).

- The record `<version>/<triple>.lock` names the owner (PID and creation
  time), its start time (local, with offset), its caller kind and every child
  recorded before it resumed. It is written complete and flushed beside its
  target, then published by a non-replacing rename, so two callers can never
  both believe they hold it.
- Every read, publication, change and removal of the record happens inside
  the kernel transition mutex
  `Global\llm-shared-git-cliff-<dev>-<ino>-<namespace>-<version>-<triple>`,
  named from the file identity of the namespace root, which is created with
  its parents first. Entering the mutex, normally or abandoned, authorizes
  nothing: only `DEAD` process identities do.
- `acquire(W, on_wait)` fixes its deadline once. Each poll enters the mutex
  and either publishes this caller's record (no record, or one whose owner
  and every child are `DEAD`, replaced in the same transition) or returns the
  live holder. The first holder gets one `on_wait` callback; polls follow
  every 250 ms until the caller's own W ends with `LockWaitError`. A holder
  change neither resets nor extends that deadline, and an `ALIVE` or
  `UNKNOWN` owner or child is never recovered, however long it holds. Since
  code review round 1 of Step 3, a poll reads the clock inside the mutex,
  after its entry and the liveness probes, and publishes or replaces nothing
  once the deadline has passed: a late wake-up or a slow transition that
  finds the lock freed still fails, naming the last live holder seen.
- A record that cannot prove an owner fails closed at once with
  `LockRecordError`: it is never recovered, and waiting cannot change it.
- `record_child` appends an identity under the mutex; `release` removes only
  this caller's current record; after `retain_record()`, used on an
  unconfirmed child end, `release` removes nothing and no change is accepted.
- `recover_attempts()`, for the holder only, lists the version directory once
  without recursion and removes a `.staging-` or `.retired-` directory only
  when its name owner and every child of its owner file are `DEAD`; anything
  live, unverifiable or refused stays for a later provisioning.

`CacheLock` takes its seams as one `LockSeams` value (clock, sleep, liveness
probe, current identity, mutex and local time), within the five-argument
limit. Recovery never reads a modification time: liveness is its only test.

Step 6 makes `publish_file` public: an evidence candidate's trust record is
published the same way, complete and flushed, by a non-replacing rename.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, Self

from tools.release_workflow.git_cliff.budget import (
    DEFAULT_DOWNLOAD_SECONDS,
    DOWNLOAD_BUDGET_VARIABLE,
    MAXIMUM_DOWNLOAD_SECONDS,
)
from tools.release_workflow.git_cliff.cache import (
    OWNER_FILE,
    SCHEMA,
    Attempt,
    CacheLayout,
    CachePin,
    OwnerFile,
    decode_children,
    identity_fields,
    local_time,
)
from tools.release_workflow.lock_records import decode_object, positive_integer, text
from tools.release_workflow.windows_process import (
    ProcessIdentity,
    ProcessState,
    current_identity,
    process_state,
    transition_mutex,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from types import TracebackType

_POLL_SECONDS = 0.25
_LABEL = "lock"
_KEYS = frozenset({"schema", "pid", "created", "started", "caller", "children"})
LOCK_WAIT_REMEDY = (
    "Another process holds the named lock; retry when it ends, or wait longer by raising"
    f" {DOWNLOAD_BUDGET_VARIABLE} ({DEFAULT_DOWNLOAD_SECONDS} through {MAXIMUM_DOWNLOAD_SECONDS} s)"
)


class LockRecordError(OSError):
    """The lock record cannot prove an owner, or this caller does not hold the lock it acts on."""


@dataclass(frozen=True)
class LockRecord:
    """The holder of one version and platform: owner, start time, caller kind and recorded children."""

    owner: ProcessIdentity
    started: str
    caller: str
    children: tuple[ProcessIdentity, ...] = ()

    def with_child(self, child: ProcessIdentity) -> LockRecord:
        """Return the record with one more recorded child."""
        return LockRecord(self.owner, self.started, self.caller, (*self.children, child))

    def encode(self) -> bytes:
        """Produce the complete record, one JSON object on one line."""
        fields = {
            "schema": SCHEMA, **identity_fields(self.owner), "started": self.started, "caller": self.caller,
            "children": [identity_fields(child) for child in self.children],
        }
        return (json.dumps(fields, ensure_ascii=True) + "\n").encode("utf-8")

    @classmethod
    def decode(cls, content: bytes) -> LockRecord:
        """Decode a schema 1 record holding exactly its six fields and a non-empty caller kind."""
        record = decode_object(content, label=_LABEL)
        if record.keys() != _KEYS or positive_integer(record, "schema", label=_LABEL) != SCHEMA:
            msg = "Invalid lock fields"
            raise ValueError(msg)
        caller = text(record, "caller", label=_LABEL)
        if not caller:
            msg = "Invalid lock caller"
            raise ValueError(msg)
        owner = ProcessIdentity(positive_integer(record, "pid", label=_LABEL), positive_integer(record, "created", label=_LABEL))
        return cls(owner, local_time(record, "started", label=_LABEL), caller, decode_children(record, label=_LABEL))


class LockWaitError(OSError):
    """The caller's own wait ended before it could publish its record.

    It names the last live holder seen; `owner` and `started` are None only
    when no live holder was seen, as when proving a dead holder took past W.
    """

    def __init__(self, path: Path, holder: LockRecord | None, wait: float) -> None:
        """Name the lock path, the last live holder (PID, start time, caller kind), the wait and the remedy."""
        state = "not acquired before its deadline" if holder is None else (
            f"held by process {holder.owner.pid} since {holder.started} ({holder.caller})"
        )
        super().__init__(f"{path}: {state} after waiting {wait:g} s. {LOCK_WAIT_REMEDY}")
        self.path = path
        self.owner = None if holder is None else holder.owner
        self.started = None if holder is None else holder.started
        self.wait = wait


class _Serialized(Protocol):
    """One entered transition of the mutex."""

    def __enter__(self) -> None:
        """Enter the transition."""
        ...

    def __exit__(self, kind: type[BaseException] | None, error: BaseException | None, trace: TracebackType | None, /) -> bool | None:
        """Leave the transition."""
        ...


def _local_now() -> datetime:
    """Return the local time with its offset."""
    return datetime.now(UTC).astimezone()


@dataclass(frozen=True, kw_only=True)
class LockSeams:
    """The cache lock's injected seams: monotonic clock and sleep, liveness probe, identity, mutex and local time."""

    clock: Callable[[], float]
    sleep: Callable[[float], None]
    probe: Callable[[ProcessIdentity], ProcessState] = process_state
    current: Callable[[], ProcessIdentity] = current_identity
    mutex: Callable[[str], _Serialized] = transition_mutex
    now: Callable[[], datetime] = _local_now


def publish_file(target: Path, content: bytes, *, replace: bool) -> None:
    """Write complete flushed bytes beside the target, then rename them into place; never keep the temporary."""
    descriptor, name = tempfile.mkstemp(prefix=f".{target.name}-", suffix=".tmp", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            temporary.replace(target)
        else:
            # Windows refuses to rename onto an existing file: publication never replaces.
            temporary.rename(target)
    finally:
        temporary.unlink(missing_ok=True)


def _removed(directory: Path) -> bool:
    """Remove a recovered attempt directory; a refusal keeps it for a later provisioning."""
    try:
        shutil.rmtree(directory)
    except OSError:
        return False
    return True


class CacheLock:
    """The provisioning lock of one version and platform, held by at most one caller at a time."""

    def __init__(self, layout: CacheLayout, pin: CachePin, *, caller: str, seams: LockSeams) -> None:
        """Bind the lock to its record path and seams without touching the filesystem yet."""
        if not caller:
            msg = "a cache lock needs a caller kind"
            raise ValueError(msg)
        self._layout = layout
        self._pin = pin
        self._caller = caller
        self._seams = seams
        self._path = layout.lock_path(pin)
        self._held: LockRecord | None = None
        self._retained = False
        self._name: str | None = None

    @property
    def path(self) -> Path:
        """Return the lock record path, for diagnostics."""
        return self._path

    def _transition(self) -> _Serialized:
        """Enter the transition mutex, creating the namespace root and version directory first."""
        if self._name is None:
            self._layout.version_dir(self._pin).mkdir(parents=True, exist_ok=True)
            root = self._layout.root.stat()
            self._name = (
                f"Global\\llm-shared-git-cliff-{root.st_dev:x}-{root.st_ino:x}"
                f"-{self._layout.namespace}-{self._pin.version}-{self._pin.triple}"
            )
        return self._seams.mutex(self._name)

    def _read(self) -> LockRecord | None:
        """Read the record inside a transition; absence permits publication, anything unverifiable fails closed."""
        try:
            content = self._path.read_bytes()
        except FileNotFoundError:
            return None
        try:
            return LockRecord.decode(content)
        except (ValueError, TypeError) as error:
            msg = (
                f"{self._path}: unverifiable lock record ({error}); remove it by hand once no provisioning"
                f" of git-cliff {self._pin.version} runs"
            )
            raise LockRecordError(msg) from error

    def _all_dead(self, actors: Iterable[ProcessIdentity]) -> bool:
        """Prove every actor DEAD, asking in order and stopping at the first one that is not."""
        return all(self._seams.probe(actor) is ProcessState.DEAD for actor in actors)

    def _poll(self, deadline: float) -> tuple[LockRecord | None, bool]:
        """In one transition, publish this caller's record before the deadline, or report why not.

        Returns `(holder, False)` for a live holder, `(None, True)` once this
        caller's record is published, and `(None, False)` when the deadline
        passed before publication: the clock is read inside the mutex, after
        its entry and the liveness probes, so an expired waiter never
        publishes its record nor replaces a dead one.
        """
        with self._transition():
            found = self._read()
            if found is not None and not self._all_dead((found.owner, *found.children)):
                return found, False
            if self._seams.clock() > deadline:
                return None, False
            mine = LockRecord(self._seams.current(), self._seams.now().isoformat(timespec="seconds"), self._caller)
            publish_file(self._path, mine.encode(), replace=found is not None)
            self._held = mine
        return None, True

    def acquire(self, wait_seconds: float, on_wait: Callable[[LockRecord, float], None]) -> Self:
        """Take the lock within the caller's own wait, polling every 250 ms behind a live holder.

        Args:
            wait_seconds: The caller's own wait W; its deadline is fixed now.
            on_wait: Called once, with the first holder found and W, before the first poll interval.

        Returns:
            This lock, held, published no later than the deadline.

        Raises:
            LockWaitError: W ended before this caller could publish its record; it names the last live holder seen.
            LockRecordError: The record is unverifiable, or this lock is already held.
        """
        if self._held is not None:
            msg = f"{self._path}: already held by this caller"
            raise LockRecordError(msg)
        deadline = self._seams.clock() + wait_seconds
        last: LockRecord | None = None
        while True:
            holder, acquired = self._poll(deadline)
            if acquired:
                return self
            if holder is not None and last is None:
                on_wait(holder, wait_seconds)
            last = holder or last
            remaining = deadline - self._seams.clock()
            if remaining <= 0:
                raise LockWaitError(self._path, last, wait_seconds)
            self._seams.sleep(min(_POLL_SECONDS, remaining))

    def _holder(self) -> LockRecord:
        """Return this caller's held record, refusing an unheld or retained lock."""
        if self._held is None or self._retained:
            msg = f"{self._path}: not held by this caller"
            raise LockRecordError(msg)
        return self._held

    def _require_current(self, held: LockRecord) -> None:
        """Inside a transition, refuse to act on a record that is no longer this caller's."""
        if self._read() != held:
            msg = f"{self._path}: the lock record is no longer this caller's"
            raise LockRecordError(msg)

    def record_child(self, child: ProcessIdentity) -> None:
        """Append a child identity to the held record, before that child resumes."""
        held = self._holder()
        with self._transition():
            self._require_current(held)
            updated = held.with_child(child)
            publish_file(self._path, updated.encode(), replace=True)
            self._held = updated

    def release(self) -> None:
        """Remove this caller's record; after `retain_record()` remove nothing."""
        if self._retained:
            return
        held = self._holder()
        with self._transition():
            self._require_current(held)
            self._path.unlink()
            self._held = None

    def retain_record(self) -> None:
        """Keep the record for a later recovery: a child's end is unconfirmed."""
        self._holder()
        self._retained = True

    def _removable(self, directory: Path, attempt: Attempt) -> bool:
        """Prove the name owner, then every child of the owner file, DEAD; keep anything unverifiable."""
        if self._seams.probe(attempt.owner) is not ProcessState.DEAD:
            return False
        try:
            content = (directory / OWNER_FILE).read_bytes()
        except FileNotFoundError:
            return True
        except OSError:
            return False
        try:
            recorded = OwnerFile.decode(content)
        except (ValueError, TypeError):
            return False
        return recorded.owner == attempt.owner and self._all_dead(recorded.children)

    def recover_attempts(self) -> tuple[str, ...]:
        """Remove the attempt directories of this version whose every actor is DEAD; return their names."""
        self._holder()
        attempts: list[tuple[Path, Attempt]] = []
        with os.scandir(self._layout.version_dir(self._pin)) as entries:
            for entry in entries:
                attempt = CacheLayout.parse_attempt(entry.name)
                if attempt is not None and entry.is_dir(follow_symlinks=False):
                    attempts.append((Path(entry.path), attempt))
        return tuple(directory.name for directory, attempt in attempts if self._removable(directory, attempt) and _removed(directory))


# eof
