"""Tests for the command line of `tools.copy_conversation`.

Host detection, transcript lookup, the tab title, the clipboard boundary and
the entry point. The clipboard is always replaced: no test starts PowerShell
or touches the real clipboard.

Fix: on Windows the clipboard is now set in-process through the Windows API,
not by starting PowerShell (about one second); a bare `YYYYMMDD` after the
host works as `--date`, since the Claude skill passes the user's words as
typed; and a chat with no turn before the request reports `Nothing to copy`
instead of the trimmer's `kept no line`.
"""

from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from tests.script_entry import run_main
from tools import copy_conversation as cli

# pyright: reportPrivateUsage=false, reportUnusedFunction=false
# ruff: noqa: RUF001, SLF001, N802

_FATAL_EXIT_CODE = 2
_HOST_VARIABLES = (
    "CLAUDE_CODE_SESSION_ID",
    "CODEX_THREAD_ID",
    "CLAUDE_CONFIG_DIR",
    "CODEX_HOME",
    "TUIOS_SESSION",
    "TUITP_PROJECT",
    "HOME",
)
_TAB_LIST = (
    "# layout\n--- dev\n=== demo qal\n+ %USERPROFILE%\\git\\demo|demo-claude|claude|qal\n"
    "# === old\n# + C:\\old|senv-claude|claude\n=== senv\n+ %PRGS%\\senv|senv-claude|claude|senv\n"
)


