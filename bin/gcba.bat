@echo off
setlocal EnableDelayedExpansion

set "PYTHON_BASE=%PRGS%\pythons"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-n "%PYTHON_BASE%\python3*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    echo ERROR: No python3* directory found in "%PYTHON_BASE%"
    exit /b 1
)

set "PATH=%PYTHON_BASE%\%LATEST_PYTHON%;%PYTHON_BASE%\%LATEST_PYTHON%\Scripts;%PATH%"

python "%~dp0..\tools\git_batch_commit.py" %*
