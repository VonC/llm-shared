@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM Read-only question scanner: use llm-shared Python without project setup.
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
"%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe" "%LLM_SHARED_DIR%\tools\question_decisions.py" %*
exit /b %ERRORLEVEL%
