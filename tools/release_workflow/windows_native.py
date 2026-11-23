"""Declare the x64 structures, constants and kernel32 functions of the Windows child layer.

Step 2 of v0.14.0 git-cliff-provisioning (plan decisions Q04 and Q05).
`windows_child` (the contained child lifecycle) and `windows_guard` (the use
guard) share these declarations. `kernel()` gives every declared kernel32
function its argument types, its result type and an error check that raises
`NativeCallError`, naming the failing call with its Windows error, then caches
the declared library. Both modules call it only when their `api` argument is
`None`: tests pass a fake kernel object instead, and the declarations are
checked through a fake loader, so no test reaches the operating system.

Pointer arguments are declared as pointers to their structure or integer type,
so callers pass the ctypes instances themselves and ctypes takes their address.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from functools import partial
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Callable

CREATE_SUSPENDED = 0x00000004
CREATE_UNICODE_ENVIRONMENT = 0x00000400
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
STARTF_USESTDHANDLES = 0x00000100
PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002
PROC_THREAD_ATTRIBUTE_JOB_LIST = 0x0002000D
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
HANDLE_FLAG_INHERIT = 0x00000001
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_BEGIN = 0
DUPLICATE_SAME_ACCESS = 0x00000002
INVALID_HANDLE_VALUE = 0xFFFFFFFFFFFFFFFF
CURRENT_PROCESS = INVALID_HANDLE_VALUE  # the pseudo handle GetCurrentProcess returns, (HANDLE)-1
STD_INPUT_HANDLE = 0xFFFFFFF6  # (DWORD)-10
STD_OUTPUT_HANDLE = 0xFFFFFFF5  # (DWORD)-11
STD_ERROR_HANDLE = 0xFFFFFFF4  # (DWORD)-12
INFINITE = 0xFFFFFFFF
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 0x00000102
WAIT_FAILED = 0xFFFFFFFF
RESUME_FAILED = 0xFFFFFFFF
CTRL_C_EVENT = 0
CTRL_BREAK_EVENT = 1
ERROR_FILE_NOT_FOUND = 2
ERROR_PATH_NOT_FOUND = 3
ERROR_ACCESS_DENIED = 5
ERROR_SHARING_VIOLATION = 32
ERROR_BROKEN_PIPE = 109
ERROR_INSUFFICIENT_BUFFER = 122

PHANDLER_ROUTINE = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)


class STARTUPINFOW(ctypes.Structure):
    """STARTUPINFOW: the window settings and the three standard handles of a new process."""

    _fields_: ClassVar = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.c_void_p),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class STARTUPINFOEXW(ctypes.Structure):
    """STARTUPINFOEXW: STARTUPINFOW plus the attribute list holding the job list and the handle list."""

    _fields_: ClassVar = [("StartupInfo", STARTUPINFOW), ("lpAttributeList", ctypes.c_void_p)]


class PROCESS_INFORMATION(ctypes.Structure):  # noqa: N801 - the Windows structure name
    """PROCESS_INFORMATION: the new process and primary thread handles and identifiers."""

    _fields_: ClassVar = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):  # noqa: N801 - the Windows structure name
    """JOBOBJECT_BASIC_LIMIT_INFORMATION: the limit flags and basic limits of a job."""

    _fields_: ClassVar = [
        ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
        ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class IO_COUNTERS(ctypes.Structure):  # noqa: N801 - the Windows structure name
    """IO_COUNTERS: the I/O accounting part of the extended limits."""

    _fields_: ClassVar = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):  # noqa: N801 - the Windows structure name
    """JOBOBJECT_EXTENDED_LIMIT_INFORMATION: the class that sets kill-on-close on a job."""

    _fields_: ClassVar = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):  # noqa: N801 - the Windows structure name
    """JOBOBJECT_BASIC_ACCOUNTING_INFORMATION: the job's process counts, including its active members."""

    _fields_: ClassVar = [
        ("TotalUserTime", wintypes.LARGE_INTEGER),
        ("TotalKernelTime", wintypes.LARGE_INTEGER),
        ("ThisPeriodTotalUserTime", wintypes.LARGE_INTEGER),
        ("ThisPeriodTotalKernelTime", wintypes.LARGE_INTEGER),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


class NativeCallError(OSError):
    """A declared kernel32 call failed: `call` names it and `winerror` holds its Windows error."""

    def __init__(self, call: str, error: int) -> None:
        """Keep the call name; OSError keeps the Windows error and its errno."""
        super().__init__(None, f"{call} failed", None, error)
        self.call = call


class Kernel(Protocol):
    """The declared kernel32 functions: the cached library, or a fake kernel in tests."""

    def __getattr__(self, name: str, /) -> Callable[..., Any]:
        """Return one declared function."""
        ...


def _failed(function: object) -> NativeCallError:
    """Build the error of a failed call from the thread's last error."""
    return NativeCallError(str(getattr(function, "__name__", "kernel32")), ctypes.get_last_error())


def _check_bool(result: int, function: object, arguments: tuple[object, ...]) -> int:
    """A BOOL result of zero is a failure."""
    del arguments
    if not result:
        raise _failed(function)
    return result


def _check_handle(result: int | None, function: object, arguments: tuple[object, ...]) -> int | None:
    """A NULL handle is a failure."""
    del arguments
    if not result:
        raise _failed(function)
    return result


def _check_file_handle(result: int | None, function: object, arguments: tuple[object, ...]) -> int | None:
    """INVALID_HANDLE_VALUE, or no handle at all, is a failure."""
    del arguments
    if not result or result == INVALID_HANDLE_VALUE:
        raise _failed(function)
    return result


def _check_wait(result: int, function: object, arguments: tuple[object, ...]) -> int:
    """WAIT_FAILED is a failure; a signal or a timeout is a result."""
    del arguments
    if result == WAIT_FAILED:
        raise _failed(function)
    return result


def _check_resume(result: int, function: object, arguments: tuple[object, ...]) -> int:
    """A suspend count of (DWORD)-1 is a failure."""
    del arguments
    if result == RESUME_FAILED:
        raise _failed(function)
    return result


def _check_attribute_list(result: int, function: object, arguments: tuple[object, ...]) -> int:
    """Only the sizing call, without a list, may answer with an insufficient buffer."""
    if not result and not (arguments[0] is None and ctypes.get_last_error() == ERROR_INSUFFICIENT_BUFFER):
        raise _failed(function)
    return result


_H, _D, _B, _V = wintypes.HANDLE, wintypes.DWORD, wintypes.BOOL, wintypes.LPVOID
_P = ctypes.POINTER
_DECLARATIONS: tuple[tuple[str, tuple[object, ...], object, object], ...] = (
    ("CloseHandle", (_H,), _B, _check_bool),
    ("CreateFileW", (wintypes.LPCWSTR, _D, _D, _V, _D, _D, _H), _H, _check_file_handle),
    ("CreateJobObjectW", (_V, wintypes.LPCWSTR), _H, _check_handle),
    ("CreatePipe", (_P(_H), _P(_H), _V, _D), _B, _check_bool),
    ("CreateProcessW", (wintypes.LPCWSTR, wintypes.LPWSTR, _V, _V, _B, _D, _V, wintypes.LPCWSTR, _P(STARTUPINFOEXW),
                        _P(PROCESS_INFORMATION)), _B, _check_bool),
    ("DeleteProcThreadAttributeList", (_V,), None, None),
    ("DuplicateHandle", (_H, _H, _H, _P(_H), _D, _B, _D), _B, _check_bool),
    ("GetExitCodeProcess", (_H, _P(_D)), _B, _check_bool),
    ("GetHandleInformation", (_H, _P(_D)), _B, _check_bool),
    ("GetProcessTimes", (_H, *(_P(wintypes.FILETIME),) * 4), _B, _check_bool),
    ("GetStdHandle", (_D,), _H, _check_file_handle),
    ("InitializeProcThreadAttributeList", (_V, _D, _D, _P(ctypes.c_size_t)), _B, _check_attribute_list),
    ("IsProcessInJob", (_H, _H, _P(_B)), _B, _check_bool),
    ("QueryInformationJobObject", (_H, ctypes.c_int, _P(JOBOBJECT_BASIC_ACCOUNTING_INFORMATION), _D, _P(_D)), _B, _check_bool),
    ("ReadFile", (_H, _V, _D, _P(_D), _V), _B, _check_bool),
    ("ResumeThread", (_H,), _D, _check_resume),
    ("SetConsoleCtrlHandler", (PHANDLER_ROUTINE, _B), _B, _check_bool),
    ("SetFilePointerEx", (_H, wintypes.LARGE_INTEGER, _P(wintypes.LARGE_INTEGER), _D), _B, _check_bool),
    ("SetHandleInformation", (_H, _D, _D), _B, _check_bool),
    ("SetInformationJobObject", (_H, ctypes.c_int, _P(JOBOBJECT_EXTENDED_LIMIT_INFORMATION), _D), _B, _check_bool),
    ("TerminateJobObject", (_H, wintypes.UINT), _B, _check_bool),
    ("UpdateProcThreadAttribute", (_V, _D, ctypes.c_size_t, _V, ctypes.c_size_t, _V, _P(ctypes.c_size_t)), _B, _check_bool),
    ("WaitForSingleObject", (_H, _D), _D, _check_wait),
)
_LOAD_KERNEL32 = partial(ctypes.WinDLL, "kernel32", use_last_error=True)
_DECLARED: dict[object, Kernel] = {}


def _declare(library: Any) -> Kernel:  # noqa: ANN401 - a ctypes DLL or a test's stand-in
    """Set the argument types, result type and error check of every function the layer calls."""
    for name, argtypes, restype, errcheck in _DECLARATIONS:
        function = getattr(library, name)
        function.argtypes = argtypes
        function.restype = restype
        if errcheck is not None:
            function.errcheck = errcheck
    return cast("Kernel", library)


def kernel(loader: Callable[[], object] | None = None) -> Kernel:
    """Return kernel32 with every function declared, loading and declaring it once per loader."""
    source = _LOAD_KERNEL32 if loader is None else loader
    declared = _DECLARED.get(source)
    if declared is None:
        declared = _declare(source())
        _DECLARED[source] = declared
    return declared


# eof
