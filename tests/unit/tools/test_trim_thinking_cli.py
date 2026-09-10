"""Tests for the trimming command line and its clipboard boundary.

Cover logging setup, PowerShell resolution, the clipboard read and write
helpers, source resolution, argument parsing, the entry point, and the fatal
exit path of `tools.trim_thinking_cli`.
"""

from __future__ import annotations

import logging
import runpy
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools import trim_thinking as trimmer
from tools import trim_thinking_cli as cli

if TYPE_CHECKING:
    from collections.abc import Generator

# pyright: reportPrivateUsage=false, reportUnusedFunction=false
# ruff: noqa: RUF001, RUF002, SLF001

_FATAL_EXIT_CODE = 2

_CLAUDE_EXPORT = (
    "❯ the question\n● opening\n● Bash(ls)\n  ⎿ output\n● the answer\n✻ done\n"
)
_TRIMMED_CLAUDE_EXPORT = "❯ the question\n● opening\n● the answer\n✻ done"


@pytest.fixture(autouse=True)
def _restored_root_logger() -> Generator[None]:
    """Keep the root logger of the test session out of the CLI setup."""
    root_logger = logging.getLogger()
    handlers = list(root_logger.handlers)
    level = root_logger.level
    try:
        yield
    finally:
        root_logger.handlers.clear()
        root_logger.handlers.extend(handlers)
        root_logger.setLevel(level)


def test_configure_logging_sends_messages_to_stdout() -> None:
    """Logging setup should own the root logger and follow the debug flag."""
    cli._configure_logging(debug=True)
    root_logger = logging.getLogger()

    assert root_logger.level == logging.DEBUG
    assert len(root_logger.handlers) == 1
    assert getattr(root_logger.handlers[0], "stream", None) is sys.stdout

    cli._configure_logging(debug=False)

    assert root_logger.level == logging.INFO


@pytest.mark.parametrize(
    ("resolved", "expected"),
    [
        ({"pwsh": "C:/pwsh.exe"}, "C:/pwsh.exe"),
        ({"powershell": "C:/powershell.exe"}, "C:/powershell.exe"),
        ({}, "powershell"),
    ],
)
def test_powershell_executable_prefers_the_modern_shell(
    monkeypatch: pytest.MonkeyPatch,
    resolved: dict[str, str],
    expected: str,
) -> None:
    """PowerShell resolution should try pwsh, then powershell, then the name."""

    def fake_which(name: str) -> str | None:
        return resolved.get(name)

    monkeypatch.setattr(cli.shutil, "which", fake_which)

    assert cli._powershell_executable() == expected


def test_run_clipboard_command_passes_the_preamble_and_returns_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The clipboard command should carry the UTF-8 preamble to PowerShell."""
    commands: list[list[str]] = []

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="clipboard text\r\n")

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli._get_clipboard_text() == "clipboard text"
    assert commands[0][-1].startswith("[Console]::OutputEncoding")
    assert commands[0][-1].endswith("Get-Clipboard -Raw")


def test_run_clipboard_command_reports_a_powershell_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing or missing PowerShell should surface as a clipboard error."""

    def fake_failing_run(command: list[str], **kwargs: object) -> None:
        del kwargs
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(cli.subprocess, "run", fake_failing_run)

    with pytest.raises(cli.ClipboardError, match="Failed to reach the clipboard"):
        cli._get_clipboard_text()


