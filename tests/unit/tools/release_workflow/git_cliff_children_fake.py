"""The fake child launcher and the provisioning world: scripted children, guards that refuse renames, simulated parent death.

Step 5 of v0.14.0 git-cliff-provisioning (plan "Shared test architecture",
plan decision Q12). No process, socket, job, native call or real wait:

- `Child`: one scripted child: how it ends (an exit with its status and
  output, never finishing, an unconfirmed end before or after its identity,
  or a refused creation), the fake seconds it lasts and those spent before
  the launcher creates it, what a worker writes,
  and the lifecycle boundary at which its parent dies (`creation`,
  `before-record` or `running`).
- `FakeChildren`: the launch seam. It sorts each request by role (`worker`,
  `probe` or `run`), plays the next scripted child of that role or the role's
  default (a worker writes the synthetic archive and reports `ok`, a probe
  reports `git-cliff <pin>`, a run exits 0), and follows `run_contained`:
  creation is one step that yields no child or a member of its job, a
  recorded child is recorded before it resumes, a child holds a copy of
  every listed guard for its lifetime, and an outcome returns only once the
  child has ended. Each launch is kept with its fake launch time, what was
  recorded at its resume and, for a child that never finishes, the attempt
  state at its reap. Since code review round 2, a child whose `expires` has
  passed by its resume is ended unrun and reported timed out, as
  `run_contained` does.
- `ProvisionWorld`: one scenario: its cache layout, fake clock, process
  states, uncontended mutex, guard opener and stderr lines, and the seams of
  `provisioning.provision`. An open guard, or a child's copy, refuses the
  rename of its file and of any directory holding it; a `busy` directory
  refuses its own rename (another open handle); `refusals` add rename
  refusals by predicate, and `renames` records every rename that happened.
  An `on_line` hook runs after each standard-error line (code review round 1:
  a broken stream, or time spent before the first download attempt).
- Parent death: at its boundary the launcher, or `die_on_rename`, snapshots
  the cache tree, closes the dying caller's guards and raises `ParentDied`, a
  `BaseException`. The test's `dies()` block then restores the snapshot,
  which is exactly what a dead parent leaves (no cleanup of its own ran),
  declares that caller `DEAD` and continues as `SECOND`, another live caller.

Step 6 serves the evidence candidates: a worker in metadata mode has its own
`metadata` role, which has no default and must be scripted (the harness fake
builds those children); the default archive and probe answer of a child take
their version from the cache path they work in (`<version>/<attempt or
triple>/...`), so two candidates share one world; a world can be built in the
evidence namespace; and `run_output` gives the status and output of each
unscripted git-cliff run from its request.

Step 8 sorts a `gcliff --version` run, which inherits standard input, as a
run rather than a probe, whose standard input is closed.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import shutil
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import (
    CURRENT,
    FakeClock,
    FakeGuard,
    FakeGuardOpener,
    LockWorld,
    ProcessStates,
    UncontendedMutex,
    install_entry,
    synthetic_archive,
    synthetic_pin,
)
from tools.release_workflow.git_cliff import provisioning
from tools.release_workflow.git_cliff.budget import resolve_budget
from tools.release_workflow.git_cliff.cache import OWNER_FILE, CacheLayout, OwnerFile
from tools.release_workflow.git_cliff.cache_lock import LockRecord
from tools.release_workflow.git_cliff.download_worker import parse_request
from tools.release_workflow.windows_child import (
    ChildOutcome,
    ChildRequest,
    ContainmentError,
    UnconfirmedEndError,
)
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from collections.abc import Generator
    from contextlib import AbstractContextManager

    from tools.release_workflow.git_cliff.budget import BudgetPolicy
    from tools.release_workflow.git_cliff.invocation import GitCliffInvocation
    from tools.release_workflow.git_cliff.manifest import AdmittedPin

SECOND = ProcessIdentity(5600, 133_000_000_000_005_600)
RUNTIME = Path("C:/runtime/python.exe")
_DEAD, _ALIVE = ProcessState.DEAD, ProcessState.ALIVE
_FIRST_CHILD = 6000


class ParentDied(BaseException):  # noqa: N818 - a simulated event, not an error a caller handles
    """The simulated death of the provisioning caller at a lifecycle boundary."""


def outcome_line(outcome: str, **fields: object) -> bytes:
    """Write the worker's one JSON outcome line."""
    return (json.dumps({"outcome": outcome, **fields}) + "\n").encode()


