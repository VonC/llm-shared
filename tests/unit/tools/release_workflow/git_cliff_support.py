"""Shared builders for the git-cliff cache and cache lock tests: no process, no native call, no real wait.

Step 3 of v0.14.0 git-cliff-provisioning (plan "Shared test architecture",
plan decision Q12). The builders are declared state, never real resources:

- `FakeClock`: monotonic seconds that only `sleep` advances, scheduled actions
  run when the time reaches them (a holder that releases mid-wait), an
  optional oversleep added to every sleep (a late wake-up), and a local wall
  clock with its offset for record stamps;
- `ProcessStates`: process states keyed by `ProcessIdentity`; an undeclared
  identity is `UNKNOWN`, and every query is recorded in order;
- `UncontendedMutex`: a transition mutex that is always free, records each
  name it is entered with, and can declare its acquisitions abandoned;
- `LockWorld`: one cache lock scenario binding the lock to those seams, with
  liveness queries that can each take fake time (a slow transition), and
  builders for another caller's lock record and for attempt directories;
- `synthetic_pin()`: an `AdmittedPin` for 2.14.2 built from a small generated
  archive, its real size and SHA-256 computed here;
- `install_entry`: a published entry (stand-in executable and its record);
- `FakeGuardOpener` and `FakeGuard`: use guards over scenario files, which the
  native `CreateFileW` could not see in the memory filesystem;
- `FakeProbe`: a version probe that plays one outcome or raises;
- `deny_writes`: every `mkdir`, `rename`, `replace`, `remove`, `unlink`,
  `rmdir`, write-mode `open` and writing `os.open` raises `PermissionError`
  and is recorded.

Step 4 adds `CannedWeb`: canned HTTPS answers by URL (a status and body, a
redirect, a body whose read stalls like a silent socket, or an exception) and
a real `urllib` opener that serves them without any socket, through the
standard redirect and error handlers, recording every open with its timeout
and every read size.
"""

from __future__ import annotations

import builtins
import errno
import hashlib
import http.client
import io
import os
import ssl
import urllib.request
import urllib.response
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from functools import cache
from typing import TYPE_CHECKING, cast

from tools.release_workflow.git_cliff.cache import OWNER_FILE, EntryRecord, Guard
from tools.release_workflow.git_cliff.cache_lock import CacheLock, LockRecord, LockSeams
from tools.release_workflow.git_cliff.manifest import PLATFORM_TRIPLE, AdmittedPin
from tools.release_workflow.windows_child import ChildOutcome
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

    import pytest

    from tools.release_workflow.git_cliff.cache import CacheLayout

VERSION = "2.14.2"
STAND_IN_EXECUTABLE = b"MZ" + bytes(range(256)) * 4
PROVISIONED = "2026-11-18T14:02:31+01:00"
CURRENT = ProcessIdentity(4812, 133_000_000_000_000_001)
PROBE_IDENTITY = ProcessIdentity(4242, 133_000_000_000_000_077)
_START = datetime(2026, 11, 18, 14, 2, 31, tzinfo=timezone(timedelta(hours=1)))
_ARCHIVE_TIME = (2026, 11, 13, 0, 0, 0)
_WRITE_MODES = frozenset("wax+")
_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
_DENIED = ("mkdir", "rename", "replace", "remove", "unlink", "rmdir")
_OPEN, _OS_OPEN = "open", "os.open"


def _no_actions() -> list[tuple[float, Callable[[], object]]]:
    """Start a clock with nothing scheduled."""
    return []


