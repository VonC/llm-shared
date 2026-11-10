"""Verify checkout-local prerequisites without executing interpreters or installers."""

from __future__ import annotations

import json
import runpy
import subprocess
from pathlib import Path

import pytest

from tools.lifecycle_compatibility import environment

_PROBE_TIMEOUT = 10


def verified(*_args: object) -> dict[str, object]:
    """Provide only the external executable's prerequisite observation."""
    return {"python": [3, 12]}


def manifest(root: Path, pin: str = "9.1.0") -> None:
    """Represent this checkout's independent supported dependency set."""
    directory = root / "tools" / "lifecycle_compatibility"
    directory.mkdir(parents=True)
    (directory / "requirements-py312.txt").write_text(f"pytest=={pin}\npytest-xdist==3.8.0\n", encoding="utf-8")


def test_checkout_and_override_resolution(tmp_path: Path) -> None:
    """Each checkout selects its own environment; overrides must be absolute."""
    expected = tmp_path / "venvs" / "python_3.12_lifecycle_compatibility" / "Scripts" / "python.exe"
    assert environment.interpreter(tmp_path, None) == expected
    assert environment.interpreter(tmp_path, str(expected)) == expected
    with pytest.raises(ValueError, match="absolute"):
        environment.interpreter(tmp_path, "python")


@pytest.mark.parametrize("pin", ["9.1.0", "9.1.1"])
def test_real_probe_uses_checkout_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pin: str) -> None:
    """Version labels and another branch's manifest cannot substitute for a probe."""
    manifest(tmp_path, pin)
    executable = tmp_path / "python.exe"
    executable.touch()
    def probe(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command[0] == str(executable)
        assert kwargs["timeout"] == _PROBE_TIMEOUT
        return subprocess.CompletedProcess(command, 0, json.dumps({"python": [3, 12], "dependencies": {"pytest": pin, "pytest-xdist": "3.8.0"}}))
    monkeypatch.setattr(environment.subprocess, "run", probe)
    assert environment.verify(tmp_path, executable)["python"] == [3, 12]


@pytest.mark.parametrize("result", [
    {"python": [3, 13], "dependencies": {}},
    {"python": [3, 12], "dependencies": {"pytest": "wrong"}},
    {"python": [3, 12], "dependencies": {}},
    [],
])
def test_unsuitable_probe_fails_with_setup_help(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, result: object) -> None:
    """A real but unsuitable executable fails instead of skipping or provisioning."""
    manifest(tmp_path)
    executable = tmp_path / "python.exe"
    executable.touch()
    def probe(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, json.dumps(result))
    monkeypatch.setattr(environment.subprocess, "run", probe)
    with pytest.raises(ValueError, match=r"--setup.*LLM_SHARED_LIFECYCLE_PYTHON"):
        environment.verify(tmp_path, executable)


def test_missing_interpreter_never_installs(tmp_path: Path) -> None:
    """Normal validation only explains explicit setup and override choices."""
    with pytest.raises(ValueError, match="--setup"):
        environment.verify(tmp_path, tmp_path / "missing.exe")


@pytest.mark.parametrize("text", ["pytest>=8", "pytest==8\npytest==9", "", "# comment\n\npytest==8\n"])
def test_bad_manifests_are_rejected(tmp_path: Path, text: str) -> None:
    """Ambiguous, empty or incomplete pins cannot provide dependency evidence."""
    manifest(tmp_path)
    (tmp_path / "tools/lifecycle_compatibility/requirements-py312.txt").write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="compatibility"):
        environment.requirements(tmp_path)


@pytest.mark.parametrize("failure", [OSError("missing"), subprocess.TimeoutExpired("probe", 10), subprocess.CalledProcessError(1, "probe"), ValueError("bad json")])
def test_failed_probe_has_explicit_remedy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: Exception) -> None:
    """Missing processes, timeouts and invalid observations all fail setup."""
    manifest(tmp_path)
    executable = tmp_path / "python.exe"
    executable.touch()
    def fail(*_args: object, **_kwargs: object) -> None:
        raise failure
    monkeypatch.setattr(environment.subprocess, "run", fail)
    with pytest.raises(ValueError, match="--setup"):
        environment.verify(tmp_path, executable)


def test_unsupported_expected_version_is_not_a_compatibility_target(tmp_path: Path) -> None:
    """The direct executable harness cannot label arbitrary versions supported."""
    with pytest.raises(ValueError, match=r"3\.12 or 3\.13"):
        environment.verify(tmp_path, tmp_path / "python.exe", (3, 11))


@pytest.mark.parametrize("retained", [False, True])
def test_validation_main_preserves_or_cleans_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, retained: bool) -> None:
    """Temporary projects disappear on return; requested evidence is retained."""
    selected = Path(environment.sys.executable)
    monkeypatch.setenv(environment.OVERRIDE, str(selected))
    monkeypatch.setattr(environment, "verify", verified)
    roots: list[Path] = []
    def validate(args: list[str]) -> int:
        root = Path(args[0])
        roots.append(root)
        root.mkdir(exist_ok=True)
        return 0
    monkeypatch.setattr(environment.runner, "main", validate)
    assert environment.main(["--evidence", str(tmp_path)] if retained else []) == 0
    assert roots[0].exists() is retained


@pytest.mark.parametrize("wrong_launcher", [False, True])
def test_main_reports_setup_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, wrong_launcher: bool) -> None:
    """Override mismatch and missing prerequisites cannot run scenarios."""
    monkeypatch.setenv(environment.OVERRIDE, str(tmp_path / "other.exe"))
    if wrong_launcher:
        monkeypatch.setattr(environment, "verify", verified)
    assert environment.main([]) == 1


def test_environment_module_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """The batch-launched module returns a failing setup verdict unchanged."""
    monkeypatch.setenv(environment.OVERRIDE, "relative")
    monkeypatch.setattr(environment.sys, "argv", ["environment"])
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(environment.__file__, run_name="__main__")
    assert caught.value.code == 1


# eof
