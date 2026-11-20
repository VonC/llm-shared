"""The committed native check record passes every check due at its milestone, for the current sources.

Step 2 of v0.14.0 git-cliff-provisioning (plan decisions Q06 and Q07). The
record `native_checks.v1.json` is written by `git_cliff_native_checks.py`,
started by hand outside pytest on a real kernel; no test starts a process or
imports the recorder. For every check due at the record's milestone (the due
sets are cumulative: Steps 4, 5 and 8 add their milestones and checks), the
validator requires outcome `passed`, the expected observation of the catalog
below as both the recorded expectation and the observation, a duration within
the catalog bound, and the LF-normalized SHA-256 of every repository file the
check exercises equal to the current file. The record also names the commit it
was taken on and the Windows build and architecture, and holds no absolute
path, user or host name. Negative records built in memory are each refused.

The Step 2 refused-creation check uses a helper parent inside a job limited to
one active process: on Windows 11 build 26200 a job with UI limits did not
refuse the nesting the design first named (user decision of 2026-11-18).

Code review round 1 of Step 2 bounded every check in its own contained runner
process. The record's `recorder_timeout` entry must show that bound working: a
deliberately stalled runner timed out at its 3 s bound, its helper child alive
at the bound and the whole tree ended after it, within 15 s overall.

Step 4 adds milestone `step-4`: the Step 2 set plus `worker-ends-at-deadline`,
a download worker started through the bootstrap, recorded in a disposable
staging directory and ended job-wide at its deadline while a local endpoint
never answers. The recorder's checks moved to `git_cliff_native_probes.py`,
so every check also binds that file's digest.

Step 5 adds milestone `step-5`: the Step 4 set plus five checks through the
provisioning service with killed helper callers (`git_cliff_native_service.py`):
kill-on-close of a recorded worker and of a git-cliff run, the inherited guard
of a reuse probe and of a git-cliff run refusing the rename after their caller
died, and an abandoned transition mutex of a live holder keeping its record.
Since code review round 1, the two guard checks also prove that the child's
inherited handle names the guarded executable and that a guard-free control
run of the same stand-in leaves the rename possible.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

_ROOT = Path(__file__).resolve().parents[5]
_RECORD = Path(__file__).with_name("native_checks.v1.json")
_MILESTONES = ("step-2", "step-4", "step-5")
_HOST_PATH = re.compile(r"[A-Za-z]:[\\/]|[\\/](?:Users|home)[\\/]")
_COMMIT = re.compile(r"[0-9a-f]{40}")
_NAME_LENGTH = 3
_TIMEOUT_BOUND = 3
_TIMEOUT_LIMIT = 15
_TIMEOUT_EXPECTED = {"timed_out": True, "helper_alive_at_bound": True, "helper_tree_ended": True}
_RELEASE = "tools/release_workflow"
_CLIFF = f"{_RELEASE}/git_cliff"
_CHILD = (f"{_RELEASE}/windows_native.py", f"{_RELEASE}/windows_child.py", f"{_RELEASE}/windows_process.py",
          "tests/unit/tools/release_workflow/git_cliff_native_checks.py", "tests/unit/tools/release_workflow/git_cliff_native_probes.py")
_GUARD = (*_CHILD, f"{_RELEASE}/windows_guard.py")
_WORKER = (*_CHILD, f"{_RELEASE}/bootstrap.py", f"{_CLIFF}/download_worker.py", f"{_CLIFF}/network.py", f"{_CLIFF}/cache.py")
_LOCK = (*_CHILD, "tests/unit/tools/release_workflow/git_cliff_native_service.py", f"{_CLIFF}/cache.py", f"{_CLIFF}/cache_lock.py")
_SERVICE = (*_LOCK, f"{_RELEASE}/windows_guard.py", f"{_CLIFF}/provisioning.py", f"{_CLIFF}/installation.py", f"{_CLIFF}/invocation.py",
            f"{_CLIFF}/messages.py")
_SERVICE_WORKER = (*_SERVICE, f"{_RELEASE}/bootstrap.py", f"{_CLIFF}/download_worker.py", f"{_CLIFF}/network.py")
_GUARD_AFTER_KILL: dict[str, object] = {"caller_dead": True, "child_alive": True, "inherited_handle_is_guard": True, "during_child": "refused",
                                         "child_ended": True, "after_child": "renamed", "control_without_guard": "renamed"}
_STEP_5 = ("worker-ends-with-killed-caller", "git-cliff-run-ends-with-killed-caller", "guard-held-by-reuse-probe-after-caller-killed",
           "guard-held-by-git-cliff-run-after-caller-killed", "abandoned-mutex-keeps-lock-record")


@dataclass(frozen=True)
class _Due:
    """A check of the catalog: its milestone, expected observation, bound in seconds and exercised sources."""

    milestone: str
    expected: dict[str, object]
    bound: float
    sources: tuple[str, ...]


_CHECKS = {
    "job-membership-before-resume": _Due("step-2", {"in_job_before_resume": True, "status": 0, "timed_out": False}, 30, _CHILD),
    "suspended-child-ends-with-parent": _Due("step-2", {"child_ended": True, "child_ran": False}, 60, _CHILD),
    "process-limit-refuses-creation": _Due(
        "step-2", {"error": "ContainmentError", "call": "CreateProcessW", "child_ran": False, "job_total_processes": 1}, 60, _CHILD),
    "kill-on-close-running-child": _Due("step-2", {"child_ran": True, "child_ended": True}, 60, _CHILD),
    "descendant-holding-stdout": _Due(
        "step-2", {"status": 0, "timed_out": False, "descendant_alive_at_teardown": True, "descendant_ended": True}, 20, _CHILD),
    "teardown-failure-exit": _Due("step-2", {"helper_error": "UnconfirmedEndError", "helper_call": "TerminateJobObject",
                                             "descendant_alive_after_error": True, "helper_status": 0, "helper_timed_out": False,
                                             "descendant_ended": True}, 60, _CHILD),
    "guard-held-before-start": _Due("step-2", {"while_held": "refused", "after_close": "renamed"}, 30, _GUARD),
    "inherited-guard-during-child": _Due("step-2", {"parent_guard_closed": True, "during_child": "refused",
                                                    "after_child": "renamed", "status": 0}, 60, _GUARD),
    "worker-ends-at-deadline": _Due("step-4", {"timed_out": True, "endpoint_connected": True, "worker_recorded": True,
                                             "worker_ended": True, "stdout_empty": True}, 60, _WORKER),
    "worker-ends-with-killed-caller": _Due("step-5", {"worker_recorded": True, "endpoint_connected": True, "worker_ended": True,
                                                    "lock_record_kept": True, "staging_kept": True}, 60, _SERVICE_WORKER),
    "git-cliff-run-ends-with-killed-caller": _Due("step-5", {"child_ran": True, "child_ended": True}, 60, _SERVICE),
    "guard-held-by-reuse-probe-after-caller-killed": _Due("step-5", _GUARD_AFTER_KILL, 60, _SERVICE),
    "guard-held-by-git-cliff-run-after-caller-killed": _Due("step-5", _GUARD_AFTER_KILL, 60, _SERVICE),
    "abandoned-mutex-keeps-lock-record": _Due("step-5", {"mutex_abandoned": True, "holder_alive": True, "waiter_error": "LockWaitError",
                                                       "holder_named": True, "record_kept": True}, 30, _LOCK),
}

type Record = dict[str, Any]


def digest(path: Path) -> str:
    """Hash a source file with LF line endings, whatever the checkout's conversion."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _due(milestone: str) -> list[str]:
    """Return the checks due at a milestone: its own and every earlier milestone's."""
    position = _MILESTONES.index(milestone)
    return [identifier for identifier, check in _CHECKS.items() if _MILESTONES.index(check.milestone) <= position]


