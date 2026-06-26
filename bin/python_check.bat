@echo off


::  ===============================================
::  INITIAL SETUP
::  ===============================================
for %%i in ("%~dp0") do SET "check_dir=%%~fi"
set "check_dir=%check_dir:~0,-1%"

for %%i in ("%PRJ_DIR%") do set "LLM_SHARED_PRJ_DIR_NAME=%%~nxi"
if defined LLM_SHARED_PRJ_DIR_NAME set "NO_MORE_SENV_%LLM_SHARED_PRJ_DIR_NAME%="
call <NUL "%PRJ_DIR%\senv.bat"
set "LLM_SHARED_PRJ_DIR_NAME="

set "check_status=0"
set "ty_status=0"
set "pyright_status=0"
set "ruff_status=0"
set "radon_cc_status=0"
set "vulture_status=0"
set "big_file_status=0"
set "shellcheck_status=0"
set "enforce_eof_status=0"
set "failed_steps="
set "did_push="

::  ===============================================
::  CHECK PROJECT
::  ===============================================

%_info% "ty check '%PRJ_DIR%'"
pushd "%PRJ_DIR%"
set "did_push=1"
cd /d "%PRJ_DIR%"
ty check "%PRJ_DIR%"
set "ty_status=%ERRORLEVEL%"
if "%ty_status%"=="0" (
  %_ok% "Ty check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Ty check failed for project '%PRJ_DIR_NAME%' with status '%ty_status%'"
  call :record_failure ty %ty_status%
)

%_info% "pyright '%PRJ_DIR%'"
pyright
set "pyright_status=%ERRORLEVEL%"
if "%pyright_status%"=="0" (
  %_ok% "Pyright check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Pyright check failed for project '%PRJ_DIR_NAME%' with status '%pyright_status%'"
  call :record_failure pyright %pyright_status%
)

%_info% "ruff check '%PRJ_DIR%'"
ruff check "%PRJ_DIR%"
set "ruff_status=%ERRORLEVEL%"
if "%ruff_status%"=="0" (
  %_ok% "Ruff check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Ruff check failed for project '%PRJ_DIR_NAME%' with status '%ruff_status%'"
  call :record_failure ruff %ruff_status%
)

%_info% "radon cc --show-closures -a --total-average -s '%PRJ_DIR%\tools' '%PRJ_DIR%\tests'"
radon cc --show-closures -a --total-average -s "%PRJ_DIR%\tools" "%PRJ_DIR%\tests" > "%PRJ_DIR%\a.radon_cc_report.txt"
set "radon_cc_status=%ERRORLEVEL%"

REM Radon sometimes exits 0 even when it prints complexity alerts.
REM Treat a non-empty report file as a failure.
set "radon_cc_report=%PRJ_DIR%\a.radon_cc_report.txt"
set "radon_cc_report_size=0"
if exist "%radon_cc_report%" (
  for %%A in ("%radon_cc_report%") do set "radon_cc_report_size=%%~zA"
) else (
  set "radon_cc_report_size=0"
)

if not "%radon_cc_report_size%"=="0" (
  type "%radon_cc_report%"
  set "radon_cc_status=1"
)

if "%radon_cc_status%"=="0" (
  %_ok% "Radon Cyclomatic Complexity check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Radon Cyclomatic Complexity check failed for project '%PRJ_DIR_NAME%' with status '%radon_cc_status%'"
  call :record_failure radon_cc %radon_cc_status%
)

%_info% "vulture '%PRJ_DIR%\tools' whitelist.py"
vulture "%PRJ_DIR%\tools" whitelist.py
set "vulture_status=%ERRORLEVEL%"
if "%vulture_status%"=="0" (
  %_ok% "Vulture check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Vulture check failed for project '%PRJ_DIR_NAME%' with status '%vulture_status%'"
  call :record_failure vulture %vulture_status%
)

