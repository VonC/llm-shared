@echo off
REM ptanc: groundhog affected --no-cov - testmon-selected tests, no coverage.
call "%~dp0ghog.bat" affected --no-cov %*
exit /b %ERRORLEVEL%