@dataclass(frozen=True)
class Child:
    """One scripted child; every field left at its default plays the role's normal exit."""

    status: int = 0
    stdout: bytes | None = None
    write: bytes | None = None
    seconds: float = 0.0
    entry_seconds: float = 0.0
    hang: bool = False
    death: str | None = None
    created: bool = True
    unconfirmed: str | None = None
    containment: bool = False
    before_record: Callable[[], object] | None = None
    after: ProcessState = _DEAD


def failed(kind: str, error: str) -> Child:
    """A worker attempt that reports a retryable or fatal failure and writes nothing."""
    return Child(status=75 if kind == "retryable" else 65, stdout=outcome_line(kind, error=error))


@dataclass
class Launched:
    """One launch: its role, request and child identity, what was recorded at its resume and the state at its reap."""

    role: str
    request: ChildRequest
    at: float = 0.0
    identity: ProcessIdentity | None = None
    recorded: tuple[tuple[ProcessIdentity, ...], tuple[ProcessIdentity, ...]] | None = None
    reaped: dict[str, bool] | None = None
    ran: bool = True

    def remaining(self) -> float:
        """Return the budget a worker request gives the worker, in seconds."""
        return parse_request(self.request.arguments[self.request.arguments.index("--") + 1:]).remaining


def _role(request: ChildRequest) -> str:
    """Sort a request: the download worker, the metadata worker, the version probe, or a git-cliff run.

    The probe is `--version` with standard input closed; a `gcliff --version` run inherits it, so it is a run.
    """
    if "git-cliff-worker" in request.arguments:
        return "metadata" if "metadata" in request.arguments else "worker"
    return "probe" if request.arguments == ("--version",) and request.stdin == "closed" else "run"


def _version(path: Path) -> str:
    """Read the version of a cache path `<version>/<attempt or triple>/<file>`."""
    return path.parent.parent.name


