"""Isolated stdlib bootstrap: validate the runtime before importing tools.

Helpers are loaded by exact sibling paths under private module names. Only a
successful gate exposes the selected checkout to the eventual release engine.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
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


class Identity(Protocol):
    """Private identity instance used exclusively inside the readiness gate."""

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
    """The post-gate CLI receives plain argument strings."""

    def main(self, argv: list[str]) -> int:
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


def check(root: Path) -> tuple[str, ...]:
    """Finish all pre-import checks without importing the tools package."""
    runtime = cast("RuntimeModule", helper("runtime_identity"))
    runtime.RuntimeIdentity.load(root).verify(Path(sys.executable), Path(sys.prefix))
    measured = environment()
    markers = cast("MarkersModule", helper("markers"))
    readiness = cast("ReadinessModule", helper("readiness"))
    return readiness.validate(root, measured, importlib.metadata.version, markers.evaluate, markers.satisfies)


def main(argv: list[str] | None = None) -> int:
    """Enter the engine after readiness, returning a repair diagnostic on failure."""
    root = Path(__file__).resolve().parents[2]
    try:
        check(root)
        sys.path.insert(0, str(root))
        engine = cast("Engine", importlib.import_module("tools.release_workflow.cli"))
    except (OSError, ValueError, ImportError, RuntimeError) as exc:
        sys.stderr.write(f"Release readiness failed: {exc}. Run this checkout's setup to repair it.\n")
        return 2
    return engine.main(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