@dataclass
class FakeClock:
    """Monotonic seconds advanced only by `sleep`, running each scheduled action once its time is reached."""

    elapsed: float = 0.0
    oversleep: float = 0.0
    sleeps: list[float] = field(default_factory=list[float])
    _actions: list[tuple[float, Callable[[], object]]] = field(default_factory=_no_actions)

    def monotonic(self) -> float:
        """Return the fake seconds elapsed since the case started."""
        return self.elapsed

    def now(self) -> datetime:
        """Return the local time with its offset at the current fake second."""
        return _START + timedelta(seconds=self.elapsed)

    def at(self, seconds: float, action: Callable[[], object]) -> None:
        """Run an action during the first sleep that reaches this time."""
        self._actions.append((seconds, action))

    def sleep(self, seconds: float) -> None:
        """Advance the time by the request plus any oversleep, without waiting, then run the actions now due."""
        self.sleeps.append(seconds)
        self.elapsed += seconds + self.oversleep
        due = [action for when, action in self._actions if when <= self.elapsed]
        self._actions = [(when, action) for when, action in self._actions if when > self.elapsed]
        for action in due:
            action()


@dataclass
class ProcessStates:
    """Declared process states; an undeclared identity is UNKNOWN, and each query is recorded."""

    states: dict[ProcessIdentity, ProcessState] = field(default_factory=dict[ProcessIdentity, ProcessState])
    queries: list[ProcessIdentity] = field(default_factory=list[ProcessIdentity])

    def __call__(self, identity: ProcessIdentity) -> ProcessState:
        """Answer one liveness query."""
        self.queries.append(identity)
        return self.states.get(identity, ProcessState.UNKNOWN)


@dataclass
class UncontendedMutex:
    """A transition mutex that is always free; it records each entry and whether it was declared abandoned."""

    abandoned: bool = False
    entries: list[tuple[str, bool]] = field(default_factory=list[tuple[str, bool]])

    @contextmanager
    def __call__(self, name: str) -> Generator[None]:
        """Enter at once, as the kernel does for a free or an abandoned mutex."""
        self.entries.append((name, self.abandoned))
        yield


def _alive_current() -> ProcessStates:
    """Declare only the current process, alive."""
    return ProcessStates({CURRENT: ProcessState.ALIVE})


@dataclass
class LockWorld:
    """One cache lock scenario: its layout, fake clock, declared states, mutex and the wait callbacks received."""

    layout: CacheLayout
    clock: FakeClock = field(default_factory=FakeClock)
    states: ProcessStates = field(default_factory=_alive_current)
    mutex: UncontendedMutex = field(default_factory=UncontendedMutex)
    waits: list[tuple[LockRecord, float]] = field(default_factory=list[tuple[LockRecord, float]])
    query_seconds: float = 0.0

    def _probe(self, identity: ProcessIdentity) -> ProcessState:
        """Answer a liveness query that lasts `query_seconds` of fake time."""
        self.clock.elapsed += self.query_seconds
        return self.states(identity)

    def lock(self, pin: AdmittedPin, caller: str = "engine") -> CacheLock:
        """Build a cache lock for the current process, bound to this scenario's seams."""
        seams = LockSeams(clock=self.clock.monotonic, sleep=self.clock.sleep, probe=self._probe, current=lambda: CURRENT,
                          mutex=self.mutex, now=self.clock.now)
        return CacheLock(self.layout, pin, caller=caller, seams=seams)

    def on_wait(self, holder: LockRecord, wait: float) -> None:
        """Receive the waiting callback, as the waiting line would be printed."""
        self.waits.append((holder, wait))

    def declare(self, state: ProcessState, *identities: ProcessIdentity) -> None:
        """Declare the state of some processes."""
        self.states.states.update(dict.fromkeys(identities, state))

    def hold(self, pin: AdmittedPin, record: LockRecord) -> bytes:
        """Publish another caller's lock record and return its bytes."""
        self.layout.version_dir(pin).mkdir(parents=True, exist_ok=True)
        content = record.encode()
        self.layout.lock_path(pin).write_bytes(content)
        return content

    def attempt(self, pin: AdmittedPin, owner: ProcessIdentity, owner_file: bytes | None, kind: str = "staging") -> Path:
        """Leave an attempt directory with an archive in it and, when given, its owner file."""
        directory = self.layout.attempt_dir(pin, kind, owner, "5eed")
        directory.mkdir(parents=True)
        (directory / pin.asset).write_bytes(b"partial")
        if owner_file is not None:
            (directory / OWNER_FILE).write_bytes(owner_file)
        return directory


