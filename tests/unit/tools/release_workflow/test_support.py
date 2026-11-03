"""Small filesystem and lock builders shared by release readiness tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

ENV = {
    "sys_platform": "win32", "os_name": "nt", "platform_system": "Windows",
    "platform_machine": "AMD64", "implementation_name": "cpython",
    "python_version": "3.13", "python_full_version": "3.13.9",
}


def prepared_runtime(root: Path) -> tuple[Path, Path]:
    """Make a designated executable fixture without choosing an ambient Python."""
    prefix = root / "venvs" / "prepared"
    executable = prefix / "Scripts" / "python.exe"
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"fixture executable")
    return executable, prefix


def write_record(root: Path, value: str) -> None:
    """Write a record fixture, including deliberately malformed values."""
    (root / "venvs" / "release-runtime.v1.txt").write_text(
        value, encoding="utf-8",
    )


def metadata(root: Path, packages: str = "", edges: str = "") -> None:
    """Write a virtual root and optional nonempty release dependency graph."""
    declarations = '["alpha"]' if edges else "[]"
    (root / "pyproject.toml").write_text(
        '[project]\nname = "Sample_Tooling"\nversion = "1"\nrequires-python = ">=3.13, <3.14"\n'
        f"[dependency-groups]\nrelease = {declarations}\n"
        'dev = [{include-group = "release"}]\n', encoding="utf-8",
    )
    locked_edges = f"[package.dev-dependencies]\nrelease = [{edges}]\n" if edges else ""
    (root / "uv.lock").write_text(
        'version = 1\n[[package]]\nname = "sample-tooling"\nversion = "1"\n'
        'source = {virtual = "."}\n'
        f"{locked_edges}[package.metadata.requires-dev]\nrelease = {declarations}\n"
        f"{packages}", encoding="utf-8",
    )


def package(name: str, *, version: str = "1.0", edges: str = "") -> str:
    """Make a registry package using generic location data."""
    return (
        f'\n[[package]]\nname = "{name}"\nversion = "{version}"\n'
        'source = {registry = "https://packages.example/simple"}\n'
        f"dependencies = [{edges}]\n"
    )

# eof
