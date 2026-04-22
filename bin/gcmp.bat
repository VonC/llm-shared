@echo off
setlocal EnableDelayedExpansion

set "PYTHON_BASE=%COPILOT_SHARED_DIR%\venvs"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-n "%PYTHON_BASE%\python_3*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    echo ERROR: No python_3* directory found in "%PYTHON_BASE%"
    exit /b 1
)

set "PATH=%PYTHON_BASE%\%LATEST_PYTHON%\Scripts;%PATH%"

python "%~dp0..\tools\group_commit_message_prompt.py" %*
