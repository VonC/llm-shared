@echo off
setlocal EnableDelayedExpansion

REM Project environment first (Q21): senv.bat must run inside this same cmd
REM process, so the pytest child of groundhog sees the project venv. senv.bat
REM is idempotent through a project-specific NO_MORE_SENV guard, but harnesses
REM can inherit that guard with a stale PATH. Clear the guard for the project
REM root this wrapper is launched from so senv.bat can repair the venv PATH.
REM Its output is parked in a side log (Q31): cli.py replays it into the
REM report stream - stdout normally, a.ghog.log when the self-redirect guard
REM armed - so a forgotten caller redirect cannot flood an LLM conversation
REM with the senv preamble. This tool is agent-facing first, so parking stays
REM the default.
REM
REM Set GHOG_SENV_LIVE to stream senv.bat straight through instead. senv can
REM take the best part of a minute - two uv.exe launches dominate it - and
REM parked, that is a blank terminal for the whole of it, with the preamble
REM landing only at the end. A human watching a run wants to see it happen;
REM the file half then comes from the caller redirect.
REM
REM Neither branch can be a tee: cmd runs both sides of a pipe in child
REM processes, so `call senv.bat | tee` would lose the PATH and VIRTUAL_ENV
REM that Q21 needs in THIS process.
REM GHOG_SENV_READY is the caller asserting it already activated senv.bat in
REM THIS process, which ghog_cycle.bat does once for a whole cycle. Only an
REM explicit assertion may skip the activation: an inherited guard alone must
REM not, because the stale-guard case is exactly what the clear-and-call above
REM exists to repair.
if not defined PRJ_DIR set "PRJ_DIR=%CD%"
set "GHOG_SENV_LOG=%PRJ_DIR%\a.ghog.senv.log"
if defined GHOG_SENV_READY (
    set "GHOG_SENV_LOG="
) else (
    for %%i in ("%PRJ_DIR%") do set "LLM_SHARED_PRJ_DIR_NAME=%%~nxi"
    if defined LLM_SHARED_PRJ_DIR_NAME set "NO_MORE_SENV_!LLM_SHARED_PRJ_DIR_NAME!="
    if exist "%PRJ_DIR%\senv.bat" (
        if defined GHOG_SENV_LIVE (
            call <NUL "%PRJ_DIR%\senv.bat" 2>&1
        ) else (
            call <NUL "%PRJ_DIR%\senv.bat" > "%GHOG_SENV_LOG%" 2>&1
        )
    )
    set "LLM_SHARED_PRJ_DIR_NAME="
)

REM groundhog itself runs from the llm-shared venv (Q17), reached by absolute
REM path: no PATH prepend, so the project PATH stays first for the pytest
REM child process. LLM_SHARED_DIR self-locates from this launcher's own path
REM (%~dp0 is the bin\ folder) when neither the caller nor the senv call above
REM set it, so a full-path call works from any shell with no environment setup.
if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."
set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-n "%PYTHON_BASE%\python_3*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    if exist "%GHOG_SENV_LOG%" (type "%GHOG_SENV_LOG%" & del "%GHOG_SENV_LOG%" 2>nul)
    echo ERROR: No python_3* directory found in "%PYTHON_BASE%"
    exit /b 5
)

"%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe" "%~dp0..\tools\groundhog\cli.py" %*
set "GHOG_EXIT=%ERRORLEVEL%"
REM cli.py replays and deletes the side log; one still here means the tool
REM never ran (failed launch, early crash) - type it so the sandbox-block
REM markers (Access is denied, gum choose) stay visible for the escalation
REM rule of the instruction files.
if exist "%GHOG_SENV_LOG%" (type "%GHOG_SENV_LOG%" & del "%GHOG_SENV_LOG%" 2>nul)
exit /b %GHOG_EXIT%
