"""Every failure of the contained lifecycle leaves no running child, or retains what it cannot confirm.

Step 2 of v0.14.0 git-cliff-provisioning (design "Child process lifecycle";
plan decisions Q04 and Q05). One test per failing call, read from the fake
kernel's log. Setup and creation faults (job, configuration, `NUL`, pipes,
attribute list sizing, initialization, each update, `CreateProcessW` with a
refused nesting) raise `ContainmentError` with no resume, no other creation
path and every handle closed. Pre-resume faults (identity, recording callback,
`ResumeThread`) and a failed deadline wait end the job, confirm the end and
only then raise; an interrupt from the callback propagates after the same end.
A failing termination, reap wait or accounting query raises
`UnconfirmedEndError` at once: no join, no `CloseHandle` of the job, process,
thread or pipe read handles, which now belong to `RETAINED`, while the daemon
readers stay on their native handles. A failed identity lookup followed by a
failed teardown reports `identity=None` with the PID from `CreateProcessW`,
after no resume and no recording.

Code review round 1 added the settling cases. A failed inheritance reset or
close keeps its handle, still releases every other one and is retried while
settling; what remains is named in `ContainmentError.cleanup` and owned by
`RETAINED`, also after a refused creation. A Ctrl+C during setup, right after
creation, while polling, or repeatedly during the recovery, never cuts the end
or the release short: it is raised once the run is settled, a termination is
not repeated, and an unconfirmed end still wins. An error while polling is an
unconfirmed end.

Code review round 2 added the reviewer's sequences: a failed close followed by
a Ctrl+C, a failed close left behind an interrupt from the callback (retained
and noted), and a Ctrl+C right after enabling a guard's inheritance, creating
the process, or acquiring a job, `NUL`, a pipe or the attribute list. The fake
delivers a Ctrl+C to the Python SIGINT handler, which a run on the main thread
replaces with its deferring handler only when the default one is installed;
every case runs on the default handler, and no handle is closed twice.
"""

from __future__ import annotations

import ctypes
import signal
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.release_workflow.native_kernel_fake import FakeChild, FakeKernel
from tools.release_workflow.windows_child import (
    RETAINED,
    ChildRequest,
    ContainmentError,
    RetainedChild,
    UnconfirmedEndError,
    run_contained,
)
from tools.release_workflow.windows_process import ProcessIdentity

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

_IDENTITY = ProcessIdentity(4242, FakeChild().created)
_INVALID_HANDLE = 6
_GUARD = 0x200
_SETUP_FAULTS = [
    ("CreateJobObjectW", 1), ("SetInformationJobObject", 1), ("CreateFileW", 1), ("CreatePipe", 1), ("CreatePipe", 2),
    ("InitializeProcThreadAttributeList", 1), ("InitializeProcThreadAttributeList", 2), ("UpdateProcThreadAttribute", 1),
    ("UpdateProcThreadAttribute", 2), ("CreateProcessW", 1),
]


def _request(**changes: Any) -> ChildRequest:
    """Build a captured request for the fake child."""
    return ChildRequest(Path("C:/tools/child.exe"), ("--version",), **changes)


def _ignore(identity: ProcessIdentity) -> None:
    """Record nothing."""
    del identity


def _refuse(identity: ProcessIdentity) -> None:
    """Fail the recording, as a refused lock record write would."""
    msg = f"cannot record {identity.pid}"
    raise ValueError(msg)


def _interrupt(identity: ProcessIdentity) -> None:
    """Interrupt the parent while the child is suspended."""
    del identity
    raise KeyboardInterrupt


@pytest.fixture(autouse=True)
def default_sigint() -> Iterator[None]:
    """Run each case on Python's default SIGINT handler, the one a contained run defers; restore the previous one."""
    previous = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.default_int_handler)
    yield
    if previous is not None:
        signal.signal(signal.SIGINT, previous)


