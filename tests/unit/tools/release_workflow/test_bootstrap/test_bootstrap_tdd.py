"""Bootstrap authenticates origin, gates imports and normalizes interruption.

Step 1 of v0.14.0 version-sources: the engine's status 3 passes through the
final process boundary like 0, 1 and 2; 4 and 23 still become 1.

Step 4 of v0.14.0 git-cliff-provisioning: the internal `git-cliff-worker`
entry kind passes the same readiness gate, loads the download worker instead
of the command dispatcher and returns its status (0, 75 or 65) unchanged; the
release kinds still turn 65 and 75 into 1.

Step 8 of v0.14.0 git-cliff-provisioning: the `gcliff-batch` kind loads the
gcliff launcher with the bootstrap facts and returns its status unchanged (0,
1, 2, 3, 69 and 101 alike); its readiness, invocation and execution failures
before the launcher runs, and an error escaping it, are 69, tested apart from
the release kinds, which keep 2 and 1.
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


@pytest.mark.parametrize(("status", "public"), [(0, 0), (1, 1), (2, 2), (3, 3), (4, 1), (23, 1), (65, 1), (75, 1)])
def test_engine_status_boundary(status: int, public: int, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Public statuses pass through; any other value, the worker's 65 and 75 included, is diagnosed as 1."""
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