@pytest.fixture(autouse=True)
def _no_host_signals(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run every case as if outside any agent pane."""
    for name in _HOST_VARIABLES:
        monkeypatch.delenv(name, raising=False)


def _claude_transcript(path: Path, prompt: str = "hello") -> Path:
    entries = [
        {"type": "user", "origin": {"kind": "human"}, "message": {"content": prompt}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "hi"}]}},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(entry) for entry in entries), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("variables", "expected"),
    [({"CLAUDE_CODE_SESSION_ID": "s"}, "claude"), ({"CODEX_THREAD_ID": "t"}, "codex")],
)
def test_detect_host_reads_the_session_variable(
    variables: dict[str, str],
    expected: str,
) -> None:
    """The one session variable set names the host."""
    assert cli.detect_host(variables) == expected


@pytest.mark.parametrize(
    ("variables", "state"),
    [
        ({}, "Neither"),
        ({"CLAUDE_CODE_SESSION_ID": "s", "CODEX_THREAD_ID": "t"}, "Both"),
    ],
)
def test_detect_host_refuses_to_guess(variables: dict[str, str], state: str) -> None:
    """No variable, or both, asks for the host by name."""
    with pytest.raises(
        cli.CopyConversationError,
        match=f"{state} of CLAUDE_CODE_SESSION_ID",
    ):
        cli.detect_host(variables)


def test_find_transcript_takes_the_newest_claude_match(tmp_path: Path) -> None:
    """A session seen under two project folders resolves to the newest file."""
    older = _claude_transcript(tmp_path / "projects" / "C--a" / "s1.jsonl")
    newer = _claude_transcript(tmp_path / "projects" / "C--b" / "s1.jsonl")
    os.utime(older, (1_000, 1_000))

    assert (
        cli.find_transcript("claude", "s1", {"CLAUDE_CONFIG_DIR": str(tmp_path)})
        == newer
    )


def test_find_transcript_searches_the_codex_sessions_tree(tmp_path: Path) -> None:
    """A rollout is found by its thread id, at any date depth."""
    rollout = (
        tmp_path
        / "sessions"
        / "2026"
        / "11"
        / "04"
        / "rollout-2026-11-04T09-07-46-t1.jsonl"
    )
    rollout.parent.mkdir(parents=True)
    rollout.write_text("", encoding="utf-8")

    assert cli.find_transcript("codex", "t1", {"CODEX_HOME": str(tmp_path)}) == rollout
    with pytest.raises(
        cli.CopyConversationError,
        match="No transcript found for codex session t2",
    ):
        cli.find_transcript("codex", "t2", {"CODEX_HOME": str(tmp_path)})


def test_resolve_transcript_prefers_the_given_file(tmp_path: Path) -> None:
    """A named file is used as is, and a missing one is refused by name."""
    given = _claude_transcript(tmp_path / "given.jsonl")

    assert cli.resolve_transcript("claude", str(given), {}) == given
    with pytest.raises(cli.CopyConversationError, match="Transcript file not found"):
        cli.resolve_transcript("claude", str(tmp_path / "absent.jsonl"), {})
    with pytest.raises(cli.CopyConversationError, match="CODEX_THREAD_ID is not set"):
        cli.resolve_transcript("codex", None, {})


def test_resolve_transcript_follows_the_session_variable(tmp_path: Path) -> None:
    """Without a file, the session variable of the host finds the transcript."""
    found = _claude_transcript(tmp_path / "projects" / "C--senv" / "s9.jsonl")
    environ = {"CLAUDE_CODE_SESSION_ID": "s9", "CLAUDE_CONFIG_DIR": str(tmp_path)}

    assert cli.resolve_transcript("claude", None, environ) == found


@pytest.mark.parametrize(
    ("session", "folder", "expected"),
    [
        ("senv-claude", "senv", "senv"),
        ("DEMO-CLAUDE", "git/demo", "demo qal"),
        ("other", "unlisted", None),
    ],
)
def test_tab_title_reads_the_tab_naming_the_session(
    tmp_path: Path,
    session: str,
    folder: str,
    expected: str | None,
) -> None:
    """Comments are skipped and project variables expand from the given env."""
    environ = {"USERPROFILE": str(tmp_path), "PRGS": str(tmp_path)}
    assert cli.tab_title(_TAB_LIST.splitlines(), session, tmp_path / folder, environ) == expected


def test_tab_title_ignores_session_lines_outside_a_tab(tmp_path: Path) -> None:
    """A `+` line before any tab, or without a session field, names nothing."""
    assert (
        cli.tab_title(
            [f"+ {tmp_path}|senv-claude", "=== t", f"+ {tmp_path}"],
            "senv-claude", tmp_path, {},
        )
        is None
    )


@pytest.mark.parametrize("session", ["stale", "current", ""])
def test_resolve_title_rejects_inherited_signals_for_another_project(
    tmp_path: Path,
    session: str,
) -> None:
    """A stale parent pane cannot title this checkout after another project."""
    tab_list = tmp_path / "tuitp.list"
    tab_list.write_text(
        "=== unrelated\n+ %USERPROFILE%/git/stale|stale||old\n"
        "=== llm-shared lifecycle-gate\n+ %userprofile%/git/current|current||gate\n",
        encoding="utf-8",
    )
    environ = {
        "TUIOS_SESSION": session,
        "TUITP_PROJECT": str(tmp_path / "git/stale"),
        "USERPROFILE": str(tmp_path),
    }
    assert (
        cli.resolve_title(environ, tab_list, tmp_path / "git/current")
        == "llm-shared lifecycle-gate"
    )


def test_resolve_title_uses_cwd_when_the_layout_cannot_identify_it(tmp_path: Path) -> None:
    """Absent or unrelated layouts fall back to cwd, never a stale project."""
    tab_list = tmp_path / "tuitp.list"
    tab_list.write_text(_TAB_LIST, encoding="utf-8")
    cwd = tmp_path / "work"
    environ = {"TUIOS_SESSION": "senv-claude", "TUITP_PROJECT": "C:\\git\\stale"}

    assert cli.resolve_title(environ, tab_list, cwd) == "work"
    assert cli.resolve_title(environ, tmp_path / "absent.list", cwd) == "work"
    assert cli.resolve_title(environ, None, cwd) == "work"


def test_tab_title_prefers_the_deepest_project_and_uses_path_boundaries(tmp_path: Path) -> None:
    """Nested checkouts beat parents; a shared string prefix is insufficient."""
    lines = [
        "=== parent", f"+ {tmp_path}|parent",
        "=== nested", f"+ {tmp_path / 'child'}|nested",
    ]
    assert cli.tab_title(lines, "parent", tmp_path / "child/tests", {}) == "nested"
    assert cli.tab_title(lines, "nested", tmp_path / "child-other", {}) == "parent"
    assert cli.tab_title(["=== invalid", "+ relative|bad"], "bad", tmp_path, {}) is None


@pytest.mark.parametrize(
    ("session", "expected"), [("SECOND", "second"), ("unknown", None)],
)
def test_tab_title_uses_session_only_to_disambiguate_matching_projects(
    tmp_path: Path,
    session: str,
    expected: str | None,
) -> None:
    """Multiple tabs of one checkout need a matching session, never list order."""
    lines = ["=== first", f"+ {tmp_path}|first", "=== second", f"+ {tmp_path}|second"]
    assert cli.tab_title(lines, session, tmp_path, {}) == expected


def test_default_tab_list_lives_in_the_home_bin_folder() -> None:
    """The tuitp list is looked up under HOME only when HOME is set."""
    assert (
        cli.default_tab_list({"HOME": "C:\\home"})
        == Path("C:\\home") / "bin" / "tuitp.list"
    )
    assert cli.default_tab_list({}) is None


def test_parse_date_and_today() -> None:
    """A compact date parses; anything else is refused; today is a real date."""
    assert cli.parse_date("20261104") == date(2026, 11, 4)
    with pytest.raises(cli.CopyConversationError, match="Not a YYYYMMDD date"):
        cli.parse_date("2026-11-04")
    assert isinstance(cli.today(), date)


def test_build_copy_puts_the_title_line_and_one_empty_line_first() -> None:
    """The first line is the title and a colon, the second is empty."""
    assert cli.build_copy("senv", "❯ hello") == "senv:\n\n❯ hello"


@pytest.mark.parametrize(
    ("resolved", "expected"),
    [
        ({"pwsh": "C:/pwsh.exe"}, "C:/pwsh.exe"),
        ({"powershell": "C:/ps.exe"}, "C:/ps.exe"),
        ({}, "powershell"),
    ],
)
def test_powershell_executable_prefers_the_modern_shell(
    monkeypatch: pytest.MonkeyPatch,
    resolved: dict[str, str],
    expected: str,
) -> None:
    """PowerShell resolution tries pwsh, then powershell, then the bare name."""
    monkeypatch.setattr(cli.shutil, "which", resolved.get)

    assert cli.powershell_executable() == expected


def test_set_clipboard_text_hands_over_a_utf8_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The text reaches PowerShell through a file it reads as UTF-8."""
    seen: list[str] = []

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        literal = command[-1].split("-LiteralPath '", 1)[1].removesuffix("')")
        seen.extend(
            [command[-1], Path(literal.replace("''", "'")).read_text(encoding="utf-8")],
        )
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(cli, "powershell_executable", lambda: "powershell")
    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    cli.powershell_clipboard("senv:\n\n❯ hello")

    assert seen[0].startswith("[Console]::OutputEncoding")
    assert seen[1] == "senv:\n\n❯ hello"


def test_set_clipboard_text_reports_a_powershell_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing PowerShell surfaces as a copy error."""

    def fake_run(command: list[str], **kwargs: object) -> None:
        del kwargs
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(cli, "powershell_executable", lambda: "powershell")
    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    with pytest.raises(
        cli.CopyConversationError,
        match="Failed to reach the clipboard",
    ):
        cli.powershell_clipboard("x")


@pytest.mark.parametrize(("os_name", "used"), [("nt", "win32"), ("posix", "powershell")])
def test_set_clipboard_text_uses_the_windows_api_on_windows_only(
    monkeypatch: pytest.MonkeyPatch,
    os_name: str,
    used: str,
) -> None:
    """Windows skips the one-second PowerShell start; other systems keep it."""
    seen: list[tuple[str, str]] = []

    def win32(text: str) -> None:
        seen.append(("win32", text))

    def powershell(text: str) -> None:
        seen.append(("powershell", text))

    monkeypatch.setattr(cli, "win32_clipboard", win32)
    monkeypatch.setattr(cli, "powershell_clipboard", powershell)
    monkeypatch.setattr(cli.os, "name", os_name)

    cli.set_clipboard_text("x")

    assert seen == [(used, "x")]


class _FakeClipboardApi:
    """Stand in for user32 and kernel32, writing into a real buffer."""

    def __init__(self, *, opens: bool = True, allocates: bool = True, accepts: bool = True) -> None:
        self.opens, self.allocates, self.accepts = opens, allocates, accepts
        self.buffer = ctypes.create_string_buffer(64)
        self.calls: list[tuple[object, ...]] = []

    def OpenClipboard(self, owner: None) -> int:
        self.calls.append(("open", owner))
        return int(self.opens)

    def EmptyClipboard(self) -> int:
        self.calls.append(("empty",))
        return 1

    def GlobalAlloc(self, flags: int, size: int) -> int:
        self.calls.append(("alloc", flags, size))
        return 7 if self.allocates else 0

    def GlobalLock(self, handle: int) -> int:
        self.calls.append(("lock", handle))
        return ctypes.addressof(self.buffer)

    def GlobalUnlock(self, handle: int) -> int:
        self.calls.append(("unlock", handle))
        return 0

    def SetClipboardData(self, data_format: int, handle: int) -> int:
        self.calls.append(("set", data_format, handle))
        return handle if self.accepts else 0

    def GlobalFree(self, handle: int) -> int:
        self.calls.append(("free", handle))
        return 0

    def CloseClipboard(self) -> int:
        self.calls.append(("close",))
        return 1


def test_win32_clipboard_hands_over_null_terminated_utf16_text() -> None:
    """The markers survive as Unicode text, and the clipboard is closed again."""
    api = _FakeClipboardApi()

    cli.win32_clipboard("❯ é", (api, api))

    data = "❯ é".encode("utf-16-le") + b"\0\0"
    assert api.buffer.raw[: len(data)] == data
    assert api.calls == [
        ("open", None), ("empty",), ("alloc", 2, len(data)), ("lock", 7), ("unlock", 7),
        ("set", 13, 7), ("close",),
    ]


@pytest.mark.parametrize(
    ("allocates", "accepts", "freed"), [(True, False, [("free", 7)]), (False, True, [])],
)
def test_win32_clipboard_frees_and_reports_a_refused_text(
    allocates: bool,  # noqa: FBT001
    accepts: bool,  # noqa: FBT001
    freed: list[tuple[object, ...]],
) -> None:
    """Memory the clipboard did not take is freed; the clipboard still closes."""
    api = _FakeClipboardApi(allocates=allocates, accepts=accepts)

    with pytest.raises(cli.CopyConversationError, match="Windows refused the text"):
        cli.win32_clipboard("x", (api, api))

    assert [call for call in api.calls if call[0] == "free"] == freed
    assert api.calls[-1] == ("close",)


def _no_sleep(seconds: float) -> None:
    del seconds


def test_win32_clipboard_reports_a_clipboard_held_open(monkeypatch: pytest.MonkeyPatch) -> None:
    """Another program holding the clipboard ends the run after a few retries."""
    api = _FakeClipboardApi(opens=False)
    monkeypatch.setattr(cli.time, "sleep", _no_sleep)

    with pytest.raises(cli.CopyConversationError, match="another program keeps it open"):
        cli.win32_clipboard("x", (api, api))

    assert api.calls == [("open", None)] * cli._OPEN_ATTEMPTS


@pytest.mark.skipif(os.name != "nt", reason="user32 and kernel32 exist on Windows only")
def test_win32_api_declares_handle_sized_results() -> None:
    """64-bit handles and pointers are not truncated to a C int."""
    user32, kernel32 = cli._win32_api()

    assert kernel32.GlobalAlloc.restype is not None
    assert kernel32.GlobalLock.restype is not None
    assert user32.SetClipboardData.restype is not None


def test_main_writes_the_trimmed_copy_without_the_clipboard(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A named transcript, title and output file need no session at all."""
    transcript = _claude_transcript(tmp_path / "s.jsonl")
    output = tmp_path / "copy.txt"

    assert (
        cli.main(
            [
                "claude",
                "--transcript",
                str(transcript),
                "--title",
                "senv",
                "--output",
                str(output),
                "--no-clipboard",
            ],
        )
        == 0
    )

    assert output.read_text(encoding="utf-8") == "senv:\n\n❯ hello\n\n● hi"
    assert capsys.readouterr().out == (
        "copy-conversation (claude): s.jsonl rendered to 3 lines, 3 kept under 'senv:'. Clipboard unchanged.\n"
    )


def test_main_detects_codex_and_titles_the_copy_from_the_tab(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The running Codex thread is found, trimmed, titled and published."""
    rollout = (
        tmp_path / "codex" / "sessions" / "2026" / "11" / "04" / "rollout-x-t1.jsonl"
    )
    rollout.parent.mkdir(parents=True)
    lines = [
        {
            "type": "event_msg",
            "payload": {"type": "user_message", "message": "20261103 start"},
        },
        {"type": "event_msg", "payload": {"type": "agent_message", "message": "done"}},
    ]
    rollout.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "tuitp.list").write_text(
        f"=== senv\n+ {tmp_path}|senv-claude|claude\n", encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    for name, value in {
        "CODEX_THREAD_ID": "t1",
        "CODEX_HOME": str(tmp_path / "codex"),
        "HOME": str(tmp_path),
        "TUIOS_SESSION": "senv-claude",
    }.items():
        monkeypatch.setenv(name, value)
    published: list[str] = []
    monkeypatch.setattr(cli, "set_clipboard_text", published.append)

    assert cli.main(["--date", "20261103"]) == 0

    assert published == ["senv:\n\n20261103 start\n\n## Assistant\n\ndone"]
    assert capsys.readouterr().out.endswith(
        "under 'senv:'. Ready to paste from clipboard.\n",
    )


@pytest.mark.parametrize(
    ("option", "positional", "extra"),
    [(None, None, None), ("20261103", None, date(2026, 11, 3)), (None, "20261102", date(2026, 11, 2))],
)
def test_trim_dates_takes_the_extra_date_as_option_or_bare_word(
    monkeypatch: pytest.MonkeyPatch,
    option: str | None,
    positional: str | None,
    extra: date | None,
) -> None:
    """The skill passes the user's words as typed, so a bare date counts too."""
    monkeypatch.setattr(cli, "today", lambda: date(2026, 11, 5))
    expected = (date(2026, 11, 5), extra) if extra else (date(2026, 11, 5),)
    assert cli.trim_dates(option, positional) == expected
    with pytest.raises(cli.CopyConversationError, match="Give the extra date once"):
        cli.trim_dates("20261103", "20261102")


def test_main_trims_from_a_bare_date_after_the_host(tmp_path: Path) -> None:
    """`claude 20261103` drops the lines before the prompt stamped with that date."""
    transcript = tmp_path / "s.jsonl"
    entries = [
        {"type": "user", "origin": {"kind": "human"}, "message": {"content": prompt}}
        for prompt in ("before", "20261103 start")
    ]
    transcript.write_text("\n".join(json.dumps(entry) for entry in entries), encoding="utf-8")
    output = tmp_path / "copy.txt"
    argv = ["claude", "20261103", "--transcript", str(transcript), "--title", "t"]

    assert cli.main([*argv, "--output", str(output), "--no-clipboard"]) == 0
    assert output.read_text(encoding="utf-8") == "t:\n\n❯ 20261103 start"


def test_main_refuses_a_chat_with_nothing_before_the_request(tmp_path: Path) -> None:
    """A cleared chat's transcript holds only the request, which is cut: no copy."""
    transcript = _claude_transcript(tmp_path / "new.jsonl", "/copy-conversation")

    with pytest.raises(cli.CopyConversationError, match=r"Nothing to copy: new\.jsonl"):
        cli.main(["claude", "--transcript", str(transcript), "--no-clipboard"])


def test_log_fatal_and_script_main_exit_with_code_two(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A fatal error is reported once on stderr and ends the run with code 2."""
    script_path = Path(cli.__file__)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(script_path), "claude", "--transcript", str(tmp_path / "absent.jsonl")],
    )

    with pytest.raises(SystemExit) as excinfo:
        run_main(str(script_path))

    assert excinfo.value.code == _FATAL_EXIT_CODE
    assert capsys.readouterr().err.startswith("ERROR: Transcript file not found")


# eof
