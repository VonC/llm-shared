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
set "COPILOT_SHARED_DIR=%PRJ_DIR%"
set "LLM_SHARED_DIR=%PRJ_DIR%"
if defined GCYGPATH (
  for /f "usebackq tokens=*" %%i in (`%GCYGPATH% -u "%COPILOT_SHARED_DIR%"`) do  set "COPILOT_SHARED_DIR_UNIX=%%i"
  for /f "usebackq tokens=*" %%i in (`%GCYGPATH% -u "%LLM_SHARED_DIR%"`) do  set "LLM_SHARED_DIR_UNIX=%%i"
  for /f "usebackq tokens=*" %%i in (`%GCYGPATH% -u "%PRJ_DIR%"`) do  set "PRJ_DIR_unix=%%i"
)

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

set "GIT_HOME=%PRGS%\gits\current"
set "GCYGPATH=%GIT_HOME%\usr\bin\cygpath.exe"
for /f "usebackq tokens=*" %%i in (`%GCYGPATH% -u "%COPILOT_SHARED_DIR%"`) do  set "COPILOT_SHARED_DIR_UNIX=%%i"
for /f "usebackq tokens=*" %%i in (`%GCYGPATH% -u "%LLM_SHARED_DIR%"`) do  set "LLM_SHARED_DIR_UNIX=%%i"
for /f "usebackq tokens=*" %%i in (`%GCYGPATH% -u "%PRJ_DIR%"`) do  set "PRJ_DIR_unix=%%i"

doskey pt=pytest --no-header --cov-report term-missing:skip-covered $* ^& echo %PRJ_DIR_NAME%: pytest done
doskey pta=pytest --testmon --no-header --no-cov -rxX $* ^& echo %PRJ_DIR_NAME%: pytest affected done
doskey ptr=del .testmondata 2>nul ^& pytest --testmon --no-header --cov-report term-missing:skip-covered $* ^& echo %PRJ_DIR_NAME%: pytest reset done
doskey ptnc=pytest --testmon --no-header --no-cov -rxX ^& echo %PRJ_DIR_NAME%: pytest no-cov done
doskey ptncs=pytest --no-header --no-cov -rxX $* ^& echo %PRJ_DIR_NAME%: pytest no-cov single done
doskey pts=pytest --no-header --no-cov -rxX $* ^& echo %PRJ_DIR_NAME%: pytest no-cov single done
doskey ptf=pytest --no-header --last-failed --lfnf=none --no-cov $* ^& echo %PRJ_DIR_NAME%: pytest done
doskey ptfn=pytest --no-header --last-failed --lfnf=none --no-cov $* ^| grep FAILED ^| cut -d " " -f 2 ^| cut -d ":" -f 1 ^| sort ^| uniq ^& echo %PRJ_DIR_NAME%: pytest last-failed test names done

doskey vmw=vulture "%PRJ_DIR%\tools" --make-whitelist --min-confidence 60 $* ^> whitelist.py ^& echo %PRJ_DIR_NAME%: vulture whitelist done
doskey vult=vulture "%PRJ_DIR%\tools" whitelist.py $* ^& echo %PRJ_DIR_NAME%: vulture done
doskey radcc=radon cc --show-closures -a --total-average -s "%PRJ_DIR%" $* ^& echo %PRJ_DIR_NAME%: radon Cyclomatic Complexity done
doskey radmi=radon mi -s "%PRJ_DIR%" $* ^& echo %PRJ_DIR_NAME%: radon Maintainability Index done
doskey radr=radon raw -s "%PRJ_DIR%" $* ^& echo %PRJ_DIR_NAME%: radon Raw Metrics done
doskey ruffc=ruff check $* ^& echo %PRJ_DIR_NAME%: ruff check done
doskey ruffcf=ruff check --fix $* ^& echo %PRJ_DIR_NAME%: ruff check --fix done
doskey ruffcuf=ruff check --unsafe-fixes --fix $* ^& echo %PRJ_DIR_NAME%: ruff check --unsafe-fixes --fix done
doskey ruffcs=ruff check --select $* ^& echo %PRJ_DIR_NAME%: ruff check select done
doskey ptws=ptw "%PRJ_DIR%\bin" --testmon --cov-report=html --cov-append --cov-report term-missing:skip-covered $* ^& echo %PRJ_DIR_NAME%: pytest-watch done
doskey switchp=switchpy %PYTHON_VERSION% local $* ^& echo %PRJ_DIR_NAME%: switchpy done
doskey c="%PRJ_DIR%\bin\python_check.bat" $* ^& echo %PRJ_DIR_NAME%: python check done
doskey cbf="%PRJ_DIR%\bin\check_big_files.bat" $* ^& echo %PRJ_DIR_NAME%: check big files done

doskey /MACROFILE="%LLM_SHARED_DIR%\senv.doskey"

doskey fga=python "%PRJ_DIR%\tools\flamegraph_analyzer.py" $1 ^& echo %PRJ_DIR_NAME%: flamegraph analyzer done

doskey pyr=pyright $* ^& echo %PRJ_DIR_NAME%: pyright done
doskey pyrb=pyright "%PRJ_DIR%\bin" $* ^& echo %PRJ_DIR_NAME%: pyright bin done

rem pcomp/pupg/psync route uv through tools\uv_run.py, which picks the
rem right TLS trust roots for a personal vs corporate (proxy) network.
doskey pcomp=python "%LLM_SHARED_DIR%\tools\uv_run.py" lock $* ^& echo %PRJ_DIR_NAME%: uv lock ^(refresh uv.lock from pyproject.toml^) done
doskey pupg=python "%LLM_SHARED_DIR%\tools\uv_run.py" lock --upgrade $* ^& echo %PRJ_DIR_NAME%: uv lock --upgrade ^(bump dev deps^) done
doskey psync=python "%LLM_SHARED_DIR%\tools\uv_run.py" sync $* ^& echo %PRJ_DIR_NAME%: uv sync ^(install dev deps from uv.lock^) done

