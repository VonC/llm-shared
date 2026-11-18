"""A contained child is created suspended inside its own job, recorded, resumed, then ended job-wide.

Step 2 of v0.14.0 git-cliff-provisioning (design "Child process lifecycle" and
"Deadline enforcement"; plan decisions Q04, Q05 and Q14). Every call goes to
the fake kernel, whose log gives the order: the kill-on-close job, the
attribute list holding exactly the job list and the handle list, the listed
handles inheritable only around `CreateProcessW`, the parent's pipe write ends
and `NUL` closed right after it, the recording callback before
`ResumeThread`, then `TerminateJobObject`, the root wait and a zero
`ActiveProcesses` count before the readers reach end of file and every handle
is closed. A normal exit keeps the root's status, expiry returns a timed-out
outcome, and a descendant holding the stdout write end cannot block the call.
The platform baseline is Windows 10 or Windows Server 2016 on x64; the console
filter is a handler routine registered for the guarded block only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from tests.unit.tools.release_workflow.native_kernel_fake import (
    STDERR,
    STDIN,
    STDOUT,
    FakeChild,
    FakeKernel,
)
from tools.release_workflow import windows_child
from tools.release_workflow import windows_native as native
from tools.release_workflow.windows_child import (
    ChildOutcome,
    ChildRequest,
    PlatformError,
    ignore_console_interrupts,
    is_process_in_job,
    require_supported_platform,
    run_contained,
)
from tools.release_workflow.windows_process import ProcessIdentity

_EXECUTABLE = Path("C:/tools/child.exe")
_FLAGS = native.CREATE_SUSPENDED | native.EXTENDED_STARTUPINFO_PRESENT | native.CREATE_UNICODE_ENVIRONMENT
_IDENTITY = ProcessIdentity(4242, FakeChild().created)
_ORDER = [
    "CreateJobObjectW", "SetInformationJobObject", "CreateFileW", "CreatePipe", "CreatePipe",
    "InitializeProcThreadAttributeList", "InitializeProcThreadAttributeList", "UpdateProcThreadAttribute",
    "UpdateProcThreadAttribute", *["GetHandleInformation", "SetHandleInformation"] * 3, "CreateProcessW",
    *["SetHandleInformation"] * 3, "DeleteProcThreadAttributeList", *["CloseHandle"] * 3, "GetProcessTimes", "record",
    "ResumeThread", "WaitForSingleObject", "TerminateJobObject", "WaitForSingleObject", "QueryInformationJobObject",
    "GetExitCodeProcess", *["CloseHandle"] * 5,
]


@dataclass(frozen=True)
class _Version:
    """The part of `sys.getwindowsversion()` the platform check reads."""

    platform_version: tuple[int, int, int]


def _request(**changes: Any) -> ChildRequest:
    """Build a captured request for the fake child."""
    return ChildRequest(_EXECUTABLE, ("--flag", "a b"), **changes)


def _recorded(kernel: FakeKernel) -> ChildRequest:
    """Build a request whose recording callback logs the identity among the kernel calls."""
    def record(identity: ProcessIdentity) -> None:
        kernel.calls.append(("record", (identity,)))

    return _request(record=record)


def _run(kernel: FakeKernel, request: ChildRequest | None = None, sleeps: list[float] | None = None) -> ChildOutcome:
    """Run a request through the fake kernel, recording each poll sleep."""
    return run_contained(request or _request(), api=kernel, sleep=(sleeps if sleeps is not None else []).append)


def _kernel_calls(kernel: FakeKernel) -> list[str]:
    """Return the call names without the reader threads' interleaved reads and pipe ends."""
    return [name for name in kernel.names() if name not in {"ReadFile", "pipe-end"}]


@pytest.mark.parametrize(("version", "machine"), [((10, 0, 19045), "AMD64"), ((10, 0, 14393), "AMD64"), ((10, 0, 26200), "x86_64")])
def test_windows_10_or_server_2016_on_x64_is_supported(version: tuple[int, int, int], machine: str) -> None:
    """Windows 10 and Windows Server 2016 both report platform version 10.0."""
    require_supported_platform(_Version(version), machine)