def _check_refusals(check: Mapping[str, Any], due: _Due, digests: Mapping[str, str]) -> list[str]:
    """Return why one recorded check does not prove its catalog entry."""
    reasons = [] if check.get("outcome") == "passed" else [f"outcome {check.get('outcome')}"]
    if check.get("expected") != due.expected or check.get("observed") != due.expected:
        reasons.append("observation")
    duration = check.get("duration_seconds")
    if check.get("bound_seconds") != due.bound or not isinstance(duration, (int, float)) or not 0 <= duration <= due.bound:
        reasons.append("duration")
    if check.get("sources") != {path: digests[path] for path in due.sources}:
        reasons.append("stale source digest")
    return reasons


def refusals(record: Mapping[str, Any], digests: Mapping[str, str]) -> list[str]:
    """Return every reason the record does not pass its milestone; empty when it passes."""
    milestone = record.get("milestone")
    if milestone not in _MILESTONES:
        return [f"unknown milestone {milestone!r}"]
    reasons = [] if _COMMIT.fullmatch(str(record.get("commit", ""))) else ["commit"]
    host = record.get("host", {})
    if set(host) != {"windows_build", "architecture"} or not all(host.values()):
        reasons.append("host facts")
    checks = {check.get("id"): check for check in record.get("checks", [])}
    for identifier in _due(str(milestone)):
        check = checks.get(identifier)
        found = [f"missing {identifier}"] if check is None else [f"{identifier}: {reason}" for reason in _check_refusals(check, _CHECKS[identifier], digests)]
        reasons.extend(found)
    return reasons + _timeout_refusals(record.get("recorder_timeout", {}))


def _timeout_refusals(timeout: Mapping[str, Any]) -> list[str]:
    """Return why the recorder's stalled-runner demonstration does not prove its bound."""
    duration = timeout.get("duration_seconds")
    proven = (timeout.get("observed") == _TIMEOUT_EXPECTED and timeout.get("bound_seconds") == _TIMEOUT_BOUND
              and isinstance(duration, (int, float)) and _TIMEOUT_BOUND <= duration <= _TIMEOUT_LIMIT)
    return [] if proven else ["recorder timeout"]


