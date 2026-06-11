@echo off
REM pts: groundhog single - named test files in focus, no coverage.
call "%~dp0ghog.bat" single %*
exit /b %ERRORLEVEL%
