@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM Guarded session journal writer: run plan, then apply, as two separate calls.
REM llm-shared Python, no project setup. The module next to this launcher runs
REM in isolated mode (-I), so neither PYTHONPATH nor the current folder can
REM shadow the modules it imports; it adds only its own llm-shared root.
if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."
set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="
for /f "delims=" %%d in ('dir /b /ad /o-d "%PYTHON_BASE%\python_3*llm-shared*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)
if not defined LATEST_PYTHON (
    echo ERROR: No python_3*llm-shared* directory found in "%PYTHON_BASE%"
    exit /b 1
)
"%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe" -I "%~dp0..\tools\session_journal.py" %*
exit /b %ERRORLEVEL%
