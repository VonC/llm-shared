"""trim_thinking_cli.py.

Command line front end for `tools.trim_thinking`.

It reads one exported LLM conversation from a file argument or, with no
argument, from the Windows clipboard, trims the reflection blocks out of it,
writes the trimmed conversation back to the clipboard, and prints one
confirmation line to stdout.

Clipboard access goes through PowerShell. The trimmed text is handed over in a
UTF-8 temporary file rather than on standard input, because PowerShell decodes
a redirected standard input with the console code page and would mangle the
export markers.
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools.trim_thinking import (
    TranscriptFormat,
    TrimThinkingError,
    build_summary_line,
    trim_transcript,
)

DATE_FORMAT = "%Y%m%d"
_DATE_ARGUMENT_PATTERN = re.compile(r"^\d{8}$")

LOGGER = logging.getLogger("trim_thinking")

AUTO_FORMAT = "auto"

_CLIPBOARD_PREAMBLE = (
    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
    "$PSModuleAutoloadingPreference = 'None'; "
    "Import-Module Microsoft.PowerShell.Management; "
)


class ClipboardError(TrimThinkingError):
    """Raised when a clipboard read or write fails."""


class InputFileNotFoundError(TrimThinkingError):
    """Raised when the transcript file given on the command line is missing."""


class EmptySourceError(TrimThinkingError):
    """Raised when the file or the clipboard holds no text to trim."""


class InvalidDateError(TrimThinkingError):
    """Raised when the extra argument is not a YYYYMMDD date."""


def _parse_date(value: str) -> date:
    """Turn one YYYYMMDD argument into a date.

    Args:
        value: The argument text.

    Returns:
        The date it names.

    Raises:
        InvalidDateError: When it is not a valid YYYYMMDD date.
    """
    try:
        return datetime.strptime(value, DATE_FORMAT).astimezone().date()
    except ValueError as err:
        msg = f"Not a YYYYMMDD date: {value}"
        raise InvalidDateError(msg) from err


def _today() -> date:
    """Return the current local date, as a seam the tests can freeze."""
    return date.today()  # noqa: DTZ011


def _resolve_dates(extra: str | None, today: date) -> tuple[date, ...]:
    """Return the dates a dated prompt line is matched against.

    Args:
        extra: The optional YYYYMMDD argument, or None.
        today: The current date.

    Returns:
        Today alone, or today and the given date.
    """
    if extra is None:
        return (today,)
    return (today, _parse_date(extra))


def _configure_logging(*, debug: bool) -> None:
    """Configure logging to stdout with message-only formatting."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def _powershell_executable() -> str:
    """Resolve the PowerShell executable used for clipboard access."""
    return shutil.which("pwsh") or shutil.which("powershell") or "powershell"


def _run_clipboard_command(script: str) -> str:
    """Run one PowerShell clipboard command and return its stdout text.

    Args:
        script: PowerShell statement appended to the clipboard preamble.

    Returns:
        The standard output of the command.

    Raises:
        ClipboardError: When PowerShell cannot be run or reports a failure.
    """
    try:
        result = subprocess.run(  # noqa: S603
            [
                _powershell_executable(),
                "-noprofile",
                "-ExecutionPolicy",
                "Bypass",
                "-command",
                _CLIPBOARD_PREAMBLE + script,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except (OSError, subprocess.SubprocessError) as err:
        msg = f"Failed to reach the clipboard through PowerShell: {err}"
        raise ClipboardError(msg) from err

    return result.stdout or ""


def _get_clipboard_text() -> str:
    """Get the clipboard text, without the newline PowerShell appends."""
    return _run_clipboard_command("Get-Clipboard -Raw").rstrip("\r\n")


def _set_clipboard_text(text: str) -> None:
    """Set the clipboard text, handing it over as a UTF-8 temporary file."""
    with tempfile.TemporaryDirectory(prefix="trim_thinking_") as directory:
        payload = Path(directory) / "clipboard.txt"
        payload.write_text(text, encoding="utf-8")
        literal = str(payload).replace("'", "''")
        _run_clipboard_command(
            f"Set-Clipboard -Value (Get-Content -Raw -Encoding UTF8 "
            f"-LiteralPath '{literal}')",
        )


def _read_source_text(source: str | None) -> str:
    """Read the conversation to trim from a file, or from the clipboard.

    Args:
        source: Path of the export file, or None to read the clipboard.

    Returns:
        The text to trim.

    Raises:
        InputFileNotFoundError: When the given path does not exist.
        EmptySourceError: When the resolved source holds no text.
    """
    if source is None:
        text = _get_clipboard_text()
        origin = "clipboard"
    else:
        path = Path(source)
        if not path.is_file():
            msg = f"Transcript file not found: {path}"
            raise InputFileNotFoundError(msg)
        # utf-8-sig, not utf-8: an editor or a PowerShell redirect can leave a
        # byte-order mark, and a leading U+FEFF stops the first line matching
        # the prompt marker, so the opening turn of the file is dropped in
        # silence. Reading it away costs nothing when there is none.
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        origin = str(path)

    if not text.strip():
        msg = f"No text to trim in the {origin}."
        raise EmptySourceError(msg)

    return text


def _resolve_format(choice: str) -> TranscriptFormat | None:
    """Turn the `--format` choice into a format, or None for auto-detection."""
    if choice == AUTO_FORMAT:
        return None
    return TranscriptFormat(choice)


def _get_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Remove the reflection blocks from an exported LLM conversation "
            "and copy the trimmed conversation to the clipboard."
        ),
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=None,
        help="Export file to trim. With no file, the clipboard is trimmed.",
    )
    parser.add_argument(
        "--format",
        dest="transcript_format",
        default=AUTO_FORMAT,
        choices=[AUTO_FORMAT, *(member.value for member in TranscriptFormat)],
        help="Export format. Detected from the markers by default.",
    )
    parser.add_argument(
        "date",
        nargs="?",
        default=None,
        help=(
            "Extra YYYYMMDD date. A prompt line stamped with it, or with "
            "today's date, removes every preceding line."
        ),
    )
    parser.add_argument(
        "--date",
        dest="date_option",
        default=None,
        help="Same as the positional date, for a call that passes no source.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def _split_source_and_date(args: argparse.Namespace) -> tuple[str | None, str | None]:
    """Separate the source from the date across both accepted call shapes.

    A single positional argument is the date when it looks like one, so
    `tth 20260903` needs no flag; otherwise it is the export file.

    Args:
        args: Parsed command line.

    Returns:
        The source path or None, and the YYYYMMDD text or None.
    """
    if args.date_option is not None:
        return args.source, args.date_option
    if args.date is not None:
        return args.source, args.date
    if args.source is not None and _DATE_ARGUMENT_PATTERN.match(args.source):
        return None, args.source
    return args.source, None


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _get_arg_parser()
    args = parser.parse_args(argv)
    _configure_logging(debug=args.debug)

    source, extra_date = _split_source_and_date(args)
    # Today always counts, so a bare call still removes everything before a
    # prompt stamped with today's date. The argument only adds a second date.
    dates = _resolve_dates(extra_date, _today())
    text = _read_source_text(source)
    result = trim_transcript(text, _resolve_format(args.transcript_format), dates)
    _set_clipboard_text(result.text)
    LOGGER.info(build_summary_line(result))
    return 0


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with code 2."""
    _configure_logging(debug=False)
    LOGGER.error("ERROR: %s", err)
    raise SystemExit(2) from err


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (TrimThinkingError, OSError) as err:
        _log_fatal(err)


# eof
