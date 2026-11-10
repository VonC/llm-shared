@echo off
setlocal
for %%I in ("%~dp0..") do set "compat_root=%%~fI"
set "compat_env=%compat_root%\venvs\python_3.12_lifecycle_compatibility"
if /i "%~1"=="--setup" goto setup
goto validate

:setup
REM Explicit independent provisioning; ordinary validation never installs.
if exist "%compat_env%\Scripts\python.exe" goto install
uv venv --no-project --python 3.12 "%compat_env%"
if errorlevel 1 exit /b 1
:install
uv pip install --python "%compat_env%\Scripts\python.exe" -r "%compat_root%\tools\lifecycle_compatibility\requirements-py312.txt"
exit /b %errorlevel%

:validate
set "compat_python=%compat_env%\Scripts\python.exe"
if defined LLM_SHARED_LIFECYCLE_PYTHON set "compat_python=%LLM_SHARED_LIFECYCLE_PYTHON%"
REM Reject relative overrides before executing anything from the current PATH.
if defined LLM_SHARED_LIFECYCLE_PYTHON (
  for %%I in ("%compat_python%") do if /i not "%%~fI"=="%compat_python%" goto missing
)
if not exist "%compat_python%" goto missing
pushd "%compat_root%"
"%compat_python%" -m tools.lifecycle_compatibility.environment %*
set "compat_status=%errorlevel%"
popd
exit /b %compat_status%

:missing
echo ERROR: lifecycle compatibility requires an absolute prepared Python 3.12 executable. 1>&2
echo Run "%~f0" --setup or set LLM_SHARED_LIFECYCLE_PYTHON to an absolute prepared interpreter. 1>&2
exit /b 1
