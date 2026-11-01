"""Small in-memory file observations for deterministic application scenarios.

Files contain real bytes, open streams have independent cursors, and rename,
exclusive creation, symlinks and missing files retain their observable rules.
This boundary does no host IO and does not interpret commands.
"""

from __future__ import annotations

# Native filesystem adapters use lexical os.path APIs to avoid recursive patches.
# ruff: noqa: ANN401, PTH118, PTH119, PTH120
import errno
import os
import stat as stat_module
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from tests.scenario_streams import FileBuffer

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Self

DESCRIPTOR_BASE = 65536


@dataclass
class Entry:
    """Bytes and metadata for one directory entry."""

    name: str
    st_ino: int
    kind: str = "file"
    content: bytes = b""
    target: str = ""
    mode: int = 0o666
    mtime: float = 1_700_000_000.0
    _stat_key: tuple[str, int, int, int, float] | None = field(default=None, init=False, repr=False, compare=False)
    _stat_value: os.stat_result | None = field(default=None, init=False, repr=False, compare=False)

    def stat(self) -> os.stat_result:
        """Reuse metadata values only while every observable field is unchanged."""
        key = (self.kind, self.st_ino, self.mode, len(self.content), self.mtime)
        if key == self._stat_key and self._stat_value is not None:
            return self._stat_value
        kind = {"file": stat_module.S_IFREG, "directory": stat_module.S_IFDIR,
                "link": stat_module.S_IFLNK, "junction": stat_module.S_IFLNK}[self.kind]
        nanoseconds = int(self.mtime * 1e9)
        result = os.stat_result((kind | self.mode, self.st_ino, 1, 1, 0, 0,
                                 len(self.content), self.mtime, self.mtime, self.mtime),
                                {"st_atime_ns": nanoseconds, "st_mtime_ns": nanoseconds, "st_ctime_ns": nanoseconds,
                                 "st_file_attributes": stat_module.FILE_ATTRIBUTE_REPARSE_POINT
                                 if self.kind in {"link", "junction"} else 0,
                                 "st_reparse_tag": stat_module.IO_REPARSE_TAG_MOUNT_POINT
                                 if self.kind == "junction" else 0})
        self._stat_key, self._stat_value = key, result
        return result


@dataclass
class DirectoryScan:
    """A scandir iterator which owns no operating-system resource."""

    entries: Iterator[DirectoryEntry]

    def __iter__(self) -> Self:
        """Yield the entries observed when scanning started."""
        return self

    def __next__(self) -> DirectoryEntry:
        """Support native os.walk's direct next(scandir) protocol."""
        return next(self.entries)

    def __enter__(self) -> Self:
        """Support pathlib and shutil context managers."""
        return self

    def __exit__(self, *_arguments: object) -> None:
        """There is no host handle to close."""


@dataclass
class DirectoryEntry:
    """One directory observation with pathlib-compatible stat predicates."""

    storage: ScenarioStorage
    path: str

    @property
    def name(self) -> str:
        """Expose only the final component."""
        return os.path.basename(self.path)

    def __fspath__(self) -> str:
        """Allow copy routines to use the observed path directly."""
        return self.path

    def stat(self, *, follow_symlinks: bool = True) -> os.stat_result:
        """Read current metadata for this entry."""
        return self.storage.stat(self.path, follow_symlinks=follow_symlinks)

    def is_dir(self, *, follow_symlinks: bool = True) -> bool:
        """Recognize directories, optionally following links."""
        return self.storage._kind(self.path, "directory", follow=follow_symlinks)

    def is_file(self, *, follow_symlinks: bool = True) -> bool:
        """Recognize ordinary files, optionally following links."""
        return self.storage._kind(self.path, "file", follow=follow_symlinks)

    def is_symlink(self) -> bool:
        """Inspect the directory entry rather than its target."""
        return self.storage.islink(self.path)

    def is_junction(self) -> bool:
        """Expose the Windows directory-entry contract used by shutil.rmtree."""
        return self.storage.isjunction(self.path)


