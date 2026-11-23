"""The invocation object is the only way to start git-cliff: contained, guarded, under one of two environment policies.

Step 5 of v0.14.0 git-cliff-provisioning (design "The provisioning entry point
for items 4 and 5" and "Version probe"; design decisions Q07, Q09 and Q17).
The engine policy removes every `GIT_CLIFF_*` variable in any case, from the
given environment or the process one, closes standard input and captures or
inherits output as asked; the passthrough policy keeps the given environment
(or inherits the process one), the working directory and the standard
streams. Both put the use guard's handle in the child's inherited-handle list
and close the object's own guard only once the child has ended, or at once
when the creation fails. An unconfirmed end retains the guard copy instead.
One object starts one git-cliff run. The version probe request follows the
engine policy with the probe's own budget.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import (
    PROBE_IDENTITY,
    FakeGuard,
)
from tools.release_workflow.git_cliff.invocation import (
    GitCliffInvocation,
    Policy,
    engine_environment,
    probe_request,
)
from tools.release_workflow.git_cliff.messages import ProvisioningError, Stage
from tools.release_workflow.windows_child import (
    ChildOutcome,
    ChildRequest,
    ContainmentError,
    UnconfirmedEndError,
)
from tools.release_workflow.windows_process import ProcessIdentity

EXECUTABLE = Path("C:/llm-shared/.tools/git-cliff/2.14.2/x86_64-pc-windows-msvc/git-cliff.exe")
WORK = Path("C:/project")
AMBIENT = {"GIT_CLIFF_CONFIG": "x.toml", "git_cliff_workdir": "w", "Git_Cliff_Token": "t", "GIT_CLIFFORD": "kept", "PATH": "C:/bin"}


@dataclass
class Launcher:
    """A child launcher that records each request and whether the guard was still open while the child ran."""

    guard: FakeGuard
    error: Exception | None = None
    requests: list[ChildRequest] = field(default_factory=list[ChildRequest])
    guard_open_during_child: list[bool] = field(default_factory=list[bool])

    def __call__(self, request: ChildRequest) -> ChildOutcome:
        """Start one child, or fail as the native layer would."""
        self.requests.append(request)
        self.guard_open_during_child.append(not self.guard.closed)
        if self.error is not None:
            raise self.error
        return ChildOutcome(status=3, stdout=b"rendered", stderr=b"", timed_out=False, identity=PROBE_IDENTITY)


def _invocation(error: Exception | None = None) -> tuple[GitCliffInvocation, Launcher, FakeGuard]:
    """Build an invocation over a fake guard and a recording launcher."""
    guard = FakeGuard(EXECUTABLE, 1234)
    launcher = Launcher(guard, error)
    return GitCliffInvocation(EXECUTABLE, "2.14.2", guard, launch=launcher), launcher, guard


def test_the_engine_policy_removes_every_git_cliff_variable_closes_stdin_and_captures() -> None:
    """Upstream settings cannot reach an engine run; other variables do."""
    invocation, launcher, guard = _invocation()
    outcome = invocation.run(["--unreleased"], policy=Policy.ENGINE, cwd=WORK, environment=AMBIENT, deadline=30.0)
    request = launcher.requests[0]
    assert (outcome.status, outcome.stdout) == (3, b"rendered")
    assert request.environment == {"GIT_CLIFFORD": "kept", "PATH": "C:/bin"}
    assert (request.executable, request.arguments, request.cwd, request.stdin, request.output) == (
        EXECUTABLE, ("--unreleased",), WORK, "closed", "capture")
    assert (request.inherited, request.deadline, request.record) == ((1234,), 30.0, None)
    assert (launcher.guard_open_during_child, guard.closed) == ([True], True)


def test_the_engine_policy_reads_the_process_environment_when_none_is_given(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without an explicit environment, the process one is copied without its git-cliff variables."""
    monkeypatch.setenv("GIT_CLIFF_OUTPUT", "elsewhere.md")
    monkeypatch.setenv("LLM_SHARED_PROBE_MARK", "kept")
    invocation, launcher, _guard = _invocation()
    invocation.run(["--version"], policy=Policy.ENGINE, cwd=WORK, output="inherit")
    environment = launcher.requests[0].environment or {}
    assert "GIT_CLIFF_OUTPUT" not in {name.upper() for name in environment}
    assert environment["LLM_SHARED_PROBE_MARK"] == "kept"
    assert (launcher.requests[0].stdin, launcher.requests[0].output) == ("closed", "inherit")


