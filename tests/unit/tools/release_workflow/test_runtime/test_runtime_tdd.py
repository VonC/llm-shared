"""Runtime records must preserve successful setup authority and reject drift."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.test_support import write_record
from tools.release_workflow.runtime_identity import RuntimeIdentity, main

if TYPE_CHECKING:
    from pathlib import Path

_ERROR = 2


def test_measured_identity_roundtrip(runtime: tuple[Path, Path, Path]) -> None:
    """Publish measured paths atomically and ignore leftover environments."""
    root, executable, prefix = runtime
    identity = RuntimeIdentity.measure(root, executable, prefix)
    identity.publish()
    (root / "venvs" / "old").mkdir()
    loaded = RuntimeIdentity.load(root)
    loaded.verify(executable, prefix)
    assert loaded.environment == "venvs/prepared"
    assert (root / "venvs/release-runtime.v1.txt").read_text(encoding="utf-8") == "1\nvenvs/prepared\n"


@pytest.mark.parametrize("value", [
    "", "1\n", "1\n\n", "1\nvenvs/prepared\nextra\n", "1\nvenvs/prepared\n\n",
    "2\nvenvs/prepared\n", "True\nvenvs/prepared\n", "1.0\nvenvs/prepared\n",
    "1\n../foreign\n", "1\nvenvs/../foreign\n", "1\n/venvs/prepared\n",
    "1\nvenvs\n", "1\nvenvs/missing\n", "1\nvenvs\\prepared\n",
])
def test_invalid_records_fail(runtime: tuple[Path, Path, Path], value: str) -> None:
    """No malformed designation becomes a fallback lookup."""
    root, _, _ = runtime
    write_record(root, value)
    with pytest.raises(ValueError, match="runtime"):
        RuntimeIdentity.load(root)


def test_missing_and_broken_records(runtime: tuple[Path, Path, Path]) -> None:
    """Unprepared or unreadable records fail without creating one."""
    root, executable, prefix = runtime
    with pytest.raises(FileNotFoundError):
        RuntimeIdentity.load(root)
    record = root / "venvs/release-runtime.v1.txt"
    record.write_text("not a record", encoding="utf-8")
    with pytest.raises(ValueError, match="runtime"):
        RuntimeIdentity.load(root)
    RuntimeIdentity.measure(root, executable, prefix).publish()
    executable.unlink()
    with pytest.raises(ValueError, match="runtime"):
        RuntimeIdentity.load(root)


def test_foreign_measurement_rejected(runtime: tuple[Path, Path, Path]) -> None:
    """Both the process prefix and executable must be this environment's."""
    root, executable, prefix = runtime
    with pytest.raises(ValueError, match="runtime"):
        RuntimeIdentity.measure(root, executable, root)
    identity = RuntimeIdentity.measure(root, executable, prefix)
    with pytest.raises(ValueError, match="runtime"):
        identity.verify(executable, root)
    with pytest.raises(ValueError, match="runtime"):
        identity.verify(root / "foreign.exe", prefix)


def test_failed_setup_preserves_record(runtime: tuple[Path, Path, Path]) -> None:
    """A failed preparation cannot replace a prior valid designation."""
    root, executable, prefix = runtime
    RuntimeIdentity.measure(root, executable, prefix).publish()
    before = (root / "venvs/release-runtime.v1.txt").read_bytes()
    status = 7
    assert main([str(root), str(status)]) == status
    assert (root / "venvs/release-runtime.v1.txt").read_bytes() == before

def test_producer_success_and_errors(runtime: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch,
                                    capsys: pytest.CaptureFixture[str]) -> None:
    """Producer reports invalid inputs and measures the process on success."""
    root, executable, prefix = runtime
    monkeypatch.setattr(sys, "executable", str(executable))
    monkeypatch.setattr(sys, "prefix", str(prefix))
    assert main([str(root), "0"]) == 0
    assert RuntimeIdentity.load(root).prefix == prefix
    assert main([]) == _ERROR
    assert main([str(root), "invalid"]) == _ERROR
    monkeypatch.setattr(sys, "argv", ["producer", str(root), "0"])
    assert main() == 0
    assert "Release runtime setup failed" in capsys.readouterr().err
    with pytest.raises(ValueError, match="outside"):
        RuntimeIdentity.measure(root, executable, root.parent)


