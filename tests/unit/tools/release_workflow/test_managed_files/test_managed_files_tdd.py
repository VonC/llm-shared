"""Prove write boundaries reject changed destinations and preserve original data."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import managed_files
from tools.release_workflow.managed_files import (
    ManagedWriteError,
    authorize_write,
    prepare_directory,
    replace_bytes,
)
from tools.release_workflow.paths import ProjectIdentity

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox


def identity(root: Path) -> ProjectIdentity:
    """Represent a previously validated root without repeating Git discovery."""
    return ProjectIdentity(root, root / ".git", root / ".git", str(root))


def test_authorization_is_read_only_and_replacement_is_atomic(tmp_path: Path) -> None:
    """Explicit directory preparation precedes a byte-exact same-parent write."""
    project = identity(tmp_path)
    destination = authorize_write(project, "output/version.txt")
    assert list(tmp_path.iterdir()) == []
    prepare_directory(authorize_write(project, "output"))
    replace_bytes(destination, b"old")
    replace_bytes(destination, b"new\x00\xff")
    assert (tmp_path / "output/version.txt").read_bytes() == b"new\x00\xff"
    assert [path.name for path in (tmp_path / "output").iterdir()] == ["version.txt"]


@pytest.mark.parametrize("name", [".", "..", "../escape", "CON", "nul.txt", "NUL .txt", "LPT¹.log", "x.", "x ", "x:stream", "x?", "x*", "x\x01"])
def test_unsafe_windows_destinations_fail_without_changes(tmp_path: Path, name: str) -> None:
    """Root aliases, escape, reserved devices and alternate streams are invalid."""
    with pytest.raises(ManagedWriteError):
        authorize_write(identity(tmp_path), name)
    assert list(tmp_path.iterdir()) == []


def test_replace_failure_preserves_original_and_cleans_owned_temporary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A failed final atomic operation neither truncates nor leaks its payload."""
    path = tmp_path / "version.txt"
    path.write_bytes(b"original")
    unrelated = tmp_path / ".release-unrelated.tmp"
    unrelated.write_bytes(b"keep")
    def denied(_source: Path, _destination: Path) -> None:
        msg = "replace denied"
        raise PermissionError(msg)
    monkeypatch.setattr("tools.release_workflow.managed_files.os.replace", denied)
    with pytest.raises(ManagedWriteError, match="replace denied"):
        replace_bytes(authorize_write(identity(tmp_path), path), b"new")
    assert path.read_bytes() == b"original"
    assert {item.name for item in tmp_path.iterdir()} == {path.name, unrelated.name}


def test_repointed_junction_rejects_preparation(git_sandbox: GitSandbox) -> None:
    """A directory authorized inside B cannot later prepare files inside A."""
    root = git_sandbox.home / "B"
    alias = git_sandbox.junction("B/alias", root / "sub")
    destination = authorize_write(identity(root), alias / "future")
    alias.rmdir()
    git_sandbox.junction("B/alias", git_sandbox.home / "A")
    with pytest.raises(ManagedWriteError):
        prepare_directory(destination)
    assert not (git_sandbox.home / "A/future").exists()


def test_temporary_flush_failure_preserves_old_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Failed durability never publishes partial bytes or cleans unrelated files."""
    target = tmp_path / "version.txt"
    target.write_bytes(b"old")
    def denied(_fd: int) -> None:
        msg = "flush denied"
        raise OSError(msg)
    monkeypatch.setattr(managed_files.os, "fsync", denied)
    with pytest.raises(ManagedWriteError, match="flush denied"):
        replace_bytes(authorize_write(identity(tmp_path), target), b"new")
    assert target.read_bytes() == b"old"
    assert list(tmp_path.iterdir()) == [target]


def test_preparation_of_file_is_execution_failure(tmp_path: Path) -> None:
    """A path that has become a file cannot be prepared as a directory."""
    destination = authorize_write(identity(tmp_path), "output")
    destination.path.write_bytes(b"keep")
    with pytest.raises(ManagedWriteError):
        prepare_directory(destination)
    assert destination.path.read_bytes() == b"keep"


def test_missing_parent_does_not_create_implicit_directories(tmp_path: Path) -> None:
    """File replacement requires explicit successful parent preparation first."""
    with pytest.raises(ManagedWriteError):
        replace_bytes(authorize_write(identity(tmp_path), "absent/version"), b"new")
    assert not (tmp_path / "absent").exists()


def test_repointed_internal_junction_rejects_replacement(git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    """Even a still-contained alias change after staging invalidates authorization."""
    root = git_sandbox.home / "B"
    first = root / "sub"
    second = root / "other"
    second.mkdir()
    (first / "version").write_bytes(b"first")
    (second / "version").write_bytes(b"second")
    alias = git_sandbox.junction("B/alias", first)
    target = authorize_write(identity(root), alias / "version")
    def redirect(_fd: int) -> None:
        alias.rmdir()
        git_sandbox.junction("B/alias", second)
    monkeypatch.setattr(managed_files.os, "fsync", redirect)
    with pytest.raises(ManagedWriteError, match="changed"):
        replace_bytes(target, b"new")
    assert (first / "version").read_bytes() == b"first"
    assert (second / "version").read_bytes() == b"second"
    assert {path.name for path in first.iterdir()} == {"version"}


def test_cleanup_preserves_a_replaced_temporary(tmp_path: Path) -> None:
    """A replacement at an owned temporary name is not owned by its old inode."""
    original = tmp_path / "owned.tmp"
    original.write_bytes(b"owned")
    target = authorize_write(identity(tmp_path), original)
    before = original.stat()
    original.rename(tmp_path / "moved.tmp")
    original.write_bytes(b"replacement")
    managed_files._cleanup_owned(target, (before.st_dev, before.st_ino))
    assert original.read_bytes() == b"replacement"


# eof