def test_set_clipboard_text_hands_the_payload_over_as_a_utf8_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The trimmed text should reach PowerShell through a UTF-8 file, not stdin."""
    payloads: list[str] = []

    def fake_run_clipboard_command(script: str) -> str:
        literal = script[script.index("'") + 1 : script.rindex("'")]
        payloads.append(Path(literal).read_text(encoding="utf-8"))
        return ""

    monkeypatch.setattr(cli, "_run_clipboard_command", fake_run_clipboard_command)

    cli._set_clipboard_text(_TRIMMED_CLAUDE_EXPORT)

    assert payloads == [_TRIMMED_CLAUDE_EXPORT]


def test_read_source_text_reads_the_named_file(tmp_path: Path) -> None:
    """A file argument should be read as UTF-8."""
    export = tmp_path / "export.txt"
    export.write_text(_CLAUDE_EXPORT, encoding="utf-8")

    assert cli._read_source_text(str(export)) == _CLAUDE_EXPORT


def test_read_source_text_strips_a_byte_order_mark(tmp_path: Path) -> None:
    """A BOM must not survive: it would hide the first prompt of the file.

    An editor, or a PowerShell redirect, can open a transcript with U+FEFF.
    Left in place it stops the first line matching the prompt marker, and the
    opening turn is then dropped without a word.
    """
    export = tmp_path / "export.txt"
    export.write_text(_CLAUDE_EXPORT, encoding="utf-8-sig")

    text = cli._read_source_text(str(export))

    assert text == _CLAUDE_EXPORT
    assert text.startswith(trimmer.PROMPT_MARKER)


def test_read_source_text_falls_back_to_the_clipboard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no file argument the clipboard is the source."""
    monkeypatch.setattr(cli, "_get_clipboard_text", lambda: _CLAUDE_EXPORT)

    assert cli._read_source_text(None) == _CLAUDE_EXPORT


def test_read_source_text_rejects_a_missing_file(tmp_path: Path) -> None:
    """A missing file argument should name the path that was not found."""
    with pytest.raises(cli.InputFileNotFoundError, match="Transcript file not found"):
        cli._read_source_text(str(tmp_path / "absent.txt"))


def test_read_source_text_rejects_an_empty_clipboard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty source should stop the run before anything is overwritten."""
    monkeypatch.setattr(cli, "_get_clipboard_text", lambda: "   \n")

    with pytest.raises(cli.EmptySourceError, match="No text to trim in the clipboard"):
        cli._read_source_text(None)


def test_resolve_format_maps_auto_to_detection() -> None:
    """The auto choice means no forced format; the others map to the enum."""
    assert cli._resolve_format(cli.AUTO_FORMAT) is None
    assert cli._resolve_format("codex") is trimmer.TranscriptFormat.CODEX


def test_get_arg_parser_exposes_the_source_format_and_debug_options() -> None:
    """The parser should default to the clipboard, auto-detection, and no debug."""
    parser = cli._get_arg_parser()

    defaults = parser.parse_args([])
    assert defaults.source is None
    assert defaults.transcript_format == cli.AUTO_FORMAT
    assert defaults.debug is False

    parsed = parser.parse_args(["export.txt", "--format", "claude", "--debug"])
    assert parsed.source == "export.txt"
    assert parsed.transcript_format == "claude"
    assert parsed.debug is True


def test_main_trims_the_file_and_publishes_one_summary_line(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """The entry point should set the clipboard and log a single ready line."""
    export = tmp_path / "export.txt"
    export.write_text(_CLAUDE_EXPORT, encoding="utf-8")
    published: list[str] = []

    def fake_configure_logging(*, debug: bool) -> None:
        del debug

    monkeypatch.setattr(cli, "_configure_logging", fake_configure_logging)
    monkeypatch.setattr(cli, "_set_clipboard_text", published.append)
    caplog.set_level(logging.INFO)

    assert cli.main([str(export)]) == 0
    assert published == [_TRIMMED_CLAUDE_EXPORT]
    assert "trim-thinking (claude)" in caplog.text
    assert "Ready to paste from clipboard." in caplog.text


def test_log_fatal_and_script_main_convert_failures_into_exit_code_two(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A fatal error should be logged once and end the run with exit code 2."""
    with pytest.raises(SystemExit) as excinfo:
        cli._log_fatal(cli.EmptySourceError("boom"))
    assert excinfo.value.code == _FATAL_EXIT_CODE

    script_path = Path(cli.__file__)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(script_path), str(tmp_path / "absent.txt")],
    )

    with pytest.raises(SystemExit) as script_excinfo:
        runpy.run_path(str(script_path), run_name="__main__")

    assert script_excinfo.value.code == _FATAL_EXIT_CODE


