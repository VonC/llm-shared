"""Interrogate exact Windows process identities and serialize lock transitions.

The named mutex protects only short record transitions. Durable ownership lives
in the project lock file and can outlive a process during retained handoffs.
An abandoned kernel mutex is safe to take; an unknown durable owner is not.
"""

from __future__ import annotations

import ctypes
import os
from contextlib import contextmanager
from ctypes import wintypes
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

_QUERY_AND_SYNCHRONIZE = 0x00101000
_INVALID_PARAMETER = 87
_WAIT_OBJECT = 0
_WAIT_ABANDONED = 0x80
_WAIT_TIMEOUT = 0x102
_TRANSITION_WAIT_MS = 1000
_HIGH_WORD_SHIFT = 32


class ProcessState(Enum):
    """Only DEAD is proof that this exact process can no longer own an operation."""

    ALIVE = "alive"
    DEAD = "dead"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProcessIdentity:
    """PID and kernel creation FILETIME, retained as an exact integer."""

    pid: int
    created: int


def _kernel() -> ctypes.WinDLL:
    """Declare pointer-width-safe signatures before calling the native API."""
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    api.OpenProcess.restype = wintypes.HANDLE
    api.GetProcessTimes.argtypes = [wintypes.HANDLE, *[ctypes.POINTER(wintypes.FILETIME)] * 4]
    api.GetProcessTimes.restype = wintypes.BOOL
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    api.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    api.CreateMutexW.restype = wintypes.HANDLE
    api.ReleaseMutex.argtypes = [wintypes.HANDLE]
    api.ReleaseMutex.restype = wintypes.BOOL
    return api


def _probe(pid: int) -> tuple[ProcessState, int]:
    """Separate inaccessible/query-failed processes from positively absent ones."""
    api = _kernel()
    handle = api.OpenProcess(_QUERY_AND_SYNCHRONIZE, 0, pid)
    if not handle:
        state = ProcessState.DEAD if ctypes.get_last_error() == _INVALID_PARAMETER else ProcessState.UNKNOWN
        return state, 0
    try:
        wait = api.WaitForSingleObject(handle, 0)
        if wait == _WAIT_OBJECT:
            return ProcessState.DEAD, 0
        if wait != _WAIT_TIMEOUT:
            return ProcessState.UNKNOWN, 0
        created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
        if not api.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)):
            return ProcessState.UNKNOWN, 0
        return ProcessState.ALIVE, (created.dwHighDateTime << _HIGH_WORD_SHIFT) | created.dwLowDateTime
    finally:
        api.CloseHandle(handle)


def current_identity() -> ProcessIdentity:
    """Fail before publication unless the current process can identify itself."""
    pid = os.getpid()
    state, created = _probe(pid)
    if state is not ProcessState.ALIVE or created <= 0:
        msg = "Cannot establish current Windows process creation time"
        raise OSError(msg)
    return ProcessIdentity(pid, created)


def process_state(owner: ProcessIdentity) -> ProcessState:
    """Treat a reused PID as dead and API uncertainty as unverifiable ownership."""
    if owner.pid <= 0 or owner.created <= 0:
        return ProcessState.UNKNOWN
    state, created = _probe(owner.pid)
    if state is ProcessState.ALIVE and created != owner.created:
        return ProcessState.DEAD
    return state


@contextmanager
def transition_mutex(name: str) -> Generator[None]:
    """Wait up to one second for a cooperating transition across Windows sessions.

    Kernel abandonment releases a crashed transition automatically. Brief record
    checks cannot interrupt owner cleanup or handoff. A mutex still busy after
    the bound, or inaccessible, fails visibly without bypassing serialization.
    """
    api = _kernel()
    handle = api.CreateMutexW(None, 0, name)
    if not handle:
        msg = "Cannot open project operation transition mutex"
        raise OSError(msg)
    acquired = False
    try:
        wait = api.WaitForSingleObject(handle, _TRANSITION_WAIT_MS)
        if wait not in {_WAIT_OBJECT, _WAIT_ABANDONED}:
            msg = f"Project operation transition mutex unavailable (wait={wait})"
            raise OSError(msg)
        acquired = True
        yield
    finally:
        if acquired:
            api.ReleaseMutex(handle)
        api.CloseHandle(handle)


# eof
