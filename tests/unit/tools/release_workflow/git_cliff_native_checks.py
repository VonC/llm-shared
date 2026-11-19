"""Record the native checks of the git-cliff provisioning layer on a real kernel, outside pytest.

Step 2 of v0.14.0 git-cliff-provisioning (plan decisions Q06 and Q07). Started
by hand and never imported by a test, from the project root:

    python -m tests.unit.tools.release_workflow.git_cliff_native_checks --milestone step-4
        --output tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json

`--milestone` selects the cumulative due set; Steps 5 and 8 add their
milestones and checks. Each check runs on stand-in children or the real
download worker, on temporary paths outside the repository and
`.tools/git-cliff/`, and ends every process it started. Since code review
round 1 of Step 2, each check runs in its own runner process, this module
started with `--run-check`, through `run_contained` with the check's bound as
deadline: a check that stalls, even inside the production reap, is ended
job-wide with its whole helper tree and recorded `timed-out`. The record's
`recorder_timeout` entry proves that bound on a deliberately stalled runner
whose helper child is alive at the bound and ended after it. Helper parents
are this module started with `--helper`.

Step 4 moved the check bodies and helper parents to
`git_cliff_native_probes.py` (this module had reached the 550 to 650 line
band); this module keeps the catalog, the runner, the record and the command
line. The Step 2 set:

- `job-membership-before-resume`: `IsProcessInJob` of the created child and its
  job, from the recording callback, before `ResumeThread`.
- `suspended-child-ends-with-parent`: a helper records its child and blocks
  before resume; the helper is killed and its suspended child ends, never run.
- `process-limit-refuses-creation`: a helper inside a job limited to one active
  process gets the job-list creation refused; its job counted only itself.
  (A job with UI limits did not refuse the nesting on Windows 11 build 26200.)
- `kill-on-close-running-child`: a helper's running child ends once the helper
  is killed.
- `descendant-holding-stdout`: the root exits while its descendant keeps the
  captured stdout open; the descendant is still alive when the teardown
  starts, the call returns within its bound and the descendant has ended.
- `teardown-failure-exit`: a helper whose `TerminateJobObject` is made to fail
  (an `api` wrapper over the real kernel) while a descendant holds its pipe
  sees the descendant alive after the error, still exits normally, and
  kill-on-close then ends that descendant; the helper runs inside this
  recorder's own bounded job, observed before that job's own termination.
- `guard-held-before-start` and `inherited-guard-during-child`: a rename is
  refused while the guard is held before any child, and while a child runs
  with the inherited guard after the parent closed its own copy.

The Step 4 set adds `worker-ends-at-deadline`: a download worker started
through the bootstrap's `git-cliff-worker` kind, recorded in the owner file
of a disposable staging directory under a temporary tooling root, connects
to a local endpoint that accepts and never answers; its 10 s deadline ends it
job-wide before it writes any outcome, and it is gone afterwards.

The record holds each check's outcome, expected and observed observations,
bound, duration and the LF-normalized SHA-256 of the sources it exercises,
plus the commit, the Windows build and the architecture. It is written with
sorted keys and LF endings, and refused if it still holds a host path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tests.unit.tools.release_workflow.git_cliff_native_probes import (
    KERNEL,
    RECORDER_MODULE,
    ROOT,
    SETTLE,
    CheckTimeoutError,
    Observed,
    check_descendant,
    check_guard_before_start,
    check_inherited_guard,
    check_membership,
    check_parent_killed,
    check_process_limit,
    check_teardown_failure,
    check_worker_deadline,
    run_helper,
)
from tools.release_workflow.windows_child import (
    ChildRequest,
    ContainmentError,
    run_contained,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_MILESTONES = ("step-2", "step-4")
_HOST_PATH = re.compile(r"[A-Za-z]:[\\/]\S*|[\\/](?:Users|home)[\\/]\S*")
_RELEASE = "tools/release_workflow"
_CHILD = (f"{_RELEASE}/windows_native.py", f"{_RELEASE}/windows_child.py", f"{_RELEASE}/windows_process.py",
          "tests/unit/tools/release_workflow/git_cliff_native_checks.py", "tests/unit/tools/release_workflow/git_cliff_native_probes.py")
_GUARD = (*_CHILD, f"{_RELEASE}/windows_guard.py")
_WORKER = (*_CHILD, f"{_RELEASE}/bootstrap.py", f"{_RELEASE}/git_cliff/download_worker.py", f"{_RELEASE}/git_cliff/network.py",
           f"{_RELEASE}/git_cliff/cache.py")
_STALLED = "stalled-runner"
_STALL_BOUND = 3
_STALL_SECONDS = 120
_ABOUT = ("Native checks of the v0.14.0 git-cliff-provisioning Windows child layer, written by "
          "tests/unit/tools/release_workflow/git_cliff_native_checks.py on a real kernel with stand-in children and temporary "
          "paths. A check passes when its observation equals its expectation within its bound; sources holds the LF-normalized "
          "SHA-256 of every repository file the check exercises.")


@dataclass(frozen=True)
class _Check:
    """One native check: its milestone, expected observation, bound, sources and run."""

    identifier: str
    milestone: str
    expected: dict[str, object]
    bound: float
    sources: tuple[str, ...]
    run: Callable[[float, Path], dict[str, object]]


_CHECKS = (
    _Check("job-membership-before-resume", "step-2", {"in_job_before_resume": True, "status": 0, "timed_out": False}, 30, _CHILD,
           check_membership),
    _Check("suspended-child-ends-with-parent", "step-2", {"child_ended": True, "child_ran": False}, 60, _CHILD,
           lambda bound, scratch: check_parent_killed("suspended", bound, scratch)),
    _Check("process-limit-refuses-creation", "step-2",
           {"error": "ContainmentError", "call": "CreateProcessW", "child_ran": False, "job_total_processes": 1}, 60, _CHILD,
           check_process_limit),
    _Check("kill-on-close-running-child", "step-2", {"child_ran": True, "child_ended": True}, 60, _CHILD,
           lambda bound, scratch: check_parent_killed("running", bound, scratch)),
    _Check("descendant-holding-stdout", "step-2",
           {"status": 0, "timed_out": False, "descendant_alive_at_teardown": True, "descendant_ended": True}, 20, _CHILD,
           check_descendant),
    _Check("teardown-failure-exit", "step-2",
           {"helper_error": "UnconfirmedEndError", "helper_call": "TerminateJobObject", "descendant_alive_after_error": True,
            "helper_status": 0, "helper_timed_out": False, "descendant_ended": True}, 60, _CHILD,
           check_teardown_failure),
    _Check("guard-held-before-start", "step-2", {"while_held": "refused", "after_close": "renamed"}, 30, _GUARD,
           check_guard_before_start),
    _Check("inherited-guard-during-child", "step-2",
           {"parent_guard_closed": True, "during_child": "refused", "after_child": "renamed", "status": 0}, 60, _GUARD,
           check_inherited_guard),
    _Check("worker-ends-at-deadline", "step-4",
           {"timed_out": True, "endpoint_connected": True, "worker_recorded": True, "worker_ended": True, "stdout_empty": True}, 60,
           _WORKER, check_worker_deadline),
)


def _run_check(identifier: str, scratch: Path, output: Path) -> int:
    """Runner mode: run one check and write its observation or failure; the stall check never returns."""
    if identifier == _STALLED:
        helper = subprocess.Popen([sys.executable, "-I", "-c", "import time; time.sleep(120)"])  # noqa: S603
        output.write_text(str(helper.pid), encoding="utf-8")
        time.sleep(_STALL_SECONDS)
        return 1
    check = next(check for check in _CHECKS if check.identifier == identifier)
    try:
        report: dict[str, object] = {"observed": check.run(check.bound, scratch)}
    except (CheckTimeoutError, subprocess.TimeoutExpired) as error:
        report = {"outcome": "timed-out", "reason": _HOST_PATH.sub("<path>", str(error))}
    except Exception as error:  # noqa: BLE001 - a check that cannot run is recorded, never raised
        report = {"outcome": "cannot-run", "reason": _HOST_PATH.sub("<path>", f"{type(error).__name__}: {error}")}
    output.write_text(json.dumps(report), encoding="utf-8")
    return 0


def _runner(identifier: str, scratch: Path, output: Path, bound: float, api: Observed | None = None) -> tuple[bool, str]:
    """Run a check in its own runner process, contained and ended job-wide at its bound; return expiry and stderr."""
    request = ChildRequest(Path(sys.executable), ("-m", RECORDER_MODULE, "--run-check", identifier, str(scratch), str(output)), cwd=ROOT,
                           deadline=bound)
    outcome = run_contained(request, api=api)
    return outcome.timed_out, outcome.stderr.decode("utf-8", "replace")[-400:]


def _digest(path: str) -> str:
    """Hash a repository file with LF line endings."""
    return hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _outcome(check: _Check, scratch: Path) -> tuple[str, dict[str, object], dict[str, str]]:
    """Run a check under its bound and read its outcome, observation and details."""
    result = scratch / "result.json"
    try:
        timed_out, errors = _runner(check.identifier, scratch, result, check.bound)
    except ContainmentError as error:
        return "cannot-run", {}, {"reason": _HOST_PATH.sub("<path>", str(error))}
    if timed_out:
        return "timed-out", {}, {"reason": f"the check runner was ended job-wide at its {check.bound} s bound"}
    if not result.exists():
        return "cannot-run", {}, {"reason": _HOST_PATH.sub("<path>", errors) or "the check runner wrote no result"}
    report = json.loads(result.read_text(encoding="utf-8"))
    if "observed" not in report:
        return report["outcome"], {}, {"reason": report["reason"]}
    return ("passed" if report["observed"] == check.expected else "failed"), report["observed"], {}


def _record(check: _Check) -> dict[str, object]:
    """Run one check in its own scratch directory and runner process, and record its outcome."""
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="git-cliff-native-", ignore_cleanup_errors=True) as scratch:
        outcome, observed, details = _outcome(check, Path(scratch))
    duration = round(time.monotonic() - start, 3)
    if outcome == "passed" and duration > check.bound:
        outcome = "timed-out"
    return {"id": check.identifier, "outcome": outcome, "expected": check.expected, "observed": observed, "details": details,
            "bound_seconds": check.bound, "duration_seconds": duration, "sources": {path: _digest(path) for path in check.sources}}


def _demonstrate_timeout() -> dict[str, object]:
    """Run a deliberately stalled runner with a helper child: alive at the bound, the whole tree ended after it."""
    seen: dict[str, Any] = {}
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="git-cliff-native-", ignore_cleanup_errors=True) as scratch:
        pid_file = Path(scratch) / "stalled.pid"

        def before_terminate() -> None:
            seen["handle"] = KERNEL.open_process(int(pid_file.read_text(encoding="utf-8")))
            seen["alive"] = KERNEL.alive(seen["handle"])

        observed = Observed(before_terminate)
        timed_out, _errors = _runner(_STALLED, Path(scratch), pid_file, _STALL_BOUND, observed)
        observed.raise_hook_error()
        ended = KERNEL.ended(seen["handle"], SETTLE)
    return {"bound_seconds": _STALL_BOUND, "duration_seconds": round(time.monotonic() - start, 3),
            "observed": {"timed_out": timed_out, "helper_alive_at_bound": seen["alive"], "helper_tree_ended": ended}}


def main(argv: Sequence[str] | None = None) -> int:
    """Run the due checks of a milestone and write the record, or run one helper parent or check runner."""
    parser = argparse.ArgumentParser(description="Record the native checks of the git-cliff provisioning Windows layer.")
    parser.add_argument("--milestone", choices=_MILESTONES)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--helper", help=argparse.SUPPRESS)
    parser.add_argument("--run-check", help=argparse.SUPPRESS)
    parser.add_argument("helper_arguments", nargs="*", help=argparse.SUPPRESS)
    arguments = parser.parse_args(argv)
    if arguments.helper:
        return run_helper(arguments.helper, arguments.helper_arguments)
    if arguments.run_check:
        return _run_check(arguments.run_check, Path(arguments.helper_arguments[0]), Path(arguments.helper_arguments[1]))
    if arguments.milestone is None or arguments.output is None:
        parser.error("--milestone and --output are required")
    return _record_milestone(arguments.milestone, Path(arguments.output))


def _record_milestone(milestone: str, output: Path) -> int:
    """Run the due checks of a milestone and the timeout demonstration, then write the record."""
    position = _MILESTONES.index(milestone)
    checks = [_record(check) for check in _CHECKS if _MILESTONES.index(check.milestone) <= position]
    timeout = _demonstrate_timeout()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()  # noqa: S603, S607
    record = {"format": 1, "about": _ABOUT, "milestone": milestone, "commit": commit,
              "host": {"windows_build": platform.version(), "architecture": platform.machine()}, "checks": checks,
              "recorder_timeout": timeout}
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if _HOST_PATH.search(text) is not None:
        msg = "the record still holds a host path; nothing was written"
        raise SystemExit(msg)
    output.write_bytes(text.encode("utf-8"))
    for check in checks:
        sys.stdout.write(f"{check['outcome']:>10}  {check['duration_seconds']:>7.3f} s  {check['id']}\n")
    sys.stdout.write(f"  timeout:  {timeout['duration_seconds']:>7.3f} s  {timeout['observed']}\n")
    return 0 if all(check["outcome"] == "passed" for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())


# eof
