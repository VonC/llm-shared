"""Pick the git-cliff run a native check started, among every process of the same image, by its pipe and its process tree.

Code review round 1 of Step 8 of v0.14.0 git-cliff-provisioning: the final
launcher check kills a launcher and ends a job, so it must never act on
another invocation that runs the same cached executable. This module holds the
decision as data, without any native call, so a test can feed it simulated
process tables; `git_cliff_native_launcher.py` builds the table from a
process snapshot.

- `ProcessRecord`: a PID, its parent PID, its creation time (None when it
  could not be read) and whether it runs the executable.
- `owned_run(table, root, run=None)` returns the one run of the executable
  that descends from the check's own root process (the `cmd.exe` it started)
  and its parent, the launcher. A run descends from the root when its chain of
  parents reaches the root's PID with the root's creation time, each parent
  created no later than its child, within a bounded depth: a reused PID can
  never link two trees, and a cycle ends. No owned run yet is None; more than
  one, or a run whose parent is the root itself, raises `OwnershipError`
  before anything is ended. Given `run`, only that PID can be the run.
- Since code review round 2, `await_ready_run(ready, snapshot, root, ...)`
  waits for positive readiness first: `ready` names the client process of the
  invocation's own pipe, which only the waiting git-cliff run opens, never the
  guarded `--version` reuse probe that the same launcher starts just before
  it. That client must then be an owned run of the executable, or the check
  stops with `OwnershipError`; no client within the bound is `NotReadyError`.
  Its clock and sleep are injected, so the probe-to-run transition and a run
  that never gets ready are tested without a process or a real wait.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

_MAXIMUM_DEPTH = 16
_POLL_SECONDS = 0.05


@dataclass(frozen=True)
class ProcessRecord:
    """One process of a snapshot: its PID, parent PID, creation time and whether it runs the executable."""

    pid: int
    parent: int
    created: int | None
    runs_executable: bool = False


class OwnershipError(RuntimeError):
    """The check cannot tell which run is its own: it refuses to end anything."""


class NotReadyError(TimeoutError):
    """No process opened the check's own pipe within its bound."""


def _descends(process: ProcessRecord, root: ProcessRecord, table: Mapping[int, ProcessRecord]) -> bool:
    """Tell whether a process descends from the root through parents each created no later than its child."""
    current = process
    for _ in range(_MAXIMUM_DEPTH):
        parent = table.get(current.parent)
        if parent is None or parent.created is None or current.created is None or parent.created > current.created:
            return False
        if parent.pid == root.pid:
            return parent.created == root.created
        current = parent
    return False


def owned_run(table: Mapping[int, ProcessRecord], root: ProcessRecord,
              run: int | None = None) -> tuple[ProcessRecord, ProcessRecord] | None:
    """Return the one run of the executable descending from the root and its launcher, None for none yet.

    Args:
        table: The recorded processes, by PID.
        root: The check's own root process.
        run: The only PID that may be the run, such as the client of the check's pipe; None for any.

    Raises:
        OwnershipError: More than one run descends from the root, or the run's parent is the root itself.
    """
    owned = [process for process in table.values()
             if process.runs_executable and run in {None, process.pid} and _descends(process, root, table)]
    if not owned:
        return None
    if len(owned) > 1:
        msg = f"{len(owned)} git-cliff runs of the executable descend from the check's own process {root.pid}"
        raise OwnershipError(msg)
    found = owned[0]
    if found.parent == root.pid:
        msg = f"the git-cliff run {found.pid} was started by the check's own process {root.pid}, not by a launcher"
        raise OwnershipError(msg)
    return found, table[found.parent]


def await_ready_run(ready: Callable[[], int | None], snapshot: Callable[[], Mapping[int, ProcessRecord]],  # noqa: PLR0913 - the seams of one wait
                    root: ProcessRecord, *, seconds: float, clock: Callable[[], float],
                    sleep: Callable[[float], None]) -> tuple[ProcessRecord, ProcessRecord]:
    """Wait until the check's own pipe names its client, then return that client as the owned run, with its launcher.

    Raises:
        NotReadyError: No process opened the pipe within `seconds`.
        OwnershipError: The pipe's client is no run of the executable descending from the root.
    """
    end = clock() + seconds
    while (client := ready()) is None:
        if clock() > end:
            msg = f"no git-cliff run opened the check's own pipe within {seconds} s"
            raise NotReadyError(msg)
        sleep(_POLL_SECONDS)
    found = owned_run(snapshot(), root, client)
    if found is None:
        msg = f"the pipe's client {client} is no run of the executable descending from the check's own process {root.pid}"
        raise OwnershipError(msg)
    return found


# eof
