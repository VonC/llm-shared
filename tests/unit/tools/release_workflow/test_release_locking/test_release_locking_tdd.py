"""Integrated operation lock ownership through production invocation.

Step 6 (2026-11-02), under the user's simulation-only test rule: a locked
write runs through bootstrap, dispatch, artifact preparation, the operation
lock and managed replacement. Competing owners are records another process
would publish; their states are declared facts, and the transition mutex is
uncontended. A live, retained or unverifiable owner blocks the write and keeps
its record byte-identical; only an exact dead owner is recovered; project B
never waits for project A. Read-only calls take no lock, so they promise no
multi-file snapshot while a writer holds it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.acceptance_support import TARGET, hold, snapshot
from tests.unit.tools.release_workflow.launcher_simulation import decoded
from tools.release_workflow.windows_process import ProcessState

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.launcher_simulation import ToolingSimulation
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox
    from tools.release_workflow import cli

_FAILED = 1
_COMPETITOR = 7
_LOCK = ".reviews/a.release-operation.lock"


def _write(tooling: ToolingSimulation, sandbox: GitSandbox, root: Path, registry: dict[str, cli.Handler],
           command: str = "write") -> tuple[int, bytes]:
    """Run one locked write of a fixed payload into a project."""
    result = tooling.run([command, "--project-root", str(root), "--input-stdin"], sandbox=sandbox, cwd=sandbox.home,
                         payload="Notes é\n".encode(), handlers=registry)
    return result.returncode, result.stderr


def test_live_owner_blocks_the_write_until_it_releases(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                       consumers: tuple[Path, Path], lock_facts: LockFacts,
                                                       acceptance_registry: dict[str, cli.Handler]) -> None:
    """A second invocation fails without touching the target or the owner's record."""
    root = consumers[0].resolve()
    competitor = hold(root, lock_facts, _COMPETITOR)
    record = (root / _LOCK).read_bytes()
    status, errors = _write(launcher_tooling, git_sandbox, root, acceptance_registry)
    assert status == _FAILED
    assert b"live or unverifiable owner" in errors
    assert not (root / TARGET).exists()
    assert (root / _LOCK).read_bytes() == record
    competitor.release()
    assert _write(launcher_tooling, git_sandbox, root, acceptance_registry)[0] == 0
    assert (root / TARGET).read_bytes() == "Notes é\n".encode()
    assert not (root / _LOCK).exists()


def test_only_an_exact_dead_owner_is_recovered(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                               consumers: tuple[Path, Path], lock_facts: LockFacts,
                                               acceptance_registry: dict[str, cli.Handler]) -> None:
    """A positively dead record is replaced, the write lands and no lock remains."""
    root = consumers[0].resolve()
    hold(root, lock_facts, _COMPETITOR)
    lock_facts.states[_COMPETITOR] = ProcessState.DEAD
    assert _write(launcher_tooling, git_sandbox, root, acceptance_registry)[0] == 0
    assert (root / TARGET).read_bytes() == "Notes é\n".encode()
    assert not (root / _LOCK).exists()


@pytest.mark.parametrize(("owner", "detail"), [
    ("retained", b"retained owner requires validated transfer"),
    ("unverifiable", b"unverifiable owner; deliberate recovery required"),
    ("unknown", b"live or unverifiable owner"),
])
def test_retained_and_unverifiable_owners_are_preserved(owner: str, detail: bytes, launcher_tooling: ToolingSimulation,  # noqa: PLR0913 - fixture matrix
                                                        git_sandbox: GitSandbox, consumers: tuple[Path, Path], lock_facts: LockFacts,
                                                        acceptance_registry: dict[str, cli.Handler]) -> None:
    """Recovery needs a positively dead owner; anything else stays for a human."""
    root = consumers[0].resolve()
    competitor = hold(root, lock_facts, _COMPETITOR)
    if owner == "retained":
        competitor.retain("build-handoff")
        lock_facts.states[_COMPETITOR] = ProcessState.DEAD
    elif owner == "unverifiable":
        (root / _LOCK).write_bytes(b"{not a lock record")
    else:
        lock_facts.states[_COMPETITOR] = ProcessState.UNKNOWN
    record = (root / _LOCK).read_bytes()
    status, errors = _write(launcher_tooling, git_sandbox, root, acceptance_registry)
    assert status == _FAILED
    assert detail in errors
    assert (root / _LOCK).read_bytes() == record
    assert not (root / TARGET).exists()


def test_independent_projects_never_wait_for_each_other(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                        consumers: tuple[Path, Path], lock_facts: LockFacts,
                                                        acceptance_registry: dict[str, cli.Handler]) -> None:
    """Project B writes while project A's owner is alive, and A stays untouched."""
    held, other = (path.resolve() for path in consumers)
    hold(held, lock_facts, _COMPETITOR)
    before = snapshot(held)
    assert _write(launcher_tooling, git_sandbox, other, acceptance_registry)[0] == 0
    assert (other / TARGET).read_bytes() == "Notes é\n".encode()
    assert snapshot(held) == before


def test_interruption_inside_the_lock_releases_it(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                  consumers: tuple[Path, Path], acceptance_registry: dict[str, cli.Handler]) -> None:
    """Cancellation after acquisition is status 1, writes nothing and frees the project."""
    root = consumers[0].resolve()
    status, errors = _write(launcher_tooling, git_sandbox, root, acceptance_registry, "write-interrupted")
    assert status == _FAILED
    assert b"interrupted" in errors
    assert not (root / TARGET).exists()
    assert not (root / _LOCK).exists()
    assert _write(launcher_tooling, git_sandbox, root, acceptance_registry)[0] == 0


def test_read_only_calls_take_no_lock(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                      consumers: tuple[Path, Path], lock_facts: LockFacts,
                                      acceptance_registry: dict[str, cli.Handler]) -> None:
    """A read proceeds beside a live writer: no read lock, so no snapshot promise."""
    root = consumers[0].resolve()
    hold(root, lock_facts, _COMPETITOR)
    before = snapshot(root)
    value = decoded(launcher_tooling.run(["describe", "--project-root", str(root)], sandbox=git_sandbox,
                                         cwd=git_sandbox.home, handlers=acceptance_registry))
    assert value["root"] == str(root)
    assert snapshot(root) == before


# eof
