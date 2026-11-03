"""Open-mode and descriptor boundaries for in-memory scenario files."""

from __future__ import annotations

# Match the public open/fdopen signatures at this resource boundary.
# ruff: noqa: ANN401, PLR0913, FBT001, FBT002
import errno
import io
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tests.scenario_storage import Entry, ScenarioStorage


class FileBuffer(io.RawIOBase):
    """Share bytes across handles while keeping each cursor and access mode."""

    def __init__(self, storage: ScenarioStorage, entry: Entry, mode: str) -> None:
        """Open existing bytes without touching a host file descriptor."""
        super().__init__()
        self.storage, self.entry, self.mode = storage, entry, mode
        self.name = entry.name
        self.position = len(entry.content) if "a" in mode else 0
        self.descriptor = storage.next_descriptor
        storage.next_descriptor += 1
        storage.handles[self.descriptor] = self

    def fileno(self) -> int:
        """Return a descriptor from the simulation's independent namespace."""
        self._checkClosed()
        return self.descriptor

    def get_object(self) -> Entry:
        """Return file identity for the platform-lock observation boundary."""
        return self.entry

    def readable(self) -> bool:
        """Honor the opened mode."""
        return "r" in self.mode or "+" in self.mode

    def writable(self) -> bool:
        """Honor the opened mode."""
        return any(flag in self.mode for flag in "wax+")

    def seekable(self) -> bool:
        """Scenario files are regular seekable streams."""
        return True

    def tell(self) -> int:
        """Read this handle's independent offset."""
        self._checkClosed()
        return self.position

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        """Move within or beyond the current bytes, rejecting negative offsets."""
        self._checkClosed()
        position = {io.SEEK_SET: 0, io.SEEK_CUR: self.position, io.SEEK_END: len(self.entry.content)}[whence] + offset
        if position < 0:
            raise ValueError("negative seek position")  # noqa: EM101, TRY003
        self.position = position
        return position

    def read(self, size: int = -1) -> bytes:
        """Read the latest shared bytes at this handle's cursor."""
        self._checkClosed()
        if not self.readable():
            raise io.UnsupportedOperation("not readable")  # noqa: EM101, TRY003
        end = len(self.entry.content) if size < 0 else self.position + size
        data = self.entry.content[self.position:end]
        self.position += len(data)
        return data

    def readinto(self, buffer: Any) -> int:
        """Support buffered Python readers without a descriptor syscall."""
        data = self.read(len(buffer))
        buffer[:len(data)] = data
        return len(data)

    def write(self, data: Any) -> int:
        """Publish writes immediately and enforce append at every write."""
        self._checkClosed()
        if not self.writable():
            raise io.UnsupportedOperation("not writable")  # noqa: EM101, TRY003
        data = bytes(data)
        if "a" in self.mode:
            self.position = len(self.entry.content)
        content = self.entry.content
        prefix = content[:self.position].ljust(self.position, b"\0")
        self.entry.content = prefix + data + content[self.position + len(data):]
        self.position += len(data)
        self.entry.mtime += 0.001
        return len(data)

    def truncate(self, size: int | None = None) -> int:
        """Change shared file length without changing this handle's offset."""
        self._checkClosed()
        if not self.writable():
            raise io.UnsupportedOperation("not writable")  # noqa: EM101, TRY003
        size = self.position if size is None else size
        if size < 0:
            raise ValueError("negative truncate size")  # noqa: EM101, TRY003
        self.entry.content = self.entry.content[:size].ljust(size, b"\0")
        return size

    def close(self) -> None:
        """Release the simulated descriptor."""
        self.storage.handles.pop(self.descriptor, None)
        super().close()


class ScenarioStreams:
    """Open real Python byte/text streams over declared file contents."""

    def __init__(self, storage: ScenarioStorage) -> None:
        """Bind streams to one isolated scenario filesystem."""
        self.storage = storage

    def open(self, file: Any, mode: str = "r", buffering: int = -1,
             encoding: str | None = None, errors: str | None = None,
             newline: str | None = None, closefd: bool = True,
             opener: Any = None) -> Any:
        """Honor read/write/append/exclusive modes with normal text codecs."""
        del buffering, closefd
        if opener is not None:
            flags = os.O_RDWR if "+" in mode else os.O_RDONLY if "r" in mode else os.O_WRONLY
            if "w" in mode:
                flags |= os.O_CREAT | os.O_TRUNC
            if "a" in mode:
                flags |= os.O_CREAT | os.O_APPEND
            if "x" in mode:
                flags |= os.O_CREAT | os.O_EXCL
            file = opener(file, flags)
        if isinstance(file, int):
            stream = self.storage.get_open_file(file)
        else:
            stream = self._buffer(file, mode)
        if "b" in mode:
            return stream
        return io.TextIOWrapper(stream, encoding=encoding, errors=errors, newline=newline)

    def _buffer(self, file: Any, mode: str) -> FileBuffer:
        """Validate file-open observations before allocating a stream."""
        entry = self._existing(file)
        if "x" in mode and entry is not None:
            raise FileExistsError(errno.EEXIST, "scenario entry exists", file)
        if "r" in mode and entry is None:
            raise FileNotFoundError(errno.ENOENT, "missing scenario file", file)
        if entry is not None and entry.kind == "directory":
            raise IsADirectoryError(errno.EISDIR, "scenario entry is a directory", file)
        if entry is None:
            self.storage._parent(file)
            entry = self.storage._create(file)
        if "w" in mode:
            entry.content = b""
        return FileBuffer(self.storage, entry, mode)

    def _existing(self, file: Any) -> Entry | None:
        """Resolve a file once per open, retaining the current mutable entry."""
        try:
            return self.storage._entry(file)
        except FileNotFoundError:
            return None

    def os_open(self, path: Any, flags: int, mode: int = 0o777, **_kwargs: Any) -> int:
        """Interpret OS open flags used by atomic publication and lock creation."""
        entry = self._os_entry(path, flags, mode)
        stream = FileBuffer(self.storage, entry, self._stream_mode(flags))
        return stream.fileno()

    def _os_entry(self, path: Any, flags: int, mode: int) -> Entry:
        """Validate creation and truncation before opening a descriptor."""
        entry = self._existing(path)
        if flags & os.O_EXCL and entry is not None:
            raise FileExistsError(errno.EEXIST, "scenario entry exists", path)
        if entry is None and not flags & os.O_CREAT:
            raise FileNotFoundError(errno.ENOENT, "missing scenario file", path)
        if entry is None:
            self.storage._parent(path)
            entry = self.storage._create(path)
            entry.mode = mode
        if entry.kind == "directory":
            raise IsADirectoryError(errno.EISDIR, "scenario entry is a directory", path)
        if flags & os.O_TRUNC:
            entry.content = b""
        return entry

    @staticmethod
    def _stream_mode(flags: int) -> str:
        """Translate access and append flags for a validated entry."""
        stream_mode = "ab" if flags & os.O_APPEND else "wb" if flags & (os.O_WRONLY | os.O_RDWR) else "rb"
        if flags & os.O_RDWR:
            stream_mode += "+"
        return stream_mode

    def fdopen(self, descriptor: int, *args: Any, **kwargs: Any) -> Any:
        """Wrap an existing descriptor using the requested text or binary mode."""
        return self.open(descriptor, *args, **kwargs)


# eof
