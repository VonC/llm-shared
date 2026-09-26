@echo off
REM Set ARTIFACT_HOME to a project's review artifact home and prepare it.
REM
REM Usage: call "%LLM_SHARED_DIR%\bin\artifact_home.bat" "<project-root>"
REM
REM Every a.* working file a launcher writes belongs in the artifact home, never
REM at the project root (see rules\artifact_files.md). The home is `.reviews`
REM unless `.review-artifacts.ini` declares `home = <relative path>`. A new home
REM gets a .gitignore of exactly "*" and a LF, the bytes the review tooling
REM validates; cmd's echo would write CRLF, so PowerShell writes that file.
REM The Python side of the same contract is tools\artifact_home.py.
set "ARTIFACT_HOME_ROOT=%~1"
if not defined ARTIFACT_HOME_ROOT set "ARTIFACT_HOME_ROOT=%CD%"
if "%ARTIFACT_HOME_ROOT:~-1%"=="\" set "ARTIFACT_HOME_ROOT=%ARTIFACT_HOME_ROOT:~0,-1%"
set "ARTIFACT_HOME_REL=.reviews"
if exist "%ARTIFACT_HOME_ROOT%\.review-artifacts.ini" (
    for /f "usebackq tokens=1,2 delims== " %%a in ("%ARTIFACT_HOME_ROOT%\.review-artifacts.ini") do (
        if /i "%%a"=="home" set "ARTIFACT_HOME_REL=%%b"
    )
)
set "ARTIFACT_HOME=%ARTIFACT_HOME_ROOT%\%ARTIFACT_HOME_REL:/=\%"
if not exist "%ARTIFACT_HOME%\" mkdir "%ARTIFACT_HOME%"
if not exist "%ARTIFACT_HOME%\.gitignore" (
    powershell -NoProfile -NonInteractive -Command "[IO.File]::WriteAllText('%ARTIFACT_HOME%\.gitignore', [string][char]42 + [char]10)"
)
set "ARTIFACT_HOME_ROOT="
set "ARTIFACT_HOME_REL="
exit /b 0
