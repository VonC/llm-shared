"""Query-only Windows process and loaded-image observations for resume-paused.

Step 1 of v0.15.0 resume-paused keeps Windows access behind one injected
protocol. ``Win32Api`` binds the calls validated by the 2026-11-12 disposable
probes: ``PROCESS_QUERY_INFORMATION`` only, an allocation-metadata walk, the
native image name and the class 44 loaded-image identity query. It never reads
process memory, command lines or environments, and never enumerates modules.
The pure helpers resolve a pane shell's direct host child and a caller's
ancestry from one process listing.

Fix (Step 1 missing work): ``list_jsonl_files`` enumerates a session or
transcript root completely, following no link or junction, and reports an
incomplete enumeration instead of a partial list.

Fix (code review round 1, R6): ``Win32Api.processes`` returns a listing only
when the toolhelp walk ends with ``ERROR_NO_MORE_FILES``; any other failure of
the first or a later call yields no listing instead of a partial one.
"""

from __future__ import annotations

import ctypes
import hashlib
from ctypes import wintypes
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

GLOBALROOT: Final = "\\\\?\\GLOBALROOT"
_FILETIME_EPOCH: Final = datetime(1601, 1, 1, tzinfo=UTC)
_PROCESS_QUERY_INFORMATION: Final = 0x0400
_MEM_COMMIT: Final = 0x1000
_MEM_IMAGE: Final = 0x1000000
_READ_EXECUTE: Final = 0xA0000000
_GENERIC_READ: Final = 0x80000000
_SHARE_READ_DELETE: Final = 0x5
_SHARE_ALL: Final = 0x7
_OPEN_EXISTING: Final = 3
_IMAGE_FILE_MAPPING: Final = 44
_SNAPSHOT_PROCESSES: Final = 0x2
_NO_MORE_FILES: Final = 18
_INVALID_HANDLE: Final = ctypes.c_void_p(-1).value
_NAME_CAPACITY: Final = 32768
_READ_CHUNK: Final = 1024 * 1024


@dataclass(frozen=True)
class ProcessRecord:
    """One row of a process listing: identifier, parent and image file name."""

    pid: int
    parent_pid: int
    name: str


@dataclass(frozen=True)
class ImageWalk:
    """Result of one allocation-metadata walk over a process address space.

    ``mapped_names`` holds the native file name of every committed image
    allocation, one per allocation base. ``complete`` is false when any query
    failed or the walk stopped early.
    """

    complete: bool
    regions: int
    mapped_names: tuple[str, ...]


class WindowsApi(Protocol):
    """Injected read-only Windows observations; failures return ``None``."""

    def os_build(self) -> int | None:
        """Return ``RtlGetVersion().dwBuildNumber``."""
        ...

    def processes(self) -> tuple[ProcessRecord, ...] | None:
        """Return one complete process listing."""
        ...

    def open_process(self, pid: int) -> int | None:
        """Open a process with query rights only."""
        ...

    def creation_time(self, process: int) -> int | None:
        """Return the process creation time in FILETIME ticks."""
        ...

    def native_image_name(self, process: int) -> str | None:
        """Return the kernel image name of the process."""
        ...

    def image_walk(self, process: int) -> ImageWalk:
        """Walk allocation metadata and name every committed image allocation."""
        ...

    def open_image(self, native_name: str) -> int | None:
        """Open an image file by native name for read and execute."""
        ...

    def image_mapping_status(self, process: int, image: int) -> int:
        """Return the class 44 status: zero only for the loaded image file."""
        ...

    def sha256(self, image: int) -> tuple[str, int] | None:
        """Hash a file through its open handle; return digest and byte count."""
        ...

    def read_file(self, path: str) -> bytes | None:
        """Read a whole file while its writer keeps it open."""
        ...

    def close(self, handle: int) -> None:
        """Close a process or file handle."""
        ...


@dataclass(frozen=True)
class JsonlFile:
    """One regular JSONL file found by a complete directory enumeration."""

    path: str
    modified_ns: int
    size: int