@pytest.mark.parametrize(("kind", "module"), [
    ("explicit-batch", "tools.release_workflow.cli"), ("alias-batch", "tools.release_workflow.cli"),
    ("explicit-native", "tools.release_workflow.cli"), ("git-cliff-worker", "tools.release_workflow.git_cliff.download_worker"),
    ("gcliff-batch", "tools.release_workflow.git_cliff.launcher"),
])
def test_each_entry_kind_imports_its_own_module(kind: str, module: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """The release kinds load the command dispatcher, the worker kind the download worker, the gcliff kind its launcher."""
    imported: list[str] = []

    def passed(_root: Path) -> bootstrap.Identity:
        return RuntimeIdentity(_root, "venvs/prepared")

    def succeeded(*_arguments: object, **_facts: object) -> int:
        return 0

    def imported_module(name: str) -> SimpleNamespace:
        imported.append(name)
        return SimpleNamespace(main=succeeded)

    monkeypatch.setattr(bootstrap, "check", passed)
    monkeypatch.setattr(bootstrap.importlib, "import_module", imported_module)
    assert bootstrap.main(["--entry-kind", kind, "--"]) == 0
    assert imported == [module]


_GCLIFF = ["--entry-kind", "gcliff-batch", "--"]
_UNAVAILABLE = 69


def test_a_gcliff_readiness_failure_is_69_with_the_setup_message(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Step 8 of git-cliff-provisioning: a readiness failure of `gcliff-batch` is 69, not 2, and names the setup remedy."""
    def failed_check(_root: Path) -> None:
        msg = "readiness failed"
        raise ValueError(msg)

    monkeypatch.setattr(bootstrap, "check", failed_check)
    assert bootstrap.main(_GCLIFF) == _UNAVAILABLE
    diagnostic = capsys.readouterr().err
    assert "readiness failed" in diagnostic
    assert "Run this checkout's setup" in diagnostic
    assert bootstrap.main(["--entry-kind", "alias-batch", "--"]) == _ERROR


@pytest.mark.parametrize("reserved", [["--entry-kind", "alias-batch"], ["--entry-kind=explicit-native"]])
def test_a_reserved_entry_kind_in_gcliff_arguments_is_69(reserved: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    """A git-cliff argument cannot repeat the reserved prefix: 69 for `gcliff-batch`, while a release kind keeps 2."""
    assert bootstrap.main([*_GCLIFF, "--version", *reserved]) == _UNAVAILABLE
    assert "Release invocation failed:" in capsys.readouterr().err
    assert bootstrap.main(["--entry-kind", "explicit-batch", "--", *reserved]) == _ERROR


@pytest.mark.parametrize("failure", [KeyboardInterrupt(), TypeError("unexpected readiness bug")])
def test_a_gcliff_execution_failure_before_its_launcher_is_69(failure: BaseException, monkeypatch: pytest.MonkeyPatch,
                                                             capsys: pytest.CaptureFixture[str]) -> None:
    """An interruption or an unexpected error before the launcher runs is 69: git-cliff never started."""
    def failed(_root: Path) -> None:
        raise failure

    monkeypatch.setattr(bootstrap, "check", failed)
    assert bootstrap.main(_GCLIFF) == _UNAVAILABLE
    assert "Release execution failed:" in capsys.readouterr().err


@pytest.mark.parametrize("status", [0, 1, 2, 3, 69, 101])
def test_the_gcliff_kind_returns_the_launcher_status_unchanged(status: int, monkeypatch: pytest.MonkeyPatch,
                                                               capsys: pytest.CaptureFixture[str]) -> None:
    """After readiness, the launcher gets the git-cliff arguments and the bootstrap facts; its status is never normalized."""
    verified = RuntimeIdentity(Path.cwd(), "venvs/prepared")
    received: list[tuple[list[str], Path, Path, bootstrap.Identity]] = []

    def passed(_root: Path) -> bootstrap.Identity:
        return verified

    def launcher_main(arguments: list[str], *, original_cwd: Path, tooling_root: Path, runtime: bootstrap.Identity) -> int:
        received.append((arguments, original_cwd, tooling_root, runtime))
        return status

    def imported_launcher(_name: str) -> SimpleNamespace:
        return SimpleNamespace(main=launcher_main)

    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(bootstrap, "check", passed)
    monkeypatch.setattr(bootstrap.importlib, "import_module", imported_launcher)
    assert bootstrap.main([*_GCLIFF, "--version"]) == status
    ((arguments, original_cwd, tooling_root, runtime),) = received
    assert (arguments, original_cwd, runtime) == (["--version"], Path.cwd(), verified)
    assert tooling_root == Path(bootstrap.__file__).resolve().parents[2]
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("boundary", ["cwd", "streams"])
@pytest.mark.parametrize(("failure", "release_status"), [(OSError("access denied"), _ERROR), (KeyboardInterrupt(), 1)])
def test_a_failure_before_the_entry_is_parsed_keeps_the_status_of_its_kind(*, boundary: str, failure: BaseException, release_status: int,
                                                                           monkeypatch: pytest.MonkeyPatch,
                                                                           capsys: pytest.CaptureFixture[str]) -> None:
    """Code review round 1 of Step 8: a valid gcliff call whose cwd capture or stream setup fails is 69; a release kind keeps 2 or 1."""
    def failed(*_arguments: object) -> None:
        raise failure

    if boundary == "cwd":
        monkeypatch.setattr(bootstrap.Path, "cwd", failed)
    else:
        monkeypatch.setattr(bootstrap, "configure_streams", failed)
    assert bootstrap.main([*_GCLIFF, "--version"]) == _UNAVAILABLE
    assert bootstrap.main(["--entry-kind", "explicit-batch", "--", "version"]) == release_status
    assert bootstrap.main(["--entry-kind", "gcliff-batch"]) == release_status
    expected = "interrupted" if isinstance(failure, KeyboardInterrupt) else "access denied"
    assert capsys.readouterr().err.count(expected) == len(("gcliff", "release", "malformed"))


def test_the_requested_kind_needs_a_well_formed_prefix() -> None:
    """The kind is read only from `--entry-kind <known kind> --`, never from the user arguments."""
    assert bootstrap.requested_kind([*_GCLIFF, "--entry-kind=alias-batch"]) == "gcliff-batch"
    malformed = [[], ["--entry-kind", "gcliff-batch"], ["--entry-kind", "unknown", "--"], ["--kind", "gcliff-batch", "--"],
                 ["--entry-kind", "gcliff-batch", "-"]]
    assert [bootstrap.requested_kind(arguments) for arguments in malformed] == [None] * len(malformed)


def test_an_error_escaping_the_gcliff_launcher_is_69(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The final boundary of `gcliff-batch` reports 69: no git-cliff status is known."""
    def passed(_root: Path) -> bootstrap.Identity:
        return RuntimeIdentity(_root, "venvs/prepared")

    def broken(*_arguments: object, **_facts: object) -> int:
        msg = "launcher bug"
        raise RuntimeError(msg)

    def imported_launcher(_name: str) -> SimpleNamespace:
        return SimpleNamespace(main=broken)

    monkeypatch.setattr(bootstrap, "check", passed)
    monkeypatch.setattr(bootstrap.importlib, "import_module", imported_launcher)
    assert bootstrap.main(_GCLIFF) == _UNAVAILABLE
    assert "launcher bug" in capsys.readouterr().err


@pytest.mark.parametrize("status", [0, 2, 65, 75])
def test_the_worker_kind_returns_its_status_unchanged(status: int, monkeypatch: pytest.MonkeyPatch,
                                                      capsys: pytest.CaptureFixture[str]) -> None:
    """Step 4 of git-cliff-provisioning: after readiness, the worker gets only its arguments and its status is kept."""
    received: list[list[str]] = []

    def passed(_root: Path) -> bootstrap.Identity:
        return RuntimeIdentity(_root, "venvs/prepared")

    def worker_main(arguments: list[str]) -> int:
        received.append(arguments)
        return status

    def imported_worker(_name: str) -> SimpleNamespace:
        return SimpleNamespace(main=worker_main)

    monkeypatch.setattr(bootstrap, "check", passed)
    monkeypatch.setattr(bootstrap.importlib, "import_module", imported_worker)
    assert bootstrap.main(["--entry-kind", "git-cliff-worker", "--", "--mode", "metadata"]) == status
    assert (received, capsys.readouterr().err) == ([["--mode", "metadata"]], "")


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