@pytest.mark.parametrize(("version", "machine"), [((6, 3, 9600), "AMD64"), ((10, 0, 19045), "x86"), ((10, 0, 19045), "ARM64")])
def test_an_older_windows_or_another_architecture_is_refused(version: tuple[int, int, int], machine: str) -> None:
    """Windows 8.1 or Server 2012 R2, 32-bit and ARM machines get the baseline remedy."""
    with pytest.raises(PlatformError, match=r"needs Windows 10 or Windows Server 2016 or later on x64") as raised:
        require_supported_platform(_Version(version), machine)
    assert (raised.value.stage, str(version[0]) in str(raised.value), machine in str(raised.value)) == ("platform", True, True)


def test_request_command_line_and_sorted_environment_block() -> None:
    """The command line is list2cmdline; the block is sorted case-insensitively and double-NUL terminated."""
    kernel = FakeKernel()
    _run(kernel, _request(environment={"b": "2", "A": "1", "=C:": "C:\\work"}, cwd=Path("C:/work")))
    assert kernel.creation is not None
    assert (kernel.creation.application, kernel.creation.command_line) == (str(_EXECUTABLE), f'{_EXECUTABLE} --flag "a b"')
    assert (kernel.creation.environment, kernel.creation.cwd) == ("=C:=C:\\work\0A=1\0b=2\0\0", str(Path("C:/work")))
    _run(empty := FakeKernel(), _request(environment={}))
    assert empty.creation is not None
    assert empty.creation.environment == "\0\0"


@pytest.mark.parametrize("changes", [
    {"environment": {"A=B": "1"}}, {"environment": {"": "1"}}, {"environment": {"A": "x\0y"}},
    {"stdin": "pipe"}, {"output": "file"},
])
def test_an_invalid_request_is_refused_before_any_native_call(changes: dict[str, object]) -> None:
    """Environment names and values and the stream modes are checked when the request is built."""
    with pytest.raises(ValueError, match="invalid"):
        _request(**changes)


def test_creation_order_contains_the_child_before_it_runs() -> None:
    """Job, attribute list, inheritance window, suspended creation, recording, resume, then the job-wide end."""
    kernel = FakeKernel(FakeChild(stdout=b"out", stderr=b"err"))
    outcome = _run(kernel, _recorded(kernel))
    assert outcome == ChildOutcome(0, b"out", b"err", timed_out=False, identity=_IDENTITY)
    assert _kernel_calls(kernel) == _ORDER
    assert kernel.calls[kernel.index("record")][1] == (_IDENTITY,)
    assert kernel.open_handles() == set()


def test_the_job_list_and_handle_list_are_exact_and_inheritable_only_for_creation() -> None:
    """Kill-on-close job, `NUL` stdin, both lists, the inheritance window and the parent's ends closed after creation."""
    kernel = FakeKernel(FakeChild(stdout=b"out", stderr=b"err"))
    _run(kernel, _recorded(kernel))
    creation = kernel.creation
    assert creation is not None
    nul, out_write, err_write = creation.standard
    job = kernel.arguments("SetInformationJobObject")[0]
    assert (kernel.arguments("CreateJobObjectW"), kernel.limits) == ((None, None), {job: native.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE})
    assert kernel.arguments("CreateFileW") == ("NUL", native.GENERIC_READ, native.FILE_SHARE_READ | native.FILE_SHARE_WRITE, None,
                                               native.OPEN_EXISTING, 0, None)
    assert creation.attributes == ((native.PROC_THREAD_ATTRIBUTE_JOB_LIST, (job,)),
                                   (native.PROC_THREAD_ATTRIBUTE_HANDLE_LIST, (nul, out_write, err_write)))
    assert (creation.inherit_handles, creation.flags, creation.inheritable) == (1, _FLAGS, dict.fromkeys(creation.standard, True))
    assert not any(kernel.inheritable[handle] for handle in creation.standard)
    assert [kernel.arguments("CloseHandle", number)[0] for number in (1, 2, 3)] == [err_write, out_write, nul]
    assert kernel.open_handles() == set()


@pytest.mark.parametrize(("stdin", "inherited", "listed"), [
    ("closed", (), None), ("inherit", (), (STDIN, STDOUT)), ("inherit", (0x200,), (STDIN, STDOUT, 0x200)),
])
def test_inherited_streams_and_guards_fill_the_handle_list(stdin: str, inherited: tuple[int, ...], listed: tuple[int, ...] | None) -> None:
    """Passthrough streams are the parent's standard handles, listed once; a guard is appended; inheritance is restored."""
    kernel = FakeKernel(FakeChild(stdout=b"ignored"))
    outcome = _run(kernel, _request(stdin=stdin, output="inherit", inherited=inherited))
    creation = kernel.creation
    assert creation is not None
    assert (outcome.stdout, outcome.stderr, "CreatePipe" in kernel.names()) == (b"", b"", False)
    expected = listed or (creation.standard[0], STDOUT)
    assert creation.standard[1:] == (STDOUT, STDERR)
    assert creation.attributes[1] == (native.PROC_THREAD_ATTRIBUTE_HANDLE_LIST, expected)
    assert creation.inheritable == dict.fromkeys(expected, True)
    assert (kernel.inheritable[STDIN], kernel.inheritable[STDOUT], kernel.inheritable.get(0x200, False)) == (True, True, False)


