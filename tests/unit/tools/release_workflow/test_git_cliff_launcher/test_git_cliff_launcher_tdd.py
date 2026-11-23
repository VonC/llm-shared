"""The gcliff launcher selects the current worktree's pin, provisions it and runs git-cliff with everything passed through.

Step 8 of v0.14.0 git-cliff-provisioning (design "The gcliff launcher",
"Selecting the project and the pin" and "Statuses"; design decisions Q09, Q10
and Q11; requirement clarifications Q08 to Q12). Every case runs the
production bootstrap and `git_cliff/launcher.py` through the launcher
simulation (`gcliff_simulation.py`): the provisioning world stands for the
cache, the Windows layer and the children, the sandbox for Git, and a fake
kernel for the console filter. No process, console handler or socket.

- A nested folder of a worktree declaring `[git-cliff] version = 2.14.2`
  provisions and runs that pin; a plain directory, a bare repository, a `.git`
  directory and a worktree without a pin get the default.
- An invalid unrelated section, an unsafe batch argument, an invalid budget
  value (with a valid entry), a genuine discovery failure, an unusable runtime
  record, a refused child creation or an unconfirmed end each return 69 with
  their diagnostic, and no git-cliff run starts before them; so does a
  manifest that admits no pin, outside a worktree (the configuration stage)
  or inside one (the configured version is not in the empty table).
- git-cliff's arguments, working directory, standard streams, environment
  (`GIT_CLIFF_*` included) and status (1, 2, 3 or 101) pass through; a
  `--workdir` naming another repository never selects that repository's pin.
- The console filter is registered only around the git-cliff run, the same
  routine is removed after a normal return and after a child error, and a
  filter that cannot register returns 69 with the guard released.
- Since code review round 1, a removal that fails after git-cliff ended is
  reported and git-cliff's own status is returned, unlike a registration
  failure before the child.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.gcliff_simulation import (
    GcliffScenario,
    gcliff_scenario,
)
from tests.unit.tools.release_workflow.git_cliff_children_fake import Child
from tests.unit.tools.release_workflow.launcher_simulation import patch_git
from tools.release_workflow import windows_native as native
from tools.release_workflow.git import GitCommandError, WorktreePresence
from tools.release_workflow.git_cliff import launcher
from tools.release_workflow.git_cliff.manifest import ADMITTED_PINS
from tools.release_workflow.runtime_identity import RuntimeIdentity
from tools.release_workflow.windows_child import ChildRequest, ignore_console_interrupts

if TYPE_CHECKING:
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox

_UNAVAILABLE = 69
_CHILD_STATUS = 3
_BUDGET ="LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS"


@pytest.fixture
def scenario(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, git_sandbox: GitSandbox) -> GcliffScenario:
    """A tooling checkout whose cache holds a valid entry of the shipped 2.14.2."""
    built = gcliff_scenario(tmp_path, monkeypatch, git_sandbox)
    built.world.install()
    return built


def _release_ini(root: Path, text: str) -> None:
    """Write a project's `.release.ini`."""
    (root / ".release.ini").write_text(text, encoding="utf-8")


def _printed(request: ChildRequest) -> tuple[int, bytes]:
    """Play git-cliff writing its version to the inherited standard output."""
    sys.stdout.write(f"git-cliff 2.14.2 {' '.join(request.arguments)}\n")
    return 0, b""


def _guards_closed(scenario: GcliffScenario) -> bool:
    """Tell whether every guard the launcher opened is closed again."""
    return all(guard.closed for guard in scenario.world.opener.opened)


def test_a_nested_folder_runs_the_pin_of_its_worktree(scenario: GcliffScenario) -> None:
    """`gcliff --version` in a nested folder provisions that worktree's declared pin and runs it, passing everything through."""
    root = scenario.sandbox.home / "B"
    _release_ini(root, "[git-cliff]\nversion = 2.14.2\n")
    scenario.world.run_output = _printed
    result = scenario.run("--version", cwd=root / "sub")
    assert (result.returncode, result.stdout, result.stderr) == (0, b"git-cliff 2.14.2 --version\n", b"")
    (run,) = scenario.runs
    request = run.request
    assert (request.executable, request.arguments, request.cwd) == (scenario.world.executable, ("--version",), root / "sub")
    assert (request.stdin, request.output, request.deadline) == ("inherit", "inherit", None)
    assert request.environment == dict(scenario.sandbox.environment)
    assert request.inherited == (scenario.world.opener.opened[0].handle,)
    assert scenario.world.lines == []
    assert _guards_closed(scenario)


@pytest.mark.parametrize("place", ["plain", "bare.git", "B/.git", "B"])
def test_without_a_worktree_or_a_pin_the_default_runs(place: str, scenario: GcliffScenario) -> None:
    """A plain directory, a bare repository, a `.git` directory and a worktree without `[git-cliff]` run the default 2.14.2."""
    directory = scenario.sandbox.home / place
    directory.mkdir(exist_ok=True)
    if place == "bare.git":
        scenario.sandbox.declare_presence(directory, WorktreePresence.NO_WORKTREE)
    result = scenario.run("--unreleased", cwd=directory)
    assert (result.returncode, result.stderr) == (0, b"")
    (run,) = scenario.runs
    assert (run.request.executable, run.request.cwd) == (scenario.world.executable, directory)


