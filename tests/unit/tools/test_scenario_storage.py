"""Observable file contracts required by process-free repository scenarios."""

from __future__ import annotations

import io
import os
import shutil
import sqlite3
import stat
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.memory_filesystem import ScenarioFilesystem
from tests.scenario_storage import Entry

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def scratch_filesystem() -> Iterator[ScenarioFilesystem]:
    """Install an isolated memory tree, counting construction and cleanup."""
    # This fixture already owns an independent, explicitly simulated store.
    # A native temporary directory contributes no file-contract evidence.
    root = Path(Path.cwd().anchor) / f"storage-contract-{os.getpid()}"
    filesystem = ScenarioFilesystem(root)
    with pytest.MonkeyPatch.context() as patch:
        filesystem.install(patch)
        yield filesystem


@pytest.fixture
def scratch(scratch_filesystem: ScenarioFilesystem) -> Path:
    """Expose the isolated tree to tests exercising native path interfaces."""
    return Path(scratch_filesystem.root)


def test_atomic_publication_retains_complete_bytes(scratch: Path) -> None:
    """NamedTemporaryFile's opener creates a file, then replace publishes it."""
    destination = scratch / "record.json"
    destination.write_bytes(b"old")
    with tempfile.NamedTemporaryFile(dir=scratch, mode="w", encoding="utf-8", newline="\n", delete=False) as stream:
        stream.write('{"text":"\u00e9"}\n')
        temporary = Path(stream.name)
    assert temporary.is_file()
    assert destination.read_bytes() == b"old"
    temporary.replace(destination)
    assert destination.read_bytes() == '{"text":"\u00e9"}\n'.encode()
    assert not temporary.exists()


def test_copytree_retains_bytes_metadata_and_independence(scratch: Path) -> None:
    """Scenario cloning exercises shutil's own recursive copy semantics."""
    source = scratch / "source"
    source.mkdir()
    item = source / "record"
    item.write_bytes(b"\x00\xff")
    os.utime(item, ns=(1_234_000_000_000, 1_234_000_000_000))
    target = scratch / "clone"
    shutil.copytree(source, target)
    copied = target / "record"
    assert copied.read_bytes() == b"\x00\xff"
    assert copied.stat().st_mtime_ns == item.stat().st_mtime_ns
    copied.write_bytes(b"changed")
    assert item.read_bytes() == b"\x00\xff"
    assert list(target.iterdir()) == [copied]


def test_metadata_observes_changes_after_repeated_reads() -> None:
    """Repeated stat reads cannot hide content, permission, time or type changes."""
    entry = Entry("record", 1, content=b"before")
    before = entry.stat()
    assert entry.stat() == before
    entry.content = b"after!"
    assert entry.stat().st_size == len(entry.content)
    entry.content = b"short"
    entry.mode = 0o400
    entry.mtime += 1
    entry.st_ino += 1
    entry.kind = "junction"
    after = entry.stat()
    assert after.st_size == len(entry.content)
    assert after.st_mode == stat.S_IFLNK | 0o400
    assert after.st_mtime_ns == before.st_mtime_ns + 1_000_000_000
    assert after.st_ino == before.st_ino + 1
    assert after.st_file_attributes == stat.FILE_ATTRIBUTE_REPARSE_POINT
    assert after.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT


def test_temporary_directory_cleans_nested_entries(scratch: Path) -> None:
    """Production tempfile cleanup traverses memory directory entries on Windows."""
    with tempfile.TemporaryDirectory(dir=scratch) as name:
        temporary = Path(name)
        nested = temporary / "nested"
        nested.mkdir()
        (nested / "record").write_bytes(b"content")
        assert nested.is_dir()
    assert not temporary.exists()


def test_exclusive_open_and_missing_parent_fail(scratch: Path) -> None:
    """Publication and lock setup retain duplicate and missing-parent errors."""
    item = scratch / "record"
    with item.open("xb") as stream:
        stream.write(b"one")
    with pytest.raises(FileExistsError):
        item.open("xb")
    with pytest.raises(FileNotFoundError):
        (scratch / "missing" / "record").write_bytes(b"two")
    assert item.read_bytes() == b"one"


