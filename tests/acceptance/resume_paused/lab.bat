@echo off
setlocal DisableDelayedExpansion
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0lab.ps1" %*
exit /b %ERRORLEVEL%
