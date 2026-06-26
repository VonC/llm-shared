@echo off
setlocal EnableDelayedExpansion

if not defined LLM_SHARED_DIR for %%i in ("%~dp0..") do set "LLM_SHARED_DIR=%%~fi"

REM Project environment first: open_questions_md writes project-root files and
REM must see the consuming project's Python environment when the project owns
REM helper dependencies. senv.bat can be skipped by a stale project-specific
REM NO_MORE_SENV guard inherited by a harness, so clear that guard before
REM calling it.
if not defined PRJ_DIR set "PRJ_DIR=%CD%"
for %%i in ("%PRJ_DIR%") do set "LLM_SHARED_PRJ_DIR_NAME=%%~nxi"
if defined LLM_SHARED_PRJ_DIR_NAME set "NO_MORE_SENV_!LLM_SHARED_PRJ_DIR_NAME!="
set "OQM_SENV_LOG=%PRJ_DIR%\a.oqm.senv.log"
if exist "%PRJ_DIR%\senv.bat" call <NUL "%PRJ_DIR%\senv.bat" > "%OQM_SENV_LOG%" 2>&1
set "OQM_SENV_EXIT=%ERRORLEVEL%"
set "LLM_SHARED_PRJ_DIR_NAME="

if not "%OQM_SENV_EXIT%"=="0" (
    if exist "%OQM_SENV_LOG%" (type "%OQM_SENV_LOG%" & del "%OQM_SENV_LOG%" 2>nul)
    exit /b %OQM_SENV_EXIT%
)

set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="

for /f "delims=" %%d in ('dir /b /ad /o-n "%PYTHON_BASE%\python_3*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)

if not defined LATEST_PYTHON (
    if exist "%OQM_SENV_LOG%" (type "%OQM_SENV_LOG%" & del "%OQM_SENV_LOG%" 2>nul)
    echo ERROR: No python_3* directory found in "%PYTHON_BASE%"
    exit /b 1
)

"%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe" "%~dp0..\tools\open_questions_md.py" %*
set "OQM_EXIT=%ERRORLEVEL%"
if exist "%OQM_SENV_LOG%" del "%OQM_SENV_LOG%" 2>nul
exit /b %OQM_EXIT%
