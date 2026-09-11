@echo off
setlocal

set "MARKDOWN_CHECK_ROOT=%~dp0"
set "MARKDOWN_CHECK_PYTHON_BASE=%MARKDOWN_CHECK_ROOT%venvs"
set "MARKDOWN_CHECK_LATEST="

for /f "delims=" %%d in ('dir /b /ad /o-d "%MARKDOWN_CHECK_PYTHON_BASE%\python_3*llm-shared*" 2^>nul') do (
    if not defined MARKDOWN_CHECK_LATEST set "MARKDOWN_CHECK_LATEST=%%d"
)

if not defined MARKDOWN_CHECK_LATEST (
    echo markdown-check: no llm-shared Python environment found 1>&2
    exit /b 1
)

set "MARKDOWN_CHECK_PYTHON=%MARKDOWN_CHECK_PYTHON_BASE%\%MARKDOWN_CHECK_LATEST%\Scripts\python.exe"
pushd "%MARKDOWN_CHECK_ROOT%" >nul
"%MARKDOWN_CHECK_PYTHON%" -m tools.markdown_check.cli %*
set "MARKDOWN_CHECK_STATUS=%ERRORLEVEL%"
popd
exit /b %MARKDOWN_CHECK_STATUS%
