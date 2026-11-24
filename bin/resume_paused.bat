@echo off
setlocal DisableDelayedExpansion

REM Wrapper for tools\resume_paused.py: the HUMAN-ONLY bulk resume of paused
REM agent sessions in TUIOS panes. Run it yourself from a terminal; agents must
REM never run it, not even with --dry-run or --help (the receiving validator is
REM bin\resume_paused_validate.bat). Self-locates llm-shared and runs its newest
REM matching virtual-environment Python without project activation, forwarding
REM every argument to tools\resume_paused.py only. Delayed expansion stays off,
REM so a literal ! in an --except or --switch-roles name reaches Python intact.
if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."
set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-d "%PYTHON_BASE%\python_3*llm-shared*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    echo ERROR: No python_3*llm-shared* directory found in "%PYTHON_BASE%"
    exit /b 2
)

set "PYTHON_EXE=%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe"
if defined PYTHONPATH (
    set "PYTHONPATH=%LLM_SHARED_DIR%;%PYTHONPATH%"
) else (
    set "PYTHONPATH=%LLM_SHARED_DIR%"
)
"%PYTHON_EXE%" "%LLM_SHARED_DIR%\tools\resume_paused.py" %*
exit /b %ERRORLEVEL%