@pytest.fixture(scope="session")
def digests() -> dict[str, str]:
    """Hash every source a check exercises, once per session."""
    return {path: digest(_ROOT / path) for path in dict.fromkeys((*_GUARD, *_WORKER, *_SERVICE_WORKER))}


@pytest.fixture(scope="session")
def record() -> Record:
    """Read the committed record once per session."""
    return json.loads(_RECORD.read_bytes())


def _valid(digests: Mapping[str, str]) -> Record:
    """Build a passing record in memory from the catalog."""
    checks = [{"id": identifier, "outcome": "passed", "expected": due.expected, "observed": due.expected, "bound_seconds": due.bound,
               "duration_seconds": due.bound / 2, "sources": {path: digests[path] for path in due.sources}} for identifier, due in _CHECKS.items()]
    return {"format": 1, "milestone": "step-2", "commit": "0" * 40, "host": {"windows_build": "10.0.19045", "architecture": "AMD64"},
            "checks": checks, "recorder_timeout": {"bound_seconds": _TIMEOUT_BOUND, "duration_seconds": 3.5,
                                                   "observed": dict(_TIMEOUT_EXPECTED)}}


def test_the_committed_record_passes_its_milestone(record: Record, digests: dict[str, str]) -> None:
    """Every due check passed, as expected, within its bound, against the current sources."""
    assert (record["format"], record["milestone"]) == (1, "step-5")
    assert refusals(record, digests) == []


def test_the_record_holds_no_absolute_path_user_or_host_name(record: Record) -> None:
    """Only the build and architecture describe the host."""
    text = json.dumps(record)
    assert _HOST_PATH.search(text) is None
    names = [os.environ.get(variable, "") for variable in ("USERNAME", "COMPUTERNAME")]
    assert not [name for name in names if len(name) >= _NAME_LENGTH and name.lower() in text.lower()]


def _set(path: tuple[str | int, ...], value: object) -> Callable[[Record], None]:
    """Return a mutation that replaces one nested value of a record."""
    def mutate(record: Record) -> None:
        target: Any = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


def _drop_first(record: Record) -> None:
    """Remove the first due check."""
    del record["checks"][0]


_FIRST = "job-membership-before-resume"


def test_a_step_4_record_needs_the_worker_check(digests: dict[str, str]) -> None:
    """The Step 4 milestone adds the stalled-endpoint worker check to the Step 2 set."""
    record = _valid(digests)
    record["milestone"] = "step-4"
    assert refusals(record, digests) == []
    record["checks"] = [check for check in record["checks"] if check["id"] != "worker-ends-at-deadline"]
    assert refusals(record, digests) == ["missing worker-ends-at-deadline"]


def test_a_step_5_record_needs_the_five_service_checks(digests: dict[str, str]) -> None:
    """The Step 5 milestone adds the service checks, which a Step 4 record does not need."""
    record = _valid(digests)
    record["checks"] = [check for check in record["checks"] if check["id"] not in _STEP_5]
    record["milestone"] = "step-4"
    assert refusals(record, digests) == []
    record["milestone"] = "step-5"
    assert refusals(record, digests) == [f"missing {identifier}" for identifier in _STEP_5]


@pytest.mark.parametrize(("mutate", "reason"), [
    (_set(("milestone",), "step-3"), "unknown milestone 'step-3'"),
    (_drop_first, f"missing {_FIRST}"),
    (_set(("checks", 0, "outcome"), "failed"), f"{_FIRST}: outcome failed"),
    (_set(("checks", 0, "outcome"), "timed-out"), f"{_FIRST}: outcome timed-out"),
    (_set(("checks", 0, "outcome"), "skipped"), f"{_FIRST}: outcome skipped"),
    (_set(("checks", 0, "observed"), {"in_job_before_resume": False, "status": 0, "timed_out": False}), f"{_FIRST}: observation"),
    (_set(("checks", 0, "duration_seconds"), 31.0), f"{_FIRST}: duration"),
    (_set(("checks", 0, "sources", "tools/release_workflow/windows_child.py"), "0" * 64), f"{_FIRST}: stale source digest"),
    (_set(("commit",), "HEAD"), "commit"),
    (_set(("host",), {"windows_build": "10.0.19045", "architecture": "AMD64", "host": "x"}), "host facts"),
    (_set(("recorder_timeout", "observed", "helper_tree_ended"), value=False), "recorder timeout"),
    (_set(("recorder_timeout", "observed", "timed_out"), value=False), "recorder timeout"),
    (_set(("recorder_timeout", "duration_seconds"), 16.0), "recorder timeout"),
    (_set(("recorder_timeout", "duration_seconds"), 1.0), "recorder timeout"),
])
def test_each_defect_refuses_the_record(digests: dict[str, str], mutate: Callable[[Record], None], reason: str) -> None:
    """An unknown milestone, a missing check, a non-passing outcome, a changed observation, an overrun or a stale digest."""
    valid = _valid(digests)
    assert refusals(valid, digests) == []
    broken = copy.deepcopy(valid)
    mutate(broken)
    assert refusals(broken, digests) == [reason]


# eof
