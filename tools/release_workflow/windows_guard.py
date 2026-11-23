"""Hold an executable against replacement from its validation until the child that runs it ends.

Step 2 of v0.14.0 git-cliff-provisioning (design "Reuse check and the use
guard", design decision Q07; plan decisions Q04 and Q05). The use guard is a
`CreateFileW` handle opened for reading with `FILE_SHARE_READ` only: other
readers and the loader's own image open stay compatible, while any open that
asks for write or delete access, including the rename a replacement needs,
fails with a sharing violation for as long as the guard is open. The handle is
not inheritable; a child that runs the executable receives it through its
explicit inherited-handle list (`ChildRequest.inherited`), so the protection
lasts for that child's actual lifetime.

`sha256_and_size()` hashes through a duplicated handle, from the start of the
file object whose position both handles share, and closes only the duplicate.
`retain()` hands the guard to `windows_child.RETAINED` when an unconfirmed
child end forbids any cleanup: `close()` then leaves the handle open, and the
operating system closes it with the process.
"""

from __future__ import annotations

import ctypes
import errno
import hashlib
from ctypes import wintypes
from typing import TYPE_CHECKING, Self

from tools.release_workflow import windows_native as native
from tools.release_workflow.windows_child import RETAINED
from tools.release_workflow.windows_native import NativeCallError

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.windows_native import Kernel

_READ_SIZE = 1 << 20
_MISSING = frozenset({native.ERROR_FILE_NOT_FOUND, native.ERROR_PATH_NOT_FOUND})


class UseGuard:
    """A read handle on an executable that denies write and delete sharing while it is open."""

    __slots__ = ("_api", "_closed", "_handle", "_path", "_retained")

    def __init__(self, path: Path, handle: int, api: Kernel) -> None:
        """Own an open guard handle."""
        self._path = path
        self._handle = handle
        self._api = api
        self._closed = False
        self._retained = False

    @property
    def path(self) -> Path:
        """Return the guarded executable."""
        return self._path

    @property
    def handle(self) -> int:
        """Return the guard handle a child lists among the handles it inherits."""
        return self._handle

    def sha256_and_size(self) -> tuple[str, int]:
        """Hash the guarded bytes through a duplicate handle, which is closed afterwards."""
        if self._closed:
            msg = f"the use guard of {self._path} is closed"
            raise ValueError(msg)
        api = self._api
        duplicate = wintypes.HANDLE()
        api.DuplicateHandle(native.CURRENT_PROCESS, self._handle, native.CURRENT_PROCESS, duplicate, 0, 0, native.DUPLICATE_SAME_ACCESS)
        digest, size = hashlib.sha256(), 0
        buffer = ctypes.create_string_buffer(_READ_SIZE)
        count = wintypes.DWORD()
        try:
            api.SetFilePointerEx(duplicate.value, 0, None, native.FILE_BEGIN)
            while True:
                api.ReadFile(duplicate.value, buffer, _READ_SIZE, count, None)
                if not count.value:
                    return digest.hexdigest(), size
                digest.update(ctypes.string_at(buffer, count.value))
                size += count.value
        finally:
            api.CloseHandle(duplicate.value)

    def close(self) -> None:
        """Close the guard once; a retained guard stays open until the process ends."""
        if self._closed or self._retained:
            return
        self._closed = True
        self._api.CloseHandle(self._handle)

    def retain(self) -> None:
        """Give the guard to the process-lifetime owner: no later path closes it."""
        self._retained = True
        RETAINED.keep(self)

    def __enter__(self) -> Self:
        """Use the guard for a block."""
        return self

    def __exit__(self, *_exception: object) -> None:
        """Close the guard, unless it was retained."""
        self.close()


def open_guard(path: Path, *, api: Kernel | None = None) -> UseGuard:
    """Open the use guard on an executable; a missing file is `FileNotFoundError`."""
    kernel = native.kernel() if api is None else api
    try:
        handle = kernel.CreateFileW(str(path), native.GENERIC_READ, native.FILE_SHARE_READ, None, native.OPEN_EXISTING,
                                    native.FILE_ATTRIBUTE_NORMAL, None)
    except NativeCallError as error:
        if error.winerror in _MISSING:
            raise FileNotFoundError(errno.ENOENT, "the executable to guard is missing", str(path)) from error
        raise OSError(None, f"cannot open the use guard: {error.call} failed", str(path), error.winerror) from error
    return UseGuard(path, handle, kernel)


# eof
