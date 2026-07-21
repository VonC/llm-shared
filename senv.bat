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

REM Doskey macros are per-console and are not inherited. Load them before the
REM guard so a new console spawned from an initialized parent still gets pw,
REM pwiki, ghog, and the other shared aliases.
doskey /MACROFILE="%LLM_SHARED_DIR%\senv.doskey"

if defined NO_MORE_SENV_%PRJ_DIR_NAME% ( goto:eof )

::##################################################
::  INITIALIZE BATCOLORS + DEV_WORKFLOW SUBMODULES
::##################################################
REM tools\init.bat junctions/initializes batcolors and the senv_dev_workflow
REM submodule (tools\dev_workflow), exports the echo macros, then calls
REM dev_workflow\init.bat to wire the changelog/version aliases (uc, gv, brel).
REM INIT_DONE is console-global, but this initialization is project-specific.
REM Clear a value inherited from another repository before wiring this project.
set "INIT_DONE="
call "%~dp0tools\init.bat" %*

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

set "SENV_PYTHON_VERSION=%LATEST_PYTHON_DIR:python=%"
set "PYTHON_VERSION=%SENV_PYTHON_VERSION%"
set "EXPECTED_VENV_NAME=python_%SENV_PYTHON_VERSION%_%PRJ_DIR_NAME%"
set "EXPECTED_VENV_DIR=%PRJ_DIR%\venvs\%EXPECTED_VENV_NAME%"
set "EXPECTED_VENV_SCRIPTS=%EXPECTED_VENV_DIR%\Scripts"
set "BASE_PYTHON=%PRGS%\pythons\%LATEST_PYTHON_DIR%\python.exe"
%_info% "Using latest Python version found: '%SENV_PYTHON_VERSION%'"

call:ensure_project_venv_scaffold
if errorlevel 1 goto:eof

REM ========================================
REM PYTHONPATH / IMPORT SETUP
REM ========================================
echo ;%PYTHONPATH%; | findstr /C:";%PRJ_DIR%\bin;" >NUL 2>&1
if errorlevel 1 (
    set "PYTHONPATH=%PRJ_DIR%\bin;%PYTHONPATH%"
)

pushd "%PRJ_DIR%"
call switchpy %SENV_PYTHON_VERSION% local
popd
REM restore echos macros unset by switchpy
call "%PRJ_DIR%\tools\batcolors\echos_macros.bat" export
call:activate_project_venv
if errorlevel 1 goto:eof
%_ok% "Environment initialized for project '%PRJ_DIR_NAME%'"

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
doskey switchp=switchpy %SENV_PYTHON_VERSION% local $* ^& echo %PRJ_DIR_NAME%: switchpy done
doskey c="%PRJ_DIR%\bin\python_check.bat" $* ^& echo %PRJ_DIR_NAME%: python check done
doskey cbf="%PRJ_DIR%\bin\check_big_files.bat" $* ^& echo %PRJ_DIR_NAME%: check big files done

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
set "UV_PROJECT_ENVIRONMENT=%EXPECTED_VENV_DIR%"

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

call:ensure_project_venv_tools
if errorlevel 1 goto:eof

REM Versioned filter install (same pattern as my-project): the filter is
REM reapplied whenever the stored filter.uv-lock-public.version differs from
REM LOCK_FILTER_VERSION, so older or corrupted values (slash-excluding
REM /simple/ class, caret eaten by cmd) are replaced on the next senv run.
REM Bump LOCK_FILTER_VERSION whenever the smudge or clean command changes.
REM The two variables differ by more than case: cmd variables are
REM case-insensitive, so LOCK_FILTER_VERSION vs lock_filter_version would be
REM one and the same variable and the comparison below would always match.
set "LOCK_FILTER_VERSION=1"
set "LOCK_FILTER_VERSION_CUR="
for /f "tokens=* delims=" %%i in ('git -C "%PRJ_DIR%" config filter."uv-lock-public".version 2^>nul') do set "LOCK_FILTER_VERSION_CUR=%%i"
if not "%LOCK_FILTER_VERSION_CUR%"=="%LOCK_FILTER_VERSION%" (
  %_task% "Must set git config filter.uv-lock-public for public uv.lock content"
  git -C "%PRJ_DIR%" config filter.uv-lock-public.smudge "cat"
  if errorlevel 1 (
    %_fatal% "git -C '%PRJ_DIR%' config filter.uv-lock-public failed" 232
  )
  REM `[^^\"]+` (not `[^\"]+`): cmd's `\"` toggles out of quoted mode, so the
  REM lone `^` between the two `\"` becomes cmd's escape char and is eaten
  REM unless doubled. Git stores it as a single literal `^`.
  git -C "%PRJ_DIR%" config filter.uv-lock-public.clean "sed -E 's#https://[^[:space:]]+/simple/?#https://pypi.org/simple/#g; s#https://[^[:space:]]+/packages/#https://files.pythonhosted.org/packages/#g; s/, size = [0-9]+, upload-time = \"[^^\"]+\"//g'"
  if errorlevel 1 (
    %_fatal% "git -C '%PRJ_DIR%' config filter.uv-lock-public failed" 232
  )
  git -C "%PRJ_DIR%" config filter.uv-lock-public.version "%LOCK_FILTER_VERSION%"
  if errorlevel 1 (
    %_fatal% "git -C '%PRJ_DIR%' config filter.uv-lock-public failed" 232
  )
  %_ok% "git -C '%PRJ_DIR%' config filter.uv-lock-public set for public uv.lock content"
) else (
  %_info% "git config filter.uv-lock-public already set, skipping"
)
set "LOCK_FILTER_VERSION="
set "LOCK_FILTER_VERSION_CUR="

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