def _assert_ended_then_closed(kernel: FakeKernel) -> None:
    """The job was terminated, the root reaped and the count read, then every handle was closed exactly once."""
    names = [name for name in kernel.names() if name not in {"ReadFile", "pipe-end"}]
    steps = [names.index(step) for step in ("TerminateJobObject", "QueryInformationJobObject")]
    assert steps == sorted(steps)
    assert names[steps[0] + 1] == "WaitForSingleObject"
    assert kernel.open_handles() == set()
    assert len(kernel.closed) == len(set(kernel.closed))


@pytest.mark.parametrize(("call", "occurrence"), _SETUP_FAULTS)
def test_setup_and_creation_faults_leave_no_child(call: str, occurrence: int) -> None:
    """No resume, no second creation path, every created handle closed and the list deleted once initialized."""
    kernel = FakeKernel()
    kernel.fail(call, occurrence=occurrence)
    with pytest.raises(ContainmentError) as raised:
        run_contained(_request(), api=kernel)
    assert type(raised.value) is ContainmentError
    assert (raised.value.call, raised.value.error, raised.value.stage) == (call, 5, "containment")
    names = kernel.names()
    assert not {"ResumeThread", "AssignProcessToJobObject", "TerminateJobObject"} & set(names)
    assert names.count("CreateProcessW") == int(call == "CreateProcessW")
    assert kernel.open_handles() == set()
    assert ("DeleteProcThreadAttributeList" in names) is (call in {"UpdateProcThreadAttribute", "CreateProcessW"})
    assert not any(kernel.inheritable.get(handle, False) for handle in kernel.created)


def test_a_missing_standard_handle_is_a_containment_failure() -> None:
    """A passthrough stream the parent lacks fails the setup like any other native call."""
    kernel = FakeKernel()
    kernel.fail("GetStdHandle", occurrence=2, error=_INVALID_HANDLE)
    with pytest.raises(ContainmentError, match="GetStdHandle") as raised:
        run_contained(_request(stdin="inherit", output="inherit"), api=kernel)
    assert raised.value.error == _INVALID_HANDLE
    assert kernel.open_handles() == set()


@pytest.mark.parametrize("fault", ["GetProcessTimes", "record", "ResumeThread"])
def test_pre_resume_faults_end_the_job_before_raising(fault: str) -> None:
    """The child never ran: the job is ended and confirmed, then `ContainmentError` names the failing step."""
    kernel = FakeKernel()
    if fault != "record":
        kernel.fail(fault)
    with pytest.raises(ContainmentError) as raised:
        run_contained(_request(record=_refuse if fault == "record" else _ignore), api=kernel)
    assert (type(raised.value), raised.value.call) == (ContainmentError, fault)
    assert kernel.names().count("ResumeThread") == int(fault == "ResumeThread")
    assert "ReadFile" not in kernel.names()
    _assert_ended_then_closed(kernel)


def test_an_interrupt_while_recording_propagates_after_the_end() -> None:
    """A KeyboardInterrupt from the callback is not wrapped, but the suspended child is still ended first."""
    kernel = FakeKernel()
    with pytest.raises(KeyboardInterrupt):
        run_contained(_request(record=_interrupt), api=kernel)
    assert "ResumeThread" not in kernel.names()
    _assert_ended_then_closed(kernel)


@pytest.mark.parametrize(("call", "occurrence"), [("WaitForSingleObject", 1), ("GetExitCodeProcess", 1), ("ReadFile", 1)])
def test_faults_after_resume_raise_once_the_end_is_confirmed(call: str, occurrence: int) -> None:
    """A failed deadline wait, status read or pipe read is reported after the job-wide end and the closes."""
    kernel = FakeKernel(FakeChild(stdout=b"out", stderr=b"err"))
    kernel.fail(call, occurrence=occurrence, error=_INVALID_HANDLE)
    with pytest.raises(ContainmentError) as raised:
        run_contained(_request(), api=kernel)
    assert (type(raised.value), raised.value.call, raised.value.error) == (ContainmentError, call, _INVALID_HANDLE)
    _assert_ended_then_closed(kernel)


