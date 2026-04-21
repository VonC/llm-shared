"""group_commit_message_prompt.py.

Prepare one grouped-commit prompt from the current staged Git state.

From the project root, this tool writes `a.diff` from `git diff --cached`,
counts staged diff entries, clears `a.commit`, builds one
`/group-commits-msg ...` prompt with a blank line, a fenced `log` block, and
a trailing `Context: ` line from staged porcelain lines, copies that full
prompt to the clipboard, and prints only one ready line to stdout.
"""

from __future__ import annotations

import argparse
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

from tools import find_project_root

LOGGER = logging.getLogger("group_commit_message_prompt")
_DIFF_PATTERN = re.compile(r"^diff ", re.MULTILINE)
_EXCLUDED_STATUS_PATTERN = re.compile(r"^[ ?]")


class GroupCommitMessagePromptError(Exception):
    """Base exception for the grouped commit prompt helper."""


class GitCommandError(GroupCommitMessagePromptError):
    """Raised when one Git command fails."""


class ClipboardError(GroupCommitMessagePromptError):
    """Raised when clipboard updates fail."""


def _configure_logging(*, debug: bool) -> None:
    """Configure logging to stdout with message-only formatting."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def _run_git_text(args: list[str], *, cwd: Path) -> str:
    """Run one Git command and return its stdout text."""
    git_executable = shutil.which("git") or "git"
    command = [git_executable, *args]

    try:
        result = subprocess.run(  # noqa: S603
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            cwd=cwd,
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else ""
        msg = f"Git command failed: {' '.join(args)}"
        if stderr:
            msg = f"{msg}: {stderr}"
        raise GitCommandError(msg) from e

    return result.stdout


def _set_clipboard_text(text: str) -> None:
    """Set text content to the Windows clipboard via PowerShell."""
    try:
        pwsh = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
        subprocess.run(  # noqa: S603
            [
                pwsh,
                "-noprofile",
                "-ExecutionPolicy",
                "Bypass",
                "-command",
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                "$PSModuleAutoloadingPreference = 'None'; "
                "Import-Module Microsoft.PowerShell.Management; "
                "$Input | Set-Clipboard",
            ],
            input=text,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except subprocess.SubprocessError as e:
        msg = f"Failed to write clipboard: {e}"
        raise ClipboardError(msg) from e


def _count_cached_diff_files(diff_text: str) -> int:
    """Count staged file diffs by the number of `diff ` headers."""
    return len(_DIFF_PATTERN.findall(diff_text))


def _filter_staged_porcelain_lines(status_text: str) -> list[str]:
    """Keep only status lines whose staged column is not blank or untracked."""
    staged_lines: list[str] = []
    for raw_line in status_text.splitlines():
        if not raw_line or _EXCLUDED_STATUS_PATTERN.match(raw_line):
            continue
        staged_lines.append(raw_line.rstrip())
    return staged_lines


def build_group_commit_prompt(file_count: int, staged_lines: list[str]) -> str:
    """Build the clipboard prompt for the grouped commit message workflow."""
    header = f"/group-commits-msg for those {file_count} files:"
    if not staged_lines:
        return header + "\n\n```log\n```\n\nContext: "

    return header + "\n\n```log\n" + "\n".join(staged_lines) + "\n```\n\nContext: "


def _build_ready_line(file_count: int) -> str:
    """Build the single stdout line shown after the prompt is copied."""
    return (
        f"/group-commits-msg for those {file_count} files: "
        "Ready to paste from clipboard into the LLM prompt."
    )


def _prepare_group_commit_prompt(root: Path) -> tuple[str, str]:
    """Write Git artifacts in the root and return the summary line and prompt."""
    diff_text = _run_git_text(["diff", "--cached"], cwd=root)
    status_text = _run_git_text(["status", "--porcelain"], cwd=root)

    (root / "a.diff").write_text(diff_text, encoding="utf-8")
    (root / "a.commit").write_text("", encoding="utf-8")

    file_count = _count_cached_diff_files(diff_text)
    staged_lines = _filter_staged_porcelain_lines(status_text)
    prompt = build_group_commit_prompt(file_count, staged_lines)
    ready_line = _build_ready_line(file_count)
    return ready_line, prompt


def _get_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Prepare a grouped commit message prompt from staged Git state.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Project root override. If not provided, scan upward for the root.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _get_arg_parser()
    args = parser.parse_args(argv)
    _configure_logging(debug=args.debug)

    root = Path(args.root).resolve() if args.root else find_project_root(Path.cwd())
    ready_line, prompt = _prepare_group_commit_prompt(root)
    _set_clipboard_text(prompt)
    LOGGER.info(ready_line)
    return 0


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with code 2."""
    _configure_logging(debug=False)
    LOGGER.exception("ERROR: %s", err)
    raise SystemExit(2) from err


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (GroupCommitMessagePromptError, OSError) as err:
        _log_fatal(err)


# eof
