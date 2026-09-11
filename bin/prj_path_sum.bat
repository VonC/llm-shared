@echo off
setlocal EnableDelayedExpansion

REM ******************************************************************
REM Script Name:  prj_path_sum.bat
REM Description:  Decide whether a project senv.bat can skip its PATH work.
REM
REM A project senv.bat spends most of its wall clock in switchver/switchpy
REM and the uv calls behind them, yet all that work only ever produces one
REM observable result in the console: %PATH%. When %PATH% already holds that
REM result, redoing it is pure cost. `ghog.bat` is the case that motivated
REM this: it clears NO_MORE_SENV on purpose so senv can repair a stale PATH,
REM and then pays the full price even when the PATH needs no repair at all.
REM
REM So this script records a fingerprint of %PATH% in %PRJ_DIR%\a.prj.path.sum
REM and compares against it on the next run. The file is in the a.* family
REM every project ignores, so the fingerprint stays local to one machine.
REM
REM Usage:
REM   call "%LLM_SHARED_DIR%\bin\prj_path_sum.bat" check
REM       Sets PRJ_PATH_SUM_MATCH=true when %PATH% still matches the recorded
REM       fingerprint. Place the call right after the NO_MORE_SENV guard, and
REM       skip every PATH assignment and switchxxx call when it is set.
REM
REM   call "%LLM_SHARED_DIR%\bin\prj_path_sum.bat" update
REM       Records the current %PATH% fingerprint, overwriting any previous
REM       one. Place the call at the very end of senv.bat, once PATH is final.
REM
REM Return Value:
REM   0 - check: %PATH% matches, the PATH work can be skipped
REM       update: the fingerprint was written
REM   1 - check: no fingerprint recorded yet, or %PATH% has changed
REM   2 - cannot decide (no PRJ_DIR, no sha256sum.exe, unwritable file).
REM       Always treat this as "proceed": a skipped decision must never
REM       become a skipped activation.
REM ******************************************************************

set "PRJ_PATH_SUM_MODE=%~1"
if not defined PRJ_PATH_SUM_MODE set "PRJ_PATH_SUM_MODE=check"

REM Without a project root there is no file to compare against.
if not defined PRJ_DIR (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 2
)
set "PRJ_PATH_SUM_FILE=%PRJ_DIR%\a.prj.path.sum"

REM A matching PATH is not on its own enough to skip the activation. switchpy
REM also exports VIRTUAL_ENV and UV_PROJECT_ENVIRONMENT, and a console can
REM easily carry the right PATH without them: ghog.bat clears the guard in a
REM process that inherited PATH, a user edits PATH by hand, or another
REM project's venv is active while this project's PATH entries are still
REM present. Skipping switchpy there would leave uv and the venv tooling
REM pointed at nothing, or at the wrong tree.
REM
REM So both variables must exist and must sit under PRJ_DIR. Anything else
REM answers 1, which sends the caller through the full activation. These
REM checks run before the hashing so a wrong venv costs no subprocess.
if /i not "%PRJ_PATH_SUM_MODE%"=="check" goto:prj_path_sum_venv_done

REM Both variables are switchpy's own output, so they are only evidence in a
REM project whose senv.bat actually calls it. Demanding them from a project
REM that does not would answer 1 on every run, and the skip would never once
REM apply. The line has to be a command: senv.bat files mention switchpy in
REM comments, and a REM never starts with `call switchpy` or `switchpy`.
if not exist "%PRJ_DIR%\senv.bat" goto:prj_path_sum_venv_done
findstr /i /r /c:"^ *call  *switchpy" /c:"^ *switchpy" "%PRJ_DIR%\senv.bat" >NUL 2>&1
if errorlevel 1 goto:prj_path_sum_venv_done

if not defined VIRTUAL_ENV (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 1
)
if not defined UV_PROJECT_ENVIRONMENT (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 1
)

REM Measure PRJ_DIR by chopping it one character at a time: batch has no
REM string length, and a prefix test needs one.
set "PRJ_PATH_SUM_TAIL=%PRJ_DIR%"
set "PRJ_PATH_SUM_LEN=0"
:prj_path_sum_len
if defined PRJ_PATH_SUM_TAIL (
    set "PRJ_PATH_SUM_TAIL=!PRJ_PATH_SUM_TAIL:~1!"
    set /a PRJ_PATH_SUM_LEN+=1
    goto:prj_path_sum_len
)

REM /i because the drive letter and the user folder reach a console with
REM whatever casing it was entered with.
if /i not "!VIRTUAL_ENV:~0,%PRJ_PATH_SUM_LEN%!"=="%PRJ_DIR%" (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 1
)
if /i not "!UV_PROJECT_ENVIRONMENT:~0,%PRJ_PATH_SUM_LEN%!"=="%PRJ_DIR%" (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 1
)
:prj_path_sum_venv_done