if defined PYTHON_BIG_FILE_LINE_LIMIT (
  set "python_big_file_line_limit=%PYTHON_BIG_FILE_LINE_LIMIT%"
  set "python_big_file_msg= (from PYTHON_BIG_FILE_LINE_LIMIT=%PYTHON_BIG_FILE_LINE_LIMIT%)"
) else (
  set "python_big_file_line_limit=700"
  set "python_big_file_msg= (default: 700 lines, set PYTHON_BIG_FILE_LINE_LIMIT to override)"
)
%_info% "Check for files too big in '%PRJ_DIR%\tools' and '%PRJ_DIR%\tests' %python_big_file_msg%"
REM Python instead of find/xargs/wc/awk: on a PATH where System32 precedes
REM Git usr\bin, `find` is the Windows text-search tool, the pipeline scans
REM nothing and the check passes vacuously ("Access denied - TOOLS").
python -c "import pathlib,sys; limit=int(sys.argv[1]); rows=[(sum(1 for _ in p.open(encoding='utf-8', errors='ignore')), p) for root in sys.argv[2:] for p in pathlib.Path(root).rglob('*.py')]; bad=[(n,p) for n,p in rows if n>limit]; [print(f'{n:6} {p}') for n,p in bad]; sys.exit(1 if bad else 0)" %python_big_file_line_limit% tools tests
set "big_file_status=%ERRORLEVEL%"
if "%big_file_status%"=="0" (
  %_ok% "No big files found in project '%PRJ_DIR_NAME%'"
) else (
  %_error% "Big files found in project '%PRJ_DIR_NAME%'"
  call :record_failure big_file %big_file_status%
)

set "shellcheck_exe=%PRGS%\shellchecks\current\shellcheck-stable.exe"
%_info% "shellcheck"
if exist "%shellcheck_exe%" (
  echo "%shellcheck_exe%" -e SC1090,SC1091 no script yet
  call set "shellcheck_status=%%ERRORLEVEL%%"
) else (
  set "shellcheck_status=1"
  %_error% "ShellCheck executable not found at '%shellcheck_exe%'"
)
if "%shellcheck_status%"=="0" (
  %_ok% "ShellCheck passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "ShellCheck failed for project '%PRJ_DIR_NAME%' with status '%shellcheck_status%'"
  call :record_failure shellcheck %shellcheck_status%
)

%_info% "call eeof"
python "%PRJ_DIR%\tools\enforce_eof.py"
set "enforce_eof_status=%ERRORLEVEL%"
if "%enforce_eof_status%"=="0" (
  %_ok% "EOF check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "EOF check failed for project '%PRJ_DIR_NAME%' with status '%enforce_eof_status%'"
  call :record_failure eof %enforce_eof_status%
)

:finalize
%_pre% "-----------------------------------------"

if defined failed_steps (
  %_error% "Failed steps for project '%PRJ_DIR_NAME%': %failed_steps%"
) else (
  %_ok% "All checks passed for project '%PRJ_DIR_NAME%'."
)

if defined did_push popd

if defined failed_steps %_error% "Check failed for project '%PRJ_DIR_NAME%' with status '%check_status%'."

REM Preserve the exit code across the cleanup: :check_unset clears
REM check_status, so stash it first; the last line clears the stash and
REM exits with it in one go (cmd expands the line before running it).
set "check_exit=%check_status%"
call :check_unset
if "%check_exit%"=="" set "check_exit=0"
set "check_exit=" & exit /b %check_exit%
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

::##################################################
::  CLEANUP
::##################################################

:check_unset
set "cmd="
call "%PRJ_DIR%\senv.bat" unset
set "big_file_status="
set "check_status="
set "check_dir="
set "did_push="
set "enforce_eof_status="
set "failed_steps="
set "python_big_file_line_limit="
set "python_big_file_msg="
set "pyright_status="
set "radon_cc_report="
set "radon_cc_report_size="
set "ruff_status="
set "radon_cc_status="
set "shellcheck_exe="
set "shellcheck_status="
set "ty_status="
set "vulture_status="
goto:eof

::##################################################
::  ECHOS STACK (called by echos.bat)
::##################################################

:call_echos_stack
if not defined ECHOS_STACK ( set "CURRENT_SCRIPT=%~nx0" & goto:eof ) else ( call "%PRJ_DIR%\tools\batcolors\echos.bat" :stack %~nx0 )
goto:eof
