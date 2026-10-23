"""Bootstrap keeps package imports behind the measured runtime readiness gate."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.test_support import metadata
from tools.release_workflow import bootstrap
from tools.release_workflow.runtime_identity import RuntimeIdentity

if TYPE_CHECKING:
    from pathlib import Path

_ERROR = 2
pytestmark = pytest.mark.usefixtures("bootstrap_state")


def test_successful_gate(runtime: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """The engine receives plain arguments only after the gate succeeds."""
    root, executable, prefix = runtime
    RuntimeIdentity.measure(root, executable, prefix).publish()
    metadata(root)
    monkeypatch.setattr(sys, "executable", str(executable))
    monkeypatch.setattr(sys, "prefix", str(prefix))
    monkeypatch.setattr(bootstrap, "environment", lambda: {
        "sys_platform": "win32", "os_name": "nt", "platform_system": "Windows",
        "platform_machine": "AMD64", "implementation_name": "cpython",
        "python_version": "3.13", "python_full_version": "3.13.9",
    })
    assert bootstrap.check(root) == ()


def test_missing_identity(runtime: tuple[Path, Path, Path]) -> None:
    """Missing designation fails before any dependency or engine work."""
    root, _, _ = runtime
    with pytest.raises(FileNotFoundError):
        bootstrap.check(root)


@pytest.mark.parametrize(("system", "machine", "width"), [
    ("linux", "AMD64", 8), ("win32", "ARM64", 8), ("win32", "AMD64", 4),
])
def test_unsupported_platform(system: str, machine: str, width: int, monkeypatch: pytest.MonkeyPatch) -> None:
    """Platform and pointer width are measured independently."""
    monkeypatch.setattr(sys, "platform", system)
    monkeypatch.setattr(bootstrap.platform, "machine", lambda: machine)
    def measured_width(_format: str) -> int:
        return width

    monkeypatch.setattr(bootstrap.struct, "calcsize", measured_width)
    with pytest.raises(ValueError, match="Windows x64"):
        bootstrap.environment()


def test_supported_platform(monkeypatch: pytest.MonkeyPatch) -> None:
    """Marker environment contains actual supported interpreter facts."""
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(bootstrap.platform, "machine", lambda: "AMD64")
    def measured_width(_format: str) -> int:
        return 8

    monkeypatch.setattr(bootstrap.struct, "calcsize", measured_width)
    assert bootstrap.environment()["implementation_name"] == sys.implementation.name


def test_helper_load_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Failed private loads are removed from the module cache."""
    monkeypatch.setattr(bootstrap, "__file__", str(tmp_path / "bootstrap.py"))
    with pytest.raises(FileNotFoundError):
        bootstrap.helper("missing")
    assert "_release_bootstrap_missing" not in sys.modules
    def missing_spec(_name: str, _path: Path) -> None:
        return None

    monkeypatch.setattr(bootstrap.importlib.util, "spec_from_file_location", missing_spec)
    with pytest.raises(ImportError, match="Cannot load"):
        bootstrap.helper("missing")


def test_main_boundary(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Main passes argument strings and reports engine import or gate failure."""
    calls: list[list[str]] = []

    def engine_main(argv: list[str]) -> int:
        calls.append(argv)
        return 0

    monkeypatch.setattr(sys, "path", list(sys.path))
    def passed_check(_root: Path) -> tuple[str, ...]:
        return ()

    def loaded_engine(_name: str) -> SimpleNamespace:
        return SimpleNamespace(main=engine_main)

    monkeypatch.setattr(bootstrap, "check", passed_check)
    monkeypatch.setattr(bootstrap.importlib, "import_module", loaded_engine)
    assert bootstrap.main(["explicit"]) == 0
    monkeypatch.setattr(sys, "argv", ["bootstrap", "ambient"])
    assert bootstrap.main() == 0
    assert calls == [["explicit"], ["ambient"]]

    def failed_import(_name: str) -> None:
        msg = "engine failed"
        raise ImportError(msg)

    monkeypatch.setattr(bootstrap.importlib, "import_module", failed_import)
    assert bootstrap.main([]) == _ERROR
    assert "engine failed" in capsys.readouterr().err

    def failed_check(_root: Path) -> None:
        msg = "readiness failed"
        raise ValueError(msg)

    monkeypatch.setattr(bootstrap, "check", failed_check)
    assert bootstrap.main([]) == _ERROR
    assert "readiness failed" in capsys.readouterr().err

# eof
