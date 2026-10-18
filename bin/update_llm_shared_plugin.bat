@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM Self-locate the llm-shared folder from this launcher's own path.
if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."

set "PLUGIN_ROOT=%LLM_SHARED_DIR%\.agents\llm-shared"
REM llm-shared validates, versions and locates its own package: Codex no longer
REM installs the plugin-creator helper scripts under .codex\skills\.system.
set "PACKAGE_TOOL=%LLM_SHARED_DIR%\tools\codex_plugin_package.py"
set "REDIRECT_VALIDATOR=%LLM_SHARED_DIR%\tools\codex_plugin_redirects.py"
set "MARKETPLACE_FILE=%USERPROFILE%\.agents\plugins\marketplace.json"

if not exist "%PLUGIN_ROOT%\.codex-plugin\plugin.json" (
    echo ERROR: llm-shared plugin manifest not found under "%PLUGIN_ROOT%".
    exit /b 1
)

if not exist "%PACKAGE_TOOL%" (
    echo ERROR: llm-shared plugin package tool not found at "%PACKAGE_TOOL%".
    exit /b 1
)

if not exist "%REDIRECT_VALIDATOR%" (
    echo ERROR: llm-shared redirect validator not found at "%REDIRECT_VALIDATOR%".
    exit /b 1
)

REM Both tools use the standard library only: run them with the llm-shared
REM Python, as the other bin launchers do, never the active project's Python.
set "PYTHON_BASE=%LLM_SHARED_DIR%\venvs"
set "LATEST_PYTHON="
for /f "delims=" %%d in ('dir /b /ad /o-n "%PYTHON_BASE%\python_3*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)
if not defined LATEST_PYTHON (
    echo ERROR: No python_3* directory found in "%PYTHON_BASE%".
    exit /b 1
)
set "PATH=%PYTHON_BASE%\%LATEST_PYTHON%\Scripts;%PATH%"

set "MARKETPLACE_NAME="
for /f "usebackq delims=" %%m in (`python "%PACKAGE_TOOL%" marketplace-name "%MARKETPLACE_FILE%"`) do set "MARKETPLACE_NAME=%%m"
if not defined MARKETPLACE_NAME (
    echo ERROR: Could not read the personal Codex marketplace name from "%MARKETPLACE_FILE%".
    exit /b 1
)
set "CACHE_BASE=%USERPROFILE%\.codex\plugins\cache\%MARKETPLACE_NAME%\llm-shared"

set "CODEX_EXE=%USERPROFILE%\.codex\packages\standalone\current\bin\codex.exe"
if not exist "%CODEX_EXE%" (
    set "CODEX_EXE="
    for %%e in (codex.exe) do set "CODEX_EXE=%%~$PATH:e"
)
if not defined CODEX_EXE (
    echo ERROR: codex.exe was not found in the standalone package or on PATH.
    exit /b 1
)

python "%PACKAGE_TOOL%" validate "%PLUGIN_ROOT%"
if errorlevel 1 exit /b 1

python "%REDIRECT_VALIDATOR%" "%PLUGIN_ROOT%" "%LLM_SHARED_DIR%" "%CACHE_BASE%"
if errorlevel 1 exit /b 1

python "%PACKAGE_TOOL%" bump-version "%PLUGIN_ROOT%"
if errorlevel 1 exit /b 1

"%CODEX_EXE%" plugin add llm-shared@%MARKETPLACE_NAME%
if errorlevel 1 exit /b 1

python "%REDIRECT_VALIDATOR%" "%PLUGIN_ROOT%" "%LLM_SHARED_DIR%" "%CACHE_BASE%" --installed
if errorlevel 1 exit /b 1

"%CODEX_EXE%" plugin list | findstr /I /C:"llm-shared@%MARKETPLACE_NAME%"
if errorlevel 1 (
    echo ERROR: llm-shared@%MARKETPLACE_NAME% was not found in the installed plugin list.
    exit /b 1
)

echo Start a new Codex thread to load the updated plugin.
