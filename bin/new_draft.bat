@echo off
setlocal EnableDelayedExpansion

REM Wrapper for tools\new_draft.py. Self-locates the llm-shared folder from this
REM launcher's own path (%~dp0 is the bin\ folder) when the caller did not set
REM LLM_SHARED_DIR, so it runs the same from any shell or repository. Picks the
REM most recent venv whose name contains "llm-shared" (newest first, /o-d), then
REM runs python by absolute path - no PATH prepend and no bare "python" lookup,
REM the form prompt_workflow.bat uses - so a nested cmd or a foreign PATH cannot resolve the
REM wrong interpreter. The trailing "*" matters: a worktree venv is named
REM python_3.13.9_llm-shared_main (note the _main suffix), so the glob must allow
REM characters after "llm-shared" while still skipping a copilot-shared venv.
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

set "PYTHON_EXE=%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe"

"%PYTHON_EXE%" "%LLM_SHARED_DIR%\tools\new_draft.py" %*
