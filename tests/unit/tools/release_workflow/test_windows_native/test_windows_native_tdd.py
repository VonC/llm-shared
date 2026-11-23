"""The Windows layer's x64 structures, constants and kernel32 declarations, checked without calling Windows.

Step 2 of v0.14.0 git-cliff-provisioning (plan decisions Q04 and Q05). The
structure sizes and field offsets are the documented x64 layouts. `kernel()` is
called with a fake loader whose functions record the argument types, the result
type and the error check each declaration sets, and the loader runs once per
cache. Each error check returns a successful result unchanged and raises
`NativeCallError`, naming the failing call with the thread's last error, on a
failed one; the attribute list sizing call accepts its expected insufficient
buffer answer only.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import pytest

from tools.release_workflow import windows_native as native
from tools.release_workflow.windows_native import NativeCallError

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

_H, _D, _B, _V = wintypes.HANDLE, wintypes.DWORD, wintypes.BOOL, wintypes.LPVOID
_SIZE = ctypes.c_size_t
_P = ctypes.POINTER
_TIMES = (_P(wintypes.FILETIME),) * 4
_EXPECTED: dict[str, tuple[tuple[object, ...], object, object]] = {
    "CloseHandle": ((_H,), _B, native._check_bool),
    "CreateFileW": ((wintypes.LPCWSTR, _D, _D, _V, _D, _D, _H), _H, native._check_file_handle),
    "CreateJobObjectW": ((_V, wintypes.LPCWSTR), _H, native._check_handle),
    "CreatePipe": ((_P(_H), _P(_H), _V, _D), _B, native._check_bool),
    "CreateProcessW": ((wintypes.LPCWSTR, wintypes.LPWSTR, _V, _V, _B, _D, _V, wintypes.LPCWSTR,
                        _P(native.STARTUPINFOEXW), _P(native.PROCESS_INFORMATION)), _B, native._check_bool),
    "DeleteProcThreadAttributeList": ((_V,), None, None),
    "DuplicateHandle": ((_H, _H, _H, _P(_H), _D, _B, _D), _B, native._check_bool),
    "GetExitCodeProcess": ((_H, _P(_D)), _B, native._check_bool),
    "GetHandleInformation": ((_H, _P(_D)), _B, native._check_bool),
    "GetProcessTimes": ((_H, *_TIMES), _B, native._check_bool),
    "GetStdHandle": ((_D,), _H, native._check_file_handle),
    "InitializeProcThreadAttributeList": ((_V, _D, _D, _P(_SIZE)), _B, native._check_attribute_list),
    "IsProcessInJob": ((_H, _H, _P(_B)), _B, native._check_bool),
    "QueryInformationJobObject": ((_H, ctypes.c_int, _P(native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION), _D, _P(_D)),
                                  _B, native._check_bool),
    "ReadFile": ((_H, _V, _D, _P(_D), _V), _B, native._check_bool),
    "ResumeThread": ((_H,), _D, native._check_resume),
    "SetConsoleCtrlHandler": ((native.PHANDLER_ROUTINE, _B), _B, native._check_bool),
    "SetFilePointerEx": ((_H, wintypes.LARGE_INTEGER, _P(wintypes.LARGE_INTEGER), _D), _B, native._check_bool),
    "SetHandleInformation": ((_H, _D, _D), _B, native._check_bool),
    "SetInformationJobObject": ((_H, ctypes.c_int, _P(native.JOBOBJECT_EXTENDED_LIMIT_INFORMATION), _D), _B, native._check_bool),
    "TerminateJobObject": ((_H, wintypes.UINT), _B, native._check_bool),
    "UpdateProcThreadAttribute": ((_V, _D, _SIZE, _V, _SIZE, _V, _P(_SIZE)), _B, native._check_bool),
    "WaitForSingleObject": ((_H, _D), _D, native._check_wait),
}


class _Library:
    """A loaded library stand-in whose functions keep what the declarations set."""

    def __init__(self) -> None:
        """Start with no function looked up."""
        self.functions: dict[str, SimpleNamespace] = {}

    def __getattr__(self, name: str) -> SimpleNamespace:
        """Return the same recording function object for each name."""
        return self.functions.setdefault(name, SimpleNamespace(argtypes=None, restype="unset", errcheck=None))


@pytest.fixture
def last_error() -> Iterator[None]:
    """Set the ctypes-private last error (no Windows call) and restore it."""
    previous = ctypes.set_last_error(native.ERROR_ACCESS_DENIED)
    yield
    ctypes.set_last_error(previous)


def test_structures_have_the_x64_layouts() -> None:
    """Sizes and offsets match the documented x64 structures the kernel reads."""
    startup, extended = native.STARTUPINFOW, native.JOBOBJECT_EXTENDED_LIMIT_INFORMATION
    assert [ctypes.sizeof(kind) for kind in (startup, native.STARTUPINFOEXW, native.PROCESS_INFORMATION, extended,
                                              native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION)] == [104, 112, 24, 144, 48]
    assert (startup.dwFlags.offset, startup.hStdInput.offset, startup.hStdOutput.offset, startup.hStdError.offset) == (60, 80, 88, 96)
    assert (native.PROCESS_INFORMATION.hThread.offset, native.PROCESS_INFORMATION.dwProcessId.offset) == (8, 16)
    assert (extended.IoInfo.offset, extended.ProcessMemoryLimit.offset) == (64, 112)
    assert (native.STARTUPINFOEXW.lpAttributeList.offset, native.JOBOBJECT_BASIC_LIMIT_INFORMATION.LimitFlags.offset,
            native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION.ActiveProcesses.offset) == (104, 16, 40)


def test_constants_are_the_documented_values() -> None:
    """Flags, attributes, classes and sentinels equal their Windows SDK values."""
    assert (native.CREATE_SUSPENDED, native.CREATE_UNICODE_ENVIRONMENT, native.EXTENDED_STARTUPINFO_PRESENT) == (0x4, 0x400, 0x80000)
    assert (native.PROC_THREAD_ATTRIBUTE_HANDLE_LIST, native.PROC_THREAD_ATTRIBUTE_JOB_LIST) == (0x20002, 0x2000D)
    assert (native.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, native.JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
            native.JOB_OBJECT_EXTENDED_LIMIT_INFORMATION) == (0x2000, 1, 9)
    assert (native.GENERIC_READ, native.FILE_SHARE_READ, native.OPEN_EXISTING, native.HANDLE_FLAG_INHERIT) == (0x80000000, 1, 3, 1)
    assert (native.STD_INPUT_HANDLE, native.STD_OUTPUT_HANDLE, native.STD_ERROR_HANDLE) == (2**32 - 10, 2**32 - 11, 2**32 - 12)
    assert (native.WAIT_TIMEOUT, native.WAIT_FAILED, native.INFINITE, native.INVALID_HANDLE_VALUE) == (
        0x102, 2**32 - 1, 2**32 - 1, 2**64 - 1)
    assert (native.CTRL_C_EVENT, native.CTRL_BREAK_EVENT, native.ERROR_BROKEN_PIPE) == (0, 1, 109)
    assert (native.PHANDLER_ROUTINE._restype_, native.PHANDLER_ROUTINE._argtypes_) == (wintypes.BOOL, (wintypes.DWORD,))


def test_kernel_declares_every_function_once_per_loader() -> None:
    """Each function gets its argument types, result type and error check; the declared library is cached."""
    library = _Library()
    loads: list[_Library] = []

    def loader() -> _Library:
        loads.append(library)
        return library

    declared = native.kernel(loader)
    assert native.kernel(loader) is declared
    assert loads == [library]
    seen = {name: (tuple(function.argtypes), function.restype, function.errcheck) for name, function in library.functions.items()}
    assert seen == _EXPECTED


def _function(name: str = "CreatePipe") -> SimpleNamespace:
    """Stand in for the ctypes function an error check receives."""
    return SimpleNamespace(__name__=name)


@pytest.mark.usefixtures("last_error")
@pytest.mark.parametrize(("check", "failed", "passed"), [
    (native._check_bool, 0, 1),
    (native._check_handle, None, 0x40),
    (native._check_file_handle, native.INVALID_HANDLE_VALUE, 0x40),
    (native._check_file_handle, None, 0x40),
    (native._check_wait, native.WAIT_FAILED, native.WAIT_TIMEOUT),
    (native._check_resume, native.RESUME_FAILED, 1),
])
def test_error_checks_name_the_failing_call(check: Callable[..., Any], failed: int | None, passed: int) -> None:
    """A failed result raises with the call name and last error; a successful one is returned."""
    with pytest.raises(NativeCallError) as raised:
        check(failed, _function(), ())
    assert (raised.value.call, raised.value.winerror, str(raised.value)) == ("CreatePipe", 5, "[WinError 5] CreatePipe failed")
    assert check(passed, _function(), ()) == passed


@pytest.mark.parametrize(("error", "list_argument", "accepted"), [
    (native.ERROR_INSUFFICIENT_BUFFER, None, True),
    (native.ERROR_ACCESS_DENIED, None, False),
    (native.ERROR_INSUFFICIENT_BUFFER, ctypes.create_string_buffer(8), False),
])
def test_attribute_list_check_accepts_only_the_sizing_answer(error: int, list_argument: object, *, accepted: bool) -> None:
    """Only the sizing call (no list yet) may fail with an insufficient buffer; success always passes."""
    previous = ctypes.set_last_error(error)
    try:
        arguments = (list_argument, 2, 0, ctypes.c_size_t())
        assert native._check_attribute_list(1, _function(), arguments) == 1
        if accepted:
            assert native._check_attribute_list(0, _function(), arguments) == 0
        else:
            with pytest.raises(NativeCallError, match="CreatePipe failed"):
                native._check_attribute_list(0, _function(), arguments)
    finally:
        ctypes.set_last_error(previous)


# eof
