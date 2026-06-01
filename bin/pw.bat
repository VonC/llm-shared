@echo off
setlocal EnableDelayedExpansion

REM Wrapper for tools\prompt_workflow.py. Uses LLM_SHARED_DIR (set by the
REM caller's senv, also when called from another repository) to locate the
REM venvs folder and the tool. Picks the most recent venv whose name ends with
REM "llm-shared" (newest first, /o-d), so the copilot-shared venv is skipped.
set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-d "%PYTHON_BASE%\python_3*llm-shared" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    echo ERROR: No python_3*llm-shared directory found in "%PYTHON_BASE%"
    exit /b 1
)

set "PATH=%PYTHON_BASE%\%LATEST_PYTHON%\Scripts;%PATH%"

REM When PW_PROFILE is set (see the pwi alias), run the tool under pyinstrument
REM to profile where the time goes; otherwise run it normally.
set "PW_CMD=python"
if defined PW_PROFILE set "PW_CMD=python -m pyinstrument"

%PW_CMD% "%LLM_SHARED_DIR%\tools\prompt_workflow.py" %*
