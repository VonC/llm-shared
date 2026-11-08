"""Isolated stdlib bootstrap: validate the runtime before importing tools.

Helpers are loaded by exact sibling paths under private module names. Capture
cwd and authenticate the reserved entry prefix before readiness or dispatch.
Only a successful gate exposes the selected checkout to the release engine.
Early diagnostics use UTF-8/LF; interruption remains an execution failure.
The engine's public statuses are 0, 1, 2 and 3 (an incomplete restoration,
since Step 1 of v0.14.0 version-sources); any other value becomes 1.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import io
import os
import platform
import struct
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from types import ModuleType

_X64_POINTER_BYTES = 8
_ENTRY_PREFIX_LENGTH = 3


class InvocationError(ValueError):
    """Reserved entry syntax errors require caller repair, not environment setup."""


class Identity(Protocol):
    """Verified private identity whose data the CLI normalizes to its public type."""

    @property
    def root(self) -> Path:
        """Return the verified tooling checkout without reloading its record."""
        ...

    @property
    def environment(self) -> str:
        """Return the verified environment relative to the tooling checkout."""
        ...

    def verify(self, executable: Path, prefix: Path) -> None:
        """Validate measured runtime paths."""
        ...


class IdentityFactory(Protocol):
    """Typed loader boundary without importing the package module twin."""

    def load(self, root: Path) -> Identity:
        """Load the setup-owned designation."""
        ...


class RuntimeModule(Protocol):
    """Minimum interface needed from the standalone identity helper."""

    RuntimeIdentity: IdentityFactory


class MarkersModule(Protocol):
    """Closed marker and version interfaces loaded before tools."""

    def evaluate(self, text: str, environment: Mapping[str, str]) -> bool:
        """Evaluate a supported marker."""
        ...

    def satisfies(self, version: str, specifier: str) -> bool:
        """Check supported interpreter clauses."""
        ...


class ReadinessModule(Protocol):
    """Explicitly wired helper interface using only standard data types."""

    def validate(self, root: Path, environment: Mapping[str, str], installed: Callable[[str], str],
                 marker: Callable[[str, Mapping[str, str]], bool],
                 satisfies: Callable[[str, str], bool]) -> tuple[str, ...]:
        """Validate the release dependency closure."""
        ...


class Engine(Protocol):
    """The post-gate CLI receives original arguments and structural identity data."""

    def main(self, argv: list[str], *, entry_kind: str, original_cwd: Path, tooling_root: Path, runtime: Identity) -> int:
        """Run a release command."""
        ...


def helper(name: str) -> ModuleType:
    """Load one exact sibling without changing the import search path."""
    sys.dont_write_bytecode = True
    path = Path(__file__).with_name(f"{name}.py")
    private_name = f"_release_bootstrap_{name}"
    spec = importlib.util.spec_from_file_location(private_name, path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load release helper: {name}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[private_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[private_name]
        raise
    return module


def environment() -> dict[str, str]:
    """Measure the supported Windows x64 interpreter and marker variables."""
    machine = platform.machine()
    if sys.platform != "win32" or machine.lower() not in {"amd64", "x86_64"} or struct.calcsize("P") != _X64_POINTER_BYTES:
        msg = "Release tooling requires Windows x64"
        raise ValueError(msg)
    return {
        "sys_platform": sys.platform, "os_name": os.name,
        "platform_system": platform.system(), "platform_machine": machine,
        "implementation_name": sys.implementation.name,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "python_full_version": platform.python_version(),
    }


def check(root: Path) -> Identity:
    """Finish pre-import checks and retain the identity verified by this gate."""
    runtime = cast("RuntimeModule", helper("runtime_identity"))
    identity = runtime.RuntimeIdentity.load(root)
    identity.verify(Path(sys.executable), Path(sys.prefix))
    measured = environment()
    markers = cast("MarkersModule", helper("markers"))
    readiness = cast("ReadinessModule", helper("readiness"))
    readiness.validate(root, measured, importlib.metadata.version, markers.evaluate, markers.satisfies)
    return identity


def entry(arguments: list[str]) -> tuple[str, list[str]]:
    """Require exactly one trusted prefix, outside the original user arguments."""
    if (len(arguments) < _ENTRY_PREFIX_LENGTH or arguments[0] != "--entry-kind"
            or arguments[1] not in {"explicit-batch", "alias-batch", "explicit-native"}
            or arguments[2] != "--"):
        msg = "Expected --entry-kind explicit-batch|alias-batch|explicit-native -- <arguments>"
        raise InvocationError(msg)
    supplied = arguments[3:]
    if any(argument == "--entry-kind" or argument.startswith("--entry-kind=") for argument in supplied):
        msg = "Duplicate reserved --entry-kind is forbidden in user arguments"
        raise InvocationError(msg)
    return arguments[1], supplied


def configure_streams() -> None:
    """Use deterministic diagnostics before checking readiness or dispatching."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace", newline="\n")


def main(argv: list[str] | None = None) -> int:
    """Capture cwd first, then gate imports and normalize outer-boundary failure."""
    try:
        original_cwd = Path.cwd()
        configure_streams()
        kind, arguments = entry(sys.argv[1:] if argv is None else argv)
        root = Path(__file__).resolve().parents[2]
        identity = check(root)
        sys.path.insert(0, str(root))
        engine = cast("Engine", importlib.import_module("tools.release_workflow.cli"))
    except InvocationError as exc:
        sys.stderr.write(f"Release invocation failed: {exc}\n")
        return 2
    except (OSError, ValueError, ImportError, RuntimeError) as exc:
        sys.stderr.write(f"Release readiness failed: {exc}. Run this checkout's setup to repair it.\n")
        return 2
    except (Exception, KeyboardInterrupt) as exc:  # noqa: BLE001 - pre-import process boundary
        detail = "interrupted" if isinstance(exc, KeyboardInterrupt) else str(exc)
        sys.stderr.write(f"Release execution failed: {detail}\n")
        return 1
    try:
        status = engine.main(arguments, entry_kind=kind, original_cwd=original_cwd, tooling_root=root, runtime=identity)
    except (Exception, KeyboardInterrupt) as exc:  # noqa: BLE001 - final process boundary
        detail = "interrupted" if isinstance(exc, KeyboardInterrupt) else str(exc)
        sys.stderr.write(f"Release execution failed: {detail}\n")
        return 1
    if status not in {0, 1, 2, 3}:
        sys.stderr.write(f"Release operation exited with native status {status}; returning 1.\n")
        return 1
    return status


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
