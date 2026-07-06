@echo off
setlocal EnableDelayedExpansion

REM Self-locate the llm-shared folder from this launcher's own path (%~dp0 is
REM the bin\ folder) when the caller did not set LLM_SHARED_DIR, so a full-path
REM call works from any shell with no environment setup.
if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."
set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-n "%PYTHON_BASE%\python_3*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    echo ERROR: No python_3* directory found in "%PYTHON_BASE%"
    exit /b 1
)

set "PATH=%PYTHON_BASE%\%LATEST_PYTHON%\Scripts;%PATH%"

python "%~dp0..\tools\git_batch_commit.py" %*
