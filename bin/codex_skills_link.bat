@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM llmup: validate this clone's Codex skill package read-only and check that
REM %USERPROFILE%\.agents\skills links to its .agents\llm-shared\skills; with
REM --create, make that junction when the folder is absent or empty. Never
REM writes inside the clone. Options and exit codes: tools\codex_skills_link.py.
REM The link must target the clone holding this launcher, so it self-locates
REM from its own path and ignores an inherited LLM_SHARED_DIR. llm-shared
REM Python, no project setup; isolated mode (-I) keeps PYTHONPATH and the
REM current folder from shadowing the modules it imports.
set "CLONE_DIR=%~dp0.."
set "PYTHON_BASE=%CLONE_DIR%\venvs"
set "LATEST_PYTHON="
for /f "delims=" %%d in ('dir /b /ad /o-d "%PYTHON_BASE%\python_3*llm-shared*" 2^>nul') do (
    if not defined LATEST_PYTHON set "LATEST_PYTHON=%%d"
)
if not defined LATEST_PYTHON (
    echo ERROR: No python_3*llm-shared* directory found in "%PYTHON_BASE%"
    exit /b 5
)
"%PYTHON_BASE%\%LATEST_PYTHON%\Scripts\python.exe" -I "%CLONE_DIR%\tools\codex_skills_link.py" %*
exit /b %ERRORLEVEL%
