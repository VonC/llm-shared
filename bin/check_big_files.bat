@echo off
setlocal EnableDelayedExpansion

REM Big-file gate, callable on its own (the cbf doskey of senv.bat): the same
REM Python scan as python_check.bat - PATH-independent, no Unix find (a PATH
REM where System32 precedes Git usr\bin would silently scan nothing).
REM Optional arguments override the scanned roots (default: tools tests).
if not defined PRJ_DIR set "PRJ_DIR=%CD%"

if defined PYTHON_BIG_FILE_LINE_LIMIT (
  set "python_big_file_line_limit=%PYTHON_BIG_FILE_LINE_LIMIT%"
  set "python_big_file_msg= (from PYTHON_BIG_FILE_LINE_LIMIT=%PYTHON_BIG_FILE_LINE_LIMIT%)"
) else (
  set "python_big_file_line_limit=700"
  set "python_big_file_msg= (default: 700 lines, set PYTHON_BIG_FILE_LINE_LIMIT to override)"
)

set "scan_roots=%*"
if "%scan_roots%"=="" set "scan_roots=tools tests"

echo Check for files too big under '%PRJ_DIR%' in '%scan_roots%'%python_big_file_msg%
pushd "%PRJ_DIR%"
python -c "import pathlib,sys; limit=int(sys.argv[1]); rows=[(sum(1 for _ in p.open(encoding='utf-8', errors='ignore')), p) for root in sys.argv[2:] for p in pathlib.Path(root).rglob('*.py')]; bad=[(n,p) for n,p in rows if n>limit]; [print(f'{n:6} {p}') for n,p in bad]; sys.exit(1 if bad else 0)" %python_big_file_line_limit% %scan_roots%
set "big_file_status=%ERRORLEVEL%"
popd

if "%big_file_status%"=="0" (
  echo OK: no file over %python_big_file_line_limit% lines
) else (
  echo ERROR: files over %python_big_file_line_limit% lines found, see the list above
)

endlocal & exit /b %big_file_status%
