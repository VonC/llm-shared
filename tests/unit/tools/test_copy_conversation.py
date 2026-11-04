"""Tests for the command line of `tools.copy_conversation`.

Host detection, transcript lookup, the tab title, the clipboard boundary and
the entry point. The clipboard is always replaced: no test starts PowerShell.
"""

from __future__ import annotations

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
# ruff: noqa: RUF001, SLF001

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
    ("session", "expected"),
    [("senv-claude", "senv"), ("DEMO-CLAUDE", "demo qal"), ("other", None)],
)
def test_tab_title_reads_the_tab_naming_the_session(
    session: str,
    expected: str | None,
) -> None:
    """Comments are skipped, and a session matches without case."""
    assert cli.tab_title(_TAB_LIST.splitlines(), session) == expected


def test_tab_title_ignores_session_lines_outside_a_tab() -> None:
    """A `+` line before any tab, or without a session field, names nothing."""
    assert (
        cli.tab_title(["+ C:\\x|senv-claude", "=== t", "+ C:\\x"], "senv-claude")
        is None
    )


def test_resolve_title_falls_back_from_the_tab_to_the_project(tmp_path: Path) -> None:
    """The tab title wins; then the tuitp project folder; then the directory."""
    tab_list = tmp_path / "tuitp.list"
    tab_list.write_text(_TAB_LIST, encoding="utf-8")
    cwd = tmp_path / "work"

    assert cli.resolve_title({"TUIOS_SESSION": "senv-claude"}, tab_list, cwd) == "senv"
    assert (
        cli.resolve_title(
            {"TUIOS_SESSION": "other", "TUITP_PROJECT": "C:\\git\\proj"},
            tab_list,
            cwd,
        )
        == "proj"
    )
    assert (
        cli.resolve_title(
            {"TUIOS_SESSION": "senv-claude"},
            tmp_path / "absent.list",
            cwd,
        )
        == "work"
    )
    assert cli.resolve_title({"TUIOS_SESSION": "senv-claude"}, None, cwd) == "work"


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
    cli.set_clipboard_text("senv:\n\n❯ hello")

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
        cli.set_clipboard_text("x")


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
    (tmp_path / "bin" / "tuitp.list").write_text(_TAB_LIST, encoding="utf-8")
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
