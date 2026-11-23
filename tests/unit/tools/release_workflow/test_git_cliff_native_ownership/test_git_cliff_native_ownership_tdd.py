"""The final native check picks its own git-cliff run among competing runs of the same image, or refuses.

Code review round 1 of Step 8 of v0.14.0 git-cliff-provisioning. The final
launcher check kills the launcher of a git-cliff run and ends its job, so a
concurrent invocation of the same cached executable must never be chosen.
`owned_run` decides from simulated process tables, without any native call:

- its own run is chosen beside a foreign run of the same image, whatever
  the order of the table;
- only foreign runs, or none, give None, so the check keeps waiting;
- two own runs, or a run started by the root itself, raise `OwnershipError`;
- a reused PID (an ancestor with the root's PID but another creation time, or
  a parent created after its child), a missing parent, an unreadable creation
  time and a parent cycle never link a run to the root.

Code review round 2: `await_ready_run` takes the run only once the check's own
pipe names its client, on a fake clock. The guarded `--version` reuse probe of
the same launcher, which never opens the pipe, is never chosen, even while it
lingers in the snapshot beside the run; a run that never opens the pipe is
`NotReadyError` at the bound, and a client outside the check's own tree stops
the check.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from tests.unit.tools.release_workflow.git_cliff_native_ownership import (
    NotReadyError,
    OwnershipError,
    ProcessRecord,
    await_ready_run,
    owned_run,
)

_ROOT = ProcessRecord(100, 4, 1_000)
_REDIRECTOR = ProcessRecord(110, 100, 1_100)
_LAUNCHER = ProcessRecord(120, 110, 1_200)
_OWN = ProcessRecord(130, 120, 1_300, runs_executable=True)
_FOREIGN_SHELL = ProcessRecord(200, 4, 900)
_FOREIGN_LAUNCHER = ProcessRecord(220, 200, 950)
_FOREIGN = ProcessRecord(230, 220, 960, runs_executable=True)


def _table(*processes: ProcessRecord) -> dict[int, ProcessRecord]:
    """Index a simulated snapshot by PID."""
    return {process.pid: process for process in processes}


@pytest.mark.parametrize("foreign_first", [False, True])
def test_the_own_run_is_chosen_beside_a_foreign_run_of_the_same_image(*, foreign_first: bool) -> None:
    """The foreign launcher is never returned, whichever run the snapshot lists first."""
    own, foreign = (_ROOT, _REDIRECTOR, _LAUNCHER, _OWN), (_FOREIGN_SHELL, _FOREIGN_LAUNCHER, _FOREIGN)
    table = _table(*foreign, *own) if foreign_first else _table(*own, *foreign)
    assert owned_run(table, _ROOT) == (_OWN, _LAUNCHER)


def test_only_foreign_runs_or_none_give_none() -> None:
    """No run of the check's own tree exists yet: the check keeps waiting, and ends nothing."""
    assert owned_run(_table(_ROOT, _REDIRECTOR, _FOREIGN_SHELL, _FOREIGN_LAUNCHER, _FOREIGN), _ROOT) is None
    assert owned_run(_table(_ROOT, _REDIRECTOR, _LAUNCHER), _ROOT) is None


def test_two_own_runs_are_ambiguous() -> None:
    """Two runs of the executable below the check's own root: it refuses to choose."""
    second = ProcessRecord(140, 120, 1_400, runs_executable=True)
    with pytest.raises(OwnershipError, match="2 git-cliff runs"):
        owned_run(_table(_ROOT, _REDIRECTOR, _LAUNCHER, _OWN, second), _ROOT)


def test_a_run_started_by_the_root_itself_has_no_launcher() -> None:
    """The root is the check's own batch process: it is never the launcher to kill."""
    direct = ProcessRecord(150, 100, 1_500, runs_executable=True)
    with pytest.raises(OwnershipError, match="not by a launcher"):
        owned_run(_table(_ROOT, direct), _ROOT)


