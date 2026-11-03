"""Integrated acceptance handlers, consumer trees and whole-tree snapshots.

Step 6 (2026-11-02): the assembled foundation runs through production
bootstrap, readiness, dispatch, invocation and rendering with the data-only
interpreter and repository ports of ``launcher_simulation``. The handlers
below are acceptance fixtures injected in process; the shipped registry stays
empty. They use the services later domains receive: project-derived paths,
artifact preparation, the operation lock and managed replacement. Snapshots
cover whole consumer and tooling trees, ignored files and legacy scratch
included, so a failed or read-only call is shown to write nothing.

The missing-launcher caller is a reference adapter for items 5 and 8, not
their production argument handling. It decides absence by the launcher file
before calling it: an ordinary intent warns and reads its local version, a
release or snapshot intent anywhere in the arguments fails, and an installed
launcher's status, including 1 or 2, is returned without any fallback.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tools.release_workflow import cli
from tools.release_workflow.artifacts import PreparedArtifacts, prepare_artifacts
from tools.release_workflow.managed_files import authorize_write, replace_bytes
from tools.release_workflow.operation_lock import OperationLock
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.results import OperationResult
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from tools.release_workflow.invocation import InvocationContext

TARGET = "release-notes.txt"
VERSION = "1.2.3-SNAPSHOT"
HANDLER_PID = 42
_CREATED = 123
_RELEASE_INTENTS = frozenset({"release", "snapshot"})
_NATIVE_STATUS = 7


def consumer(root: Path) -> Path:
    """Give a simulated repository version data, ignored output and legacy scratch."""
    (root / "version.txt").write_text(f"{VERSION}\n", encoding="utf-8")
    (root / ".gitignore").write_text("build/\na.*\n", encoding="utf-8")
    (root / "build").mkdir(exist_ok=True)
    (root / "build" / "output.log").write_text("ignored build output\n", encoding="utf-8")
    (root / "a.md").write_text("legacy scratch\n", encoding="utf-8")
    return root


def snapshot(root: Path) -> dict[str, bytes | None]:
    """Record every path below a root: file bytes, or ``None`` for a directory."""
    return {path.relative_to(root).as_posix(): path.read_bytes() if path.is_file() else None
            for path in root.rglob("*")}


def describe(context: InvocationContext) -> OperationResult:
    """Read version data and expose every location derived from the project."""
    return OperationResult(data=json.dumps({
        "root": context.root_windows, "posix": context.root_posix, "name": context.project_name,
        "version": context.version_file.read_text(encoding="utf-8").strip(),
        "pom": str(context.pom_file), "package": str(context.package_file),
        "changelog": str(context.changelog_header), "workflow": str(context.dev_workflow),
        "tooling": str(context.runtime.root), "payload": context.payload,
        "diagnostics": list(context.diagnostics), "child_environment": sorted(context.git.environment.values),
    }, ensure_ascii=False) + "\n")


def build_step(context: InvocationContext) -> OperationResult:
    """Change into the build directory, then read the payload frozen at preflight."""
    os.chdir(context.project.root / "build")
    if context.input_file is None:
        msg = "build step needs an input file"
        raise ValueError(msg)
    return OperationResult(data=context.input_file.read_text(encoding="utf-8"))


def native_status(_context: InvocationContext) -> OperationResult:
    """Return a child build's status 7 with non-ASCII output and diagnostics."""
    return OperationResult(_NATIVE_STATUS, data="partial résumé\n", diagnostics=("child build failed: échec",))


@dataclass
class LockFacts:
    """Declared process identity and owner states for the operation lock."""

    pid: int = HANDLER_PID
    states: dict[int, ProcessState] = field(default_factory=dict[int, ProcessState])

    def identity(self) -> ProcessIdentity:
        """Return the identity the next lock owner publishes."""
        return ProcessIdentity(self.pid, _CREATED)

    def probe(self, owner: ProcessIdentity) -> ProcessState:
        """Report a declared state; an undeclared owner is alive."""
        return self.states.get(owner.pid, ProcessState.ALIVE)


@dataclass(frozen=True)
class LockedWrite:
    """Prepare the home, hold the operation lock and replace one managed file."""

    facts: LockFacts
    interrupt: bool = False

    def __call__(self, context: InvocationContext) -> OperationResult:
        """Write the payload only while this invocation owns the project lock."""
        prepared = prepare_artifacts(context.artifacts, context.git)
        lock = OperationLock(prepared, probe=self.facts.probe).acquire()
        try:
            if self.interrupt:
                raise KeyboardInterrupt
            replace_bytes(authorize_write(context.project, TARGET), (context.payload or "").encode("utf-8"))
        finally:
            lock.release()
        return OperationResult(data=f"wrote {TARGET}\n")


def handlers(facts: LockFacts) -> dict[str, cli.Handler]:
    """Return the acceptance registry injected in process, never shipped."""
    return {
        "describe": cli.Handler(describe), "build": cli.Handler(build_step),
        "native": cli.Handler(native_status),
        "write": cli.Handler(LockedWrite(facts), requires_input=True),
        "write-interrupted": cli.Handler(LockedWrite(facts, interrupt=True), requires_input=True),
    }


def hold(root: Path, facts: LockFacts, pid: int) -> OperationLock:
    """Publish a competing owner record in a prepared home, as another process would."""
    home = root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    previous, facts.pid = facts.pid, pid
    try:
        return OperationLock(PreparedArtifacts(project, authorize_write(project, home)), probe=facts.probe).acquire()
    finally:
        facts.pid = previous


@dataclass(frozen=True)
class CallerOutcome:
    """What a build caller does with the release tooling, or without it."""

    status: int
    version: str | None = None
    warnings: tuple[str, ...] = ()


def build_caller(launcher: Path, arguments: Sequence[str], *, run: Callable[[Path, Sequence[str]], int],
                 local_version: Callable[[], str]) -> CallerOutcome:
    """Decide absence by the launcher file; never fall back after it ran."""
    if not launcher.is_file():
        if _RELEASE_INTENTS.intersection(argument.lower() for argument in arguments):
            return CallerOutcome(1, warnings=(f"{launcher.name} is missing; release and snapshot need the release tooling",))
        return CallerOutcome(0, local_version(), (f"{launcher.name} is missing; using the local version",))
    return CallerOutcome(run(launcher, arguments))


# eof