def list_jsonl_files(root: str) -> tuple[JsonlFile, ...] | None:
    """List the regular ``.jsonl`` files under a root, across every sub-directory.

    Returns:
        The files in discovery order, or ``None`` when the enumeration is
        incomplete: any listing error, or any symbolic link or junction.
        Nothing is followed and nothing is guessed.
    """
    found: list[JsonlFile] = []
    pending = [Path(root)]
    try:
        while pending:
            for entry in pending.pop().iterdir():
                if entry.is_symlink() or entry.is_junction():
                    return None
                if entry.is_dir():
                    pending.append(entry)
                elif entry.is_file() and entry.suffix == ".jsonl":
                    status = entry.lstat()
                    found.append(JsonlFile(str(entry), status.st_mtime_ns, status.st_size))
    except OSError:
        return None
    return tuple(found)


def filetime_to_datetime(ticks: int) -> datetime:
    """Convert FILETIME 100-nanosecond ticks to a UTC instant."""
    return _FILETIME_EPOCH + timedelta(microseconds=ticks // 10)


def direct_children(processes: Sequence[ProcessRecord], parent_pid: int, image_name: str) -> tuple[ProcessRecord, ...]:
    """Return the direct children of one process that run the named image."""
    wanted = image_name.casefold()
    return tuple(p for p in processes if p.parent_pid == parent_pid and p.name.casefold() == wanted)


def ancestry_names(processes: Sequence[ProcessRecord], pid: int) -> tuple[str, ...] | None:
    """Return ancestor image names, nearest first, or ``None`` when unavailable.

    A listing carries no creation times, so a reused parent identifier can name
    an unrelated process. The result only supports rejecting recognized agents;
    it never proves a human origin.
    """
    by_pid = {process.pid: process for process in processes}
    current = by_pid.get(pid)
    if current is None:
        return None
    names: list[str] = []
    seen = {pid}
    while (parent := by_pid.get(current.parent_pid)) is not None and parent.pid not in seen:
        seen.add(parent.pid)
        names.append(parent.name)
        current = parent
    return tuple(names)


class _Region(ctypes.Structure):
    _fields_ = (
        ("base", ctypes.c_void_p), ("allocation", ctypes.c_void_p), ("allocation_protect", wintypes.DWORD),
        ("partition", wintypes.WORD), ("size", ctypes.c_size_t), ("state", wintypes.DWORD),
        ("protect", wintypes.DWORD), ("kind", wintypes.DWORD),
    )


class _SystemInfo(ctypes.Structure):
    _fields_ = (
        ("arch", wintypes.DWORD), ("page", wintypes.DWORD), ("minimum", ctypes.c_void_p),
        ("maximum", ctypes.c_void_p), ("mask", ctypes.c_size_t), ("processors", wintypes.DWORD),
        ("processor_type", wintypes.DWORD), ("granularity", wintypes.DWORD),
        ("level", wintypes.WORD), ("revision", wintypes.WORD),
    )


class _OsVersion(ctypes.Structure):
    _fields_ = (
        ("size", wintypes.DWORD), ("major", wintypes.DWORD), ("minor", wintypes.DWORD),
        ("build", wintypes.DWORD), ("platform", wintypes.DWORD), ("service_pack", wintypes.WCHAR * 128),
    )


class _ProcessEntry(ctypes.Structure):
    _fields_ = (
        ("size", wintypes.DWORD), ("usage", wintypes.DWORD), ("pid", wintypes.DWORD),
        ("heap", ctypes.c_size_t), ("module", wintypes.DWORD), ("threads", wintypes.DWORD),
        ("parent_pid", wintypes.DWORD), ("priority", wintypes.LONG), ("flags", wintypes.DWORD),
        ("name", wintypes.WCHAR * 260),
    )


def _bind(library: Any, name: str, result: Any, *arguments: Any) -> Any:  # noqa: ANN401
    """Declare one foreign function's result and argument types."""
    function = getattr(library, name)
    function.restype = result
    function.argtypes = arguments
    return function


class Win32Api:
    """``WindowsApi`` over kernel32, psapi and ntdll with query-only rights."""

    def __init__(self) -> None:
        """Bind the foreign functions once; requires Windows."""
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
        native = ctypes.WinDLL("ntdll")  # type: ignore[attr-defined]
        psapi = ctypes.WinDLL("psapi", use_last_error=True)  # type: ignore[attr-defined]
        handle, dword, pointer = wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER
        self._open_process = _bind(kernel, "OpenProcess", handle, dword, wintypes.BOOL, dword)
        self._close = _bind(kernel, "CloseHandle", wintypes.BOOL, handle)
        self._image_name = _bind(kernel, "QueryFullProcessImageNameW", wintypes.BOOL, handle, dword, wintypes.LPWSTR, pointer(dword))
        self._mapped_name = _bind(psapi, "GetMappedFileNameW", dword, handle, ctypes.c_void_p, wintypes.LPWSTR, dword)
        self._create_file = _bind(kernel, "CreateFileW", handle, wintypes.LPCWSTR, dword, dword, ctypes.c_void_p, dword, dword, handle)
        self._read = _bind(kernel, "ReadFile", wintypes.BOOL, handle, ctypes.c_void_p, dword, pointer(dword), ctypes.c_void_p)
        self._query = _bind(kernel, "VirtualQueryEx", ctypes.c_size_t, handle, ctypes.c_void_p, pointer(_Region), ctypes.c_size_t)
        self._system_info = _bind(kernel, "GetNativeSystemInfo", None, pointer(_SystemInfo))
        self._times = _bind(kernel, "GetProcessTimes", wintypes.BOOL, handle, *(pointer(wintypes.FILETIME),) * 4)
        self._snapshot = _bind(kernel, "CreateToolhelp32Snapshot", handle, dword, dword)
        self._first = _bind(kernel, "Process32FirstW", wintypes.BOOL, handle, pointer(_ProcessEntry))
        self._next = _bind(kernel, "Process32NextW", wintypes.BOOL, handle, pointer(_ProcessEntry))
        self._version = _bind(native, "RtlGetVersion", wintypes.LONG, pointer(_OsVersion))
        self._identity = _bind(native, "NtQueryInformationProcess", wintypes.LONG, handle, dword, ctypes.c_void_p, dword, pointer(dword))

    def os_build(self) -> int | None:
        """Return ``RtlGetVersion().dwBuildNumber`` or ``None`` on failure."""
        version = _OsVersion()
        version.size = ctypes.sizeof(version)
        return version.build if self._version(ctypes.byref(version)) == 0 else None

    def processes(self) -> tuple[ProcessRecord, ...] | None:
        """Return one toolhelp process listing, or ``None`` when it fails."""
        snapshot = self._snapshot(_SNAPSHOT_PROCESSES, 0)
        if snapshot in (None, _INVALID_HANDLE):  # pragma: no cover - needs a failing kernel snapshot
            return None
        try:
            entry = _ProcessEntry()
            entry.size = ctypes.sizeof(entry)
            records: list[ProcessRecord] = []
            ctypes.set_last_error(0)
            more = self._first(snapshot, ctypes.byref(entry))
            while more:
                records.append(ProcessRecord(entry.pid, entry.parent_pid, entry.name))
                more = self._next(snapshot, ctypes.byref(entry))
            # Only the documented end of the listing completes it: any other
            # failure could hide a second host child behind a partial list.
            return tuple(records) if ctypes.get_last_error() == _NO_MORE_FILES else None
        finally:
            self._close(snapshot)

    def open_process(self, pid: int) -> int | None:
        """Open a process with ``PROCESS_QUERY_INFORMATION`` only."""
        return self._open_process(_PROCESS_QUERY_INFORMATION, False, pid) or None  # noqa: FBT003

    def creation_time(self, process: int) -> int | None:
        """Return the creation time of an opened process in FILETIME ticks."""
        times = [wintypes.FILETIME() for _ in range(4)]
        if not self._times(process, *(ctypes.byref(value) for value in times)):
            return None
        return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime

    def native_image_name(self, process: int) -> str | None:
        """Return the kernel image name through ``PROCESS_NAME_NATIVE``."""
        buffer = ctypes.create_unicode_buffer(_NAME_CAPACITY)
        size = wintypes.DWORD(_NAME_CAPACITY)
        return buffer.value if self._image_name(process, 1, buffer, ctypes.byref(size)) else None

    def image_walk(self, process: int) -> ImageWalk:
        """Group regions by allocation base and name each committed image."""
        system = _SystemInfo()
        self._system_info(ctypes.byref(system))
        buffer = ctypes.create_unicode_buffer(_NAME_CAPACITY)
        names: dict[int, str] = {}
        address, regions = 0, 0
        while address < system.maximum:
            region = _Region()
            if self._query(process, address, ctypes.byref(region), ctypes.sizeof(region)) != ctypes.sizeof(region):
                return ImageWalk(complete=False, regions=regions, mapped_names=tuple(names.values()))
            regions += 1
            if region.state == _MEM_COMMIT and region.kind == _MEM_IMAGE and region.allocation not in names:
                if not self._mapped_name(process, region.base, buffer, _NAME_CAPACITY):  # pragma: no cover - race only
                    return ImageWalk(complete=False, regions=regions, mapped_names=tuple(names.values()))
                names[region.allocation] = buffer.value
            address = (region.base or 0) + region.size
        return ImageWalk(complete=True, regions=regions, mapped_names=tuple(names.values()))

    def _open_file(self, path: str, access: int, share: int) -> int | None:
        handle = self._create_file(path, access, share, None, _OPEN_EXISTING, 0, None)
        return None if handle in (None, _INVALID_HANDLE) else handle

    def open_image(self, native_name: str) -> int | None:
        """Open the native image path for read and execute, sharing read and delete."""
        return self._open_file(GLOBALROOT + native_name, _READ_EXECUTE, _SHARE_READ_DELETE)

    def image_mapping_status(self, process: int, image: int) -> int:
        """Return the unsigned ``ProcessImageFileMapping`` status for a file handle."""
        candidate = wintypes.HANDLE(image)
        returned = wintypes.DWORD()
        status = self._identity(process, _IMAGE_FILE_MAPPING, ctypes.byref(candidate), ctypes.sizeof(candidate), ctypes.byref(returned))
        return status & 0xFFFFFFFF

    def _chunks(self, handle: int) -> Iterator[bytes | None]:
        """Yield each chunk to the end of the file, or ``None`` when a read fails."""
        buffer = ctypes.create_string_buffer(_READ_CHUNK)
        count = wintypes.DWORD()
        while self._read(handle, buffer, _READ_CHUNK, ctypes.byref(count), None):
            if not count.value:
                return
            yield ctypes.string_at(buffer, count.value)
        yield None

    def sha256(self, image: int) -> tuple[str, int] | None:
        """Hash through the retained handle from its current position.

        The handle is read once to its end: the caller keeps the digest for the
        invocation instead of hashing the same handle again.
        """
        digest = hashlib.sha256()
        total = 0
        for chunk in self._chunks(image):
            if chunk is None:
                return None
            digest.update(chunk)
            total += len(chunk)
        return digest.hexdigest(), total

    def read_file(self, path: str) -> bytes | None:
        """Read a whole file, sharing read, write and delete with its writer."""
        handle = self._open_file(path, _GENERIC_READ, _SHARE_ALL)
        if handle is None:
            return None
        try:
            chunks = list(self._chunks(handle))
        finally:
            self._close(handle)
        return None if None in chunks else b"".join(chunk for chunk in chunks if chunk is not None)

    def close(self, handle: int) -> None:
        """Close one handle returned by this adapter."""
        self._close(handle)


# eof
