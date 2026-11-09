@echo off
REM Detect the calling shell state before disabling expansion for preparation.
if "!"=="" goto delayed_on
setlocal DisableDelayedExpansion
set "_LLM_PYTEST_DELAYED=off"
goto prepare
:delayed_on
setlocal DisableDelayedExpansion
set "_LLM_PYTEST_DELAYED=on"
:prepare
REM Use the project's already-selected Python, never activate another venv.
set "_LLM_PYTEST_TRANSFER="
set "_LLM_PYTEST_CODE_PAGE="
for /f "tokens=2 delims=:" %%C in ('chcp') do set "_LLM_PYTEST_CODE_PAGE=%%C"
if not defined _LLM_PYTEST_CODE_PAGE goto failed
REM Python exclusively creates the file and prints its path only after success.
for /f "delims=" %%F in ('python "%~dp0..\tools\pytest_plugin_shell.py" --project-root "%CD%\." --shared-root "%~dp0.." --code-page %_LLM_PYTEST_CODE_PAGE% --delayed-expansion %_LLM_PYTEST_DELAYED%') do set "_LLM_PYTEST_TRANSFER=%%F"
if not defined _LLM_PYTEST_TRANSFER goto failed
if not exist "%_LLM_PYTEST_TRANSFER%" goto failed
REM The caller's expansion scan also applies to the quoted transfer filename.
set "_LLM_PYTEST_APPLY=%_LLM_PYTEST_TRANSFER%"
if "%_LLM_PYTEST_DELAYED%"=="off" goto apply
if "%_LLM_PYTEST_TRANSFER:!=%"=="%_LLM_PYTEST_TRANSFER%" goto apply
set "_LLM_PYTEST_APPLY=%_LLM_PYTEST_APPLY:^=^^%"
set "_LLM_PYTEST_APPLY=%_LLM_PYTEST_APPLY:!=^!%"
:apply
REM FOR values are data: percent/quote/ampersand characters are not reparsed.
endlocal & (for /f "usebackq delims=" %%V in ("%_LLM_PYTEST_APPLY%") do set "%%V") & del /q "%_LLM_PYTEST_APPLY%" 2>nul
exit /b 0
:failed
if defined _LLM_PYTEST_TRANSFER del /q "%_LLM_PYTEST_TRANSFER%" 2>nul
endlocal & exit /b 4
