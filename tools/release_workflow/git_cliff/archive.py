"""Check a staged archive against its pin from its own bytes, then extract only the manifest member.

Step 4 of v0.14.0 git-cliff-provisioning (design "Archive verification" and
"Single-member extraction"; design decision Q01; plan decision Q10).

- `verify_archive` recomputes the size and SHA-256 of the staged file and
  compares them with the pin, instead of trusting the worker's report; a
  mismatch is `VerificationError`, which is never retried.
- `extract_member` reads only the manifest member, with `zipfile`, and writes
  it as `git-cliff.exe` in the target directory, hashing the written bytes.
  No other member is read and no member path becomes a filesystem path, so
  traversal, absolute or drive-letter names cannot write anywhere. A missing
  member, a file that is not a readable ZIP archive, a failed CRC or an
  uncompressed size other than the directory entry is `ExtractionError`.

The caller removes the staging directory on any failure; nothing here
deletes a file.
"""

from __future__ import annotations

import hashlib
import zipfile
import zlib
from typing import TYPE_CHECKING, Protocol

from tools.release_workflow.git_cliff.cache import EXECUTABLE

if TYPE_CHECKING:
    from pathlib import Path

_CHUNK = 1 << 20


class VerificationError(ValueError):
    """The staged archive is not the asset the manifest recorded."""


class ExtractionError(ValueError):
    """The manifest member cannot be extracted whole from the staged archive."""


class ArchivePin(Protocol):
    """What identifies an asset: its size in bytes, its SHA-256 and the member to extract."""

    @property
    def size(self) -> int:
        """Return the archive size in bytes."""
        ...

    @property
    def sha256(self) -> str:
        """Return the archive's lowercase hexadecimal SHA-256."""
        ...

    @property
    def member(self) -> str:
        """Return the archive member holding `git-cliff.exe`."""
        ...


def verify_archive(path: Path, pin: ArchivePin) -> None:
    """Recompute the staged archive's size and SHA-256 and require the pin's."""
    digest, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while chunk := stream.read(_CHUNK):
            digest.update(chunk)
            size += len(chunk)
    if size != pin.size:
        msg = f"{path.name}: {size} bytes, expected {pin.size}"
        raise VerificationError(msg)
    if digest.hexdigest() != pin.sha256:
        msg = f"{path.name}: SHA-256 {digest.hexdigest()}, expected {pin.sha256}"
        raise VerificationError(msg)


def extract_member(path: Path, pin: ArchivePin, target_dir: Path) -> tuple[str, int]:
    """Write the manifest member as `git-cliff.exe` and return the SHA-256 and size of the written bytes."""
    digest, size = hashlib.sha256(), 0
    try:
        with zipfile.ZipFile(path) as archive:
            info = archive.getinfo(pin.member)
            with archive.open(info) as source, (target_dir / EXECUTABLE).open("xb") as target:
                while chunk := source.read(_CHUNK):
                    target.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
    except KeyError as error:
        msg = f"{path.name}: no member {pin.member}"
        raise ExtractionError(msg) from error
    except (zipfile.BadZipFile, EOFError, zlib.error) as error:
        msg = f"{path.name}: not a readable ZIP archive or member {pin.member}: {error}"
        raise ExtractionError(msg) from error
    if size != info.file_size:
        msg = f"{path.name}: member {pin.member} holds {size} bytes, its directory entry {info.file_size}"
        raise ExtractionError(msg)
    return digest.hexdigest(), size


# eof
