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
REM with the senv preamble.
if not defined PRJ_DIR set "PRJ_DIR=%CD%"
for %%i in ("%PRJ_DIR%") do set "LLM_SHARED_PRJ_DIR_NAME=%%~nxi"
if defined LLM_SHARED_PRJ_DIR_NAME set "NO_MORE_SENV_!LLM_SHARED_PRJ_DIR_NAME!="
set "GHOG_SENV_LOG=%PRJ_DIR%\a.ghog.senv.log"
if exist "%PRJ_DIR%\senv.bat" call <NUL "%PRJ_DIR%\senv.bat" > "%GHOG_SENV_LOG%" 2>&1
set "LLM_SHARED_PRJ_DIR_NAME="

REM groundhog itself runs from the llm-shared venv (Q17), reached by absolute
REM path: no PATH prepend, so the project PATH stays first for the pytest
REM child process.
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