rem Recompute the corporate CA bundle on each activation so stale values from
rem a previous repo shell do not survive a fresh `fsenv`.
rem Prefer a bundle-like PEM in an ignored certs\ folder under the repo,
rem else in the parent folder. Fall back to the newest generic PEM only when
rem no bundle-like PEM exists. If neither exists, leave unset.
set "UV_CERT="
set "SSL_CERT_FILE="
set "CURL_CA_BUNDLE="
set "DEFAULT_CA_BUNDLE="
for %%i in ("%PRJ_DIR%\..") do set "PARENT_DIR=%%~fi"
if exist "%PRJ_DIR%\certs\" (
  for /f "delims=" %%f in ('dir /b /a:-d /o:-d "%PRJ_DIR%\certs\*bundle*.pem" 2^>nul') do if not defined DEFAULT_CA_BUNDLE set "DEFAULT_CA_BUNDLE=%PRJ_DIR%\certs\%%f"
  for /f "delims=" %%f in ('dir /b /a:-d /o:-d "%PRJ_DIR%\certs\*.pem" 2^>nul') do if not defined DEFAULT_CA_BUNDLE set "DEFAULT_CA_BUNDLE=%PRJ_DIR%\certs\%%f"
)
if not defined DEFAULT_CA_BUNDLE (
  for /f "delims=" %%f in ('dir /b /a:-d /o:-d "%PARENT_DIR%\*bundle*.pem" 2^>nul') do if not defined DEFAULT_CA_BUNDLE set "DEFAULT_CA_BUNDLE=%PARENT_DIR%\%%f"
  for /f "delims=" %%f in ('dir /b /a:-d /o:-d "%PARENT_DIR%\*.pem" 2^>nul') do if not defined DEFAULT_CA_BUNDLE set "DEFAULT_CA_BUNDLE=%PARENT_DIR%\%%f"
)
if defined DEFAULT_CA_BUNDLE set "UV_CERT=%DEFAULT_CA_BUNDLE%"
if defined UV_CERT set "SSL_CERT_FILE=%UV_CERT%"
if defined UV_CERT set "CURL_CA_BUNDLE=%UV_CERT%"

rem uv / uvw / uvx are left unaliased so they resolve to the venv binaries
rem on PATH. uv honours SSL_CERT_FILE directly: on a non-corporate machine
rem if no PEM is found, assume a personal machine where no extra cert is needed.
doskey uv=
doskey uvw=
doskey uvx=
set "EXPECTED_VENV_NAME=python_%PYTHON_VERSION%_%PRJ_DIR_NAME%"
if exist "%PRJ_DIR%\venvs\%EXPECTED_VENV_NAME%" (
  set "UV_PROJECT_ENVIRONMENT=%PRJ_DIR%\venvs\%EXPECTED_VENV_NAME%"
) else (
  set "UV_PROJECT_ENVIRONMENT=%VIRTUAL_ENV%"
)

doskey gdca=git diff --cached ^> a.diff ^& grep "^diff " a.diff ^| wc -l ^& git status --porcelain ^| grep -v "^[ \?]"
doskey gcma=gcm.bat a ^& git commit --amend


REM Set the default max size in KB for inspect_api.py JSON dump file splitting.
set "INSPECT_API_MAXSIZE_KB=150"

REM Set the line limit for big python file check
set "PYTHON_BIG_FILE_LINE_LIMIT=650"

REM Recompute uv index settings on each activation so stale values from a
REM previous shell do not survive a fresh `fsenv`.
set "UV_INDEX_URL="
set "UV_EXTRA_INDEX_URL="

if exist "%PRJ_DIR%\bin\senv.local.bat" (
  REM Can override variables from senv.bat
  %_info% "Loading local environment variables from '%PRJ_DIR%\bin\senv.local.bat'"
  call "%PRJ_DIR%\bin\senv.local.bat"
) else (
  %_info% "No local environment variables file (senv.local.bat) found in '%PRJ_DIR%\bin\'. Skipping."
)

REM llm-shared is a public repository: keep local uv usage unchanged, but
REM rewrite staged uv.lock URLs to public hosts before commit.
if not defined UV_INDEX_URL if defined PYPI_HOST set "UV_INDEX_URL=https://%PYPI_HOST%"

set "lock_filter_smudge="
for /f "tokens=* delims=" %%i in ('git -C "%PRJ_DIR%" config filter."uv-lock-public".smudge') do set "lock_filter_smudge=%%i"
if not defined lock_filter_smudge (
  %_task% "Must set git config filter.uv-lock-public for public uv.lock content"
  git -C "%PRJ_DIR%" config filter.uv-lock-public.smudge "cat"
  git -C "%PRJ_DIR%" config filter.uv-lock-public.clean "sed -E 's#https://[^[:space:]/]+/simple/#https://pypi.org/simple/#g; s#https://[^[:space:]]+/packages/#https://files.pythonhosted.org/packages/#g; s/, size = [0-9]+, upload-time = \"[^\\\"]+\"//g'"
  if errorlevel 1 (
    %_fatal% "git -C '%PRJ_DIR%' config filter.uv-lock-public failed" 232
  )
  %_ok% "git -C '%PRJ_DIR%' config filter.uv-lock-public set for public uv.lock content"
) else (
  %_info% "git config filter.uv-lock-public.smudge already set to '%lock_filter_smudge%', skipping"
)
set "lock_filter_smudge="

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
