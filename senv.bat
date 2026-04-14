@echo off

REM ******************************************************************
REM Script Name:  senv.bat
REM Description:  environment setup for the project
REM
REM Parameters:
REM none
REM
REM Usage:
REM First script to be called to setup the environment for the project
REM Copy this script to the root of your project (remove the .tpl in the name)
REM
REM Return Value: 0 - Success, 1 - Error
REM
REM ******************************************************************

for %%i in ("%~dp0") do SET "PRJ_DIR=%%~fi"
set "PRJ_DIR=%PRJ_DIR:~0,-1%"
for %%i in ("%PRJ_DIR%") do SET "PRJ_DIR_NAME=%%~nxi"

if defined NO_MORE_SENV_%PRJ_DIR_NAME% ( goto:eof )

::##################################################
::  CHECK BATCOLORS SUBMODULE
::##################################################
set "okInit="
set "tool_dir=%PRJ_DIR%\tools"
if not exist "%tool_dir%\batcolors\echos.bat" (
    echo [dev_workflow] WARN: Missing submodules
    if not exist "%PRJ_DIR%\.gitmodules" (
          echo [dev_workflow] FATAL: Submodule batcolors not properly added
          call:iExitBatch 6
    ) else (
      echo [dev_workflow] INFO: Executing 'git submodule update --init' in '%PRJ_DIR%'
      git -C "%PRJ_DIR%" submodule update --init
      if errorlevel 1 (
          echo FATAL: Submodules not properly initialized
          call:iExitBatch 6
      )
    )
    call  "%tool_dir%\batcolors\echos_macros.bat" export
    set "okInit=[dev_workflow] OK: Submodules initialized"
) else (
  call  "%tool_dir%\batcolors\echos_macros.bat" export
  set "okInit=[dev_workflow] Submodule batcolors already initialized"
)

if not defined okInit (
  echo [dev_workflow] FATAL: Submodules not properly initialized
  call:iExitBatch 6
)

%_ok% "Environment initialized for project '%PRJ_DIR_NAME%'"
if not defined QUIET_PRJ ( %_ok% "%okInit%" )

REM Add python local venv path to %PATH%
if not exist "%PRGS%\pythons" (
  %_fatal% "Directory '%PRGS%\pythons' not found." 110
  goto:eof
)

set "LATEST_PYTHON_DIR="
for /f "delims=" %%d in ('dir /B /AD /O:-N "%PRGS%\pythons\python3.*"') do (
  if not defined LATEST_PYTHON_DIR set "LATEST_PYTHON_DIR=%%d"
)

if not defined LATEST_PYTHON_DIR (
  %_fatal% "No python3.x.y directory found in '%PRGS%\pythons'." 111
  goto:eof
)

set "PYTHON_VERSION=%LATEST_PYTHON_DIR:python=%"
%_info% "Using latest Python version found: '%PYTHON_VERSION%'"

REM ========================================
REM PYTHONPATH / IMPORT SETUP
REM ========================================
echo ;%PYTHONPATH%; | findstr /C:";%PRJ_DIR%\bin;" >NUL 2>&1
if errorlevel 1 (
    set "PYTHONPATH=%PRJ_DIR%\bin;%PYTHONPATH%"
)

pushd "%PRJ_DIR%"
call switchpy %PYTHON_VERSION% local
popd
REM restore echos macros unset by switchpy
call "%PRJ_DIR%\tools\batcolors\echos_macros.bat" export

doskey pt=pytest --no-header --cov-report term-missing:skip-covered $* ^& echo %PRJ_DIR_NAME%: pytest done
doskey pta=pytest --testmon --cov-append --no-header --cov-report term-missing:skip-covered $* ^& echo %PRJ_DIR_NAME%: pytest affected done
doskey ptr=del .testmondata 2>nul ^& pytest --testmon --no-header --cov-report term-missing:skip-covered $* ^& echo %PRJ_DIR_NAME%: pytest reset done
doskey ptnc=pytest --testmon --no-header --no-cov -rxX ^& echo %PRJ_DIR_NAME%: pytest no-cov done
doskey ptncs=pytest --no-header --no-cov -rxX $* ^& echo %PRJ_DIR_NAME%: pytest no-cov single done
doskey pts=pytest --no-header --no-cov -rxX $* ^& echo %PRJ_DIR_NAME%: pytest no-cov single done
doskey ptf=pytest --no-header --last-failed --lfnf=none --no-cov $* ^& echo %PRJ_DIR_NAME%: pytest done
doskey ptfn=pytest --no-header --last-failed --lfnf=none --no-cov $* ^| grep FAILED ^| cut -d " " -f 2 ^| cut -d ":" -f 1 ^| sort ^| uniq ^& echo %PRJ_DIR_NAME%: pytest last-failed test names done

