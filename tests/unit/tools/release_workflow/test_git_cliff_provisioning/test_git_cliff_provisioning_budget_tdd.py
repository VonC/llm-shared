"""The download budget D and the caller's wait W reach the worker, the retry and the waiting line; refused values stop everything.

Step 5 of v0.14.0 git-cliff-provisioning (design "Time budgets and retries",
"The download budget override" and "Deadline enforcement"; design decisions
Q05, Q06 and Q18). Unset, `900` and `3600` give the first worker the whole D
and the waiting line the caller's W = D + 60. Every refused form fails as the
budget-setting stage before any guard, probe, child, network or cache access,
also with a valid entry. With `900`, a reset answered with `Retry-After: 2000`
keeps the 5 s delay and the retry inside 900 s. With `3600`, every probe
keeps its 15 s. A default waiter behind a holder that runs with D = 1800 s
fails at its own 360 s and keeps the holder's lock and staging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_children_fake import (
    Child,
    ProvisionWorld,
    failed,
)
from tools.release_workflow.git_cliff import provisioning
from tools.release_workflow.git_cliff.budget import (
    DOWNLOAD_BUDGET_VARIABLE,
    BudgetPolicy,
)
from tools.release_workflow.git_cliff.cache import OwnerFile
from tools.release_workflow.git_cliff.cache_lock import LockRecord
from tools.release_workflow.git_cliff.messages import (
    ProvisioningError,
    Stage,
    waiting_line,
)
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from pathlib import Path

HOLDER = ProcessIdentity(4900, 133_000_000_000_000_900)
STARTED = "2026-11-18T13:58:00+01:00"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProvisionWorld:
    """Give each case its own cache, clock, process states, guards and children."""
    return ProvisionWorld.build(tmp_path, monkeypatch)


def _budget(world: ProvisionWorld, environment: dict[str, str]) -> BudgetPolicy:
    """Resolve the policy as a caller does, once, before provisioning."""
    return provisioning.provisioning_budget(environment, tooling_root=world.layout.tooling_root, pin=world.pin)


@pytest.mark.parametrize(("environment", "download", "wait"), [
    ({}, 300, 360),
    ({DOWNLOAD_BUDGET_VARIABLE: "900"}, 900, 960),
    ({DOWNLOAD_BUDGET_VARIABLE.lower(): "3600"}, 3600, 3660),
])
def test_the_policy_reaches_the_worker_deadline_and_the_waiting_line(
        world: ProvisionWorld, environment: dict[str, str], download: int, wait: int) -> None:
    """The waiting line shows W; the first attempt receives the whole D."""
    budget = _budget(world, environment)
    world.hold(LockRecord(HOLDER, STARTED, "engine"))
    world.states.states[HOLDER] = ProcessState.ALIVE

    def release() -> None:
        world.layout.lock_path(world.pin).unlink()

    world.clock.at(1, release)
    world.provision(budget)
    (worker,) = world.children.of("worker")
    assert worker.request.expires is not None
    assert (budget.download, budget.wait, worker.request.expires - worker.at, worker.remaining()) == (download, wait, download, download)
    assert f"--remaining {float(download)!r}" in " ".join(worker.request.arguments)
    assert world.lines[0] == waiting_line(world.pin.version, HOLDER.pid, STARTED, wait)


@pytest.mark.parametrize("value", ["", "-1", "300.5", "600s", " 600", "299", "3601"])
def test_a_refused_value_fails_before_any_guard_probe_child_network_or_cache_access(world: ProvisionWorld, value: str) -> None:
    """Even a valid cached entry is not used: the setup failure comes first and names the variable."""
    world.install()
    files = world.tree()
    with pytest.raises(ProvisioningError) as raised:
        _budget(world, {DOWNLOAD_BUDGET_VARIABLE: value})
    assert (raised.value.stage, raised.value.path, raised.value.version, raised.value.exit_code) == (
        Stage.BUDGET_SETTING, world.entry, world.pin.version, 2)
    assert raised.value.detail == f"{DOWNLOAD_BUDGET_VARIABLE}={value!r} is refused"
    assert (world.opener.opened, world.children.launched, world.mutex.entries, world.tree()) == ([], [], [], files)


def test_a_refused_value_without_a_pin_names_the_cache_root(world: ProvisionWorld) -> None:
    """Before any pin exists, the path named is the cache of the checkout."""
    with pytest.raises(ProvisioningError) as raised:
        provisioning.provisioning_budget({DOWNLOAD_BUDGET_VARIABLE: "0"}, tooling_root=world.layout.tooling_root, pin=None)
    assert (raised.value.path, raised.value.version) == (world.layout.root, None)


def test_a_reset_with_retry_after_keeps_the_delay_and_the_retry_inside_d(world: ProvisionWorld) -> None:
    """The header extends nothing: one 5 s delay, the second attempt gets what is left of 900 s."""
    budget = _budget(world, {DOWNLOAD_BUDGET_VARIABLE: "900"})
    world.children.script("worker", failed("retryable", "HTTPError: HTTP Error 429: Too Many Requests (Retry-After: 2000)"), Child())
    world.provision(budget)
    assert [(launched.request.expires, launched.remaining()) for launched in world.children.of("worker")] == [(900, 900), (900, 895)]
    assert world.clock.sleeps == [5]


def test_a_raised_budget_keeps_every_probe_at_15_seconds(world: ProvisionWorld) -> None:
    """The override is for download and wait only."""
    budget = _budget(world, {DOWNLOAD_BUDGET_VARIABLE: "3600"})
    world.install()
    world.corrupt_record()
    world.provision(budget)
    world.provision(budget)
    assert [launched.request.deadline for launched in world.children.of("probe")] == [15, 15]


def test_a_default_waiter_behind_a_1800_s_holder_fails_at_360_s_and_keeps_its_lock_and_staging(world: ProvisionWorld) -> None:
    """Every caller owns its finite W; a holder's larger D never extends it."""
    budget = _budget(world, {})
    content = world.hold(LockRecord(HOLDER, STARTED, "engine"))
    staging = world.lock_world().attempt(world.pin, HOLDER, OwnerFile(HOLDER).encode())
    world.states.states[HOLDER] = ProcessState.ALIVE
    world.clock.oversleep = 29.75
    with pytest.raises(ProvisioningError) as raised:
        world.provision(budget)
    assert (raised.value.stage, world.clock.elapsed) == (Stage.LOCK_WAIT, 360)
    assert (world.layout.lock_path(world.pin).read_bytes(), staging.is_dir()) == (content, True)


# eof
