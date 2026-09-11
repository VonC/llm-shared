@echo off
setlocal

REM Run the read-only commit-plan checker from the newest llm-shared Python.
set "COMMIT_PLAN_CHECK_ROOT=%~dp0"
set "COMMIT_PLAN_CHECK_PYTHON_BASE=%COMMIT_PLAN_CHECK_ROOT%venvs"
set "COMMIT_PLAN_CHECK_LATEST="

for /f "delims=" %%d in ('dir /b /ad /o-d "%COMMIT_PLAN_CHECK_PYTHON_BASE%\python_3*llm-shared*" 2^>nul') do (
    if not defined COMMIT_PLAN_CHECK_LATEST set "COMMIT_PLAN_CHECK_LATEST=%%d"
)

if not defined COMMIT_PLAN_CHECK_LATEST (
    echo commit-plan-check: no llm-shared Python environment found 1>&2
    exit /b 2
)

set "COMMIT_PLAN_CHECK_PYTHON=%COMMIT_PLAN_CHECK_PYTHON_BASE%\%COMMIT_PLAN_CHECK_LATEST%\Scripts\python.exe"
REM Keep the caller's directory so default root discovery checks its repository.
REM -P is what makes that safe: without it python -m prepends the caller's
REM directory to sys.path ahead of PYTHONPATH, so a project carrying its own
REM tools package - a tools\__init__.py, which eye-focus has - shadows the one
REM below, and the run dies on "No module named tools.commit_plan_check" as if
REM the checker were missing. -P drops that entry only; the process working
REM directory is untouched, so root discovery still sees the caller.
if defined PYTHONPATH (
    set "PYTHONPATH=%COMMIT_PLAN_CHECK_ROOT%;%PYTHONPATH%"
) else (
    set "PYTHONPATH=%COMMIT_PLAN_CHECK_ROOT%"
)
"%COMMIT_PLAN_CHECK_PYTHON%" -P -m tools.commit_plan_check %*
set "COMMIT_PLAN_CHECK_STATUS=%ERRORLEVEL%"
exit /b %COMMIT_PLAN_CHECK_STATUS%