@cache
def synthetic_archive() -> bytes:
    """Build a small archive holding the stand-in executable at the 2.14.2 member path."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in ((f"git-cliff-{VERSION}/git-cliff.exe", STAND_IN_EXECUTABLE), (f"git-cliff-{VERSION}/README.md", b"stand-in\n")):
            archive.writestr(zipfile.ZipInfo(name, date_time=_ARCHIVE_TIME), content)
    return buffer.getvalue()


@cache
def synthetic_pin() -> AdmittedPin:
    """Admit 2.14.2 with the real size and SHA-256 of the synthetic archive."""
    archive = synthetic_archive()
    return AdmittedPin(
        version=VERSION, default=True, triple=PLATFORM_TRIPLE, asset=f"git-cliff-{VERSION}-{PLATFORM_TRIPLE}.zip",
        size=len(archive), sha256=hashlib.sha256(archive).hexdigest(), member=f"git-cliff-{VERSION}/git-cliff.exe",
        evidence=f"tools/release_workflow/git_cliff/bundles/{VERSION}",
    )


def entry_record(pin: AdmittedPin, executable: bytes = STAND_IN_EXECUTABLE) -> EntryRecord:
    """Describe an entry of this pin whose executable holds these bytes."""
    return EntryRecord(
        version=pin.version, triple=pin.triple, asset=pin.asset, asset_sha256=pin.sha256,
        executable_sha256=hashlib.sha256(executable).hexdigest(), executable_size=len(executable), provisioned=PROVISIONED,
    )


def install_entry(layout: CacheLayout, pin: AdmittedPin, executable: bytes = STAND_IN_EXECUTABLE) -> EntryRecord:
    """Publish an entry: the executable and the record describing exactly those bytes."""
    layout.entry_dir(pin).mkdir(parents=True)
    layout.executable(pin).write_bytes(executable)
    record = entry_record(pin, executable)
    layout.record(pin).write_bytes(record.encode())
    return record


@dataclass
class FakeGuard:
    """A use guard over a scenario file: hashing reads the file, and close and retain are recorded."""

    path: Path
    handle: int
    hashed: int = 0
    closed: bool = False
    retained: bool = False

    def sha256_and_size(self) -> tuple[str, int]:
        """Hash the guarded bytes, as the real guard does through a duplicate handle."""
        self.hashed += 1
        content = self.path.read_bytes()
        return hashlib.sha256(content).hexdigest(), len(content)

    def close(self) -> None:
        """Close the guard, unless it was retained."""
        if not self.retained:
            self.closed = True

    def retain(self) -> None:
        """Hand the guard to the process-lifetime owner: no later close takes effect."""
        self.retained = True


@dataclass
class FakeGuardOpener:
    """Open fake guards over scenario files; a missing executable is `FileNotFoundError`."""

    opened: list[FakeGuard] = field(default_factory=list[FakeGuard])

    def __call__(self, path: Path) -> FakeGuard:
        """Open one guard, as `windows_guard.open_guard` does."""
        if not path.is_file():
            raise FileNotFoundError(errno.ENOENT, "the executable to guard is missing", str(path))
        guard = FakeGuard(path, 1000 + len(self.opened))
        self.opened.append(guard)
        return guard


@dataclass
class FakeProbe:
    """Play one version probe outcome, or raise, recording the guard each probe inherited."""

    stdout: bytes = f"git-cliff {VERSION}\n".encode()
    status: int = 0
    timed_out: bool = False
    error: Exception | None = None
    guards: list[Guard] = field(default_factory=list[Guard])

    def __call__(self, guard: Guard) -> ChildOutcome:
        """Run one probe with the guard in its inherited list."""
        self.guards.append(guard)
        if self.error is not None:
            raise self.error
        return ChildOutcome(status=self.status, stdout=self.stdout, stderr=b"", timed_out=self.timed_out, identity=PROBE_IDENTITY)


@dataclass
class WriteDenial:
    """The write attempts refused while the helper is installed, as (call, path) pairs."""

    attempts: list[tuple[str, str]] = field(default_factory=list[tuple[str, str]])

    def refuse(self, call: str, path: object) -> PermissionError:
        """Record one attempt and build the refusal."""
        name = str(path)
        self.attempts.append((call, name))
        return PermissionError(errno.EACCES, f"write denied by the test: {call}", name)


def _denied(denial: WriteDenial, call: str) -> Callable[..., None]:
    """Build a replacement that refuses every call of one path operation."""
    def refuse(path: object, *_arguments: object, **_keywords: object) -> None:
        raise denial.refuse(call, path)
    return refuse


def deny_writes(monkeypatch: pytest.MonkeyPatch) -> WriteDenial:
    """Make every write-capable filesystem call raise `PermissionError` and record it; reads keep working."""
    denial = WriteDenial()
    for call in _DENIED:
        monkeypatch.setattr(os, call, _denied(denial, call))
    reader = cast("Callable[..., object]", io.open)
    raw_open = cast("Callable[..., int]", os.open)

    def guarded_open(file: object, mode: str = "r", *arguments: object, **keywords: object) -> object:
        if _WRITE_MODES & set(mode):
            raise denial.refuse(_OPEN, file)
        return reader(file, mode, *arguments, **keywords)

    def guarded_os_open(path: object, flags: int, *arguments: object, **keywords: object) -> int:
        if flags & _WRITE_FLAGS:
            raise denial.refuse(_OS_OPEN, path)
        return raw_open(path, flags, *arguments, **keywords)

    monkeypatch.setattr(io, "open", guarded_open)
    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(os, "open", guarded_os_open)
    return denial


@dataclass(frozen=True)
class Canned:
    """One canned HTTPS answer: a status with its body, a redirect, or a body whose first read stalls."""

    status: int = 200
    body: bytes = b""
    location: str | None = None
    stall: bool = False


class _Body(io.BytesIO):
    """A response body that records the size of every read and can stall like a silent socket."""

    def __init__(self, content: bytes, reads: list[int], *, stall: bool) -> None:
        """Serve these bytes, recording each read into the shared list."""
        super().__init__(content)
        self._reads = reads
        self._stall = stall

    def read(self, size: int | None = -1, /) -> bytes:
        """Return the next bytes, or raise the socket timeout of a stalled read."""
        if self._stall:
            msg = "The read operation timed out"
            raise TimeoutError(msg)
        chunk = super().read(size)
        self._reads.append(len(chunk))
        return chunk


@dataclass
class CannedWeb:
    """Canned HTTPS answers by URL and a socket-free opener serving them, recording each open and read."""

    answers: dict[str, Canned | Exception]
    opened: list[tuple[str, float | None]] = field(default_factory=list[tuple[str, float | None]])
    reads: list[int] = field(default_factory=list[int])

    def opener(self) -> urllib.request.OpenerDirector:
        """Build a real opener that serves the canned answers first, with no proxy and no certificate loading."""
        quiet = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
        return urllib.request.build_opener(urllib.request.ProxyHandler({}), quiet, _CannedHandler(self))


class _CannedHandler(urllib.request.BaseHandler):
    """Answer HTTPS requests from a `CannedWeb` before the real handler; redirects and errors go through the standard ones."""

    handler_order = 100

    def __init__(self, web: CannedWeb) -> None:
        """Serve one canned web."""
        self._web = web

    def https_open(self, req: urllib.request.Request) -> urllib.response.addinfourl:
        """Record the open and play its canned answer."""
        self._web.opened.append((req.full_url, req.timeout))
        answer = self._web.answers[req.full_url]
        if isinstance(answer, Exception):
            raise answer
        headers = http.client.HTTPMessage()
        if answer.location is not None:
            headers["Location"] = answer.location
        response = urllib.response.addinfourl(_Body(answer.body, self._web.reads, stall=answer.stall), headers, req.full_url, answer.status)
        setattr(response, "msg", "canned")  # the error processor reads the reason phrase
        return response


# eof