def _assert_retained(kernel: FakeKernel, call: str, before: int) -> tuple[int, ...]:
    """The job, process, thread and pipe read handles are owned by `RETAINED` and none was closed; return the read ends."""
    process, thread = kernel.arguments("GetProcessTimes")[0], kernel.arguments("ResumeThread")[0]
    job = kernel.arguments("SetInformationJobObject")[0]
    reads = tuple(kernel.arguments("CreatePipe", number)[0].value for number in (1, 2))
    assert RETAINED.entries()[before:] == (RetainedChild(4242, _IDENTITY, call, (job, process, thread, *reads)),)
    assert not {job, process, thread, *reads} & set(kernel.closed)
    assert "GetExitCodeProcess" not in kernel.names()
    return reads


def _assert_unjoined_daemon_readers(kernel: FakeKernel, reads: tuple[int, ...], *, held: bool) -> None:
    """Readers are daemon threads on the native read handles with private buffers; a held pipe's reader still runs."""
    readers = {handle: (reader, buffer) for handle, reader, buffer in kernel.readers}
    assert set(readers) <= set(reads)
    assert all(reader.daemon and isinstance(buffer, ctypes.Array) for reader, buffer in readers.values())
    assert readers[reads[0]][0].is_alive() or not held


@pytest.mark.parametrize(("call", "occurrence"), [("TerminateJobObject", 1), ("WaitForSingleObject", 2), ("QueryInformationJobObject", 1)])
def test_an_unconfirmed_end_retains_every_handle_and_joins_no_reader(call: str, occurrence: int) -> None:
    """The error names the child and the call; nothing is joined or closed; the handles belong to `RETAINED`."""
    kernel = FakeKernel(FakeChild(stdout=b"held", descendant=True))
    kernel.fail(call, occurrence=occurrence)
    before = len(RETAINED.entries())
    try:
        with pytest.raises(UnconfirmedEndError) as raised:
            run_contained(_request(), api=kernel)
        error = raised.value
        assert (error.call, error.pid, error.identity, error.stage) == (call, 4242, _IDENTITY, "unconfirmed-end")
        reads = _assert_retained(kernel, call, before)
        _assert_unjoined_daemon_readers(kernel, reads, held=call == "TerminateJobObject")
    finally:
        kernel.release()
        for _handle, reader, _buffer in kernel.readers:
            reader.join()


def test_an_identity_failure_with_an_unconfirmed_teardown_has_no_identity() -> None:
    """The PID comes from `CreateProcessW`; the child stays suspended, unrecorded and never resumed."""
    kernel = FakeKernel()
    kernel.fail("GetProcessTimes")
    kernel.fail("TerminateJobObject")
    recorded: list[ProcessIdentity] = []
    before = len(RETAINED.entries())
    with pytest.raises(UnconfirmedEndError) as raised:
        run_contained(_request(record=recorded.append), api=kernel)
    assert (raised.value.identity, raised.value.pid, raised.value.call) == (None, 4242, "TerminateJobObject")
    assert (recorded, "ResumeThread" in kernel.names(), kernel.readers) == ([], False, [])
    (entry,) = RETAINED.entries()[before:]
    assert isinstance(entry, RetainedChild)
    assert entry.identity is None


def _sleeps(*effects: BaseException | None) -> Callable[[float], None]:
    """Return a poll sleep that raises each given exception in turn, then returns."""
    pending = list(effects)

    def sleep(seconds: float) -> None:
        del seconds
        effect = pending.pop(0) if pending else None
        if effect is not None:
            raise effect

    return sleep


def test_a_failed_inheritance_reset_is_retried_while_settling() -> None:
    """A guard whose reset fails once stays tracked: the child is ended, the reset retried, every handle closed."""
    kernel = FakeKernel()
    kernel.fail("SetHandleInformation", occurrence=8, error=_INVALID_HANDLE)
    before = len(RETAINED.entries())
    with pytest.raises(ContainmentError) as raised:
        run_contained(_request(inherited=(_GUARD,)), api=kernel)
    assert (raised.value.call, raised.value.cleanup) == ("SetHandleInformation", ())
    assert (kernel.inheritable[_GUARD], kernel.arguments("SetHandleInformation", 9)) == (False, (_GUARD, 1, 0))
    assert ("ResumeThread" in kernel.names(), len(RETAINED.entries())) == (False, before)
    _assert_ended_then_closed(kernel)