doskey vmw=vulture "%PRJ_DIR%\bin" --make-whitelist --min-confidence 60 $* ^> whitelist.py ^& echo %PRJ_DIR_NAME%: vulture whitelist done
doskey vult=vulture "%PRJ_DIR%\bin" whitelist.py $* ^& echo %PRJ_DIR_NAME%: vulture done
doskey radcc=radon cc --show-closures -a --total-average -s "%PRJ_DIR%\bin" $* ^& echo %PRJ_DIR_NAME%: radon Cyclomatic Complexity done
doskey radmi=radon mi -s "%PRJ_DIR%\bin" $* ^& echo %PRJ_DIR_NAME%: radon Maintainability Index done
doskey radr=radon raw -s "%PRJ_DIR%\bin" $* ^& echo %PRJ_DIR_NAME%: radon Raw Metrics done
doskey ruffc=ruff check $* ^& echo %PRJ_DIR_NAME%: ruff check done
doskey ruffcf=ruff check --fix $* ^& echo %PRJ_DIR_NAME%: ruff check --fix done
doskey ruffcuf=ruff check --unsafe-fixes --fix $* ^& echo %PRJ_DIR_NAME%: ruff check --unsafe-fixes --fix done
doskey ruffcs=ruff check --select $* ^& echo %PRJ_DIR_NAME%: ruff check select done
doskey ptws=ptw "%PRJ_DIR%\bin" --testmon --cov-report=html --cov-append --cov-report term-missing:skip-covered $* ^& echo %PRJ_DIR_NAME%: pytest-watch done
doskey switchp=switchpy %PYTHON_VERSION% local $* ^& echo %PRJ_DIR_NAME%: switchpy done
doskey c="%PRJ_DIR%\bin\python_check.bat" $* ^& echo %PRJ_DIR_NAME%: python check done
doskey cbf="%PRJ_DIR%\bin\check_big_files.bat" $* ^& echo %PRJ_DIR_NAME%: check big files done

doskey gcb=python "%PRJ_DIR%\tools\git_batch_commit.py" $* ^& echo %PRJ_DIR_NAME%: git batch commit done
doskey gbc=python "%PRJ_DIR%\tools\git_batch_commit.py" $* ^& echo %PRJ_DIR_NAME%: git batch commit done
doskey gcbr=python "%PRJ_DIR%\tools\git_batch_commit.py" --root-a-commit $* ^& echo %PRJ_DIR_NAME%: git batch commit --root-a-commit done
doskey gbcr=python "%PRJ_DIR%\tools\git_batch_commit.py" --root-a-commit  $* ^& echo %PRJ_DIR_NAME%: git batch commit --root-a-commit done
doskey gcba=python "%PRJ_DIR%\tools\git_batch_commit.py" --root-a-commit $* ^&^& echo %PRJ_DIR_NAME%: git batch commit --root-a-commit done
doskey gbca=python "%PRJ_DIR%\tools\git_batch_commit.py" --root-a-commit $* ^&^& echo %PRJ_DIR_NAME%: git batch commit --root-a-commit done

doskey fga=python "%PRJ_DIR%\tools\flamegraph_analyzer.py" $1 ^& echo %PRJ_DIR_NAME%: flamegraph analyzer done

doskey pyr=pyright $* ^& echo %PRJ_DIR_NAME%: pyright done
doskey pyrb=pyright "%PRJ_DIR%\bin" $* ^& echo %PRJ_DIR_NAME%: pyright bin done

doskey pcomp=pip-compile --strip-extras requirements.in $* ^&^& pip-compile --strip-extras requirements.dev.in $* ^& echo %PRJ_DIR_NAME%: pip-compile runtime+dev upgrade done
doskey pupg=pip-compile --strip-extras --upgrade requirements.in $* ^&^& pip-compile --strip-extras --upgrade requirements.dev.in $* ^& echo %PRJ_DIR_NAME%: pip-compile upgrade runtime+dev upgrade done

doskey gdca=git diff --cached ^> a.diff ^& grep "^diff " a.diff ^| wc -l ^& git status --porcelain ^| grep -v "^[ \?]"
doskey gcma=gcm.bat a ^& git commit --amend


REM Set the default max size in KB for inspect_api.py JSON dump file splitting.
set "INSPECT_API_MAXSIZE_KB=150"

REM Set the line limit for big python file check
set "PYTHON_BIG_FILE_LINE_LIMIT=650"

if exist "%PRJ_DIR%\bin\senv.local.bat" (
  REM Can override variables from senv.bat
  %_info% "Loading local environment variables from '%PRJ_DIR%\bin\senv.local.bat'"
  call "%PRJ_DIR%\bin\senv.local.bat"
) else (
  %_info% "No local environment variables file (senv.local.bat) found in '%PRJ_DIR%\bin\'. Skipping."
)

REM check.bat and other scripts in the root of the project should be in the %PATH% for direct calling from anywhere,
REM but only if not already present (to avoid duplicates in case of multiple calls to senv.bat from the same command prompt)
echo ;%PATH%; | findstr /C:";%PRJ_DIR%\bin;" >NUL 2>&1
if errorlevel 1 (
  set "PATH=%PRJ_DIR%\bin;%PATH%"
)

REM Set project-specific flag when done
REM Next call to senv.bat will be skipped
set "NO_MORE_SENV_%PRJ_DIR_NAME%=true"
doskey fsenv=set "NO_MORE_SENV_%PRJ_DIR_NAME%=" ^& "%PRJ_DIR%\senv.bat" force $*

%_info% "local dev senv applied for '%PRJ_DIR_NAME%'"

goto:eof

:call_echos_stack
if not defined ECHOS_STACK ( set "CURRENT_SCRIPT=%~nx0" & goto:eof ) else ( call "%PRJ_DIR%\tools\batcolors\echos.bat" :stack %~nx0 )
goto:eof

:iExitBatch - Cleanly exit batch processing, regardless how many CALLs
@echo off
if not exist "%temp%\ExitBatchYes.txt" call :ibuildYes
call :iCtrlC <"%temp%\ExitBatchYes.txt" 1>nul 2>&1
:iCtrlC
cmd /c exit -1073741510%1
goto:eof