def test_an_invalid_unrelated_section_returns_69_before_any_child(scenario: GcliffScenario) -> None:
    """The whole `.release.ini` is validated: an invalid `[source:npm]` section is the reader diagnostic and status 69."""
    _release_ini(scenario.sandbox.home / "B", "[source:npm]\nunexpected = value\n")
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B" / "sub")
    assert (result.returncode, result.stdout) == (_UNAVAILABLE, b"")
    assert b"gcliff: Unknown configuration key:" in result.stderr
    assert b"[source:npm] unexpected='value'" in result.stderr
    assert (scenario.world.children.launched, scenario.world.guard_opens) == ([], 0)


@pytest.mark.parametrize("status", [1, 2, 3, 101])
def test_git_cliffs_own_status_is_returned_unchanged(status: int, scenario: GcliffScenario) -> None:
    """A failing render, a usage error, any other status or a panic reach the caller as git-cliff returned them."""
    scenario.world.children.script("run", Child(status=status))
    result = scenario.run("--no-such-flag", cwd=scenario.sandbox.home / "B")
    assert (result.returncode, result.stderr) == (status, b"")


def test_a_target_argument_never_selects_another_repositorys_pin(scenario: GcliffScenario) -> None:
    """`--workdir` and `--repository` naming A stay git-cliff's arguments: B's pin runs, A's `.release.ini` is never read."""
    other = scenario.sandbox.home / "A"
    _release_ini(other, "[git-cliff]\nversion = 2.15.0\n")
    arguments = ("--workdir", str(other), "--repository", str(other))
    result = scenario.run(*arguments, cwd=scenario.sandbox.home / "B")
    assert result.returncode == 0
    assert scenario.runs[0].request.arguments == arguments


@pytest.mark.parametrize("token", ["50%", "a^b", "wow!", 'say"hi'])
def test_an_unsafe_batch_argument_returns_69_before_any_work(token: str, scenario: GcliffScenario) -> None:
    """`%`, `^`, `!` and `"` cannot pass the batch launcher safely: 69, naming `cliff.toml` as their place."""
    result = scenario.run("--tag", token, cwd=scenario.sandbox.home / "B")
    assert result.returncode == _UNAVAILABLE
    assert b"put such values in cliff.toml" in result.stderr
    assert (scenario.world.children.launched, scenario.world.guard_opens) == ([], 0)


def test_an_invalid_budget_returns_69_even_with_a_valid_entry(scenario: GcliffScenario) -> None:
    """The budget variable is validated before the reuse check: the valid entry is neither guarded nor probed."""
    environment = dict(scenario.sandbox.environment, **{_BUDGET: "600s"})
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B", environment=environment)
    assert result.returncode == _UNAVAILABLE
    assert b"(budget-setting stage)" in result.stderr
    assert f"{_BUDGET}='600s' is refused".encode() in result.stderr
    assert (scenario.world.children.launched, scenario.world.guard_opens) == ([], 0)


def test_git_cliff_variables_and_the_user_environment_reach_the_child(scenario: GcliffScenario) -> None:
    """The passthrough policy keeps every variable, `GIT_CLIFF_*` in any case and the legacy location names included."""
    environment = dict(scenario.sandbox.environment, GIT_CLIFF_CONFIG="cliff.toml", git_cliff_workdir="docs", PRJ_DIR="elsewhere")
    assert scenario.run("-u", cwd=scenario.sandbox.home / "B", environment=environment).returncode == 0
    assert scenario.runs[0].request.environment == environment


def test_the_console_filter_surrounds_the_git_cliff_run_only(scenario: GcliffScenario) -> None:
    """The reuse probe starts with no filter, the run with the routine registered; the same routine is removed after it."""
    assert scenario.run("--version", cwd=scenario.sandbox.home / "B").returncode == 0
    (probe, before), (run, during) = scenario.consoles
    assert (probe, before, run) == (("--version",), (), ("--version",))
    ((routine, added),) = during
    assert (added, isinstance(routine, native.PHANDLER_ROUTINE)) == (1, True)
    assert scenario.kernel.handlers == [(routine, 1), (routine, 0)]


@pytest.mark.parametrize(("child", "stage"), [
    (Child(containment=True), b"(containment stage)"),
    (Child(unconfirmed="after-run"), b"is unconfirmed"),
])
def test_a_refused_or_unconfirmed_child_returns_69_and_removes_the_filter(child: Child, stage: bytes, scenario: GcliffScenario) -> None:
    """A creation refused by Windows or a child whose end is unconfirmed is 69; the filter is removed after the error."""
    scenario.world.children.script("run", child)
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert result.returncode == _UNAVAILABLE
    assert stage in result.stderr
    assert [added for _routine, added in scenario.kernel.handlers] == [1, 0]