@pytest.mark.parametrize("chain", [
    (ProcessRecord(100, 4, 5_000), ProcessRecord(120, 100, 5_100), ProcessRecord(130, 120, 5_200, runs_executable=True)),
    (_ROOT, ProcessRecord(120, 100, 1_400), ProcessRecord(130, 120, 1_300, runs_executable=True)),
    (_ROOT, ProcessRecord(130, 120, 1_300, runs_executable=True)),
    (_ROOT, ProcessRecord(120, 100, None), ProcessRecord(130, 120, 1_300, runs_executable=True)),
    (_ROOT, ProcessRecord(120, 130, 1_300), ProcessRecord(130, 120, 1_300, runs_executable=True)),
], ids=["root-pid-reused", "parent-newer-than-child", "parent-missing", "creation-unreadable", "parent-cycle"])
def test_a_broken_or_reused_chain_never_links_a_run_to_the_root(chain: tuple[ProcessRecord, ...]) -> None:
    """Only an unbroken chain of older parents up to the root's own PID and creation time makes a run the check's own."""
    assert owned_run(_table(*chain), _ROOT) is None


_PROBE = ProcessRecord(125, 120, 1_250, runs_executable=True)
_RUN = ProcessRecord(135, 120, 1_350, runs_executable=True)


@dataclass
class _Wait:
    """A fake clock whose sleep advances time, and scripted answers of the pipe and of the snapshots."""

    clients: list[int | None]
    tables: list[dict[int, ProcessRecord]]
    elapsed: float = 0.0
    sleeps: int = 0

    def ready(self) -> int | None:
        """Name the pipe's client, the last answer repeating."""
        return self.clients.pop(0) if len(self.clients) > 1 else self.clients[0]

    def snapshot(self) -> dict[int, ProcessRecord]:
        """Return the next process table, the last one repeating."""
        return self.tables.pop(0) if len(self.tables) > 1 else self.tables[0]

    def clock(self) -> float:
        """Return the fake seconds elapsed."""
        return self.elapsed

    def sleep(self, seconds: float) -> None:
        """Advance the fake time."""
        self.sleeps += 1
        self.elapsed += seconds

    def run(self, seconds: float = 1.0) -> tuple[ProcessRecord, ProcessRecord]:
        """Wait for the check's own run, as the launcher check does."""
        return await_ready_run(self.ready, self.snapshot, _ROOT, seconds=seconds, clock=self.clock, sleep=self.sleep)


def test_the_guarded_probe_is_never_taken_for_the_run() -> None:
    """Code review round 2: while the reuse probe runs, the pipe has no client; once the run opens it, the run is chosen."""
    wait = _Wait(clients=[None, None, _RUN.pid], tables=[_table(_ROOT, _REDIRECTOR, _LAUNCHER, _RUN)])
    assert wait.run() == (_RUN, _LAUNCHER)
    assert wait.sleeps == len((None, None))


def test_the_run_is_the_pipes_client_even_beside_a_lingering_probe() -> None:
    """A probe of the same image and launcher still in the snapshot is ignored: only the pipe's client can be the run."""
    wait = _Wait(clients=[_RUN.pid], tables=[_table(_ROOT, _REDIRECTOR, _LAUNCHER, _PROBE, _RUN)])
    assert wait.run() == (_RUN, _LAUNCHER)
    with pytest.raises(OwnershipError, match="2 git-cliff runs"):
        owned_run(_table(_ROOT, _REDIRECTOR, _LAUNCHER, _PROBE, _RUN), _ROOT)


def test_a_run_that_never_opens_its_pipe_is_not_ready_at_the_bound() -> None:
    """No client within the bound: `NotReadyError`, a timeout, after polling without a real wait; no snapshot is read."""
    wait = _Wait(clients=[None], tables=[])
    with pytest.raises(NotReadyError, match=r"within 0\.12 s"):
        wait.run(0.12)
    assert wait.sleeps == len((0.0, 0.05, 0.1))


def test_a_pipe_client_that_is_no_owned_run_stops_the_check() -> None:
    """A client of the pipe outside the check's own tree, or not running the executable, ends nothing."""
    wait = _Wait(clients=[_FOREIGN.pid], tables=[_table(_ROOT, _REDIRECTOR, _LAUNCHER, _FOREIGN_SHELL, _FOREIGN_LAUNCHER, _FOREIGN)])
    with pytest.raises(OwnershipError, match=f"pipe's client {_FOREIGN.pid}"):
        wait.run()


# eof