_DAY = date(2026, 9, 3)


def test_parse_date_accepts_yyyymmdd_and_rejects_anything_else() -> None:
    """The extra argument is read as a compact date, or refused by name."""
    assert cli._parse_date("20260903") == _DAY

    with pytest.raises(cli.InvalidDateError, match="Not a YYYYMMDD date"):
        cli._parse_date("2026-09-03")


def test_resolve_dates_always_keeps_today() -> None:
    """Today matches with or without the extra argument."""
    assert cli._resolve_dates(None, _DAY) == (_DAY,)
    assert cli._resolve_dates("20251231", _DAY) == (_DAY, date(2025, 12, 31))


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        ([], (None, None)),
        (["export.md"], ("export.md", None)),
        (["20260903"], (None, "20260903")),
        (["export.md", "20260903"], ("export.md", "20260903")),
        (["--date", "20260903"], (None, "20260903")),
        (["export.md", "--date", "20260903"], ("export.md", "20260903")),
    ],
)
def test_split_source_and_date_reads_every_call_shape(
    argv: list[str],
    expected: tuple[str | None, str | None],
) -> None:
    """A lone date needs no flag, and a lone path is still a path."""
    args = cli._get_arg_parser().parse_args(argv)

    assert cli._split_source_and_date(args) == expected


def test_main_drops_every_line_before_an_explicitly_dated_prompt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The dated pass reaches the clipboard through the entry point."""
    export = tmp_path / "export.md"
    export.write_text(
        "❯ first ask\n● opening\n● the answer\n✻ done\n"
        "※ recap before the dated turn\n"
        "❯ 20260903 the dated ask\n● opening two\n● answer two\n✻ done two\n",
        encoding="utf-8",
    )
    published: list[str] = []
    monkeypatch.setattr(cli, "_set_clipboard_text", published.append)

    assert cli.main([str(export), "20260903"]) == 0

    assert published == [
        "❯ 20260903 the dated ask\n● opening two\n● answer two\n✻ done two",
    ]


def test_today_seam_reports_the_current_date() -> None:
    """The seam the tests freeze must really return today."""
    assert cli._today() == date.today()  # noqa: DTZ011


def test_main_uses_today_when_no_date_argument_is_given(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A bare call truncates at a prompt stamped with today."""
    export = tmp_path / "export.md"
    export.write_text(
        "❯ first ask\n● opening\n● the answer\n✻ done\n"
        "※ recap before the dated turn\n"
        "❯ 20260903 the dated ask\n● opening two\n● answer two\n✻ done two\n",
        encoding="utf-8",
    )
    published: list[str] = []
    monkeypatch.setattr(cli, "_set_clipboard_text", published.append)
    monkeypatch.setattr(cli, "_today", lambda: _DAY)

    assert cli.main([str(export)]) == 0

    assert published == [
        "❯ 20260903 the dated ask\n● opening two\n● answer two\n✻ done two",
    ]


def test_main_keeps_the_transcript_before_another_days_prompt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A prompt stamped with a different day leaves the transcript intact."""
    export = tmp_path / "export.md"
    export.write_text(
        "❯ first ask\n● opening\n● the answer\n✻ done\n"
        "※ recap before the dated turn\n"
        "❯ 20251231 the dated ask\n● opening two\n● answer two\n✻ done two\n",
        encoding="utf-8",
    )
    published: list[str] = []
    monkeypatch.setattr(cli, "_set_clipboard_text", published.append)
    monkeypatch.setattr(cli, "_today", lambda: _DAY)

    assert cli.main([str(export)]) == 0

    assert "❯ first ask" in published[0]
    assert "※ recap before the dated turn" in published[0]


# eof
