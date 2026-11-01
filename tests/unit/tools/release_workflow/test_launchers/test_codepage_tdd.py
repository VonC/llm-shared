"""Source contracts for batch-only behavior; no shell execution or emulation."""

from __future__ import annotations

from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[5]
_CODEPAGE_OPERATIONS = 3


@pytest.mark.parametrize(("launcher", "entry"), [
    ("release_workflow.bat", "explicit-batch"), ("release_alias.bat", "alias-batch"),
])
def test_batch_boundary_contract(launcher: str, entry: str) -> None:
    """Entry syntax, isolated interpreter flags and cleanup remain explicit."""
    source = (_ROOT / "bin" / launcher).read_text(encoding="utf-8")
    assert source.startswith("@echo off\nsetlocal DisableDelayedExpansion\n")
    assert 'for %%R in ("%~dp0..") do set "_release_root=%%~fR"' in source
    assert f' -I -X utf8 "%_release_root%\\tools\\release_workflow\\bootstrap.py" --entry-kind {entry} -- %*' in source
    assert 'set "_release_status=%ERRORLEVEL%"' in source
    assert source.rstrip().endswith("endlocal & exit /b %_release_status%")
    assert source.count('"%SystemRoot%\\System32\\chcp.com"') == _CODEPAGE_OPERATIONS
    assert ':cleanup\nif defined _release_cp "%SystemRoot%\\System32\\chcp.com" %_release_cp% >nul 2>&1' in source
    assert 'if not "%_release_cp%"=="65001"' in source


@pytest.mark.parametrize("launcher", ["release_workflow.bat", "release_alias.bat"])
def test_codepage_parser_source(launcher: str) -> None:
    """The source retains final-colon parsing and leading numeric restoration."""
    source = (_ROOT / "bin" / launcher).read_text(encoding="utf-8")
    assert 'for /f "tokens=1,* delims=:" %%A in ("%_release_cp%") do set "_release_tail=%%B"' in source
    assert 'set "_release_cp=%_release_tail%"\ngoto codepage_tail' in source
    assert 'for %%D in (0 1 2 3 4 5 6 7 8 9) do if "%_release_cp:~0,1%"=="%%D" goto codepage_digit' in source
    assert 'set "_release_digits=%_release_digits%%_release_cp:~0,1%"' in source
    assert 'set "_release_cp=%_release_cp:~1%"\ngoto codepage_next' in source


@pytest.mark.parametrize("launcher", ["release_workflow.bat", "release_alias.bat"])
def test_runtime_prerequisites_source(launcher: str) -> None:
    """Every pre-Python rejection keeps status 2 and reaches the diagnostic."""
    source = (_ROOT / "bin" / launcher).read_text(encoding="utf-8")
    prerequisite = source[:source.index('python.exe" -I -X utf8')]
    expected = [
        'set "_release_status=2"',
        'set "_release_error=missing or unreadable runtime record"',
        'if not exist "%_release_root%\\venvs\\release-runtime.v1.txt" goto runtime_error',
        'for /f "usebackq delims=" %%L in ("%_release_root%\\venvs\\release-runtime.v1.txt") do (',
        'if not defined _release_version (\n        set "_release_version=%%L"',
        ') else if not defined _release_environment (\n        set "_release_environment=%%L"',
        ') else (\n        set "_release_extra=%%L"',
        'set "_release_error=invalid runtime record version or length"',
        "if defined _release_extra goto runtime_error",
        'if not "!_release_version!"=="1" goto invalid_version',
        'set "_release_error=invalid runtime environment path"',
        'if not "!_release_environment:~0,6!"=="venvs/" goto invalid_environment',
        'set "_release_safe=!_release_environment:"=!"',
        'set "_release_safe=!_release_safe:\\=!"',
        'set "_release_safe=!_release_safe::=!"',
        'set "_release_safe=!_release_safe:..=!"',
        'if not "!_release_safe!"=="!_release_environment!" goto invalid_environment',
        'set "_release_error=missing designated runtime interpreter"',
        'if not exist "%_release_root%\\%_release_environment%\\Scripts\\python.exe" goto runtime_error',
    ]
    positions = [prerequisite.index(line) for line in expected]
    assert positions == sorted(positions)
    assert prerequisite.count('set "_release_status=') == 1
    assert (
        ":invalid_version\n:invalid_environment\nendlocal\n:runtime_error\n"
        ">&2 echo Release readiness failed: %_release_error%. Run this checkout's setup.\n:cleanup\n"
    ) in source


@pytest.mark.parametrize("launcher", ["release_workflow.bat", "release_alias.bat"])
def test_native_status_normalization_source(launcher: str) -> None:
    """Public statuses pass through; every other status is diagnosed as 1."""
    source = (_ROOT / "bin" / launcher).read_text(encoding="utf-8")
    assert (
        'set "_release_status=%ERRORLEVEL%"\n'
        'if "%_release_status%"=="0" goto cleanup\n'
        'if "%_release_status%"=="1" goto cleanup\n'
        'if "%_release_status%"=="2" goto cleanup\n'
        '>&2 echo Release operation exited with native status %_release_status%; returning 1.\n'
        'set "_release_status=1"\ngoto cleanup\n'
    ) in source


def test_runtime_record_producer_source() -> None:
    """Setup gates preparation, missing environments and interpreter failure."""
    source = (_ROOT / "bin/release_runtime_record.bat").read_text(encoding="utf-8")
    assert source.startswith("@echo off\n")
    blocks = [
        'setlocal DisableDelayedExpansion\nif "%~2"=="" exit /b 2\nif not "%~2"=="0" exit /b %~2\n',
        "if not defined VIRTUAL_ENV (\n"
        "    >&2 echo Warning: release runtime identity not updated; no environment prepared.\n"
        "    exit /b 0\n)",
        'if not exist "%VIRTUAL_ENV%\\Scripts\\python.exe" (\n'
        '    >&2 echo Release runtime setup failed: prepared interpreter is missing.\n'
        '    exit /b 2\n)',
        '"%VIRTUAL_ENV%\\Scripts\\python.exe" -I -X utf8 '
        '"%~1\\tools\\release_workflow\\runtime_identity.py" "%~1" "0"\nexit /b %ERRORLEVEL%',
    ]
    positions = [source.index(block) for block in blocks]
    assert positions == sorted(positions)
    assert source.rstrip().endswith("exit /b %ERRORLEVEL%")


# eof