def test_a_persistent_reset_failure_leaves_the_guard_retained_and_named() -> None:
    """A guard still inheritable after the retry is reported in `cleanup` and owned by `RETAINED`."""
    kernel = FakeKernel()
    for occurrence in (8, 9):
        kernel.fail("SetHandleInformation", occurrence=occurrence, error=_INVALID_HANDLE)
    before = len(RETAINED.entries())
    with pytest.raises(ContainmentError) as raised:
        run_contained(_request(inherited=(_GUARD,)), api=kernel)
    assert (raised.value.call, raised.value.cleanup, kernel.inheritable[_GUARD]) == ("SetHandleInformation", ("SetHandleInformation",), True)
    (entry,) = RETAINED.entries()[before:]
    assert isinstance(entry, RetainedChild)
    assert (entry.call, entry.handles) == ("SetHandleInformation", (_GUARD,))
    _assert_ended_then_closed(kernel)


def test_a_failed_close_keeps_the_handle_and_still_closes_the_others() -> None:
    """A write end that cannot be closed twice is retained and named; every other handle is closed after the end."""
    kernel = FakeKernel()
    for occurrence in (1, 4):
        kernel.fail("CloseHandle", occurrence=occurrence, error=_INVALID_HANDLE)
    before = len(RETAINED.entries())
    with pytest.raises(ContainmentError) as raised:
        run_contained(_request(), api=kernel)
    err_write = kernel.arguments("CloseHandle", 1)[0]
    assert (raised.value.call, raised.value.cleanup, kernel.open_handles()) == ("CloseHandle", ("CloseHandle",), {err_write})
    (entry,) = RETAINED.entries()[before:]
    assert isinstance(entry, RetainedChild)
    assert entry.handles == (err_write,)
    assert kernel.index("TerminateJobObject") < kernel.index("CloseHandle", 5)


def test_a_creation_failure_with_cleanup_failures_still_releases_the_rest() -> None:
    """A refused creation whose guard reset and one close fail still closes every other handle and names both."""
    kernel = FakeKernel()
    kernel.fail("CreateProcessW")
    kernel.fail("SetHandleInformation", occurrence=8, error=_INVALID_HANDLE)
    kernel.fail("CloseHandle", occurrence=2, error=_INVALID_HANDLE)
    before = len(RETAINED.entries())
    with pytest.raises(ContainmentError) as raised:
        run_contained(_request(inherited=(_GUARD,)), api=kernel)
    out_write = kernel.arguments("CloseHandle", 2)[0]
    assert (raised.value.call, raised.value.cleanup) == ("CreateProcessW", ("SetHandleInformation", "CloseHandle"))
    assert (kernel.open_handles(), kernel.names().count("CloseHandle")) == ({out_write}, 6)
    (entry,) = RETAINED.entries()[before:]
    assert isinstance(entry, RetainedChild)
    assert entry.handles == (_GUARD, out_write)


def test_a_failed_close_after_the_end_is_reported_once_the_rest_is_closed() -> None:
    """In the drain, a job handle that cannot be closed is retained after every other handle closed."""
    kernel = FakeKernel()
    kernel.fail("CloseHandle", occurrence=8, error=_INVALID_HANDLE)
    with pytest.raises(ContainmentError) as raised:
        run_contained(_request(), api=kernel)
    job = kernel.arguments("SetInformationJobObject")[0]
    assert (raised.value.call, raised.value.cleanup, kernel.open_handles()) == ("CloseHandle", ("CloseHandle",), {job})


def test_an_interrupt_during_setup_releases_what_exists() -> None:
    """Ctrl+C while the attribute list is sized closes the job, the pipes and `NUL`; no child is created."""
    kernel = FakeKernel()
    kernel.interrupt("InitializeProcThreadAttributeList")
    with pytest.raises(KeyboardInterrupt):
        run_contained(_request(), api=kernel)
    assert ("CreateProcessW" in kernel.names(), kernel.open_handles()) == (False, set())


