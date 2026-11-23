"""Acceptance of `gcliff`: the design rows the Step 8 launcher owns, run through the bootstrap's `gcliff-batch` entry.

Step 8 of v0.14.0 git-cliff-provisioning (design "Acceptance cases for the
git-cliff provisioning design", plan "Acceptance ownership map", requirement
acceptance criteria AC2 to AC4). Each row runs the production bootstrap,
launcher, configuration reader and provisioning service against the shipped
manifest through the launcher simulation; the provisioning world stands for
the cache, the Windows layer and the children. Downloads use a synthetic
2.14.2 pin table whose archive the fake worker delivers, since no test
downloads the published asset.

- The warm-up `bin/gcliff.bat --version` in a nested folder of a pinned
  worktree, on an empty cache: one download, the downloading and ready lines
  on standard error, then git-cliff's version on standard output; the next run
  reuses the entry and prints nothing of its own.
- `gcliff` with an invalid `[source:npm]` section: the reader diagnostic,
  status 69, git-cliff not started and the cache untouched.
- `gcliff` with a bad git-cliff argument: git-cliff's own error and status.
- `GIT_CLIFF_*` variables in the console: the engine-policy reuse probe has
  them removed, the `gcliff` run keeps them.
- The download budget through `gcliff`: unset, `900` and `3600` give the
  first worker the whole D and the waiting line W = D + 60; each refused form
  is 69 naming the variable before any guard, child or cache access, also with
  a valid entry; with `900`, a reset answered `Retry-After: 2000` gets one
  5 s delay and a second attempt inside D; `3600` keeps the probe at 15 s; a
  default waiter behind a holder that runs with D = 1800 s is 69 at its own
  360 s, the holder's lock and staging kept.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.gcliff_simulation import (
    GcliffScenario,
    gcliff_scenario,
)
from tests.unit.tools.release_workflow.git_cliff_children_fake import Child, failed
from tests.unit.tools.release_workflow.git_cliff_support import VERSION, synthetic_pin
from tools.release_workflow.git_cliff.budget import DOWNLOAD_BUDGET_VARIABLE
from tools.release_workflow.git_cliff.cache import OwnerFile
from tools.release_workflow.git_cliff.cache_lock import LockRecord
from tools.release_workflow.git_cliff.messages import (
    downloading_line,
    ready_line,
    waiting_line,
)
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox
    from tools.release_workflow.windows_child import ChildRequest

_UNAVAILABLE = 69
_HOLDER = ProcessIdentity(4900, 133_000_000_000_000_900)
_STARTED = "2026-11-18T13:58:00+01:00"


@pytest.fixture
def scenario(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, git_sandbox: GitSandbox) -> GcliffScenario:
    """An empty cache, a tooling checkout and a pin table whose 2.14.2 archive the fake worker can deliver."""
    built = gcliff_scenario(tmp_path, monkeypatch, git_sandbox)
    built.world.pin = synthetic_pin(VERSION)
    built.pins = (built.world.pin,)
    return built


def _version(request: ChildRequest) -> tuple[int, bytes]:
    """Play git-cliff printing its version on the inherited standard output."""
    del request
    sys.stdout.write(f"git-cliff {VERSION}\n")
    return 0, b""


def _environment(scenario: GcliffScenario, **variables: str) -> dict[str, str]:
    """Return the sandbox's environment with more variables."""
    return dict(scenario.sandbox.environment, **variables)


def test_the_warm_up_provisions_a_nested_worktrees_pin_then_reuses_it_silently(scenario: GcliffScenario) -> None:
    """`bin/gcliff.bat --version` downloads once with its two lines, runs the pin, and the next call reuses it."""
    root = scenario.sandbox.home / "B"
    (root / ".release.ini").write_text("[git-cliff]\nversion = 2.14.2\n", encoding="utf-8")
    scenario.world.run_output = _version
    first = scenario.run("--version", cwd=root / "sub")
    assert (first.returncode, first.stdout, first.stderr) == (0, b"git-cliff 2.14.2\n", b"")
    assert scenario.world.lines == [downloading_line(scenario.world.pin), ready_line(VERSION, scenario.world.entry)]
    second = scenario.run("--version", cwd=root / "sub")
    assert (second.returncode, second.stdout) == (0, b"git-cliff 2.14.2\n")
    assert len(scenario.world.lines) == len(("downloading", "ready"))
    assert [launched.role for launched in scenario.world.children.launched] == ["worker", "probe", "run", "probe", "run"]
    assert {run.request.executable for run in scenario.runs} == {scenario.world.executable}


def test_an_invalid_source_section_is_the_reader_diagnostic_and_69(scenario: GcliffScenario) -> None:
    """Whole-file validation: git-cliff is not started and nothing is provisioned."""
    root = scenario.sandbox.home / "B"
    (root / ".release.ini").write_text("[git-cliff]\nversion = 2.14.2\n[source:npm]\nunexpected = value\n", encoding="utf-8")
    result = scenario.run("--version", cwd=root / "sub")
    assert (result.returncode, result.stdout) == (_UNAVAILABLE, b"")
    assert b"Unknown configuration key:" in result.stderr
    assert (scenario.world.children.launched, scenario.world.tree()) == ([], {})


def test_a_bad_git_cliff_argument_gives_git_cliffs_own_error_and_status(scenario: GcliffScenario) -> None:
    """Passthrough: git-cliff reports a usage error on the inherited standard error and returns 2."""
    def usage(_request: ChildRequest) -> tuple[int, bytes]:
        sys.stderr.write("error: unexpected argument '--frobnicate' found\n")
        return 2, b""

    scenario.world.install()
    scenario.world.run_output = usage
    result = scenario.run("--frobnicate", cwd=scenario.sandbox.home / "B")
    assert (result.returncode, result.stderr) == (2, b"error: unexpected argument '--frobnicate' found\n")


