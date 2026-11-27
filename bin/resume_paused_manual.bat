@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "PYTHON_BASE=%~dp0..\venvs"
set "LATEST_PYTHON="
for /f "delims=" %%d in ('dir /b /ad /o-d "%PYTHON_BASE%\python_3*llm-shared*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)
if not defined LATEST_PYTHON (
    echo ERROR: No llm-shared Python environment in "%PYTHON_BASE%"
    exit /b 1
)
set "PYTHONPATH=%~dp0.."
"%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe" -P -m tools.resume_paused_manual %*
exit /b %ERRORLEVEL%
