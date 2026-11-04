r"""copy_conversation.py.

Copy the conversation of the running agent session to the clipboard, trimmed.

One call renders the session's own transcript as an export, trims it exactly
as `tth` does (`tools.trim_thinking.trim_transcript`, with today's date and an
optional extra one), and publishes it under a title line:

    <tab title>:

    <trimmed conversation>

- Host: `claude` or `codex`, given or detected from `CLAUDE_CODE_SESSION_ID`
  and `CODEX_THREAD_ID`, the session ids both hosts export to their shells.
- Transcript: `~/.claude/projects/*/<session id>.jsonl` (`CLAUDE_CONFIG_DIR`
  replaces `~/.claude`), or `~/.codex/sessions/**/rollout-*-<thread id>.jsonl`
  (`CODEX_HOME` replaces `~/.codex`); `--transcript` names one directly.
- Title: `--title`; otherwise the tab of a tuitp list (`%HOME%\\bin\\tuitp.list`
  by default) whose `+` line names the `TUIOS_SESSION` of the pane; otherwise
  the folder name of `TUITP_PROJECT` or of the current directory.

The clipboard is written through PowerShell from a UTF-8 temporary file, as
`tth` does, because a redirected standard input would mangle the markers.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools.copy_conversation_claude import render_claude_transcript
from tools.copy_conversation_codex import render_codex_rollout
from tools.trim_thinking import TranscriptFormat, TrimThinkingError, trim_transcript

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence

CLAUDE = "claude"
CODEX = "codex"
HOSTS = (CLAUDE, CODEX)
SESSION_VARIABLES = {CLAUDE: "CLAUDE_CODE_SESSION_ID", CODEX: "CODEX_THREAD_ID"}
DATE_FORMAT = "%Y%m%d"

_RENDERERS: dict[str, Callable[[Iterable[str]], str]] = {
    CLAUDE: render_claude_transcript,
    CODEX: render_codex_rollout,
}
_FORMATS = {CLAUDE: TranscriptFormat.CLAUDE, CODEX: TranscriptFormat.CODEX}
_TAB_PATTERN = re.compile(r"^===\s+(?P<title>\S.*?)\s*$")
_SESSION_LINE_PATTERN = re.compile(r"^\+\s*(?P<fields>.*)$")
_CLIPBOARD_PREAMBLE = (
    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
    "$PSModuleAutoloadingPreference = 'None'; "
    "Import-Module Microsoft.PowerShell.Management; "
)


class CopyConversationError(Exception):
    """Raised when the conversation cannot be found, read or published."""


def detect_host(environ: Mapping[str, str]) -> str:
    """Return the host whose session variable is set.

    Args:
        environ: The process environment.

    Returns:
        `claude` or `codex`.

    Raises:
        CopyConversationError: When neither or both variables are set.
    """
    found = [host for host in HOSTS if environ.get(SESSION_VARIABLES[host])]
    if len(found) == 1:
        return found[0]
    names = " and ".join(SESSION_VARIABLES.values())
    state = "Both" if found else "Neither"
    msg = f"{state} of {names} is set: pass the host, claude or codex."
    raise CopyConversationError(msg)


def _newest(paths: Iterable[Path], description: str) -> Path:
    """Return the most recently written path, or fail naming what was sought."""
    candidates = sorted(paths, key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        msg = f"No transcript found for {description}: pass --transcript."
        raise CopyConversationError(msg)
    return candidates[0]


def find_transcript(host: str, session_id: str, environ: Mapping[str, str]) -> Path:
    """Find the transcript of one Claude session or Codex thread.

    Args:
        host: `claude` or `codex`.
        session_id: The session or thread id.
        environ: The process environment, for the host home overrides.

    Returns:
        The newest matching transcript.
    """
    if host == CLAUDE:
        root = Path(environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
        matches = (root / "projects").glob(f"*/{session_id}.jsonl")
    else:
        root = Path(environ.get("CODEX_HOME") or Path.home() / ".codex")
        matches = (root / "sessions").rglob(f"rollout-*-{session_id}.jsonl")
    return _newest(matches, f"{host} session {session_id} under {root}")


def resolve_transcript(
    host: str,
    explicit: str | None,
    environ: Mapping[str, str],
) -> Path:
    """Return the transcript to copy: the given one, or the running session's.

    Raises:
        CopyConversationError: When the given file is missing, or the session
            variable of the host is unset.
    """
    if explicit is not None:
        path = Path(explicit)
        if not path.is_file():
            msg = f"Transcript file not found: {path}"
            raise CopyConversationError(msg)
        return path
    session_id = environ.get(SESSION_VARIABLES[host])
    if not session_id:
        msg = f"{SESSION_VARIABLES[host]} is not set: pass --transcript."
        raise CopyConversationError(msg)
    return find_transcript(host, session_id, environ)


def tab_title(list_lines: Iterable[str], session: str) -> str | None:
    """Return the title of the tuitp tab holding one tuios session.

    A tab opens on a `=== <title>` line; each `+ folder|session|kind|id` line
    under it names one session. Lines starting with `#` are comments.

    Args:
        list_lines: Lines of the tuitp list.
        session: The tuios session name, compared without case.

    Returns:
        The tab title, or None when no tab names the session.
    """
    title: str | None = None
    for line in list_lines:
        stripped = line.strip()
        if (tab := _TAB_PATTERN.match(stripped)) is not None:
            title = tab.group("title")
            continue
        entry = _SESSION_LINE_PATTERN.match(stripped)
        if entry is None or title is None:
            continue
        fields = entry.group("fields").split("|")
        if len(fields) > 1 and fields[1].strip().casefold() == session.casefold():
            return title
    return None


def default_tab_list(environ: Mapping[str, str]) -> Path | None:
    r"""Return the tuitp list under `%HOME%\\bin`, when HOME is set."""
    home = environ.get("HOME")
    return Path(home) / "bin" / "tuitp.list" if home else None


def resolve_title(environ: Mapping[str, str], tab_list: Path | None, cwd: Path) -> str:
    """Return the title line text for the copy.

    Args:
        environ: The process environment.
        tab_list: The tuitp list to read, or None.
        cwd: The current directory, the last fallback.

    Returns:
        The tab title of the pane's session, else a project folder name.
    """
    session = environ.get("TUIOS_SESSION")
    if session and tab_list is not None and tab_list.is_file():
        lines = tab_list.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        if (title := tab_title(lines, session)) is not None:
            return title
    project = environ.get("TUITP_PROJECT")
    return Path(project).name if project else cwd.name


def parse_date(value: str) -> date:
    """Turn one YYYYMMDD argument into a date.

    Raises:
        CopyConversationError: When it is not a valid YYYYMMDD date.
    """
    try:
        return datetime.strptime(value, DATE_FORMAT).astimezone().date()
    except ValueError as err:
        msg = f"Not a YYYYMMDD date: {value}"
        raise CopyConversationError(msg) from err


def today() -> date:
    """Return the current local date, as a seam the tests can freeze."""
    return date.today()  # noqa: DTZ011


def build_copy(title: str, trimmed: str) -> str:
    """Put the title line and one empty line above the trimmed conversation."""
    return f"{title}:\n\n{trimmed}"


def powershell_executable() -> str:
    """Resolve the PowerShell executable used for clipboard access."""
    return shutil.which("pwsh") or shutil.which("powershell") or "powershell"


def set_clipboard_text(text: str) -> None:
    """Set the clipboard text, handing it over as a UTF-8 temporary file.

    Raises:
        CopyConversationError: When PowerShell cannot be run or fails.
    """
    with tempfile.TemporaryDirectory(prefix="copy_conversation_") as directory:
        payload = Path(directory) / "clipboard.txt"
        payload.write_text(text, encoding="utf-8")
        literal = str(payload).replace("'", "''")
        script = (
            f"{_CLIPBOARD_PREAMBLE}Set-Clipboard -Value "
            f"(Get-Content -Raw -Encoding UTF8 -LiteralPath '{literal}')"
        )
        command = [
            powershell_executable(),
            "-noprofile",
            "-ExecutionPolicy",
            "Bypass",
            "-command",
            script,
        ]
        try:
            subprocess.run(  # noqa: S603
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
        except (OSError, subprocess.SubprocessError) as err:
            msg = f"Failed to reach the clipboard through PowerShell: {err}"
            raise CopyConversationError(msg) from err


def _get_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Copy the running agent session to the clipboard, trimmed as tth "
            "trims an export, under a '<tab title>:' line and one empty line."
        ),
    )
    parser.add_argument(
        "host",
        nargs="?",
        choices=HOSTS,
        help="Agent host; detected by default.",
    )
    parser.add_argument(
        "--transcript",
        help="Transcript .jsonl to copy instead of the session's own.",
    )
    parser.add_argument(
        "--title",
        help="Title line text; the tuitp tab title by default.",
    )
    parser.add_argument(
        "--tab-list",
        help="tuitp list giving the tab titles; %%HOME%%\\bin\\tuitp.list by default.",
    )
    parser.add_argument(
        "--date",
        help="Extra YYYYMMDD date: a prompt stamped with it, or with today's date, drops every line before it.",
    )
    parser.add_argument("--output", help="Also write the copy to this file.")
    parser.add_argument(
        "--no-clipboard",
        action="store_true",
        help="Leave the clipboard unchanged.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""
    args = _get_arg_parser().parse_args(argv)
    environ = os.environ
    host: str = args.host or detect_host(environ)
    transcript = resolve_transcript(host, args.transcript, environ)
    dates = (today(), parse_date(args.date)) if args.date else (today(),)
    lines = transcript.read_text(encoding="utf-8", errors="replace").splitlines()
    result = trim_transcript(_RENDERERS[host](lines), _FORMATS[host], dates)
    tab_list = Path(args.tab_list) if args.tab_list else default_tab_list(environ)
    title: str = args.title or resolve_title(environ, tab_list, Path.cwd())
    copy = build_copy(title, result.text)
    if args.output:
        Path(args.output).write_text(copy, encoding="utf-8")
    if not args.no_clipboard:
        set_clipboard_text(copy)
    destination = (
        "Ready to paste from clipboard."
        if not args.no_clipboard
        else "Clipboard unchanged."
    )
    sys.stdout.write(
        f"copy-conversation ({host}): {transcript.name} rendered to "
        f"{result.source_lines} lines, {result.kept_lines} kept under "
        f"'{title}:'. {destination}\n",
    )
    return 0


def _log_fatal(err: Exception) -> NoReturn:
    """Report a fatal error and exit with code 2."""
    sys.stderr.write(f"ERROR: {err}\n")
    raise SystemExit(2) from err


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CopyConversationError, TrimThinkingError, OSError) as err:
        _log_fatal(err)


# eof
