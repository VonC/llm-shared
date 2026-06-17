@echo off

::********************************************************************
:: Script Name:  build.bat
:: Description:  Build / release entry point for the tooling-only
::               llm-shared repository.
::
::               It is a thin wrapper around the dev_workflow release
::               machinery: tools\dev_workflow\t_build.bat does the work
::               in two phases and build.bat runs the test suite as the
::               gate between them.
::
::               build.bat rel (the brel alias) cuts a vX.Y.Z release:
::                 - :pre-processing calls update-version.bat, which
::                   turns the version.txt X.Y.Z-SNAPSHOT into the tag
::                   vX.Y.Z, finalizes the CHANGELOG and bumps version.txt
::                   to the next snapshot.
::                 - the pytest suite is the build gate.
::                 - :post-processing marks the new tag [valid] when the
::                   suite is green, or cancels the release (reset + tag
::                   delete) when it is red.
::
:: Parameters:
::    rel              cut a release from the version.txt -SNAPSHOT line
::    rel_title "..."  set the release title for that release
::    snap             bump the snapshot version only (no release tag)
::    (extra args)     forwarded to pytest as build_params
::
:: Usage:
::    build.bat            run the test-suite build gate
::    build.bat rel        cut a release (brel)
::
:: Return Value: pytest exit code (0 - Success, non-zero - build failed)
::********************************************************************

::  ===============================================
::  INITIAL SETUP
::  ===============================================
for %%i in ("%~dp0") do SET "build_dir=%%~fi"
set "build_dir=%build_dir:~0,-1%"

call <NUL "%build_dir%\senv.bat"
call "%build_dir%\tools\dev_workflow\t_build.bat" :pre-processing %*

::  ===============================================
::  BUILD PROJECT (run the test suite as the release gate)
::  ===============================================
%_stack_call% "%build_dir%\tools\dev_workflow\get-version.bat"

rem Pre-build steps here, if needed.

%_info% "----------------------------------------"
%_info% "Build the project '%PRJ_DIR_NAME%', version '%project_version%'"
%_info% "----------------------------------------"

REM build_params_echos is set by tools\dev_workflow\t_build.bat :pre-processing;
REM it shows the build params with " replaced by a look-alike so the echo of
REM the command stays safe even when a param carries a double quote.
%_task% "Start build of '%PRJ_DIR_NAME%' with build_params '%build_params_echos%'"

REM llm-shared is a tooling-only repository (its source tree is tools\, there is
REM no src\) and ghog / pt and check.bat are the real test, coverage and static
REM gates. The release build only confirms pytest itself runs, by executing the
REM single tests\test_dummy.py, exactly like the pdfsplitter template.
REM
REM test_dummy.py passes by default. To get a deterministic single test under
REM --last-failed, force it to fail once (PYTEST_DUMMY_FAIL=1) to seed the
REM last-failed cache, then re-run with the variable unset so it passes. That
REM also sidesteps the empty --last-failed --lfnf=none collection issue,
REM https://github.com/pytest-dev/pytest/issues/13614.
set "PYTEST_DUMMY_FAIL=1"
pytest --no-header --no-cov --color=no "%PRJ_DIR%\tests\test_dummy.py" >NUL
set "PYTEST_DUMMY_FAIL="

set "cmd=pytest --no-header --last-failed --lfnf=none --no-cov %build_params%"
%_info% "cmd is 'pytest --no-header --last-failed --lfnf=none --no-cov %build_params_echos%'"
set "QUIET_PRJ=true"
call <NUL %cmd%
set "build_status=%ERRORLEVEL%"
REM 5 means "run-last-failure: no previously failed tests, deselecting all items."
if "%build_status%"=="5" ( set "build_status=0" )
set "QUIET_PRJ=true"

REM check if this build is a release build for which a "valid" marker needs to be
REM created. The marker is set on the tag created for that release for which the
REM build has just been done.
call "%build_dir%\tools\dev_workflow\t_build.bat" :post-processing %build_status%
call:build_unset
exit /b %build_status%
goto:eof

::##################################################
::  CLEANUP
::##################################################

:build_unset
set "cmd="
call "%build_dir%\senv.bat" unset
call "%build_dir%\tools\dev_workflow\t_build.bat" :build_unset
set "build_dir="
goto:eof

::##################################################
::  ECHOS STACK (called by echos.bat)
::##################################################

:call_echos_stack
if not defined ECHOS_STACK ( set "CURRENT_SCRIPT=%~nx0" & goto:eof ) else ( call "%PRJ_DIR%\tools\batcolors\echos.bat" :stack %~nx0 )
goto:eof