REM sha256sum.exe ships with Git for Windows. senv.bat has not set GIT_HOME
REM yet at the point this runs, so look on PATH first, then at the usual Git
REM location. Its absence is not an error: the caller simply proceeds.
set "PRJ_PATH_SUM_EXE="
for %%i in (sha256sum.exe) do if not defined PRJ_PATH_SUM_EXE set "PRJ_PATH_SUM_EXE=%%~$PATH:i"
if not defined PRJ_PATH_SUM_EXE if defined GIT_HOME (
    if exist "%GIT_HOME%\usr\bin\sha256sum.exe" set "PRJ_PATH_SUM_EXE=%GIT_HOME%\usr\bin\sha256sum.exe"
)
if not defined PRJ_PATH_SUM_EXE if defined PRGS (
    if exist "%PRGS%\gits\current\usr\bin\sha256sum.exe" set "PRJ_PATH_SUM_EXE=%PRGS%\gits\current\usr\bin\sha256sum.exe"
)
if not defined PRJ_PATH_SUM_EXE (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 2
)

REM Hash the live %PATH% through a file, never a pipe. Piping would put the
REM value on a command line that `for /f` hands to a child cmd, and that child
REM re-parses it: one & inside a directory name, as in "C:\A & B", splits the
REM command and the loop captures a fragment of PATH instead of a hash.
REM Redirecting `echo(!PATH!` stays in this process, where delayed expansion
REM does protect the value.
REM
REM The hashing runs from inside PRJ_DIR so the operand is a bare file name.
REM GNU coreutils escapes an operand containing a backslash and marks the line
REM with a leading backslash, which would otherwise be stored as part of the
REM hash. The outer ^" ^" pair is needed too: a command that merely starts
REM with a quoted path loses its quotes to cmd /c.
set "PRJ_PATH_SUM_NOW="
pushd "%PRJ_DIR%"
if errorlevel 1 (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 2
)
> "a.prj.path.sum.in" echo(!PATH!
for /f "usebackq tokens=1" %%h in (`^""!PRJ_PATH_SUM_EXE!" a.prj.path.sum.in 2^>NUL^"`) do (
    if not defined PRJ_PATH_SUM_NOW set "PRJ_PATH_SUM_NOW=%%h"
)
del /q "a.prj.path.sum.in" 2>NUL
popd
REM A hash is 64 hex characters. Anything shorter means the tool failed or
REM its output was not what we expect, and a bad value must not be recorded
REM or compared: it would either skip an activation or force one forever.
if not defined PRJ_PATH_SUM_NOW (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 2
)
if not "!PRJ_PATH_SUM_NOW:~63,1!"=="" if "!PRJ_PATH_SUM_NOW:~64,1!"=="" goto:prj_path_sum_hashed
endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 2

:prj_path_sum_hashed

if /i "%PRJ_PATH_SUM_MODE%"=="update" goto:prj_path_sum_update
if /i "%PRJ_PATH_SUM_MODE%"=="check" goto:prj_path_sum_check
endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 2

:prj_path_sum_check
REM No file yet means a first run on this machine: proceed and let the update
REM call record the result.
if not exist "%PRJ_PATH_SUM_FILE%" (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 1
)
set "PRJ_PATH_SUM_WAS="
set /p PRJ_PATH_SUM_WAS=<"%PRJ_PATH_SUM_FILE%"
REM An empty or truncated file reads as "changed", never as a match: a bad
REM read must not skip the activation.
if not defined PRJ_PATH_SUM_WAS (
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 1
)
for /f "tokens=1" %%w in ("!PRJ_PATH_SUM_WAS!") do set "PRJ_PATH_SUM_WAS=%%w"
if /i "!PRJ_PATH_SUM_WAS!"=="!PRJ_PATH_SUM_NOW!" (
    endlocal & set "PRJ_PATH_SUM_MATCH=true" & exit /b 0
)
endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 1

:prj_path_sum_update
REM Write through a side file so an interrupted write cannot leave a half
REM fingerprint that would read as a mismatch forever.
> "%PRJ_PATH_SUM_FILE%.tmp" echo !PRJ_PATH_SUM_NOW!
if errorlevel 1 (
    del /q "%PRJ_PATH_SUM_FILE%.tmp" 2>NUL
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 2
)
move /y "%PRJ_PATH_SUM_FILE%.tmp" "%PRJ_PATH_SUM_FILE%" >NUL
if errorlevel 1 (
    del /q "%PRJ_PATH_SUM_FILE%.tmp" 2>NUL
    endlocal & set "PRJ_PATH_SUM_MATCH=" & exit /b 2
)
endlocal & set "PRJ_PATH_SUM_MATCH=true" & exit /b 0