def test_an_interrupt_right_after_creation_ends_the_child_before_propagating() -> None:
    """Ctrl+C during the first inheritance reset: the suspended child is ended, the resets finished, all closed."""
    kernel = FakeKernel()
    kernel.interrupt("SetHandleInformation", occurrence=4)
    with pytest.raises(KeyboardInterrupt):
        run_contained(_request(), api=kernel)
    assert "ResumeThread" not in kernel.names()
    assert not any(kernel.inheritable.get(handle, False) for handle in kernel.created)
    _assert_ended_then_closed(kernel)


def test_an_interrupt_while_polling_is_delivered_after_the_confirmed_end() -> None:
    """The poll resumes without a second termination; the outcome is complete, then the interrupt is raised."""
    kernel = FakeKernel(FakeChild(stdout=b"out"))
    kernel.lingering = 1
    with pytest.raises(KeyboardInterrupt):
        run_contained(_request(), api=kernel, sleep=_sleeps(KeyboardInterrupt()))
    assert (kernel.names().count("TerminateJobObject"), kernel.names().count("QueryInformationJobObject")) == (1, 2)
    assert "GetExitCodeProcess" in kernel.names()
    _assert_ended_then_closed(kernel)


def test_repeated_interrupts_while_recovering_still_end_and_release_the_run() -> None:
    """An interrupt from the callback, two more while polling and one during a close: ended once, all closed."""
    kernel = FakeKernel()
    kernel.lingering = 2
    kernel.interrupt("CloseHandle", occurrence=4)
    with pytest.raises(KeyboardInterrupt) as raised:
        run_contained(_request(record=_interrupt), api=kernel, sleep=_sleeps(KeyboardInterrupt(), KeyboardInterrupt()))
    assert raised.value.__cause__ is None
    assert (kernel.names().count("TerminateJobObject"), "ResumeThread" in kernel.names()) == (1, False)
    _assert_ended_then_closed(kernel)


def test_a_pending_interrupt_replaces_a_containment_error() -> None:
    """A recording failure is settled first; the interrupt met while polling is then raised from it."""
    kernel = FakeKernel()
    kernel.lingering = 1
    with pytest.raises(KeyboardInterrupt) as raised:
        run_contained(_request(record=_refuse), api=kernel, sleep=_sleeps(KeyboardInterrupt()))
    assert isinstance(raised.value.__cause__, ContainmentError)
    _assert_ended_then_closed(kernel)


def test_an_error_while_polling_is_an_unconfirmed_end() -> None:
    """A poll that fails without a native error cannot confirm the end: everything is retained."""
    kernel = FakeKernel()
    kernel.lingering = 1
    before = len(RETAINED.entries())
    with pytest.raises(UnconfirmedEndError) as raised:
        run_contained(_request(), api=kernel, sleep=_sleeps(RuntimeError("sleep failed")))
    assert (raised.value.call, raised.value.error) == ("teardown", None)
    job, process = kernel.arguments("SetInformationJobObject")[0], kernel.arguments("GetProcessTimes")[0]
    assert not {job, process} & set(kernel.closed)
    (entry,) = RETAINED.entries()[before:]
    assert isinstance(entry, RetainedChild)
    assert (entry.call, entry.handles[:2]) == ("teardown", (job, process))
    kernel.release()


def test_a_failed_close_then_a_ctrl_c_loses_and_repeats_no_close() -> None:
    """Round 2 sequence: the failed write end stays owned through the Ctrl+C, is closed while settling, once."""
    kernel = FakeKernel()
    kernel.fail("CloseHandle", occurrence=1, error=_INVALID_HANDLE)
    kernel.interrupt("CloseHandle", occurrence=2)
    with pytest.raises(KeyboardInterrupt) as raised:
        run_contained(_request(), api=kernel)
    cause = raised.value.__cause__
    assert isinstance(cause, ContainmentError)
    assert (cause.call, cause.cleanup) == ("CloseHandle", ())
    _assert_ended_then_closed(kernel)


