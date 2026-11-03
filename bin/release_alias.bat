@echo off
setlocal DisableDelayedExpansion
REM Self-locate without inherited tooling variables or a directory change.
for %%R in ("%~dp0..") do set "_release_root=%%~fR"
set "_release_status=2"
set "_release_error=missing or unreadable runtime record"
set "_release_cp="
for /f "delims=" %%C in ('"%SystemRoot%\System32\chcp.com" ^<nul 2^>nul') do set "_release_cp=%%C"
:codepage_tail
set "_release_tail="
for /f "tokens=1,* delims=:" %%A in ("%_release_cp%") do set "_release_tail=%%B"
if not defined _release_tail goto codepage_digits
set "_release_cp=%_release_tail%"
goto codepage_tail
:codepage_digits
for /f "tokens=*" %%C in ("%_release_cp%") do set "_release_cp=%%C"
REM Retain leading digits even when localized output ends with punctuation.
set "_release_digits="
:codepage_next
if not defined _release_cp goto codepage_done
for %%D in (0 1 2 3 4 5 6 7 8 9) do if "%_release_cp:~0,1%"=="%%D" goto codepage_digit
:codepage_done
set "_release_cp=%_release_digits%"
goto codepage_ready
:codepage_digit
set "_release_digits=%_release_digits%%_release_cp:~0,1%"
set "_release_cp=%_release_cp:~1%"
goto codepage_next
:codepage_ready
REM An existing UTF-8 console needs no redundant codepage child process.
if not "%_release_cp%"=="65001" "%SystemRoot%\System32\chcp.com" 65001 <nul >nul 2>&1
REM Read the setup record as data with delayed expansion disabled.
set "_release_version="
set "_release_environment="
set "_release_extra="
if not exist "%_release_root%\venvs\release-runtime.v1.txt" goto runtime_error
for /f "usebackq delims=" %%L in ("%_release_root%\venvs\release-runtime.v1.txt") do (
    if not defined _release_version (
        set "_release_version=%%L"
    ) else if not defined _release_environment (
        set "_release_environment=%%L"
    ) else (
        set "_release_extra=%%L"
    )
)
set "_release_error=invalid runtime record version or length"
if defined _release_extra goto runtime_error
REM Expand record data after cmd parses operators; never reparse it in a pipe.
setlocal EnableDelayedExpansion
if not "!_release_version!"=="1" goto invalid_version
endlocal
set "_release_error=invalid runtime environment path"
setlocal EnableDelayedExpansion
if not "!_release_environment:~0,6!"=="venvs/" goto invalid_environment
set "_release_safe=!_release_environment:"=!"
set "_release_safe=!_release_safe:\=!"
set "_release_safe=!_release_safe::=!"
set "_release_safe=!_release_safe:..=!"
if not "!_release_safe!"=="!_release_environment!" goto invalid_environment
endlocal
set "_release_error=missing designated runtime interpreter"
if not exist "%_release_root%\%_release_environment%\Scripts\python.exe" goto runtime_error
"%_release_root%\%_release_environment%\Scripts\python.exe" -I -X utf8 "%_release_root%\tools\release_workflow\bootstrap.py" --entry-kind alias-batch -- %*
set "_release_status=%ERRORLEVEL%"
if "%_release_status%"=="0" goto cleanup
if "%_release_status%"=="1" goto cleanup
if "%_release_status%"=="2" goto cleanup
>&2 echo Release operation exited with native status %_release_status%; returning 1.
set "_release_status=1"
goto cleanup
:invalid_version
:invalid_environment
endlocal
:runtime_error
>&2 echo Release readiness failed: %_release_error%. Run this checkout's setup.
:cleanup
if defined _release_cp "%SystemRoot%\System32\chcp.com" %_release_cp% >nul 2>&1
endlocal & exit /b %_release_status%
