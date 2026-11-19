@echo off
setlocal EnableDelayedExpansion

REM Wrapper for tools\resume_paused_validation.py: the read-only, agent-callable
REM validator of one marked resume receiver. It never runs the human-only bulk
REM resume command. Self-locates llm-shared and runs its newest matching
REM virtual-environment Python without project activation.
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
"%PYTHON_EXE%" "%LLM_SHARED_DIR%\tools\resume_paused_validation.py" %*
exit /b %ERRORLEVEL%