def test_atomic_publication_failure(runtime: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """A failed replace preserves the previous record and removes the temp file."""
    root, executable, prefix = runtime
    identity = RuntimeIdentity.measure(root, executable, prefix)
    identity.publish()
    record = root / "venvs/release-runtime.v1.txt"
    before = record.read_bytes()

    def fail_replace(_self: Path, _target: Path) -> None:
        msg = "replace denied"
        raise OSError(msg)

    monkeypatch.setattr(type(root), "replace", fail_replace)
    with pytest.raises(OSError, match="denied"):
        identity.publish()
    assert record.read_bytes() == before
    assert not list(record.parent.glob(".release-runtime-*"))

@pytest.mark.parametrize("escaped", ["venvs", "venvs/prepared", "venvs/prepared/Scripts/python.exe"])
def test_physical_escapes(runtime: tuple[Path, Path, Path], escaped: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Physical resolution cannot escape through a junction at any path level."""
    root, executable, prefix = runtime
    identity = RuntimeIdentity.measure(root, executable, prefix)
    original = type(root).resolve

    def redirected(path: Path, *, strict: bool = False) -> Path:
        if path == root / escaped:
            return root.parent / "outside"
        return original(path, strict=strict)

    monkeypatch.setattr(type(root), "resolve", redirected)
    with pytest.raises(ValueError, match="escaped"):
        identity.verify(executable, prefix)


def test_moved_environment(runtime: tuple[Path, Path, Path]) -> None:
    """Moving the designated environment makes its old record unusable."""
    root, executable, prefix = runtime
    RuntimeIdentity.measure(root, executable, prefix).publish()
    prefix.rename(root / "venvs/renamed")
    with pytest.raises(ValueError, match="runtime"):
        RuntimeIdentity.load(root)


def test_non_ascii_environment_roundtrip(runtime: tuple[Path, Path, Path]) -> None:
    """The record preserves Unicode literally for the future batch reader."""
    root, _, prefix = runtime
    renamed = prefix.rename(root / "venvs" / "préparé 日本")
    identity = RuntimeIdentity.measure(root, renamed / "Scripts/python.exe", renamed)
    identity.publish()
    assert (root / "venvs/release-runtime.v1.txt").read_text(encoding="utf-8") == "1\nvenvs/préparé 日本\n"
    assert RuntimeIdentity.load(root) == identity
    assert RuntimeIdentity.parse(root, identity.serialize().replace("\n", "\r\n")) == identity


def test_global_setup_preserves_record(runtime: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch,
                                      capsys: pytest.CaptureFixture[str]) -> None:
    """A successful global setup warns without replacing an existing record."""
    root, executable, prefix = runtime
    RuntimeIdentity.measure(root, executable, prefix).publish()
    record = root / "venvs/release-runtime.v1.txt"
    before = record.read_bytes()
    monkeypatch.setattr(sys, "prefix", str(root.parent / "global"))
    assert main([str(root), "0"]) == 0
    assert record.read_bytes() == before
    assert "no checkout-local environment" in capsys.readouterr().err

def test_producer_through_checkout_alias(runtime: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """The interpreter and root may share a lexical alias of the same checkout."""
    root, executable, prefix = runtime
    alias = root.parent / "checkout-alias"
    original = type(root).resolve

    def resolved(path: Path, *, strict: bool = False) -> Path:
        if path.is_relative_to(alias):
            path = root / path.relative_to(alias)
        return original(path, strict=strict)

    monkeypatch.setattr(type(root), "resolve", resolved)
    monkeypatch.setattr(sys, "prefix", str(alias / prefix.relative_to(root)))
    monkeypatch.setattr(sys, "executable", str(alias / executable.relative_to(root)))
    assert main([str(alias), "0"]) == 0
    assert RuntimeIdentity.load(root).prefix == prefix


def test_producer_rejects_physical_escape(runtime: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch,
                                        capsys: pytest.CaptureFixture[str]) -> None:
    """A lexically local prefix escaping physically fails instead of warning."""
    root, executable, prefix = runtime
    original = type(root).resolve

    def resolved(path: Path, *, strict: bool = False) -> Path:
        return root.parent / "outside" if path == prefix else original(path, strict=strict)

    monkeypatch.setattr(type(root), "resolve", resolved)
    monkeypatch.setattr(sys, "prefix", str(prefix))
    monkeypatch.setattr(sys, "executable", str(executable))
    assert main([str(root), "0"]) == _ERROR
    assert not (root / "venvs/release-runtime.v1.txt").exists()
    assert "outside the tooling checkout" in capsys.readouterr().err


# eof