def test_handles_a_failed_close_left_are_retained_when_an_interrupt_propagates() -> None:
    """Round 2 sequence: after an interrupt from the callback, an unclosable thread handle is retained and noted."""
    kernel = FakeKernel()
    kernel.fail("CloseHandle", occurrence=4, error=_INVALID_HANDLE)
    before = len(RETAINED.entries())
    with pytest.raises(KeyboardInterrupt) as raised:
        run_contained(_request(record=_interrupt), api=kernel)
    failed = kernel.arguments("CloseHandle", 4)[0]
    (entry,) = RETAINED.entries()[before:]
    assert isinstance(entry, RetainedChild)
    assert (entry.call, entry.handles, kernel.open_handles()) == ("CloseHandle", (failed,), {failed})
    assert any("CloseHandle failed" in note for note in raised.value.__notes__)


def test_a_ctrl_c_while_a_guard_is_made_inheritable_still_resets_it() -> None:
    """Round 2 sequence: the guard is registered before its inheritance is set, so the reset still happens."""
    kernel = FakeKernel()
    kernel.interrupt("SetHandleInformation", occurrence=4)
    with pytest.raises(KeyboardInterrupt):
        run_contained(_request(inherited=(_GUARD,)), api=kernel)
    assert (kernel.inheritable[_GUARD], "ResumeThread" in kernel.names()) == (False, False)
    _assert_ended_then_closed(kernel)


def test_a_ctrl_c_as_the_process_is_created_ends_it_and_closes_its_handles() -> None:
    """Round 2 sequence: the process and thread handles are owned once created; the child is ended before resuming."""
    kernel = FakeKernel()
    kernel.interrupt("CreateProcessW")
    with pytest.raises(KeyboardInterrupt):
        run_contained(_request(), api=kernel)
    assert "ResumeThread" not in kernel.names()
    _assert_ended_then_closed(kernel)


@pytest.mark.parametrize(("call", "occurrence"), [
    ("CreateJobObjectW", 1), ("CreateFileW", 1), ("CreatePipe", 2), ("InitializeProcThreadAttributeList", 2),
])
def test_a_ctrl_c_as_a_handle_is_acquired_loses_nothing(call: str, occurrence: int) -> None:
    """The Ctrl+C is held until the setup is complete, then every acquired handle and the list are released."""
    kernel = FakeKernel()
    kernel.interrupt(call, occurrence=occurrence)
    with pytest.raises(KeyboardInterrupt):
        run_contained(_request(), api=kernel)
    names = kernel.names()
    assert ("CreateProcessW" in names, "DeleteProcThreadAttributeList" in names, kernel.open_handles()) == (False, True, set())


def _handler_seen(seen: list[object]) -> Callable[[ProcessIdentity], None]:
    """Return a recording callback that notes the SIGINT handler in force while the child is suspended."""
    def record(identity: ProcessIdentity) -> None:
        del identity
        seen.append(signal.getsignal(signal.SIGINT))

    return record


def test_ctrl_c_is_deferred_only_on_the_main_thread_with_the_default_handler() -> None:
    """The run's handler replaces the default one for the run only; another thread or handler is left alone."""
    seen: list[object] = []
    run_contained(_request(record=_handler_seen(seen)), api=FakeKernel())
    assert (callable(seen[0]), seen[0] is signal.default_int_handler) == (True, False)
    assert signal.getsignal(signal.SIGINT) is signal.default_int_handler
    worker = threading.Thread(target=run_contained, args=(_request(record=_handler_seen(seen)),), kwargs={"api": FakeKernel()})
    worker.start()
    worker.join()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    run_contained(_request(record=_handler_seen(seen)), api=FakeKernel())
    assert seen[1:] == [signal.default_int_handler, signal.SIG_IGN]


def test_an_unconfirmed_end_wins_over_a_pending_interrupt() -> None:
    """When the resumed poll then fails, the caller gets `UnconfirmedEndError`, so it keeps every resource."""
    kernel = FakeKernel()
    kernel.lingering = 1
    kernel.fail("QueryInformationJobObject", occurrence=2)
    with pytest.raises(UnconfirmedEndError) as raised:
        run_contained(_request(), api=kernel, sleep=_sleeps(KeyboardInterrupt()))
    assert raised.value.call == "QueryInformationJobObject"
    kernel.release()


# eof
