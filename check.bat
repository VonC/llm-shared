@echo off


::  ===============================================
::  INITIAL SETUP
::  ===============================================
for %%i in ("%~dp0") do SET "check_dir=%%~fi"
set "check_dir=%check_dir:~0,-1%"

call <NUL "%check_dir%\senv.bat"
REM restore echos macros if unset
call "%PRJ_DIR%\tools\batcolors\echos_macros.bat" export

set "check_status=0"
set "failed_steps="
set "eof_status=0"
set "ty_status=0"

::  ===============================================
::  CHECK PROJECT
::  ===============================================

REM This is the root check.bat ghog day looks for (%PRJ_DIR%\check.bat). It is
REM the static gate for llm-shared, a tooling-only repository whose source tree
REM is tools\ (there is no src\). radon, vulture and the big-file scan target
REM both tools\ and tests\, so the complexity, dead-code and line-budget gates
REM cover the test suite as well as the tool code.

pushd "%PRJ_DIR%"
cd /d "%PRJ_DIR%"

%_info% "ty check '%PRJ_DIR%'"
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
REM First make sure no trivial issues are left unfixed, to avoid noise in the
REM report and to fix the safe ones automatically.
ruff check --fix "%PRJ_DIR%"
REM Then run the full check to get the final status and report.
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

%_info% "vulture '%PRJ_DIR%\tools' '%PRJ_DIR%\tests' whitelist.py"
vulture "%PRJ_DIR%\tools" "%PRJ_DIR%\tests" whitelist.py
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
  call :record_failure big_files %big_file_status%
)

set "shellcheck_exe=%PRGS%\shellchecks\current\shellcheck.exe"
%_info% "shellcheck '%PRJ_DIR%\scripts\prepare_release_notes.sh' '%PRJ_DIR%\scripts\update-merge-commit-msg\git-extract-merge-docs.sh' '%PRJ_DIR%\scripts\update-merge-commit-msg\git-reword-merge.sh'"
if exist "%shellcheck_exe%" (
  "%shellcheck_exe%" -e SC1090,SC1091 "%PRJ_DIR%\scripts\prepare_release_notes.sh" "%PRJ_DIR%\scripts\update-merge-commit-msg\git-extract-merge-docs.sh" "%PRJ_DIR%\scripts\update-merge-commit-msg\git-reword-merge.sh"
  set "shellcheck_status=%ERRORLEVEL%"
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
set "eof_status=%ERRORLEVEL%"
if "%eof_status%"=="0" (
  %_ok% "EOF check passed for project '%PRJ_DIR_NAME%'"
) else (
  %_error% "EOF check failed for project '%PRJ_DIR_NAME%' with status '%eof_status%'"
  call :record_failure eof %eof_status%
)

%_pre% "-----------------------------------------"

if defined failed_steps (
  %_error% "Failed steps for project '%PRJ_DIR_NAME%': %failed_steps%"
  %_error% "Check failed for project '%PRJ_DIR_NAME%' with status '%check_status%'."
) else (
  %_ok% "All checks passed for project '%PRJ_DIR_NAME%'."
)

REM Preserve the exit code across the cleanup: :check_unset must not clear
REM final_check_status, and the last line clears the stash and exits with it
REM in one go (cmd expands the line before running it), so the failed status
REM reaches the caller (ghog check relies on it) without leaking a variable.
set "final_check_status=%check_status%"

popd

call:check_unset
if "%final_check_status%"=="" set "final_check_status=0"
set "final_check_status=" & exit /b %final_check_status%
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
call "%check_dir%\senv.bat" unset
set "big_file_status="
set "check_dir="
set "check_status="
set "eof_status="
set "failed_steps="
set "pyright_status="
set "python_big_file_line_limit="
set "python_big_file_msg="
set "radon_cc_report="
set "radon_cc_report_size="
set "ruff_status="
set "radon_cc_status="
set "shellcheck_exe="
set "ty_status="
set "vulture_status="
set "shellcheck_status="
goto:eof

::##################################################
::  ECHOS STACK (called by echos.bat)
::##################################################

:call_echos_stack
if not defined ECHOS_STACK ( set "CURRENT_SCRIPT=%~nx0" & goto:eof ) else ( call "%PRJ_DIR%\tools\batcolors\echos.bat" :stack %~nx0 )
goto:eof
