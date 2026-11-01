"""Production runtime publication and readiness with explicit interpreter facts."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.unit.tools.release_workflow.launcher_simulation import decoded, tooling
from tests.unit.tools.release_workflow.repository_simulation import create_template
from tools.release_workflow import runtime_identity

_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(("scenario", "status"), [
    ("success", 0), ("failed_setup", 7), ("missing_python", 2), ("foreign_python", 0),
])
def test_setup_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
                     scenario: str, status: int) -> None:
    """Only successful local measurement publishes; failures preserve prior bytes."""
    selected = tooling(tmp_path / "tooling")
    record = selected.root / "venvs/release-runtime.v1.txt"
    before = record.read_bytes()
    if scenario == "success":
        record.unlink()
    if scenario == "missing_python":
        selected.identity.executable.unlink()
    prefix = tmp_path / "foreign" if scenario == "foreign_python" else selected.identity.prefix
    monkeypatch.setattr(sys, "prefix", str(prefix))
    monkeypatch.setattr(sys, "executable", str(prefix / "Scripts/python.exe"))
    code = runtime_identity.main([str(selected.root), "7" if scenario == "failed_setup" else "0"])
    assert code == status
    assert record.read_bytes() == before
    if scenario == "foreign_python":
        assert "Warning: release runtime identity not updated" in capsys.readouterr().err


def test_setup_status_cleanup_source() -> None:
    """The batch boundary preserves status and clears its temporary variables."""
    source = (_ROOT / "senv.bat").read_text(encoding="utf-8")
    start = source.index('pushd "%PRJ_DIR%"\ncall switchpy')
    block = source[start:source.index("REM Install composable hooks", start)]
    assert 'set "RELEASE_SETUP_STATUS=%ERRORLEVEL%"' in block
    assert 'set "RELEASE_RUNTIME_STATUS=%ERRORLEVEL%"' in block
    assert 'set "RELEASE_SETUP_STATUS="' in block
    assert 'set "RELEASE_RUNTIME_STATUS="' in block
    assert "exit /b" in block


@pytest.mark.parametrize(("scenario", "status"), [
    ("ready", 0), ("missing_record", 2), ("escaped_record", 2), ("missing_engine", 2),
])
def test_bootstrap_readiness(tmp_path: Path, scenario: str, status: int) -> None:
    """Readiness rejects invalid records and leaves caller contents untouched."""
    selected = tooling(tmp_path / "tooling")
    home = tmp_path / "repository"
    home.mkdir()
    sandbox = create_template(home)
    root = home / "B"
    sentinel = root / "keep.txt"
    sentinel.write_bytes(b"caller content")
    record = selected.root / "venvs/release-runtime.v1.txt"
    if scenario == "missing_record":
        record.unlink()
    elif scenario == "missing_engine":
        (selected.root / "tools/release_workflow/cli.py").unlink()
    elif scenario == "escaped_record":
        outside = tmp_path / "outside/Scripts"
        outside.mkdir(parents=True)
        (outside / "python.exe").write_bytes(b"data only")
        # The frozen filesystem simulation supplies the escaping junction.
        import _winapi  # noqa: PLC0415 - Windows filesystem boundary

        _winapi.CreateJunction(str(outside.parent), str(selected.root / "venvs/escaped"))
        record.write_text("1\nvenvs/escaped\n", encoding="utf-8")
    result = selected.run(["probe", "--project-root", str(root)], sandbox=sandbox, cwd=root)
    assert result.returncode == status
    if status:
        assert b"Run this checkout's setup" in result.stderr
        assert not result.stdout
    assert sentinel.read_bytes() == b"caller content"


def test_bootstrap_disables_bytecode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Production bootstrap changes the interpreter flag before dispatch."""
    selected = tooling(tmp_path / "tooling")
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    home = tmp_path / "repository"
    home.mkdir()
    sandbox = create_template(home)
    root = home / "B"
    result = selected.run(["probe", "--project-root", str(root)], sandbox=sandbox, cwd=root)
    assert result.returncode == 0
    assert decoded(result)["dont_write_bytecode"] is True


def test_isolated_interpreter_source() -> None:
    """The shipped entries explicitly request isolated, UTF-8 Python startup."""
    for name in ("release_workflow.bat", "release_alias.bat"):
        source = (_ROOT / "bin" / name).read_text(encoding="utf-8")
        assert 'python.exe" -I -X utf8' in source


# eof