def test_engine_environment_matches_any_case_and_only_the_prefix() -> None:
    """The removal rule lives in one function, shared by runs and probes."""
    assert engine_environment(AMBIENT) == {"GIT_CLIFFORD": "kept", "PATH": "C:/bin"}


def test_the_passthrough_policy_keeps_the_environment_directory_and_streams() -> None:
    """`gcliff` hands git-cliff the user's environment, working directory and console."""
    invocation, launcher, guard = _invocation()
    invocation.run(["--bad-flag"], policy=Policy.PASSTHROUGH, cwd=WORK, environment=AMBIENT, output="inherit")
    request = launcher.requests[0]
    assert (request.environment, request.cwd, request.stdin, request.output, request.inherited) == (AMBIENT, WORK, "inherit", "inherit", (1234,))
    assert guard.closed


def test_the_passthrough_policy_inherits_the_process_environment_when_none_is_given() -> None:
    """No environment block is built: the child inherits the launcher's own."""
    invocation, launcher, _guard = _invocation()
    invocation.run([], policy=Policy.PASSTHROUGH, cwd=WORK, output="inherit")
    assert launcher.requests[0].environment is None


def test_the_passthrough_policy_refuses_captured_output_and_closes_the_guard() -> None:
    """Passthrough always inherits the streams; a refused start creates no child and releases the guard."""
    invocation, launcher, guard = _invocation()
    with pytest.raises(ValueError, match="passthrough policy inherits"):
        invocation.run([], policy=Policy.PASSTHROUGH, cwd=WORK)
    assert (launcher.requests, guard.closed) == ([], True)


def test_a_refused_creation_closes_the_guard_at_once_with_the_containment_stage() -> None:
    """No child exists, so nothing needs the guard any more."""
    refused = ContainmentError("cannot contain git-cliff.exe: CreateProcessW failed", call="CreateProcessW", error=1816)
    invocation, _launcher, guard = _invocation(refused)
    with pytest.raises(ProvisioningError) as raised:
        invocation.run([], policy=Policy.ENGINE, cwd=WORK, environment={})
    assert (raised.value.stage, raised.value.path, raised.value.version) == (Stage.CONTAINMENT, EXECUTABLE.parent, "2.14.2")
    assert raised.value.__cause__ is refused
    assert (guard.closed, guard.retained) == (True, False)


def test_an_unconfirmed_end_retains_the_guard_copy() -> None:
    """The child may still run the binary: the guard stays open until this process ends."""
    unconfirmed = UnconfirmedEndError(pid=4242, identity=ProcessIdentity(4242, 77), call="TerminateJobObject", error=5)
    invocation, _launcher, guard = _invocation(unconfirmed)
    with pytest.raises(ProvisioningError) as raised:
        invocation.run([], policy=Policy.ENGINE, cwd=WORK, environment={})
    assert raised.value.stage is Stage.CONTAINMENT
    assert "use guard stays open" in raised.value.detail
    assert (guard.retained, guard.closed) == (True, False)


def test_an_invocation_starts_one_run_only() -> None:
    """The guard ended with the first run, so a second start is refused before any child."""
    invocation, launcher, _guard = _invocation()
    invocation.run([], policy=Policy.ENGINE, cwd=WORK, environment={})
    with pytest.raises(ValueError, match="already been used"):
        invocation.run([], policy=Policy.ENGINE, cwd=WORK, environment={})
    assert len(launcher.requests) == 1


def test_an_unused_invocation_releases_its_guard_on_close_or_at_the_end_of_a_block() -> None:
    """A caller that fails before starting git-cliff still drops the guard."""
    invocation, launcher, guard = _invocation()
    with invocation as used:
        assert (used.executable, used.version) == (EXECUTABLE, "2.14.2")
    assert (guard.closed, launcher.requests) == (True, [])
    with pytest.raises(ValueError, match="already been used"):
        invocation.run([], policy=Policy.ENGINE, cwd=WORK, environment={})


def test_the_probe_request_follows_the_engine_policy_with_its_own_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    """`--version` in the executable's directory, input closed, output captured, guards and recorder as given."""
    monkeypatch.setenv("git_cliff_config", "ambient.toml")

    def record(identity: ProcessIdentity) -> None:
        del identity

    request = probe_request(EXECUTABLE, inherited=(1234,), deadline=15, record=record)
    assert (request.executable, request.arguments, request.cwd, request.stdin, request.output) == (
        EXECUTABLE, ("--version",), EXECUTABLE.parent, "closed", "capture")
    assert (request.inherited, request.deadline, request.record) == ((1234,), 15, record)
    assert "GIT_CLIFF_CONFIG" not in {name.upper() for name in request.environment or {}}


# eof
