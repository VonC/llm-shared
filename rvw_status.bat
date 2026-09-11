@echo off
setlocal

REM Run review status, with at most one bounded safe artifact migration, from the newest llm-shared Python.
set "REVIEW_STATUS_ROOT=%~dp0"
set "REVIEW_STATUS_PYTHON_BASE=%REVIEW_STATUS_ROOT%venvs"
set "REVIEW_STATUS_LATEST="

for /f "delims=" %%d in ('dir /b /ad /o-d "%REVIEW_STATUS_PYTHON_BASE%\python_3*llm-shared*" 2^>nul') do (
    if not defined REVIEW_STATUS_LATEST set "REVIEW_STATUS_LATEST=%%d"
)

if not defined REVIEW_STATUS_LATEST (
    echo rvw_status: no llm-shared Python environment found 1>&2
    exit /b 2
)

set "REVIEW_STATUS_PYTHON=%REVIEW_STATUS_PYTHON_BASE%\%REVIEW_STATUS_LATEST%\Scripts\python.exe"
REM Keep the caller directory so default root discovery inspects its repository.
REM -P is what makes that safe: without it python -m prepends the caller's
REM directory to sys.path ahead of PYTHONPATH, so a project carrying its own
REM tools package (tools\__init__.py) shadows the shared package and the run
REM dies on "No module named tools.review_status_cli". -P drops that entry
REM only; the process working directory is untouched, so root discovery still
REM sees the caller.
if defined PYTHONPATH (
    set "PYTHONPATH=%REVIEW_STATUS_ROOT%;%PYTHONPATH%"
) else (
    set "PYTHONPATH=%REVIEW_STATUS_ROOT%"
)
"%REVIEW_STATUS_PYTHON%" -P -m tools.review_status_cli %*
set "REVIEW_STATUS_STATUS=%ERRORLEVEL%"
exit /b %REVIEW_STATUS_STATUS%
