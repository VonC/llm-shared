@echo off
setlocal

REM Claude Code runs this launcher while it loads /copy-conversation (the
REM !-command of SKILL.md), so the model only relays the line it prints instead
REM of reading the instruction and running the shared launcher itself.
REM
REM Find the llm-shared checkout holding this skill, cheapest first: the skill
REM folder's own parents, then the checkout the session names. When
REM %USERPROFILE%\.claude\skills is a junction to this checkout's .claude\skills,
REM %~dp0..\..\.. names the user folder instead, and only git (about 0.6 s)
REM resolves the junction to the real root.
set "LLM_SHARED_ROOT="
if exist "%~dp0..\..\..\instructions\copy-conversation.md" set "LLM_SHARED_ROOT=%~dp0..\..\.."
if not defined LLM_SHARED_ROOT if defined LLM_SHARED_DIR if exist "%LLM_SHARED_DIR%\instructions\copy-conversation.md" set "LLM_SHARED_ROOT=%LLM_SHARED_DIR%"
if not defined LLM_SHARED_ROOT for /f "delims=" %%r in ('git -C "%~dp0." rev-parse --show-toplevel 2^>nul') do set "LLM_SHARED_ROOT=%%r"
if not defined LLM_SHARED_ROOT (
    echo ERROR: No llm-shared checkout holds "%~dp0".
    exit /b 0
)

REM Errors go to stdout and the launcher exits 0: a failing skill command
REM aborts the skill, and the model could not report the ERROR line.
call "%LLM_SHARED_ROOT%\bin\copy_conversation.bat" claude %* 2>&1
exit /b 0
