"""Hold waiter-driver processes by handle, so cleanup reaches the real interpreter.

On Windows, the ``python`` of a virtual environment is a launcher stub that
runs the real interpreter as its child. Killing the process a test started
ended only the stub and left the waiter polling for an hour. The driver now
reports its own pid, and a :class:`TrackedProcess` opens that exact process
once: Windows never reuses a pid while a handle to it stays open, so the
liveness check and the kill can never reach an unrelated process. The driver
also tracks its parents with the same class, to exit once they are gone.
"""

from __future__ import annotations

import ctypes
import errno
import os
import signal
from typing import Final

# Access rights: wait on the process, and terminate it.
_SYNCHRONIZE: Final = 0x00100000
_PROCESS_TERMINATE: Final = 0x0001
# WaitForSingleObject result while the process still runs.
_WAIT_TIMEOUT: Final = 0x00000102
# The exit code given to a waiter ended by its parent's cleanup.
_KILLED_EXIT: Final = 1
# OpenProcess handle inheritance: child processes never inherit this handle.
_NOT_INHERITED: Final = 0
# Milliseconds a kill waits for the process to be gone; termination is asynchronous.
_EXIT_WAIT_MS: Final = 5000


class TrackedProcess:
    """One process, held by a handle on Windows and by its pid elsewhere."""

    def __init__(self, pid: int) -> None:
        """Open the process as it is now; a process already gone reads as dead.

        Args:
            pid: The process id.
        """
        self.pid = pid
        self._handle: int | None = None
        if os.name == "nt":
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.OpenProcess.restype = ctypes.c_void_p
            kernel32.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
            kernel32.TerminateProcess.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
            kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
            self._kernel32 = kernel32
            self._handle = kernel32.OpenProcess(_SYNCHRONIZE | _PROCESS_TERMINATE, _NOT_INHERITED, pid) or None

    def alive(self) -> bool:
        """Tell whether this exact process still runs.

        Returns:
            True while it runs.
        """
        if os.name == "nt":
            return self._handle is not None and self._kernel32.WaitForSingleObject(self._handle, 0) == _WAIT_TIMEOUT
        try:
            os.kill(self.pid, 0)
        except OSError as error:
            return error.errno == errno.EPERM
        return True

    def kill(self) -> None:
        """End this exact process if it still runs, and wait until it is gone."""
        if not self.alive():
            return
        if os.name == "nt":
            self._kernel32.TerminateProcess(self._handle, _KILLED_EXIT)
            self._kernel32.WaitForSingleObject(self._handle, _EXIT_WAIT_MS)
            return
        os.kill(self.pid, signal.SIGKILL)

    def close(self) -> None:
        """Release the handle; the pid may be reused afterwards."""
        if self._handle is not None:
            self._kernel32.CloseHandle(self._handle)
            self._handle = None


# eof
