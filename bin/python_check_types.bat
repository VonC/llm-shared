@echo off


::  ===============================================
::  INITIAL SETUP
::  ===============================================
for %%i in ("%~dp0") do SET "check_dir=%%~fi"
set "check_dir=%check_dir:~0,-1%"

call <NUL "%PRJ_DIR%\senv.bat"

set "check_status=0"
set "pyright_status=0"
set "ruff_status=0"
set "ty_status=0"
set "pts_status=0"
set "failed_steps="
set "test_args="
set "pts_note="
set "did_push="

if "%~1"=="" (
  set "check_status=2"
  set "failed_steps=arguments(2)"
  %_error% "No targets provided to '%~nx0'."
  %_info% "Usage: %~nx0 <path-or-flag> [more targets...]"
  goto:finalize
)

pushd "%PRJ_DIR%"
set "did_push=1"
cd /d "%PRJ_DIR%"

::  ===============================================
::  CHECK TARGETS
::  ===============================================

%_info% "pyright %*"
pyright %*
set "pyright_status=%ERRORLEVEL%"
if "%pyright_status%"=="0" (
  %_ok% "Pyright check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Pyright check failed for project '%PRJ_DIR_NAME%' with status '%pyright_status%'"
  call :record_failure pyright %pyright_status%
)

%_info% "ruff check %*"
ruff check %*
set "ruff_status=%ERRORLEVEL%"
if "%ruff_status%"=="0" (
  %_ok% "Ruff check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Ruff check failed for project '%PRJ_DIR_NAME%' with status '%ruff_status%'"
  call :record_failure ruff %ruff_status%
)

%_info% "ty check %*"
ty check %*
set "ty_status=%ERRORLEVEL%"
if "%ty_status%"=="0" (
  %_ok% "Ty check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Ty check failed for project '%PRJ_DIR_NAME%' with status '%ty_status%'"
  call :record_failure ty %ty_status%
)

if "%pyright_status%"=="0" if "%ruff_status%"=="0" if "%ty_status%"=="0" (
  call :collect_test_args %*
  if defined test_args (
    call :run_pts
  ) else (
    set "pts_note= PTS skipped (no '/tests/' targets)."
    %_info% "No '/tests/' targets provided; pts skipped."
  )
)

:finalize
%_pre% "-----------------------------------------"

if defined failed_steps (
  %_error% "Failed steps for project '%PRJ_DIR_NAME%': %failed_steps%"
) else (
  %_ok% "All requested checks passed for project '%PRJ_DIR_NAME%'.%pts_note%"
)

if defined did_push popd

call :check_unset

if defined failed_steps (
  %_error% "Check failed for project '%PRJ_DIR_NAME%'. Failed steps: %failed_steps%"
  exit /b %check_status%
)

exit /b 0
goto:eof

::##################################################
::  HELPERS
::##################################################

:record_failure
if "%~2"=="0" goto:eof
if "%check_status%"=="0" set "check_status=%~2"
if defined failed_steps (
  set "failed_steps=%failed_steps%, %~1(%~2)"
) else (
  set "failed_steps=%~1(%~2)"
)
goto:eof

:collect_test_args
set "test_args="
:collect_test_args_loop
if "%~1"=="" goto:eof
set "arg=%~1"
call set "normalized_arg=%%arg:\=/%%"
echo(%normalized_arg%| findstr /I /C:"/tests/" >NUL 2>&1
if not errorlevel 1 (
  if defined test_args (
    call set "test_args=%%test_args%% "%arg%""
  ) else (
    set "test_args="%arg%""
  )
)
shift
goto:collect_test_args_loop

:run_pts
%_info% "pytest --no-header --no-cov -rxX %test_args%"
pytest --no-header --no-cov -rxX %test_args%
set "pts_status=%ERRORLEVEL%"
if "%pts_status%"=="0" (
  set "pts_note= PTS passed for matching test targets."
  %_ok% "PTS passed for project '%PRJ_DIR_NAME%' with test targets:%test_args%"
) else (
  %_error% "PTS failed for project '%PRJ_DIR_NAME%' with status '%pts_status%' and test targets:%test_args%"
  call :record_failure pts %pts_status%
)
goto:eof

::##################################################
::  CLEANUP
::##################################################

:check_unset
set "cmd="
call "%PRJ_DIR%\senv.bat" unset
set "arg="
set "check_dir="
set "check_status="
set "did_push="
set "failed_steps="
set "normalized_arg="
set "pts_note="
set "pts_status="
set "pyright_status="
set "ruff_status="
set "test_args="
set "ty_status="
goto:eof

::##################################################
::  ECHOS STACK (called by echos.bat)
::##################################################

:call_echos_stack
if not defined ECHOS_STACK ( set "CURRENT_SCRIPT=%~nx0" & goto:eof ) else ( call "%PRJ_DIR%\tools\batcolors\echos.bat" :stack %~nx0 )
goto:eof