class FakeChildren:
    """The launch seam: plays scripted children by role with the contained lifecycle of `run_contained`."""

    def __init__(self, world: ProvisionWorld) -> None:
        """Start with no script and no launch."""
        self._world = world
        self._scripts: dict[str, list[Child]] = {"worker": [], "metadata": [], "probe": [], "run": []}
        self.launched: list[Launched] = []

    def script(self, role: str, *children: Child) -> None:
        """Queue children for one role; once the queue is empty the role's default plays."""
        self._scripts[role].extend(children)

    def of(self, role: str) -> list[Launched]:
        """Return the launches of one role, in order."""
        return [launched for launched in self.launched if launched.role == role]

    def _identity(self) -> ProcessIdentity:
        """Give the next child its PID and creation time, alive."""
        number = _FIRST_CHILD + len(self.launched)
        identity = ProcessIdentity(number, 133_000_000_000_000_000 + number)
        self._world.states.states[identity] = _ALIVE
        return identity

    def __call__(self, request: ChildRequest) -> ChildOutcome:
        """Create, record, run and end one child as scripted."""
        role = _role(request)
        queue = self._scripts[role]
        child = queue.pop(0) if queue else Child()
        world = self._world
        launched = Launched(role, request, at=world.clock.elapsed)
        self.launched.append(launched)
        world.clock.elapsed += child.entry_seconds
        identity = self._create(child, request, launched)
        if request.record is not None:
            self._record(child, request, launched, identity)
        if request.expires is not None and world.clock.elapsed >= request.expires:
            # As `run_contained`: past its expiry before its resume, the child is ended suspended and never runs.
            launched.ran = False
            world.end(identity)
            return ChildOutcome(status=1, stdout=b"", stderr=b"", timed_out=True, identity=identity)
        world.copies.extend((guard.path, identity) for guard in world.opener.opened if guard.handle in request.inherited)
        world.clock.elapsed += child.seconds
        written = self._write(role, child, request)
        return self._end(role, child, launched, identity, written)

    def _create(self, child: Child, request: ChildRequest, launched: Launched) -> ProcessIdentity:
        """Create the child as one step, yielding no child or a suspended member of its job, or stop at a creation boundary."""
        world = self._world
        if child.containment:
            msg = f"cannot contain {request.executable.name}: CreateProcessW failed"
            raise ContainmentError(msg, call="CreateProcessW", error=1816)
        if child.death == "creation":
            if child.created:
                world.end(self._identity())
            world.die()
        identity = launched.identity = self._identity()
        if child.unconfirmed == "before-identity":
            world.states.states[identity] = child.after
            raise UnconfirmedEndError(pid=identity.pid, identity=None, call="GetProcessTimes", error=5)
        if child.death == "before-record":
            world.end(identity)
            world.die()
        return identity

    def _record(self, child: Child, request: ChildRequest, launched: Launched, identity: ProcessIdentity) -> None:
        """Record the suspended child; a failing recorder ends it unrun, as `run_contained` does."""
        if child.before_record is not None:
            child.before_record()
        try:
            if request.record is not None:
                request.record(identity)
        except Exception as error:
            self._world.end(identity)
            msg = f"cannot contain {request.executable.name}: record failed: {error}"
            raise ContainmentError(msg, call="record", error=None) from error
        launched.recorded = self._world.recorded_children()

    def _write(self, role: str, child: Child, request: ChildRequest) -> bytes | None:
        """Let a worker write its target: the scripted bytes, or the archive when it reports success."""
        if role != "worker":
            return None
        target = parse_request(request.arguments[request.arguments.index("--") + 1:]).target
        if target is None:
            return None
        content = child.write if child.write is not None or child.stdout is not None or child.hang else synthetic_archive(_version(target))
        if content is not None:
            target.write_bytes(content)
        return content

    def _end(self, role: str, child: Child, launched: Launched, identity: ProcessIdentity, written: bytes | None) -> ChildOutcome:
        """End the child at its scripted boundary, or confirm its end and return its outcome."""
        world = self._world
        if child.death == "running":
            world.states.states[identity] = child.after
            world.die()
        if child.unconfirmed == "after-run":
            world.states.states[identity] = child.after
            raise UnconfirmedEndError(pid=identity.pid, identity=identity, call="TerminateJobObject", error=5)
        if child.hang:
            launched.reaped = world.attempt_state()
        world.end(identity)
        if child.hang:
            return ChildOutcome(status=1, stdout=b"", stderr=b"", timed_out=True, identity=identity)
        status, stdout = self._result(role, child, launched.request, written)
        return ChildOutcome(status=status, stdout=stdout, stderr=b"", timed_out=False, identity=identity)

    def _result(self, role: str, child: Child, request: ChildRequest, written: bytes | None) -> tuple[int, bytes]:
        """The scripted status and output, or the role's default ones; a probe reports the version of its cache path."""
        if child.stdout is not None:
            return child.status, child.stdout
        if role == "worker":
            content = written or b""
            return child.status, outcome_line("ok", size=len(content), sha256=hashlib.sha256(content).hexdigest())
        if role == "probe":
            return child.status, f"git-cliff {_version(request.executable)}\n".encode()
        if role == "run" and self._world.run_output is not None:
            return self._world.run_output(request)
        return child.status, b""


def _alive_current() -> ProcessStates:
    """Declare only the first caller, alive."""
    return ProcessStates({CURRENT: _ALIVE})


