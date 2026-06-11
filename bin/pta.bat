@echo off
REM pta: groundhog affected - testmon-selected tests, appended coverage.
call "%~dp0ghog.bat" affected %*
exit /b %ERRORLEVEL%
