"""Source contract of `bin/gcliff.bat` and its alias fragment; no shell execution or emulation.

Step 8 of v0.14.0 git-cliff-provisioning (design "The gcliff launcher" and
"Alias definition"; design decisions Q09 and Q12). `bin/gcliff.bat` is the
release launcher `bin/release_workflow.bat` with four changes only: status 69
before the runtime record checks (every failure before Python, the same
"Run this checkout's setup" diagnostic), the `gcliff-batch` entry kind, no
status normalization, since a git-cliff status is not a release status, and
(code review round 1) a caller variable named ERRORLEVEL dropped from the
local scope after the child and before the status capture, so it cannot hide
the child's dynamic status while the child still inherits it. So it
keeps the self-location, the code page save, switch to 65001 and restore, and
the runtime record blocks, and every path, a readiness error as a normal child
return, reaches the restore at `:cleanup`. The launcher simulation side of the
same contract (69 for an unusable record, any status of the launcher returned
unchanged) is in `test_git_cliff_launcher`.

`bin/gcliff.doskey` is exactly one macro line, read with the `name=definition`
rule of `senv.doskey`; `senv.doskey` itself has no `gcliff` macro (item 8 adds
it), and the cross-site status contract of `test_codepage_tdd.py` keeps the two
release launchers only.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
_CODEPAGE_OPERATIONS = 3
_ENTRY = ' -I -X utf8 "%_release_root%\\tools\\release_workflow\\bootstrap.py" --entry-kind gcliff-batch -- %*'
_NORMALIZATION = (
    'if "%_release_status%"=="0" goto cleanup\n'
    'if "%_release_status%"=="1" goto cleanup\n'
    'if "%_release_status%"=="2" goto cleanup\n'
    'if "%_release_status%"=="3" goto cleanup\n'
    '>&2 echo Release operation exited with native status %_release_status%; returning 1.\n'
    'set "_release_status=1"\ngoto cleanup\n'
)
_STATUS_NOTE = "REM git-cliff's own status passes through unchanged; 69 marks every failure before it starts.\n"
_CAPTURE = 'set "_release_status=%ERRORLEVEL%"\n'
_DYNAMIC = ("REM A caller variable named ERRORLEVEL would hide the child's status: drop it here, after the child inherited it.\n"
            'set "ERRORLEVEL="\n' + _CAPTURE)
_MACRO = 'gcliff="%LLM_SHARED_DIR%\\bin\\gcliff.bat" $*'


def _source(name: str) -> str:
    """Read a shipped file as text with universal newlines."""
    return (_ROOT / name).read_text(encoding="utf-8")


def _macros(text: str) -> dict[str, str]:
    """Read doskey macro lines as `name=definition`, the first `=` ending the name."""
    pairs = (line.split("=", 1) for line in text.splitlines() if line.strip() and "=" in line)
    return {name.strip(): definition for name, definition in pairs}


def test_gcliff_is_the_release_launcher_with_four_changes() -> None:
    """Status 69 first, the gcliff-batch entry, the dynamic status, no normalization; every other block is the release launcher's."""
    release = _source("bin/release_workflow.bat")
    expected = (release.replace('set "_release_status=2"\n', f'set "_release_status=69"\n{_STATUS_NOTE}')
                .replace("--entry-kind explicit-batch -- %*", "--entry-kind gcliff-batch -- %*")
                .replace(_CAPTURE + _NORMALIZATION, _DYNAMIC + "goto cleanup\n"))
    assert expected != release
    assert _source("bin/gcliff.bat") == expected


def test_an_inherited_errorlevel_variable_is_dropped_only_after_the_child() -> None:
    """Code review round 1: the child inherits the caller's ERRORLEVEL variable, and only then is it dropped from the local scope.

    A variable named ERRORLEVEL expands in place of cmd's dynamic status; deleting it inside `setlocal`, between the
    child and the capture, keeps the child's environment and the caller's variable, and the capture reads the status.
    """
    source = _source("bin/gcliff.bat")
    child = source.index(_ENTRY)
    assert source.count('set "ERRORLEVEL="') == 1
    assert child < source.index('set "ERRORLEVEL="') < source.index(_CAPTURE)
    assert source.index("setlocal DisableDelayedExpansion") < child
    assert "ERRORLEVEL" not in source[:child]


def test_gcliff_sets_69_before_the_record_checks_and_never_normalizes() -> None:
    """The one status assignment before Python is 69, the entry is gcliff-batch, and no line maps a status to 1."""
    source = _source("bin/gcliff.bat")
    prerequisite = source[:source.index('python.exe" -I -X utf8')]
    assert prerequisite.count('set "_release_status=') == 1
    assert prerequisite.index('set "_release_status=69"') < prerequisite.index("release-runtime.v1.txt")
    assert _ENTRY in source
    assert "returning 1" not in source
    assert 'set "_release_status=1"' not in source
    assert _DYNAMIC + "goto cleanup\n" in source


def test_every_gcliff_path_restores_the_saved_code_page() -> None:
    """A readiness error falls through to `:cleanup`, a child return jumps to it, and `:cleanup` restores the code page."""
    source = _source("bin/gcliff.bat")
    assert source.count('"%SystemRoot%\\System32\\chcp.com"') == _CODEPAGE_OPERATIONS
    assert 'if not "%_release_cp%"=="65001" "%SystemRoot%\\System32\\chcp.com" 65001 <nul >nul 2>&1' in source
    assert (
        ":runtime_error\n>&2 echo Release readiness failed: %_release_error%. Run this checkout's setup.\n"
        ':cleanup\nif defined _release_cp "%SystemRoot%\\System32\\chcp.com" %_release_cp% >nul 2>&1\n'
        "endlocal & exit /b %_release_status%\n"
    ) in source
    assert source.rstrip().endswith("endlocal & exit /b %_release_status%")


def test_the_alias_fragment_is_one_gcliff_macro_and_senv_has_none() -> None:
    """`bin/gcliff.doskey` holds exactly the gcliff macro line; `senv.doskey` defines no gcliff macro."""
    fragment = _source("bin/gcliff.doskey")
    assert fragment.splitlines() == [_MACRO]
    assert _macros(fragment) == {"gcliff": '"%LLM_SHARED_DIR%\\bin\\gcliff.bat" $*'}
    assert "gcliff" not in _macros(_source("senv.doskey"))
    assert "gcliff" not in _source("senv.doskey")


def test_gcliff_checks_out_with_crlf_like_the_release_launchers() -> None:
    """The batch file keeps the release launchers' `text eol=crlf` attribute, so cmd reads its labels reliably."""
    attributes = _source(".gitattributes").splitlines()
    assert {"bin/release_workflow.bat text eol=crlf", "bin/gcliff.bat text eol=crlf"} <= set(attributes)


# eof