:ensure_project_venv_scaffold
if not exist "%BASE_PYTHON%" (
  %_fatal% "Base Python executable '%BASE_PYTHON%' is missing" 112
  exit /b 112
)

set "VENV_REBUILD_REASON="
if not exist "%EXPECTED_VENV_DIR%\pyvenv.cfg" set "VENV_REBUILD_REASON=pyvenv.cfg"
if not defined VENV_REBUILD_REASON if not exist "%EXPECTED_VENV_SCRIPTS%\python.exe" set "VENV_REBUILD_REASON=python.exe"
if not defined VENV_REBUILD_REASON if not exist "%EXPECTED_VENV_SCRIPTS%\activate.bat" set "VENV_REBUILD_REASON=activate.bat"
if not defined VENV_REBUILD_REASON exit /b 0

%_warning% "Project venv '%EXPECTED_VENV_NAME%' is incomplete: missing '%VENV_REBUILD_REASON%'"
%_task% "Must repair the project venv scaffold before activation"
if not exist "%PRJ_DIR%\venvs" mkdir "%PRJ_DIR%\venvs"
"%BASE_PYTHON%" "%PRJ_DIR%\tools\repair_venv_scaffold.py" "%EXPECTED_VENV_DIR%"
if errorlevel 1 (
  %_fatal% "Unable to repair project venv '%EXPECTED_VENV_DIR%'" 113
  exit /b 113
)
if not exist "%EXPECTED_VENV_SCRIPTS%\activate.bat" (
  %_fatal% "Rebuilt project venv has no activation script" 114
  exit /b 114
)
set "VENV_REBUILT=true"
%_ok% "Project venv scaffold repaired"
exit /b 0

:activate_project_venv
echo ;%PATH%; | findstr /I /C:";%EXPECTED_VENV_SCRIPTS%;" >NUL 2>&1
if errorlevel 1 (
  %_warning% "Project venv Scripts directory is missing from PATH: activating it"
  call "%EXPECTED_VENV_SCRIPTS%\activate.bat"
)
echo ;%PATH%; | findstr /I /C:";%EXPECTED_VENV_SCRIPTS%;" >NUL 2>&1
if errorlevel 1 (
  %_fatal% "Unable to add '%EXPECTED_VENV_SCRIPTS%' to PATH" 115
  exit /b 115
)
set "VIRTUAL_ENV=%EXPECTED_VENV_DIR%"
set "VIRTUAL_ENV_PROMPT=%EXPECTED_VENV_NAME%"
%_ok% "Project venv '%EXPECTED_VENV_NAME%' is active on PATH"
exit /b 0

:ensure_project_venv_tools
set "VENV_TOOL_REPAIR="
if defined VENV_REBUILT set "VENV_TOOL_REPAIR=venv scaffold was rebuilt"
if not exist "%EXPECTED_VENV_SCRIPTS%\pip.exe" set "VENV_TOOL_REPAIR=pip.exe is missing"
if not defined VENV_TOOL_REPAIR "%EXPECTED_VENV_SCRIPTS%\python.exe" -m pip --version >NUL 2>&1
if not defined VENV_TOOL_REPAIR if errorlevel 1 set "VENV_TOOL_REPAIR=pip is unusable"
if not exist "%EXPECTED_VENV_SCRIPTS%\uv.exe" set "VENV_TOOL_REPAIR=uv.exe is missing"
if not defined VENV_TOOL_REPAIR "%EXPECTED_VENV_SCRIPTS%\uv.exe" --version >NUL 2>&1
if not defined VENV_TOOL_REPAIR if errorlevel 1 set "VENV_TOOL_REPAIR=uv is unusable"

if defined VENV_TOOL_REPAIR (
  %_warning% "Project venv tools need repair: %VENV_TOOL_REPAIR%"
  %_task% "Must bootstrap pip in the project venv"
  "%EXPECTED_VENV_SCRIPTS%\python.exe" -m ensurepip --upgrade
  if errorlevel 1 goto:project_venv_tools_failed
  "%EXPECTED_VENV_SCRIPTS%\python.exe" -m pip install --upgrade pip
  if errorlevel 1 goto:project_venv_tools_failed
  "%EXPECTED_VENV_SCRIPTS%\python.exe" -m pip install uv
  if errorlevel 1 goto:project_venv_tools_failed
)

"%EXPECTED_VENV_SCRIPTS%\python.exe" -m pip --version
if errorlevel 1 goto:project_venv_tools_failed
"%EXPECTED_VENV_SCRIPTS%\uv.exe" --version
if errorlevel 1 goto:project_venv_tools_failed

%_task% "Must sync every project dependency group from uv.lock"
pushd "%PRJ_DIR%"
"%EXPECTED_VENV_SCRIPTS%\uv.exe" sync --frozen --all-groups
set "VENV_SYNC_STATUS=%ERRORLEVEL%"
popd
if not "%VENV_SYNC_STATUS%"=="0" goto:project_venv_tools_failed

where python.exe >NUL 2>&1
if errorlevel 1 goto:project_venv_tools_failed
where pip.exe >NUL 2>&1
if errorlevel 1 goto:project_venv_tools_failed
where uv.exe >NUL 2>&1
if errorlevel 1 goto:project_venv_tools_failed

set "VENV_REBUILT="
set "VENV_REBUILD_REASON="
set "VENV_TOOL_REPAIR="
set "VENV_SYNC_STATUS="
%_ok% "Project venv pip, uv, PATH, and dependency sync verified"
exit /b 0

:project_venv_tools_failed
%_fatal% "Unable to repair or sync project venv '%EXPECTED_VENV_DIR%'" 116
exit /b 116

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