@dataclass
class ScenarioStorage:
    """Declared file state and file operations, with constant-time common reads."""

    cwd: str
    entries: dict[str, Entry] = field(default_factory=dict[str, Entry])
    handles: dict[int, FileBuffer] = field(default_factory=dict[int, FileBuffer])
    links: dict[str, str] = field(default_factory=dict[str, str])
    children: dict[str, dict[str, None]] = field(default_factory=dict[str, dict[str, None]])
    absolute_names: dict[tuple[str, str], str] = field(default_factory=dict[tuple[str, str], str])
    normalized_names: dict[str, str] = field(default_factory=dict[str, str])
    path_prefixes: dict[str, tuple[str, ...]] = field(default_factory=dict[str, tuple[str, ...]])
    resolved_names: dict[str, str] = field(default_factory=dict[str, str])
    next_descriptor: int = DESCRIPTOR_BASE
    next_inode: int = 1

    def abspath(self, path: Any) -> str:
        """Normalize a name against the simulated caller directory."""
        name = path if isinstance(path, str) else os.fsdecode(path)
        key = (self.cwd, name)
        if key not in self.absolute_names:
            self.absolute_names[key] = os.path.normpath(os.path.join(self.cwd, name))
        return self.absolute_names[key]

    def _normalized(self, name: str) -> str:
        """Cache lexical case normalization, never mutable file observations."""
        if name not in self.normalized_names:
            self.normalized_names[name] = os.path.normcase(name)
        return self.normalized_names[name]

    def _key(self, path: Any) -> str:
        return self._normalized(self.abspath(path))

    def _prefixes(self, key: str) -> tuple[str, ...]:
        """Cache lexical components, keeping lookup independent of other trees."""
        if key not in self.path_prefixes:
            self.path_prefixes[key] = (*(
                key[:index] for index, character in enumerate(key) if character == os.sep
            ), key)
        return self.path_prefixes[key]

    def realpath(self, path: Any, *, strict: bool = False) -> str:
        """Resolve declared links and reject cycles without host path queries."""
        name = self.abspath(path)
        original = name
        if original in self.resolved_names:
            return self._resolved_entry_name(self.resolved_names[original], strict=strict)
        if not self.links:
            return self._resolved_entry_name(name, strict=strict)
        for _ in range(40):
            key = self._normalized(name)
            for link in self._prefixes(key):
                target = self.links.get(link)
                if target is not None:
                    name = os.path.normpath(target + name[len(link):])
                    break
            else:
                self.resolved_names[original] = name
                return self._resolved_entry_name(name, strict=strict)
        raise OSError(errno.ELOOP, "scenario link cycle", name)

    def _resolved_entry_name(self, name: str, *, strict: bool) -> str:
        """Observe current existence and original spelling after link resolution."""
        entry = self.entries.get(self._normalized(name))
        if strict and entry is None:
            raise FileNotFoundError(errno.ENOENT, "missing scenario file", name)
        return entry.name if entry is not None else name

    def _entry(self, path: Any, *, follow: bool = True) -> Entry:
        name = self.realpath(path) if follow else self.abspath(path)
        try:
            return self.entries[self._normalized(name)]
        except KeyError:
            raise FileNotFoundError(errno.ENOENT, "missing scenario file", name) from None

    def _create(self, path: Any, kind: str = "file") -> Entry:
        name = self.realpath(path)
        entry = Entry(name, self.next_inode, kind)
        self.next_inode += 1
        key = self._normalized(name)
        self.entries[key] = entry
        self.children.setdefault(os.path.dirname(key), {})[key] = None
        return entry

    def create_dir(self, path: Any) -> None:
        """Create initial parents for the scratch tree."""
        name = self.abspath(path)
        parent = os.path.dirname(name)
        if parent != name and self._key(parent) not in self.entries:
            self.create_dir(parent)
        self._create(name, "directory")

    def discard_tree(self, path: Any) -> None:
        """Release one finished fixture's observations without following links."""
        root = self._key(path)
        self.children.get(os.path.dirname(root), {}).pop(root, None)
        pending = [root]
        while pending:
            key = pending.pop()
            pending.extend(self.children.pop(key, {}))
            self.entries.pop(key, None)
            self.links.pop(key, None)
        # These caches contain lexical paths, not reusable domain evidence.
        # Bound their lifetime to a test as well as releasing its file bytes.
        self.absolute_names.clear()
        self.normalized_names.clear()
        self.path_prefixes.clear()
        self.resolved_names.clear()

    def _parent(self, path: Any) -> None:
        if not self.isdir(os.path.dirname(self.abspath(path))):
            raise FileNotFoundError(errno.ENOENT, "missing scenario parent", path)

    def stat(self, path: Any, *, follow_symlinks: bool = True, **_kwargs: Any) -> os.stat_result:
        """Observe a file or descriptor's metadata."""
        entry = self.get_open_file(path).entry if isinstance(path, int) else self._entry(path, follow=follow_symlinks)
        return entry.stat()

    def lstat(self, path: Any, **kwargs: Any) -> os.stat_result:
        """Observe the entry itself."""
        return self.stat(path, follow_symlinks=False, **kwargs)

    fstat = stat

    def exists(self, path: Any) -> bool:
        """Report whether the resolved entry exists."""
        return self._normalized(self.realpath(path)) in self.entries

    def lexists(self, path: Any) -> bool:
        """Report whether a potentially dangling link exists."""
        return self._key(path) in self.entries

    def _kind(self, path: Any, kind: str, *, follow: bool = True) -> bool:
        try:
            return self._entry(path, follow=follow).kind == kind
        except OSError:
            return False

    def isfile(self, path: Any) -> bool:
        """Recognize a regular file."""
        return self._kind(path, "file")

    def isdir(self, path: Any) -> bool:
        """Recognize a directory."""
        return self._kind(path, "directory")

    def islink(self, path: Any) -> bool:
        """Recognize a symlink independently of its target."""
        return self._kind(path, "link", follow=False)

    def isjunction(self, path: Any) -> bool:
        """Recognize a declared Windows directory junction."""
        return self._kind(path, "junction", follow=False)

    def mkdir(self, path: Any, mode: int = 0o777, **_kwargs: Any) -> None:
        """Create exactly one directory, preserving missing-parent errors."""
        if self.lexists(path):
            raise FileExistsError(errno.EEXIST, "scenario entry exists", path)
        self._parent(path)
        self._create(path, "directory").mode = mode

    def listdir(self, path: Any = ".") -> list[str]:
        """Return immediate child names."""
        parent = os.path.normcase(self.realpath(path, strict=True))
        return [os.path.basename(self.entries[key].name) for key in self.children.get(parent, {}) if key != parent]

    def scandir(self, path: Any = ".") -> DirectoryScan:
        """Snapshot immediate children for production glob and copy routines."""
        parent = os.fsdecode(path)
        return DirectoryScan(iter(DirectoryEntry(self, os.path.join(parent, name)) for name in self.listdir(parent)))

    def unlink(self, path: Any, **_kwargs: Any) -> None:
        """Remove one file or link while leaving open streams valid."""
        entry = self._entry(path, follow=False)
        if entry.kind == "directory":
            raise IsADirectoryError(errno.EISDIR, "scenario entry is a directory", path)
        self._remove_entry(path)

    def _remove_entry(self, path: Any) -> None:
        key = self._key(path)
        self.entries.pop(key)
        if self.links.pop(key, None) is not None:
            self.resolved_names.clear()
        self.children.get(os.path.dirname(key), {}).pop(key, None)

    remove = unlink

    def rmdir(self, path: Any, **_kwargs: Any) -> None:
        """Remove an empty directory."""
        if self.isjunction(path):
            self._remove_entry(path)
            return
        if self.listdir(path):
            raise OSError(errno.ENOTEMPTY, "scenario directory is not empty", path)
        self._remove_entry(path)

    def replace(self, source: Any, target: Any, **_kwargs: Any) -> None:
        """Publish one complete entry atomically at its destination."""
        entry = self._entry(source, follow=False)
        self._parent(target)
        existing = self.entries.get(self._key(target))
        if existing is not None and (existing.kind == "directory" or entry.kind == "directory"):
            raise PermissionError(errno.EACCES, "scenario destination is an existing directory", target)
        source_key = self._key(source)
        descendants = list(self.children.get(source_key, {}))
        self._remove_entry(source)
        entry.name = self.abspath(target)
        target_key = self._key(target)
        self.entries[target_key] = entry
        self.children.setdefault(os.path.dirname(target_key), {})[target_key] = None
        for child in descendants:
            self.replace(self.entries[child].name, os.path.join(entry.name, os.path.basename(child)))

    def rename(self, source: Any, target: Any, **kwargs: Any) -> None:
        """Preserve Windows refusal to overwrite an existing destination."""
        if os.name == "nt" and self.lexists(target):
            raise FileExistsError(errno.EEXIST, "scenario target exists", target)
        self.replace(source, target, **kwargs)

    def chmod(self, path: Any, mode: int, **_kwargs: Any) -> None:
        """Record declared permission metadata."""
        self._entry(path).mode = mode

    def utime(self, path: Any, times: Any = None, *, ns: Any = None, **_kwargs: Any) -> None:
        """Retain timestamps used by copy and staleness policies."""
        self._entry(path).mtime = ns[1] / 1e9 if ns is not None else times[1] if times is not None else 1_700_000_001.0

    def symlink(self, source: Any, target: Any, target_is_directory: bool = False, **_kwargs: Any) -> None:  # noqa: FBT001, FBT002
        """Declare a symbolic link, including a missing target."""
        del target_is_directory
        self._parent(target)
        entry = self._create(target, "link")
        entry.target = os.fsdecode(source)
        self.links[self._key(target)] = os.path.normpath(os.path.join(os.path.dirname(entry.name), entry.target))
        self.resolved_names.clear()

    def junction(self, source: Any, target: Any) -> None:
        """Declare the directory-link observation made by Windows."""
        self.symlink(source, target)
        self._entry(target, follow=False).kind = "junction"

    def link(self, source: Any, target: Any, **_kwargs: Any) -> None:
        """Expose the same inode at a second directory entry."""
        self._parent(target)
        self.entries[self._key(target)] = self._entry(source)
        self.children.setdefault(self._key(os.path.dirname(self.abspath(target))), {})[self._key(target)] = None

    def readlink(self, path: Any, **_kwargs: Any) -> str:
        """Read an existing declared link."""
        return self._entry(path, follow=False).target

    def getcwd(self) -> str:
        """Return the simulated caller directory."""
        return self.cwd

    def chdir(self, path: Any) -> None:
        """Select an existing simulated directory."""
        if not self.isdir(path):
            raise FileNotFoundError(errno.ENOENT, "missing scenario directory", path)
        self.cwd = self.realpath(path)

    def get_open_file(self, descriptor: int) -> FileBuffer:
        """Look up one simulated file descriptor."""
        try:
            return self.handles[descriptor]
        except KeyError:
            raise OSError(errno.EBADF, "closed scenario descriptor") from None

    def close(self, descriptor: int) -> None:
        """Close one simulated descriptor."""
        self.get_open_file(descriptor).close()

    def fsync(self, descriptor: int) -> None:
        """Observe a valid descriptor; memory writes are already visible."""
        self.get_open_file(descriptor)

    def read(self, descriptor: int, size: int) -> bytes:
        """Read from the descriptor's cursor."""
        return self.get_open_file(descriptor).read(size)

    def write(self, descriptor: int, data: bytes) -> int:
        """Write at the descriptor's cursor."""
        return self.get_open_file(descriptor).write(data)

    def lseek(self, descriptor: int, offset: int, whence: int) -> int:
        """Move the descriptor's cursor."""
        return self.get_open_file(descriptor).seek(offset, whence)


# eof
