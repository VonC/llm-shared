@echo off
rem Publish only through the environment whose preparation just succeeded.
setlocal DisableDelayedExpansion
if "%~2"=="" exit /b 2
if not "%~2"=="0" exit /b %~2
if not defined VIRTUAL_ENV (
    >&2 echo Warning: release runtime identity not updated; no environment prepared.
    exit /b 0
)
if not exist "%VIRTUAL_ENV%\Scripts\python.exe" (
    >&2 echo Release runtime setup failed: prepared interpreter is missing.
    exit /b 2
)
"%VIRTUAL_ENV%\Scripts\python.exe" -I -X utf8 "%~1\tools\release_workflow\runtime_identity.py" "%~1" "0"
exit /b %ERRORLEVEL%
