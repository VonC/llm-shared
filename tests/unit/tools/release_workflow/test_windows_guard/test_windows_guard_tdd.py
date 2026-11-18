"""The use guard opens a read handle that denies write and delete sharing, and hashes through a duplicate.

Step 2 of v0.14.0 git-cliff-provisioning (design "Reuse check and the use
guard", design decision Q07; plan decision Q05). `open_guard` calls
`CreateFileW` with `GENERIC_READ`, `FILE_SHARE_READ` only, `OPEN_EXISTING` and
no security attributes, so the handle is not inheritable; a missing file is
`FileNotFoundError` and a sharing violation an `OSError` carrying the Windows
error. `sha256_and_size()` duplicates the handle, rewinds the shared position,
reads to the end and closes only the duplicate, so it can run again.
`close()` is idempotent, the context manager closes, and `retain()` hands the
guard to `RETAINED`, after which neither `close()` nor the context exit closes
the handle.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.unit.tools.release_workflow.native_kernel_fake import FakeKernel
from tools.release_workflow import windows_native as native
from tools.release_workflow.windows_child import RETAINED
from tools.release_workflow.windows_guard import UseGuard, open_guard

_EXECUTABLE = Path("C:/cache/2.14.2/git-cliff.exe")
_CONTENT = bytes(range(256)) * 9000


def _kernel() -> FakeKernel:
    """Declare one cached executable larger than one read."""
    kernel = FakeKernel()
    kernel.files[str(_EXECUTABLE)] = _CONTENT
    return kernel


def test_the_guard_denies_write_and_delete_sharing() -> None:
    """The open requests reading, shares reading only and is not inheritable."""
    kernel = _kernel()
    guard = open_guard(_EXECUTABLE, api=kernel)
    assert kernel.arguments("CreateFileW") == (str(_EXECUTABLE), native.GENERIC_READ, native.FILE_SHARE_READ, None,
                                               native.OPEN_EXISTING, native.FILE_ATTRIBUTE_NORMAL, None)
    assert (guard.path, guard.handle, kernel.inheritable.get(guard.handle, False)) == (_EXECUTABLE, kernel.created[0], False)


@pytest.mark.parametrize("error", [native.ERROR_FILE_NOT_FOUND, native.ERROR_PATH_NOT_FOUND])
def test_a_missing_executable_is_file_not_found(error: int) -> None:
    """A missing file or folder makes the entry absent."""
    kernel = FakeKernel()
    kernel.fail("CreateFileW", error=error)
    with pytest.raises(FileNotFoundError) as raised:
        open_guard(_EXECUTABLE, api=kernel)
    assert raised.value.filename == str(_EXECUTABLE)


def test_a_sharing_violation_keeps_the_windows_error() -> None:
    """An executable opened for writing elsewhere is refused with its Windows error."""
    kernel = _kernel()
    kernel.denied.add(str(_EXECUTABLE))
    with pytest.raises(OSError, match="cannot open the use guard") as raised:
        open_guard(_EXECUTABLE, api=kernel)
    assert (raised.value.winerror, raised.value.filename) == (native.ERROR_SHARING_VIOLATION, str(_EXECUTABLE))


def test_hashing_reads_through_a_duplicate_it_closes() -> None:
    """The digest and size cover every byte, twice in a row, and only the duplicate handle is closed."""
    kernel = _kernel()
    expected = (hashlib.sha256(_CONTENT).hexdigest(), len(_CONTENT))
    with open_guard(_EXECUTABLE, api=kernel) as guard:
        assert guard.sha256_and_size() == expected
        assert guard.sha256_and_size() == expected
        duplicates = [kernel.arguments("DuplicateHandle", number)[3].value for number in (1, 2)]
        assert [kernel.arguments("DuplicateHandle", number)[:3] for number in (1, 2)] == [
            (native.CURRENT_PROCESS, guard.handle, native.CURRENT_PROCESS)] * 2
        assert {arguments[0] for name, arguments in kernel.calls if name in {"ReadFile", "SetFilePointerEx"}} == set(duplicates)
        assert kernel.closed == duplicates
    assert kernel.closed == [*duplicates, guard.handle]


def test_close_is_idempotent_and_hashing_a_closed_guard_is_refused() -> None:
    """A second close changes nothing; a closed guard cannot vouch for the file."""
    kernel = _kernel()
    guard = open_guard(_EXECUTABLE, api=kernel)
    guard.close()
    guard.close()
    assert kernel.closed == [guard.handle]
    with pytest.raises(ValueError, match="closed"):
        guard.sha256_and_size()


def test_a_retained_guard_is_never_closed() -> None:
    """After `retain()`, the guard belongs to `RETAINED`; close and the context exit leave the handle open."""
    kernel = _kernel()
    with open_guard(_EXECUTABLE, api=kernel) as guard:
        guard.retain()
        guard.close()
    assert isinstance(guard, UseGuard)
    assert RETAINED.entries()[-1] is guard
    assert kernel.closed == []
    assert guard.sha256_and_size()[1] == len(_CONTENT)


# eof
