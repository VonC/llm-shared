"""Locked digest-only ownership persistence for review exchanges.

Step 3 extracts the transition lock and coordination compare-and-swap storage
from the risk-band exchange store. Claims are calculated by the pure ownership
service and exposed only after their complete coordination replacement is
durable. Read-only discovery uses the same lock without creating files or
waiting behind an in-progress publication.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import errno
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from threading import Lock, RLock
from typing import TYPE_CHECKING, Final

from tools.review_exchange_models import (
    ArtifactPaths,
    ReviewContext,
    ReviewExchangeError,
    mapping_value,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    parse_json_markdown,
    render_json_markdown,
)
from tools.review_exchange_ownership import OwnershipRejectedError

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import BinaryIO

    from tools.review_exchange_models import Actor
    from tools.review_exchange_ownership import (
        OwnershipCapability,
        OwnershipClaim,
        OwnershipService,
    )

if os.name == "nt":
    import msvcrt  # pragma: no cover - platform-specific import
else:
    import fcntl  # pragma: no cover - platform-specific import

_ATOMIC_REPLACE_ATTEMPTS: Final[int] = 5
_ATOMIC_REPLACE_DELAY_SECONDS: Final[float] = 0.01
_LOCAL_LOCKS: dict[Path, RLock] = {}
_LOCAL_LOCKS_GUARD = Lock()


def _local_lock(path: Path) -> RLock:
    """Return one process-local lock for an exact transition-lock path."""
    resolved = path.resolve()
    with _LOCAL_LOCKS_GUARD:
        return _LOCAL_LOCKS.setdefault(resolved, RLock())


@contextmanager
def observe_transition(path: Path) -> Generator[bool]:
    """Try a non-mutating snapshot lock; busy publishers defer to the next poll."""
    local = _local_lock(path)
    if not local.acquire(blocking=False):
        yield False
        return
    try:
        try:
            stream = path.open("rb")
        except FileNotFoundError:
            # Legacy evidence has no lock yet and must still be validated.
            yield True
            return
        with stream:
            acquired = _try_observation_lock(stream)
            try:
                yield acquired
            finally:
                if acquired:
                    _unlock_stream(stream)
    finally:
        local.release()


def _try_observation_lock(stream: BinaryIO) -> bool:
    """Take a nonblocking platform read lock, preserving actual IO failures."""
    try:
        if os.name == "nt":
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBRLCK, 1)
        else:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
    except OSError as error:
        if error.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
            raise
        return False
    return True


def _unlock_stream(stream: BinaryIO) -> None:
    """Release the shared platform lock used by readers and transition writers."""
    stream.seek(0)
    if os.name == "nt":
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        return
    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


class ReviewExchangeOwnershipStore:
    """Persist coordination and ownership claims under one transition lock."""

    def __init__(self, paths: ArtifactPaths) -> None:
        """Bind ownership storage to one exact exchange path set."""
        self.paths = paths
        self._local_transition_lock = _local_lock(paths.transition_lock)

    @contextmanager
    def transition_lock(self) -> Generator[None]:
        """Hold the identity-specific operating-system lock for one transition."""
        with self._local_transition_lock:
            lock_path = self.paths.transition_lock
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            with lock_path.open("a+b") as stream:
                self._ensure_lock_byte(stream)
                self._lock_stream(stream)
                try:
                    yield
                finally:
                    self._unlock_stream(stream)

    def claim(
        self,
        record: CoordinationRecord,
        service: OwnershipService,
        actor: Actor,
        *,
        presented: OwnershipCapability | None = None,
        force: bool = False,
    ) -> OwnershipClaim:
        """Calculate and persist one ordinary claim or forced pickup."""
        with self._local_transition_lock:
            stored = self.read_coordination(required=True)
            if stored != record:
                if (
                    stored is not None
                    and stored.owner is actor
                    and presented is None
                    and not force
                ):
                    raise OwnershipRejectedError(
                        service.already_claimed_failure(stored),
                    )
                raise ReviewExchangeError("stale coordination record for ownership claim")
            claim = service.claim(record, actor, presented=presented, force=force)
            self.write_coordination(claim.record)
            return claim

    def write_coordination(self, record: CoordinationRecord) -> None:
        """Atomically persist strict digest-only coordination for this identity."""
        self._validate_context(record.context)
        title = f"Review exchange coordination for {record.context.identity.key}"
        content = render_json_markdown(title, record.to_dict(), "").encode("utf-8")
        prepared = self._prepare_atomic(self.paths.coordination, content)
        try:
            self._commit_prepared(prepared, self.paths.coordination)
        except OSError as error:
            raise ReviewExchangeError(
                f"coordination publication failed: {error}",
            ) from error
        finally:
            prepared.unlink(missing_ok=True)

    def read_coordination(
        self,
        *,
        required: bool = False,
    ) -> CoordinationRecord | None:
        """Read one exact coordination record without artifact discovery."""
        path = self.paths.coordination
        if not path.exists():
            if required:
                raise ReviewExchangeError("coordination record does not exist")
            return None
        try:
            content = path.read_text(encoding="utf-8")
            data, trailing = parse_json_markdown(content)
            if trailing.strip():
                raise ReviewExchangeError(
                    "coordination record has unexpected trailing content",
                )
            record = CoordinationRecord.from_dict(
                mapping_value(data, "coordination JSON"),
            )
        except (OSError, UnicodeError) as error:
            raise ReviewExchangeError(
                f"cannot read coordination record: {error}",
            ) from error
        self._validate_context(record.context)
        return record

    def _validate_context(self, context: ReviewContext) -> None:
        """Reject coordination that does not belong to this exact path set."""
        if context.identity != self.paths.identity:
            raise ReviewExchangeError(
                "coordination identity does not match exact paths",
            )
        if context.document_path.parent != self.paths.transcript.parent:
            raise ReviewExchangeError(
                "reviewed document differs from transcript parent",
            )

    @staticmethod
    def _prepare_atomic(target: Path, content: bytes) -> Path:
        """Write and synchronize one same-directory coordination replacement."""
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(
            prefix=".tmp-review-ownership-",
            suffix=".tmp",
            dir=target.parent,
        )
        prepared = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            prepared.unlink(missing_ok=True)
            raise
        return prepared

    @staticmethod
    def _commit_prepared(prepared: Path, target: Path) -> None:
        """Expose a prepared record with bounded transient-sharing retries."""
        for attempt in range(_ATOMIC_REPLACE_ATTEMPTS):
            try:
                prepared.replace(target)
            except PermissionError:
                if attempt + 1 == _ATOMIC_REPLACE_ATTEMPTS:
                    raise
                time.sleep(_ATOMIC_REPLACE_DELAY_SECONDS * (2**attempt))
            else:
                return

    @staticmethod
    def _ensure_lock_byte(stream: BinaryIO) -> None:
        """Give Windows one byte range for the transition lock."""
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)

    @staticmethod
    def _lock_stream(stream: BinaryIO) -> None:
        """Acquire the blocking platform lock."""
        if os.name == "nt":
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
            return
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)

    @staticmethod
    def _unlock_stream(stream: BinaryIO) -> None:
        """Delegate platform release before the transition stream closes."""
        _unlock_stream(stream)


__all__ = ["ReviewExchangeOwnershipStore", "observe_transition"]


# eof
