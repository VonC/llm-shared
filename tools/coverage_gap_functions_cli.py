"""CLI helpers for coverage gap analysis.

Fix: Split the clipboard and command-dispatch code out of
`tools.coverage_gap_functions` so the script entry point can stay small while
keeping the same report and clipboard behavior.
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

from tools.coverage_gap_functions_mapping import render_mapping
from tools.coverage_gap_functions_shared import (
    POST_COVERAGE_LINES,
    CoverageGapError,
    CoverageJsonNotFoundError,
    InputFileNotFoundError,
    LineRange,
    find_project_root,
    load_missing_ranges_from_coverage_json,
)

LOGGER = logging.getLogger("coverage_gap_functions")


# ----------------------------
# CLI
# ----------------------------


def _configure_logging(*, debug: bool) -> None:
    """Configure logging to stdout with message-only formatting."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def _get_clipboard_text() -> str:
    """Get text content from the Windows clipboard via PowerShell."""
    try:
        # Use shutil.which to resolve the full path to powershell (fixes S607)
        pwsh = shutil.which("powershell") or "powershell"

        # Use PowerShell to get clipboard content
        result = subprocess.run(  # noqa: S603
            [
                pwsh,
                "-noprofile",
                "-ExecutionPolicy",
                "Bypass",
                "-command",
                "$PSModuleAutoloadingPreference = 'None'; Import-Module Microsoft.PowerShell.Management; Get-Clipboard",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.SubprocessError as err:
        LOGGER.warning("Failed to read clipboard: %s", err)
        return ""


def _set_clipboard_text(text: str) -> None:
    """Set text content to the Windows clipboard via PowerShell."""
    # --- DEBUG START: Print what we are trying to set ---
    # Log the length and the first 100 characters to verify content exists
    if LOGGER.isEnabledFor(logging.INFO):
        clean_preview = text.replace("\n", "\\n")[:100]
        LOGGER.info(
            "DEBUG: Setting clipboard (%d chars). Preview: '%s...'",
            len(text),
            clean_preview,
        )
    # --- DEBUG END ---

    try:
        pwsh = shutil.which("powershell") or "powershell"

        # Use PowerShell to set clipboard content
        subprocess.run(  # noqa: S603
            [
                pwsh,
                "-noprofile",
                "-command",
                # FIX 1: Added '$' prefix to PSModuleAutoloadingPreference
                # FIX 2: Added '$Input |' before Set-Clipboard to pipe Python's input
                "$PSModuleAutoloadingPreference = 'None'; Import-Module Microsoft.PowerShell.Management; $Input | Set-Clipboard",
            ],
            input=text,
            text=True,
            check=True,
        )
    except subprocess.SubprocessError as err:
        LOGGER.warning("Failed to write to clipboard: %s", err)


def _strip_percent_prefixed_args(argv: list[str]) -> list[str]:
    """If any arg contains '%', drop that arg and all args before it, except argv[0].

    This is meant to tolerate Windows launchers that inject placeholder args like
    '%VAR%'. When such an arg appears, we keep the first arg (argv[0]) and then
    keep only the args that follow the last percent-containing arg.
    """
    if not argv:
        return argv

    last_percent_index: int | None = None
    for index, arg in enumerate(argv):
        if "%" in arg:
            last_percent_index = index

    if last_percent_index is None:
        return argv

    suffix = argv[last_percent_index + 1 :]
    if last_percent_index <= 0:
        return suffix

    return [argv[0], *suffix]


def _get_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Map uncovered line ranges to function/method names, and optionally to branch contexts "
            "(if/else/except/finally/case/etc)."
        ),
    )
    parser.add_argument(
        "file",
        help="Relative path to the Python source file (relative to project root).",
    )
    parser.add_argument(
        "ranges",
        nargs="*",
        help="Uncovered ranges: N or N-M (e.g., 120 130-145). Ignored if --coverage-json is set.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Project root override. If not provided, scan upward for .git/pyproject.toml/etc.",
    )
    parser.add_argument(
        "--coverage-json",
        default=None,
        help="Load missing lines for FILE from this coverage.json (coverage.py format).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def _run_analysis(args: argparse.Namespace) -> str:
    """Run the gap analysis logic for the parsed arguments and return the report.

    An explicit ``--root`` is used verbatim, as its help text promises: the
    upward marker scan runs only when no override is given. Scanning upward
    from an explicit root would let a marker in an ancestor (a Git repository
    in the user's home directory, say) silently replace the requested root.
    """
    _configure_logging(debug=args.debug)

    root = Path(args.root).resolve() if args.root else find_project_root(Path.cwd())

    file_rel = args.file
    file_path = (root / file_rel).resolve()
    if not file_path.is_file():
        raise InputFileNotFoundError(file_path)

    ranges: list[LineRange]
    if args.coverage_json:
        cov_path = (root / args.coverage_json).resolve()
        if not cov_path.is_file():
            raise CoverageJsonNotFoundError(cov_path)
        ranges = load_missing_ranges_from_coverage_json(cov_path, file_rel)
    else:
        if not args.ranges:
            msg = "Provide ranges (N or N-M) or use --coverage-json"
            raise CoverageGapError(msg)
        ranges = [LineRange.parse(s) for s in args.ranges]

    return render_mapping(file_path, ranges, root=root)


def _build_final_clipboard_text(reports: list[str]) -> str | None:
    """Build the clipboard text only when there is non-empty coverage content."""
    normalized_reports = [report.strip() for report in reports if report.strip()]
    if not normalized_reports:
        return None

    final_text = "Extend test coverage to cover:\n\n" + "\n\n".join(
        normalized_reports,
    )
    if POST_COVERAGE_LINES:
        final_text += "\n\n" + "\n".join(POST_COVERAGE_LINES)
    return final_text


def _copy_reports_to_clipboard(reports: list[str]) -> None:
    """Log reports and copy the combined message when there is report content."""
    for report in reports:
        LOGGER.info(report)

    final_text = _build_final_clipboard_text(reports)
    if final_text is not None:
        _set_clipboard_text(final_text)


def _run_cli_mode(parser: argparse.ArgumentParser, raw_argv: list[str]) -> int:
    """Handle direct CLI invocation when arguments are provided."""
    effective_argv = _strip_percent_prefixed_args(list(raw_argv))
    args = parser.parse_args(effective_argv)
    report = _run_analysis(args)
    _copy_reports_to_clipboard([report])
    return 0


def _collect_reports_from_clipboard(
    parser: argparse.ArgumentParser,
    clipboard_content: str,
) -> list[str]:
    """Parse clipboard lines and return rendered reports for matching entries."""
    reports: list[str] = []
    # Lines matching "path/to/file.py ... 87% ..."
    regex_clipboard_line = re.compile(r"^\S+\.py.*\d%\s.*$")

    for raw_line in clipboard_content.splitlines():
        line = raw_line.strip()
        if not regex_clipboard_line.match(line):
            continue

        # Treat the line as arguments
        # Split by whitespace
        line_args = line.split()

        # Apply the strip logic (handles stripping the '%' token if present)
        # Note: arg 0 (file) matches regex \S+\.py, so it won't contain '%'.
        # The percentage token (e.g. 50%) is what we expect to strip.
        line_clean_args = _strip_percent_prefixed_args(line_args)

        try:
            parsed_args = parser.parse_args(line_clean_args)
            reports.append(_run_analysis(parsed_args))
        except (CoverageGapError, OSError) as err:
            # Log error but continue processing other lines
            LOGGER.warning("Skipping line '%s': %s", line, err)
        except SystemExit:
            # argparse calls sys.exit on failure. Catch to verify next lines.
            LOGGER.warning("Skipping invalid line args '%s'", line)

    return reports


def _run_clipboard_mode(parser: argparse.ArgumentParser) -> int:
    """Handle clipboard-driven invocation when no CLI args are provided."""
    clipboard_content = _get_clipboard_text()
    if not clipboard_content:
        parser.print_help()
        return 0

    reports = _collect_reports_from_clipboard(parser, clipboard_content)
    if reports:
        _copy_reports_to_clipboard(reports)
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _get_arg_parser()

    # If argv is provided specifically (e.g. tests), use it.
    # checking sys.argv directly to decide if we are in "no args" mode.
    # argv is usually None when called typically.
    raw_argv = sys.argv[1:] if argv is None else argv

    if raw_argv:
        return _run_cli_mode(parser, raw_argv)
    return _run_clipboard_mode(parser)


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with code 2."""
    _configure_logging(debug=False)
    LOGGER.exception("ERROR: %s", err)
    raise SystemExit(2) from err


__all__ = [
    "LOGGER",
    "_build_final_clipboard_text",
    "_collect_reports_from_clipboard",
    "_configure_logging",
    "_copy_reports_to_clipboard",
    "_get_arg_parser",
    "_get_clipboard_text",
    "_log_fatal",
    "_run_analysis",
    "_run_cli_mode",
    "_run_clipboard_mode",
    "_set_clipboard_text",
    "_strip_percent_prefixed_args",
    "main",
]


# eof