def test_git_cliff_variables_are_removed_from_the_probe_and_kept_for_the_run(scenario: GcliffScenario,
                                                                            monkeypatch: pytest.MonkeyPatch) -> None:
    """One place for the environment rule: the engine policy drops `GIT_CLIFF_*`, the passthrough policy keeps them."""
    monkeypatch.setenv("GIT_CLIFF_CONFIG", "elsewhere.toml")
    scenario.world.install()
    environment = _environment(scenario, GIT_CLIFF_CONFIG="elsewhere.toml", Git_Cliff_Tag="v9.9.9")
    assert scenario.run("--unreleased", cwd=scenario.sandbox.home / "B", environment=environment).returncode == 0
    (probe,) = scenario.world.children.of("probe")
    assert probe.request.environment is not None
    assert not [name for name in probe.request.environment if name.upper().startswith("GIT_CLIFF_")]
    assert scenario.runs[0].request.environment == environment


@pytest.mark.parametrize(("value", "download", "wait"), [(None, 300, 360), ("900", 900, 960), ("3600", 3600, 3660)])
def test_the_budget_reaches_the_worker_and_the_waiting_line_through_gcliff(*, value: str | None, download: int, wait: int,
                                                                          scenario: GcliffScenario) -> None:
    """The first attempt receives the whole D and the waiting line shows W, from the console's variable."""
    world = scenario.world
    world.hold(LockRecord(_HOLDER, _STARTED, "engine"))
    world.states.states[_HOLDER] = ProcessState.ALIVE

    def release() -> None:
        world.layout.lock_path(world.pin).unlink()

    world.clock.at(1, release)
    environment = _environment(scenario) if value is None else _environment(scenario, **{DOWNLOAD_BUDGET_VARIABLE: value})
    assert scenario.run("--version", cwd=scenario.sandbox.home / "B", environment=environment).returncode == 0
    (worker,) = world.children.of("worker")
    assert worker.request.expires is not None
    assert (worker.request.expires - worker.at, worker.remaining()) == (download, download)
    assert world.lines[0] == waiting_line(VERSION, _HOLDER.pid, _STARTED, wait)


@pytest.mark.parametrize("value", ["", "-1", "300.5", "600s", " 600", "299", "3601"])
def test_a_refused_budget_is_69_before_anything_even_with_a_valid_entry(value: str, scenario: GcliffScenario) -> None:
    """The setup failure names the variable and its range; the valid entry is neither guarded, probed nor changed."""
    scenario.world.install()
    files = scenario.world.tree()
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B", environment=_environment(scenario, **{DOWNLOAD_BUDGET_VARIABLE: value}))
    assert result.returncode == _UNAVAILABLE
    assert f"{DOWNLOAD_BUDGET_VARIABLE}={value!r} is refused".encode() in result.stderr
    assert b"from 300 through 3600" in result.stderr
    assert (scenario.world.opener.opened, scenario.world.children.launched, scenario.world.tree()) == ([], [], files)


def test_a_retry_after_a_reset_stays_inside_the_raised_budget_through_gcliff(scenario: GcliffScenario) -> None:
    """With D = 900 s, a 429 with `Retry-After: 2000` gives one 5 s delay, and the second attempt gets what is left of D."""
    scenario.world.children.script("worker", failed("retryable", "HTTPError: HTTP Error 429: Too Many Requests (Retry-After: 2000)"), Child())
    environment = _environment(scenario, **{DOWNLOAD_BUDGET_VARIABLE: "900"})
    assert scenario.run("--version", cwd=scenario.sandbox.home / "B", environment=environment).returncode == 0
    workers = scenario.world.children.of("worker")
    assert [(launched.request.expires, launched.remaining()) for launched in workers] == [(900, 900), (900, 895)]
    assert scenario.world.clock.sleeps == [5]


def test_a_raised_budget_keeps_the_probe_at_15_seconds_through_gcliff(scenario: GcliffScenario) -> None:
    """The override is for download and wait only: the staging probe of a repaired entry keeps 15 s."""
    scenario.world.install()
    scenario.world.corrupt_record()
    environment = _environment(scenario, **{DOWNLOAD_BUDGET_VARIABLE: "3600"})
    assert scenario.run("--version", cwd=scenario.sandbox.home / "B", environment=environment).returncode == 0
    probes = scenario.world.children.of("probe")
    assert probes
    assert {launched.request.deadline for launched in probes} == {15}


def test_a_default_waiter_behind_an_1800_s_holder_is_69_at_360_s(scenario: GcliffScenario) -> None:
    """A holder's larger D never extends this caller's W; the live holder's lock record and staging stay."""
    world = scenario.world
    content = world.hold(LockRecord(_HOLDER, _STARTED, "engine"))
    staging = world.lock_world().attempt(world.pin, _HOLDER, OwnerFile(_HOLDER).encode())
    world.states.states[_HOLDER] = ProcessState.ALIVE
    world.clock.oversleep = 29.75
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert result.returncode == _UNAVAILABLE
    assert b"(lock-wait stage)" in result.stderr
    assert world.clock.elapsed == 360  # noqa: PLR2004 - the default W
    assert (world.layout.lock_path(world.pin).read_bytes(), staging.is_dir(), scenario.runs) == (content, True, [])


# eof
