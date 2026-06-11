@echo off
setlocal EnableDelayedExpansion

REM Project environment first (Q21): senv.bat must run inside this same cmd
REM process, so the pytest child of groundhog sees the project venv. senv.bat
REM is idempotent (NO_MORE_SENV guard), so a loaded shell pays nothing.
if not defined PRJ_DIR set "PRJ_DIR=%CD%"
if exist "%PRJ_DIR%\senv.bat" call <NUL "%PRJ_DIR%\senv.bat"

REM groundhog itself runs from the llm-shared venv (Q17), reached by absolute
REM path: no PATH prepend, so the project PATH stays first for the pytest
REM child process.
set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-n "%PYTHON_BASE%\python_3*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    echo ERROR: No python_3* directory found in "%PYTHON_BASE%"
    exit /b 5
)

"%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe" "%~dp0..\tools\groundhog\cli.py" %*
exit /b %ERRORLEVEL%
