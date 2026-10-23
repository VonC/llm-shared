"""Setup-owned runtime identity with measured paths and atomic publication.

This module also runs directly under isolated Python, before importing tools.
Release startup reads the record; only successful setup may replace it.
"""

from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

RECORD_NAME = "release-runtime.v1.txt"
_RECORD_VERSION = "1"
_RECORD_LINES = 2
_MIN_PATH_PARTS = 2
_PRODUCER_ARGUMENTS = 2


class InvalidRecordError(ValueError):
    """A setup-owned designation is invalid or unusable."""


@dataclass(frozen=True)
class RuntimeIdentity:
    """A measured environment confined to the selected tooling checkout."""

    root: Path
    environment: str

    @property
    def prefix(self) -> Path:
        """Return the designated environment without scanning other directories."""
        return self.root / self.environment

    @property
    def executable(self) -> Path:
        """Return the sole designated Windows interpreter path."""
        return self.prefix / "Scripts" / "python.exe"

    def _validate_relative(self) -> None:
        """Reject absolute or escaping record paths before filesystem access."""
        relative = PurePosixPath(self.environment)
        if (
            relative.is_absolute()
            or len(relative.parts) < _MIN_PATH_PARTS
            or relative.parts[0] != "venvs"
            or ".." in relative.parts
            or any(char in self.environment for char in "\\:\r\n\0")
        ):
            msg = "Invalid runtime environment path"
            raise ValueError(msg)

    def _validate_paths(self) -> None:
        """Reject lexical escapes, physical escapes and unusable targets."""
        self._validate_relative()
        environments = (self.root / "venvs").resolve()
        prefix = self.prefix.resolve()
        executable = self.executable.resolve()
        if (
            not environments.is_relative_to(self.root)
            or not prefix.is_relative_to(environments)
            or prefix == environments
            or not executable.is_relative_to(prefix)
            or not self.executable.is_file()
        ):
            msg = "Missing or escaped runtime executable"
            raise ValueError(msg)

    @classmethod
    def measure(cls, root: Path, executable: Path, prefix: Path) -> RuntimeIdentity:
        """Derive the identity from the interpreter setup actually prepared."""
        root = root.resolve()
        try:
            relative = prefix.resolve().relative_to(root).as_posix()
        except ValueError as exc:
            msg = "Prepared runtime prefix is outside the tooling checkout"
            raise ValueError(msg) from exc
        identity = cls(root, relative)
        identity.verify(executable, prefix)
        return identity

    @classmethod
    def load(cls, root: Path) -> RuntimeIdentity:
        """Read exactly one designation and validate its complete schema."""
        root = root.resolve()
        record = (root / "venvs" / RECORD_NAME).read_text(encoding="utf-8")
        return cls.parse(root, record)

    @classmethod
    def parse(cls, root: Path, record: str) -> RuntimeIdentity:
        """Validate two UTF-8 lines and their target: version, relative directory."""
        lines = record.replace("\r\n", "\n").removesuffix("\n").split("\n")
        if len(lines) != _RECORD_LINES or lines[0] != _RECORD_VERSION:
            msg = "Unsupported runtime record lines or version"
            raise InvalidRecordError(msg)
        identity = cls(root, lines[1])
        identity._validate_paths()
        return identity

    def serialize(self) -> str:
        """Keep non-ASCII path text literal for the pre-Python batch reader."""
        self._validate_relative()
        return f"{_RECORD_VERSION}\n{self.environment}\n"

    def verify(self, executable: Path, prefix: Path) -> None:
        """Reject moved environments and execution through a foreign Python."""
        self._validate_paths()
        if executable.resolve() != self.executable.resolve() or prefix.resolve() != self.prefix.resolve():
            msg = "Executing runtime does not match the setup-owned identity"
            raise ValueError(msg)

    def publish(self) -> None:
        """Atomically replace the private record after all measurement checks."""
        self._validate_paths()
        target = self.root / "venvs" / RECORD_NAME
        data = self.serialize()
        descriptor, filename = tempfile.mkstemp(prefix=".release-runtime-", dir=target.parent)
        temporary = Path(filename)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            self._validate_paths()
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    """Record a successful preparation; propagate saved setup failures."""
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != _PRODUCER_ARGUMENTS:
        sys.stderr.write("Runtime producer needs a tooling root and saved setup status\n")
        return 2
    try:
        status = int(arguments[1])
        if status:
            return status
        root = Path(arguments[0]).absolute()
        prefix = Path(sys.prefix)
        # A successful global setup remains supported, but cannot designate a
        # release runtime. Lexically local paths still receive all physical
        # containment checks, so a junction escape remains a hard failure.
        if not prefix.absolute().is_relative_to(root / "venvs"):
            sys.stderr.write("Warning: release runtime identity not updated; no checkout-local environment prepared.\n")
            return 0
        RuntimeIdentity.measure(root, Path(sys.executable), prefix).publish()
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"Release runtime setup failed: {exc}\n")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
