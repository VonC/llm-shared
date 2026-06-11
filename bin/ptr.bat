@echo off
REM ptr: groundhog full - delete .testmondata, full suite with coverage.
call "%~dp0ghog.bat" full %*
exit /b %ERRORLEVEL%
