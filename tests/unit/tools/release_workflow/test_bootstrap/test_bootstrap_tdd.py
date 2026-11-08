"""Bootstrap authenticates origin, gates imports and normalizes interruption.

Step 1 of v0.14.0 version-sources: the engine's status 3 passes through the
final process boundary like 0, 1 and 2; 4 and 23 still become 1.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.unit.tools.release_workflow.test_support import metadata
from tools.release_workflow import bootstrap
from tools.release_workflow.runtime_identity import RuntimeIdentity

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
    identity = bootstrap.check(root)
    identity.verify(executable, prefix)


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
    verified = RuntimeIdentity(Path.cwd(), "venvs/prepared")

    def engine_main(argv: list[str], *, entry_kind: str, original_cwd: Path, tooling_root: Path, runtime: bootstrap.Identity) -> int:
        assert entry_kind == "explicit-native"
        assert original_cwd.is_absolute()
        assert tooling_root.is_absolute()
        assert runtime is verified
        calls.append(argv)
        return 0

    monkeypatch.setattr(sys, "path", list(sys.path))
    def passed_check(_root: Path) -> bootstrap.Identity:
        return verified

    def loaded_engine(_name: str) -> SimpleNamespace:
        return SimpleNamespace(main=engine_main)

    monkeypatch.setattr(bootstrap, "check", passed_check)
    monkeypatch.setattr(bootstrap.importlib, "import_module", loaded_engine)
    prefix = ["--entry-kind", "explicit-native", "--"]
    assert bootstrap.main([*prefix, "explicit"]) == 0
    monkeypatch.setattr(sys, "argv", ["bootstrap", *prefix, "ambient"])
    assert bootstrap.main() == 0
    assert calls == [["explicit"], ["ambient"]]

    def failed_import(_name: str) -> None:
        msg = "engine failed"
        raise ImportError(msg)

    monkeypatch.setattr(bootstrap.importlib, "import_module", failed_import)
    assert bootstrap.main(prefix) == _ERROR
    assert "engine failed" in capsys.readouterr().err

    def failed_check(_root: Path) -> None:
        msg = "readiness failed"
        raise ValueError(msg)

    monkeypatch.setattr(bootstrap, "check", failed_check)
    assert bootstrap.main(prefix) == _ERROR
    assert "readiness failed" in capsys.readouterr().err

@pytest.mark.parametrize("arguments", [[], ["--entry-kind", "alias-batch"],
    ["--entry-kind", "unknown", "--"], ["--entry-kind", "explicit-native", "--", "--entry-kind=alias-batch"],
    ["--entry-kind", "explicit-native", "--", "--entry-kind", "alias-batch"],
])
def test_entry_protocol(arguments: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    """Missing or duplicate origins fail before runtime checks or imports."""
    assert bootstrap.main(arguments) == _ERROR
    diagnostic = capsys.readouterr().err
    assert "Release invocation failed:" in diagnostic
    assert "entry-kind" in diagnostic
    assert "setup" not in diagnostic

@pytest.mark.parametrize("failure", [KeyboardInterrupt(), TypeError("unexpected readiness bug")])
def test_readiness_execution_failure(failure: BaseException, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Interruption and unexpected readiness errors remain execution failures."""
    def failed(_root: Path) -> tuple[str, ...]:
        raise failure

    monkeypatch.setattr(bootstrap, "check", failed)
    assert bootstrap.main(["--entry-kind", "explicit-native", "--"]) == 1
    expected = "interrupted" if isinstance(failure, KeyboardInterrupt) else "unexpected readiness bug"
    assert expected in capsys.readouterr().err


@pytest.mark.parametrize(("outcome", "expected"), [(23, "native status 23"), (KeyboardInterrupt(), "interrupted"), (RuntimeError("domain failed"), "domain failed")])
def test_engine_failure(outcome: int | BaseException, expected: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Native failures retain detail while normalizing the public status."""
    def passed(_root: Path) -> bootstrap.Identity:
        return RuntimeIdentity(_root, "venvs/prepared")

    def execute(_argv: list[str], **_facts: object) -> int:
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    def imported(_name: str) -> SimpleNamespace:
        return SimpleNamespace(main=execute)

    monkeypatch.setattr(bootstrap, "check", passed)
    monkeypatch.setattr(bootstrap.importlib, "import_module", imported)
    assert bootstrap.main(["--entry-kind", "explicit-native", "--"]) == 1
    diagnostic = capsys.readouterr().err
    assert expected in diagnostic


@pytest.mark.parametrize(("status", "public"), [(0, 0), (1, 1), (2, 2), (3, 3), (4, 1), (23, 1)])
def test_engine_status_boundary(status: int, public: int, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Public statuses pass through; any other value is diagnosed as 1."""
    def passed(_root: Path) -> bootstrap.Identity:
        return RuntimeIdentity(_root, "venvs/prepared")

    def execute(_argv: list[str], **_facts: object) -> int:
        return status

    def imported(_name: str) -> SimpleNamespace:
        return SimpleNamespace(main=execute)

    monkeypatch.setattr(bootstrap, "check", passed)
    monkeypatch.setattr(bootstrap.importlib, "import_module", imported)
    assert bootstrap.main(["--entry-kind", "explicit-native", "--"]) == public
    diagnostic = capsys.readouterr().err
    assert (f"native status {status}; returning 1" in diagnostic) == (status != public)


def test_early_diagnostic_encoding(monkeypatch: pytest.MonkeyPatch) -> None:
    """Readiness errors use UTF-8/LF before importing any tools package."""
    output = io.BytesIO()
    stream = io.TextIOWrapper(output, encoding="ascii", newline="\r\n")
    monkeypatch.setattr(sys, "stderr", stream)

    def failed(_root: Path) -> tuple[str, ...]:
        message = "réparer"
        raise ValueError(message)

    monkeypatch.setattr(bootstrap, "check", failed)
    assert bootstrap.main(["--entry-kind", "explicit-native", "--"]) == _ERROR
    stream.flush()
    assert "réparer".encode() in output.getvalue()
    assert b"\r" not in output.getvalue()


# eof