def test_an_interruption_reported_by_the_run_is_69(scenario: GcliffScenario) -> None:
    """A Ctrl+C that reaches the launcher instead of git-cliff leaves no git-cliff status: 69, interrupted."""
    def interrupted(_request: ChildRequest) -> tuple[int, bytes]:
        raise KeyboardInterrupt

    scenario.world.run_output = interrupted
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert (result.returncode, result.stderr) == (_UNAVAILABLE, b"gcliff: interrupted\n")
    assert [added for _routine, added in scenario.kernel.handlers] == [1, 0]


def test_a_console_filter_that_cannot_register_returns_69_and_releases_the_guard(scenario: GcliffScenario) -> None:
    """No run starts without the filter, and the provisioned entry's guard is released."""
    scenario.kernel.fail("SetConsoleCtrlHandler")
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert result.returncode == _UNAVAILABLE
    assert b"SetConsoleCtrlHandler" in result.stderr
    assert scenario.runs == []
    assert _guards_closed(scenario)


def test_a_filter_removal_failure_after_git_cliff_ended_keeps_its_status(scenario: GcliffScenario) -> None:
    """Code review round 1: the removal Windows refuses after a status-3 run is reported, and 3 is returned, not 69."""
    scenario.world.children.script("run", Child(status=_CHILD_STATUS))
    scenario.kernel.fail("SetConsoleCtrlHandler", occurrence=2)
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert result.returncode == _CHILD_STATUS
    assert result.stderr.startswith(b"gcliff: ")
    assert b"SetConsoleCtrlHandler" in result.stderr
    assert [added for _routine, added in scenario.kernel.handlers] == [1]
    assert len(scenario.runs) == 1
    assert _guards_closed(scenario)


@pytest.mark.parametrize("failure", ["ownership", "configuration"])
def test_a_genuine_discovery_failure_returns_69(failure: str, scenario: GcliffScenario) -> None:
    """A dubious ownership refusal or a rejected Git configuration is a launcher failure, never the default pin."""
    root = scenario.sandbox.home / "B"
    environment = dict(scenario.sandbox.environment)
    if failure == "ownership":
        refusal = subprocess.CompletedProcess(["git"], 128, "", f"fatal: detected dubious ownership in repository at '{root}'\n")
        scenario.sandbox.declare_presence(root, GitCommandError(refusal))
    else:
        selected = scenario.sandbox.home / "chosen.cfg"
        selected.write_text("", encoding="utf-8")
        environment["GIT_CONFIG"] = str(selected)
    result = scenario.run("--version", cwd=root, environment=environment)
    assert result.returncode == _UNAVAILABLE
    assert b"gcliff: Cannot discover project from" in result.stderr
    assert scenario.world.children.launched == []


@pytest.mark.parametrize("place", ["plain", "B"])
def test_a_manifest_admitting_no_pin_returns_69_before_any_child(place: str, scenario: GcliffScenario) -> None:
    """Without an admitted pin, outside a worktree or inside one, git-cliff cannot start: 69 and no child."""
    scenario.pins = ()
    directory = scenario.sandbox.home / place
    directory.mkdir(exist_ok=True)
    result = scenario.run("--version", cwd=directory)
    assert result.returncode == _UNAVAILABLE
    assert (b"(configuration stage)" if place == "plain" else b"not a tested git-cliff pin; tested: none") in result.stderr
    assert (scenario.world.children.launched, scenario.world.guard_opens) == ([], 0)


def test_an_unusable_runtime_record_returns_69_with_the_setup_message(scenario: GcliffScenario) -> None:
    """The bootstrap's readiness gate fails before the launcher: 69 and the setup remedy."""
    (scenario.simulation.root / "venvs/release-runtime.v1.txt").unlink()
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert result.returncode == _UNAVAILABLE
    assert b"Run this checkout's setup" in result.stderr
    assert scenario.world.children.launched == []


def test_without_seams_main_binds_the_production_seams_of_the_verified_runtime(scenario: GcliffScenario,
                                                                              monkeypatch: pytest.MonkeyPatch) -> None:
    """`main` builds its seams from the verified runtime's interpreter, the worker runtime of a download."""
    runtimes: list[Path] = []

    def bound(runtime: Path) -> launcher.LauncherSeams:
        runtimes.append(runtime)
        return scenario.seams()

    monkeypatch.setattr(launcher, "production_seams", bound)
    patch_git(monkeypatch, scenario.sandbox)
    identity = RuntimeIdentity(scenario.simulation.root, "venvs/prepared")
    status = launcher.main(["--version"], original_cwd=scenario.sandbox.home / "B", tooling_root=scenario.simulation.root,
                           runtime=identity, environment=dict(scenario.sandbox.environment))
    assert (status, runtimes) == (0, [identity.executable])


def test_the_production_seams_bind_the_windows_layer_the_console_filter_and_the_shipped_pins() -> None:
    """The service seams run children contained for this runtime; the console filter and the pin table are the shipped ones."""
    runtime = Path("C:/tooling/venvs/prepared/Scripts/python.exe")
    seams = launcher.production_seams(runtime)
    assert (seams.provisioning.runtime, seams.console, seams.pins) == (runtime, ignore_console_interrupts, ADMITTED_PINS)
    assert launcher.GCLIFF_UNAVAILABLE == _UNAVAILABLE


# eof