@dataclass
class ProvisionWorld:
    """One provisioning scenario with its seams, guard table and simulated parent death."""

    layout: CacheLayout
    pin: AdmittedPin = field(default_factory=synthetic_pin)
    clock: FakeClock = field(default_factory=FakeClock)
    states: ProcessStates = field(default_factory=_alive_current)
    mutex: UncontendedMutex = field(default_factory=UncontendedMutex)
    opener: FakeGuardOpener = field(default_factory=FakeGuardOpener)
    lines: list[str] = field(default_factory=list[str])
    current: ProcessIdentity = CURRENT
    platform_error: Exception | None = None
    guard_errors: dict[int, OSError] = field(default_factory=dict[int, OSError])
    holders: dict[int, ProcessIdentity] = field(default_factory=dict[int, ProcessIdentity])
    dead: set[ProcessIdentity] = field(default_factory=set[ProcessIdentity])
    copies: list[tuple[Path, ProcessIdentity]] = field(default_factory=list[tuple[Path, ProcessIdentity]])
    busy: set[Path] = field(default_factory=set[Path])
    refusals: list[Callable[[Path, Path], bool]] = field(default_factory=list[Callable[[Path, Path], bool]])
    renames: list[tuple[Path, Path]] = field(default_factory=list[tuple[Path, Path]])
    die_on_rename: Callable[[Path, Path], bool] | None = None
    guard_opens: int = 0
    query_seconds: float = 0.0
    mutex_error: OSError | None = None
    on_line: Callable[[str], object] | None = None
    run_output: Callable[[ChildRequest], tuple[int, bytes]] | None = None
    _left: dict[str, bytes | None] | None = None

    def __post_init__(self) -> None:
        """Attach the fake launcher."""
        self.children = FakeChildren(self)

    @classmethod
    def build(cls, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, namespace: str = "production") -> ProvisionWorld:
        """Create the tooling root and route every rename through the guard table; the layout is in the given namespace."""
        world = cls(CacheLayout(tmp_path / "tooling", namespace))
        world.layout.tooling_root.mkdir(parents=True)
        original = os.rename

        def rename(source: str | Path, target: str | Path) -> None:
            moved, place = Path(source), Path(target)
            if world.die_on_rename is not None and world.die_on_rename(moved, place):
                world.die()
            if world.blocks(moved) or any(refuse(moved, place) for refuse in world.refusals):
                raise PermissionError(errno.EACCES, "open elsewhere (simulated sharing violation)", str(source))
            original(source, target)
            world.renames.append((moved, place))

        monkeypatch.setattr(os, "rename", rename)
        return world

    @property
    def entry(self) -> Path:
        """Return the entry directory of the pin."""
        return self.layout.entry_dir(self.pin)

    @property
    def executable(self) -> Path:
        """Return the entry's executable."""
        return self.layout.executable(self.pin)

    def _current(self) -> ProcessIdentity:
        """Answer the current identity seam."""
        return self.current

    def _platform(self) -> None:
        """Answer the platform check seam."""
        if self.platform_error is not None:
            raise self.platform_error

    def _line(self, line: str) -> None:
        """Keep a standard-error line, then run the declared hook, which may advance time or fail like a broken stream."""
        self.lines.append(line)
        if self.on_line is not None:
            self.on_line(line)

    def _state(self, identity: ProcessIdentity) -> ProcessState:
        """Answer a liveness query that lasts `query_seconds` of fake time."""
        self.clock.elapsed += self.query_seconds
        return self.states(identity)

    def _mutex(self, name: str) -> AbstractContextManager[None]:
        """Enter the uncontended mutex, or fail as an unavailable one does."""
        if self.mutex_error is not None:
            raise self.mutex_error
        return self.mutex(name)

    def _open_guard(self, path: Path) -> FakeGuard:
        """Open a guard held by the current caller, or fail as declared for this open."""
        number, self.guard_opens = self.guard_opens, self.guard_opens + 1
        error = self.guard_errors.get(number)
        if error is not None:
            raise error
        guard = self.opener(path)
        self.holders[guard.handle] = self.current
        return guard

    def seams(self) -> provisioning.ProvisioningSeams:
        """Bind the provisioning seams to this scenario."""
        return provisioning.ProvisioningSeams(
            launch=self.children, open_guard=self._open_guard, process_state=self._state, current_identity=self._current,
            mutex=self._mutex, clock=self.clock.monotonic, sleep=self.clock.sleep, stderr=self._line, runtime=RUNTIME,
            platform_check=self._platform, now=self.clock.now,
        )

    def provision(self, budget: BudgetPolicy | None = None, caller: str = "engine") -> GitCliffInvocation:
        """Run the service as the current caller."""
        policy = resolve_budget({}) if budget is None else budget
        return provisioning.provision(self.layout.tooling_root, self.pin, policy, seams=self.seams(), caller=caller)

    def lock_world(self) -> LockWorld:
        """Share this scenario's layout, clock, states and mutex with the lock builders."""
        return LockWorld(self.layout, self.clock, self.states, self.mutex)

    def hold(self, record: LockRecord) -> bytes:
        """Publish another caller's lock record."""
        return self.lock_world().hold(self.pin, record)

    def install(self, executable: bytes | None = None) -> None:
        """Publish a valid entry of the pin."""
        if executable is None:
            install_entry(self.layout, self.pin)
        else:
            install_entry(self.layout, self.pin, executable)

    def corrupt_record(self) -> None:
        """Make the entry invalid after a caller validated it: its record no longer describes the executable."""
        record = json.loads(self.layout.record(self.pin).read_bytes())
        record["executable_size"] += 1
        self.layout.record(self.pin).write_bytes((json.dumps(record) + "\n").encode())

    def hold_guard(self, holder: ProcessIdentity) -> FakeGuard:
        """Open a guard on the entry's executable on behalf of another release."""
        guard = self.opener(self.executable)
        self.holders[guard.handle] = holder
        return guard

    def _guarded(self) -> list[Path]:
        """Every path an open guard or a live child's copy protects."""
        opened = [guard.path for guard in self.opener.opened
                  if (guard.retained or not guard.closed) and self.holders.get(guard.handle) not in self.dead]
        return opened + [path for path, _child in self.copies]

    def blocks(self, path: Path) -> bool:
        """Tell whether a rename of this file or directory is refused by a guard or another open handle."""
        return path in self.busy or any(guarded == path or path in guarded.parents for guarded in self._guarded())

    def end(self, identity: ProcessIdentity) -> None:
        """End a child: DEAD, and its guard copies closed with it."""
        self.states.states[identity] = _DEAD
        self.copies = [(path, child) for path, child in self.copies if child != identity]

    def kill(self, identity: ProcessIdentity) -> None:
        """End a caller outside any child boundary: DEAD, its own guards closed."""
        self.dead.add(identity)
        self.states.states[identity] = _DEAD

    def die(self) -> NoReturn:
        """Leave the cache as it is now, close the dying caller's guards and stop it."""
        self._left = self.tree()
        self.dead.add(self.current)
        raise ParentDied

    @contextmanager
    def dies(self) -> Generator[None]:
        """Expect the caller's death, restore what it left, declare it DEAD and continue as SECOND."""
        with pytest.raises(ParentDied):
            yield
        left, self._left = self._left, None
        assert left is not None
        shutil.rmtree(self.layout.root, ignore_errors=True)
        for name, content in sorted(left.items()):
            path = self.layout.root / name
            if content is None:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        self.states.states[self.current] = _DEAD
        self.current = SECOND
        self.states.states[SECOND] = _ALIVE

    def tree(self) -> dict[str, bytes | None]:
        """Read the cache tree: each relative path with its bytes, or None for a directory."""
        found: dict[str, bytes | None] = {}
        pending = [self.layout.root] if self.layout.root.is_dir() else []
        while pending:
            for path in pending.pop().iterdir():
                name = path.relative_to(self.layout.root).as_posix()
                if path.is_dir():
                    found[name] = None
                    pending.append(path)
                else:
                    found[name] = path.read_bytes()
        return found

    def attempts(self, kind: str = "staging") -> list[Path]:
        """Return the attempt directories of one kind in the version directory."""
        version = self.layout.version_dir(self.pin)
        return sorted(path for path in version.iterdir() if path.name.startswith(f".{kind}-")) if version.is_dir() else []

    def attempt_state(self) -> dict[str, bool]:
        """Tell whether a staging directory and the lock record exist now."""
        return {"staging": bool(self.attempts()), "lock": self.layout.lock_path(self.pin).exists()}

    def lock_record(self) -> LockRecord | None:
        """Read the lock record, or None."""
        path = self.layout.lock_path(self.pin)
        return LockRecord.decode(path.read_bytes()) if path.exists() else None

    def recorded_children(self) -> tuple[tuple[ProcessIdentity, ...], tuple[ProcessIdentity, ...]]:
        """Read the children recorded in the lock record and in the newest staging owner file."""
        record = self.lock_record()
        staging = self.attempts()
        owner = OwnerFile.decode((staging[-1] / OWNER_FILE).read_bytes()) if staging else None
        return (() if record is None else record.children), (() if owner is None else owner.children)


# eof
