"""A staged archive is checked against the pin from its own bytes, and only its manifest member is extracted.

Step 4 of v0.14.0 git-cliff-provisioning (design "Archive verification" and
"Single-member extraction"; design decision Q01; plan decision Q10). The
parent recomputes size and SHA-256 from the staged file instead of trusting
the worker, and a mismatch is a verification error. Extraction reads only the
manifest member and writes it as `git-cliff.exe`, hashing the written bytes;
a missing member, a file that is not a ZIP archive or an uncompressed size
other than the directory entry is an extraction error, and traversal,
absolute or drive-letter member names beside the member never become paths.
"""

from __future__ import annotations

import hashlib
import io
import struct
import zipfile
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import (
    STAND_IN_EXECUTABLE,
    synthetic_archive,
    synthetic_pin,
)
from tools.release_workflow.git_cliff.archive import (
    ExtractionError,
    VerificationError,
    extract_member,
    verify_archive,
)

if TYPE_CHECKING:
    from pathlib import Path

PIN = synthetic_pin()
_CENTRAL = b"PK\x01\x02"
_CENTRAL_SIZE_OFFSET = 24


def _zip(members: dict[str, bytes], *, compression: int = zipfile.ZIP_DEFLATED) -> bytes:
    """Build an archive holding these members in order."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=compression) as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _staged(tmp_path: Path, content: bytes) -> tuple[Path, Path]:
    """Stage an archive and an empty staging directory beside it."""
    archive, staging = tmp_path / "archive.zip", tmp_path / "staging"
    archive.write_bytes(content)
    staging.mkdir()
    return archive, staging


def test_a_staged_archive_matching_the_pin_verifies(tmp_path: Path) -> None:
    """The recomputed size and digest equal the manifest's."""
    archive, _ = _staged(tmp_path, synthetic_archive())
    verify_archive(archive, PIN)


@pytest.mark.parametrize(("content", "reason"), [
    pytest.param(synthetic_archive()[:-1], "bytes, expected", id="truncated"),
    pytest.param(synthetic_archive()[:-1] + b"!", "SHA-256", id="altered"),
])
def test_a_staged_archive_differing_from_the_pin_fails_verification(tmp_path: Path, content: bytes, reason: str) -> None:
    """A size or digest other than the manifest's is never extracted."""
    archive, _ = _staged(tmp_path, content)
    with pytest.raises(VerificationError, match=reason):
        verify_archive(archive, PIN)


def test_only_the_manifest_member_is_written_as_git_cliff_exe(tmp_path: Path) -> None:
    """The member is written under the fixed name, and its written bytes are hashed."""
    archive, staging = _staged(tmp_path, synthetic_archive())
    assert extract_member(archive, PIN, staging) == (hashlib.sha256(STAND_IN_EXECUTABLE).hexdigest(), len(STAND_IN_EXECUTABLE))
    assert [path.name for path in staging.iterdir()] == ["git-cliff.exe"]
    assert (staging / "git-cliff.exe").read_bytes() == STAND_IN_EXECUTABLE


def test_traversal_absolute_and_drive_names_never_become_paths(tmp_path: Path) -> None:
    """Members named outside staging are ignored, like every member other than the manifest's."""
    members = {"../escape.exe": b"x", "/absolute.exe": b"x", "C:/drive.exe": b"x", "C:relative.exe": b"x", PIN.member: STAND_IN_EXECUTABLE,
               "git-cliff-2.14.2/git-cliff-mangen.exe": b"x"}
    archive, staging = _staged(tmp_path, _zip(members))
    extract_member(archive, PIN, staging)
    assert sorted(path.name for path in tmp_path.iterdir()) == ["archive.zip", "staging"]
    assert [path.name for path in staging.iterdir()] == ["git-cliff.exe"]


def test_a_missing_member_is_an_extraction_error(tmp_path: Path) -> None:
    """An archive without the manifest member gives nothing to install."""
    archive, staging = _staged(tmp_path, _zip({"git-cliff-2.14.2/README.md": b"readme"}))
    with pytest.raises(ExtractionError, match=r"no member git-cliff-2\.14\.2/git-cliff\.exe"):
        extract_member(archive, PIN, staging)
    assert list(staging.iterdir()) == []


def test_a_file_that_is_not_a_zip_archive_is_an_extraction_error(tmp_path: Path) -> None:
    """Bytes that are not an archive cannot be read as one (longer than the end record `zipfile` seeks back to)."""
    archive, staging = _staged(tmp_path, b"not an archive at all\n" * 8)
    with pytest.raises(ExtractionError, match="not a readable ZIP archive"):
        extract_member(archive, PIN, staging)


@pytest.mark.parametrize("change", [-1, 1])
def test_an_uncompressed_size_other_than_the_directory_entry_is_an_extraction_error(tmp_path: Path, change: int) -> None:
    """A directory entry that declares fewer or more bytes than the member holds is refused."""
    content = bytearray(_zip({PIN.member: STAND_IN_EXECUTABLE}, compression=zipfile.ZIP_STORED))
    offset = content.index(_CENTRAL) + _CENTRAL_SIZE_OFFSET
    struct.pack_into("<I", content, offset, len(STAND_IN_EXECUTABLE) + change)
    archive, staging = _staged(tmp_path, bytes(content))
    with pytest.raises(ExtractionError, match=r"git-cliff-2\.14\.2/git-cliff\.exe"):
        extract_member(archive, PIN, staging)


# eof
