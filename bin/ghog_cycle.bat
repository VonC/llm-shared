@echo off
setlocal EnableDelayedExpansion

REM One senv.bat activation for a whole ghog cycle.
REM
REM ghog.bat activates the project environment per invocation, so a cycle made
REM of several commands -- `ghog day` then `ghog timings`, say -- paid for the
REM activation once per command. senv.bat is idempotent through its
REM NO_MORE_SENV_<project> guard, but ghog.bat deliberately clears that guard
REM because a harness can inherit it with a stale PATH, so the guard alone
REM cannot collapse the repeats.
REM
REM This wrapper does the clear-and-activate once, in THIS process, then sets
REM GHOG_SENV_READY so every ghog.bat it calls trusts the prepared environment
REM and skips its own activation. Each ghog runs in this process's environment,
REM so PATH and VIRTUAL_ENV are the ones senv just established.
REM
REM Usage, with each argument one ghog subcommand line:
REM   ghog_cycle.bat day
REM   ghog_cycle.bat day timings
REM   ghog_cycle.bat check "affected --no-cov" full
REM
REM With no argument it runs the default cycle: one ghog day walk, alone.
REM The walk follows the level rule (--full, else GHOG_FULL, else none), so
REM GHOG_FULL=speed already adds the timing pass inside the walk in a
REM parallel project; an explicit sequence such as "day timings" still runs
REM each command as given.
REM The exit code is the first non-zero of the sequence, so a failing phase
REM still reports its own contract code and the later commands are skipped.

if not defined PRJ_DIR set "PRJ_DIR=%CD%"
REM The parked activation lands in the project's artifact home, never at the
REM project root: artifact_home.bat prepares it and sets ARTIFACT_HOME.
call "%~dp0artifact_home.bat" "%PRJ_DIR%"
set "GHOG_CYCLE_SENV_LOG=%ARTIFACT_HOME%\a.ghog.senv.log"

for %%i in ("%PRJ_DIR%") do set "LLM_SHARED_PRJ_DIR_NAME=%%~nxi"
if defined LLM_SHARED_PRJ_DIR_NAME set "NO_MORE_SENV_!LLM_SHARED_PRJ_DIR_NAME!="
if exist "%PRJ_DIR%\senv.bat" (
    if defined GHOG_SENV_LIVE (
        call <NUL "%PRJ_DIR%\senv.bat" 2>&1
    ) else (
        call <NUL "%PRJ_DIR%\senv.bat" > "%GHOG_CYCLE_SENV_LOG%" 2>&1
    )
)
set "LLM_SHARED_PRJ_DIR_NAME="

REM Replay the parked activation once, the way cli.py replays its own copy, so
REM a sandbox block or a missing venv stays visible instead of dying silently.
if exist "%GHOG_CYCLE_SENV_LOG%" (
    type "%GHOG_CYCLE_SENV_LOG%"
    del "%GHOG_CYCLE_SENV_LOG%" 2>nul
)
set "GHOG_CYCLE_SENV_LOG="

set "GHOG_SENV_READY=1"
set "CYCLE_EXIT=0"

if "%~1"=="" (
    call :run_one day
    goto :done
)

:next_argument
if "%~1"=="" goto :done
call :run_one %~1
if !CYCLE_EXIT! neq 0 goto :done
shift
goto :next_argument

:run_one
echo.
echo ghog_cycle: %*
call "%~dp0ghog.bat" %*
if !ERRORLEVEL! neq 0 set "CYCLE_EXIT=!ERRORLEVEL!"
goto :eof

:done
set "GHOG_SENV_READY="
exit /b %CYCLE_EXIT%
