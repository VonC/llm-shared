@echo off
setlocal EnableDelayedExpansion

REM Wrapper for tools\prompt_workflow.py. Self-locates the llm-shared folder
REM from this launcher's own path (%~dp0 is the bin\ folder) when the caller did
REM not set LLM_SHARED_DIR, so it runs the same from any shell or repository.
REM Picks the most recent venv whose name ends with "llm-shared" (newest first,
REM /o-d), so the copilot-shared venv is skipped, then runs python by absolute
REM path - no PATH prepend and no bare "python" lookup, the form ghog.bat uses -
REM so a nested cmd or a foreign PATH cannot resolve the wrong interpreter.
if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."
set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-d "%PYTHON_BASE%\python_3*llm-shared" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    echo ERROR: No python_3*llm-shared directory found in "%PYTHON_BASE%"
    exit /b 1
)

set "PYTHON_EXE=%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe"

REM When PW_PROFILE is set (see the pwi alias), run the tool under pyinstrument
REM to profile where the time goes; otherwise run it normally.
if defined PW_PROFILE (
    "%PYTHON_EXE%" -m pyinstrument "%LLM_SHARED_DIR%\tools\prompt_workflow.py" %*
) else (
    "%PYTHON_EXE%" "%LLM_SHARED_DIR%\tools\prompt_workflow.py" %*
)