def test_open_handles_share_bytes_but_have_independent_cursors(scratch: Path) -> None:
    """Two handles observe writes and truncation without overwriting stale bytes."""
    item = scratch / "record"
    item.write_bytes(b"abc")
    with item.open("rb") as reader, item.open("r+b") as writer:
        assert reader.read(1) == b"a"
        writer.seek(1)
        writer.write(b"Z")
        assert reader.read() == b"Zc"
        with pytest.raises(io.UnsupportedOperation):
            reader.write(b"bad")
        writer.truncate(2)
        reader.seek(0)
        assert reader.read() == b"aZ"
    with item.open("ab") as appender:
        appender.seek(0)
        appender.write(b"!")
    assert item.read_bytes() == b"aZ!"


def test_link_and_cwd_resolution(scratch: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Relative paths, symlink reads and dangling links stay in the model."""
    item = scratch / "record"
    item.write_text("content", encoding="utf-8")
    link = scratch / "link"
    link.symlink_to("record")
    monkeypatch.chdir(scratch)
    assert Path("link").read_text(encoding="utf-8") == "content"
    assert link.resolve() == item
    item.unlink()
    with pytest.raises(FileNotFoundError):
        link.resolve(strict=True)
    assert link.is_symlink()
    assert not link.exists()


def test_link_resolution_observes_repointing_among_unrelated_trees(
    scratch: Path, scratch_filesystem: ScenarioFilesystem,
) -> None:
    """Link lookup scales with path depth and never caches mutable targets."""
    first, second = scratch / "first", scratch / "second"
    first.mkdir()
    second.mkdir()
    (first / "record").write_bytes(b"first")
    (second / "record").write_bytes(b"second")
    # These neighbors are input records, not symlink-creation assertions.
    # Keep all 256 while avoiding 256 repetitions of the path/router protocol.
    storage = scratch_filesystem.filesystem
    parent = storage._key(scratch)
    for index in range(256):
        name = str(scratch / f"unrelated-{index}")
        key = storage._normalized(name)
        storage.entries[key] = Entry(name, storage.next_inode, kind="link", target=str(first))
        storage.next_inode += 1
        storage.links[key] = str(first)
        storage.children[parent][key] = None
    link = scratch / "alias"
    link.symlink_to(first, target_is_directory=True)
    nested = link / "record"
    assert nested.resolve() == first / "record"
    assert nested.read_bytes() == b"first"
    link.unlink()
    link.symlink_to(second, target_is_directory=True)
    assert nested.resolve() == second / "record"
    assert nested.read_bytes() == b"second"
    assert not (scratch / "alias-other" / "record").exists()
    link.unlink()
    link.symlink_to("alias", target_is_directory=True)
    with pytest.raises(OSError, match="scenario link cycle"):
        nested.resolve()


def test_sqlite_reopens_committed_pages_and_rejects_corruption(scratch: Path) -> None:
    """The real SQLite engine retains schema, rows and errors in memory bytes."""
    path = scratch / "evidence"
    connection = sqlite3.connect(str(path))
    connection.execute("create table evidence (line integer)")
    connection.execute("insert into evidence values (1)")
    connection.commit()
    connection.close()
    connection.close()
    assert path.read_bytes().startswith(b"SQLite format 3")
    reopened = sqlite3.connect(str(path))
    try:
        assert reopened.execute("select line from evidence").fetchall() == [(1,)]
        reopened.execute("insert into evidence values (2)")
        reopened.rollback()
        assert reopened.execute("select line from evidence").fetchall() == [(1,)]
        reopened.execute("insert into evidence values (3)")
    finally:
        reopened.close()
    after_close = sqlite3.connect(str(path))
    try:
        assert after_close.execute("select line from evidence").fetchall() == [(1,)]
    finally:
        after_close.close()
    path.write_bytes(b"invalid database")
    corrupt = sqlite3.connect(str(path))
    try:
        with pytest.raises(sqlite3.DatabaseError):
            corrupt.execute("select line from evidence")
    finally:
        corrupt.close()
    assert path.read_bytes() == b"invalid database"


# eof