def test_the_poll_continues_until_no_member_is_active() -> None:
    """Members still counted after termination are polled through the injected sleep, with no budget of its own."""
    kernel = FakeKernel()
    kernel.lingering = 2
    sleeps: list[float] = []
    _run(kernel, sleeps=sleeps)
    assert (kernel.names().count("QueryInformationJobObject"), sleeps) == (3, [windows_child._POLL_SECONDS] * 2)


@pytest.mark.parametrize(("deadline", "milliseconds"), [(None, native.INFINITE), (2.5, 2500), (0.0001, 1), (-1.0, 0)])
def test_the_deadline_bounds_only_the_wait(deadline: float | None, milliseconds: int) -> None:
    """The root wait receives the deadline in milliseconds, rounded up; the reap wait is unbounded."""
    kernel = FakeKernel()
    _run(kernel, _request(deadline=deadline))
    process = kernel.arguments("GetProcessTimes")[0]
    assert [kernel.arguments("WaitForSingleObject", number) for number in (1, 2)] == [(process, milliseconds), (process, native.INFINITE)]


def test_expiry_returns_a_timed_out_outcome() -> None:
    """A root still running at its deadline is terminated with the job, reaped, then reported timed out."""
    kernel = FakeKernel(FakeChild(stdout=b"partial", exits=False))
    outcome = _run(kernel, _request(deadline=1.0))
    assert outcome == ChildOutcome(windows_child._TERMINATED_STATUS, b"partial", b"", timed_out=True, identity=_IDENTITY)
    assert kernel.index("TerminateJobObject") < kernel.index("GetExitCodeProcess")
    assert kernel.open_handles() == set()


@pytest.mark.parametrize("exits", [True, False])
def test_a_descendant_holding_stdout_cannot_block_the_call(*, exits: bool) -> None:
    """The stdout pipe ends only when the job is terminated, so the join comes after it; the root's status is kept."""
    kernel = FakeKernel(FakeChild(status=7, stdout=b"started", exits=exits, descendant=True))
    outcome = _run(kernel, _request(deadline=1.0))
    out_read = kernel.arguments("CreatePipe", 1)[0].value
    assert kernel.calls.index(("pipe-end", (out_read,))) > kernel.index("TerminateJobObject")
    assert (outcome.status, outcome.stdout, outcome.timed_out) == (7 if exits else windows_child._TERMINATED_STATUS, b"started", not exits)
    assert kernel.open_handles() == set()


def test_membership_is_read_for_a_process_and_a_job() -> None:
    """The recorder's job membership query asks for the given process and job."""
    kernel = FakeKernel()
    _run(kernel)
    process, job = kernel.arguments("GetProcessTimes")[0], kernel.arguments("SetInformationJobObject")[0]
    assert (is_process_in_job(process, job, api=kernel), is_process_in_job(process, job + 4, api=kernel)) == (True, False)
    assert kernel.arguments("IsProcessInJob")[:2] == (process, job)


def test_the_console_filter_is_a_handler_routine_removed_after_the_block() -> None:
    """The routine ignores Ctrl+C and Ctrl+Break, stays referenced while registered and is removed on success and errors."""
    kernel = FakeKernel()
    with ignore_console_interrupts(api=kernel):
        ((handler, added),) = kernel.handlers
        assert isinstance(handler, native.PHANDLER_ROUTINE)
        assert added == 1
        assert [handler(event) for event in (native.CTRL_C_EVENT, native.CTRL_BREAK_EVENT, 2, 5)] == [1, 1, 0, 0]
    assert kernel.handlers == [(handler, 1), (handler, 0)]
    failing = FakeKernel()
    message = "launcher failure"
    with pytest.raises(RuntimeError, match=message), ignore_console_interrupts(api=failing):
        raise RuntimeError(message)
    assert [added for _handler, added in failing.handlers] == [1, 0]
    assert failing.handlers[0][0] is failing.handlers[1][0] is not None


# eof
