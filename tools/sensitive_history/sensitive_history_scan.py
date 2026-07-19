#!/usr/bin/env python3
"""CLI for contextual case-insensitive scans across reachable Git history."""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if __name__ == "__main__":  # pragma: no cover - script bootstrap
    with contextlib.suppress(Exception):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from tools.sensitive_history.history_scan import (
    GitRepository,
    HistoryMatch,
    HistoryScanError,
    PatternSpec,
    ScanReport,
    merge_patterns,
    patterns_from_replacement_file,
    patterns_from_terms,
    patterns_from_terms_file,
    scan_repository,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

MIN_LINE_CHARS = 40


def _parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="sensitive-history-scan",
        description=(
            "List case-insensitive sensitive-term matches in all reachable Git "
            "commit messages, tags, paths, and unique historical blobs."
        ),
    )
    parser.add_argument("terms", nargs="*", help="Literal terms to find.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--terms-file", type=Path, help="One literal term per line.")
    parser.add_argument(
        "--rules",
        type=Path,
        help="git-filter-repo replacement file; scans each left-hand pattern.",
    )
    parser.add_argument("--output", type=Path, help="Write the report to this ignored file.")
    parser.add_argument("--json", action="store_true", help="Render JSON instead of Markdown.")
    parser.add_argument(
        "--max-line-chars",
        type=int,
        default=500,
        help="Bound long matching lines to this many characters (default: 500).",
    )
    parser.add_argument(
        "--full-lines",
        action="store_true",
        help="Keep complete matching lines regardless of length.",
    )
    parser.add_argument(
        "--validation-term",
        help="Fail unless this known term occurs in at least one historical blob.",
    )
    parser.add_argument(
        "--fail-on-match",
        action="store_true",
        help="Return exit code 1 when the scan finds any match.",
    )
    return parser


def _summary_lines(report: ScanReport) -> list[str]:
    """Render the report summary and exact case forms."""
    lines = [
        "## Summary",
        "",
        "| Term or pattern | Commit lines | Tag lines | Paths | Blob lines | Blobs |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for term in report.terms:
        counts = report.kind_counts(term)
        lines.append(
            f"| `{term}` | {counts['commit']} | {counts['tag']} | "
            f"{counts['path']} | {counts['blob']} | {report.blob_counts(term)} |",
        )
    lines.extend(["", "## Exact casing", ""])
    for term in report.terms:
        casing = report.casing_counts(term)
        rendered = ", ".join(f"`{form}` x {count}" for form, count in casing.items())
        lines.append(f"- `{term}`: {rendered or 'no matches'}")
    return lines


def _match_location(match: HistoryMatch) -> str:
    """Render one match location and its display flags."""
    location = f"`{match.oid}`"
    if match.ref:
        location += f" (`{match.ref}`)"
    if match.line_number is not None:
        location += f" line {match.line_number}"
    if match.paths:
        location += ": " + ", ".join(f"`{path}`" for path in match.paths)
    flags: list[str] = []
    if match.binary:
        flags.append("binary")
    if match.truncated:
        flags.append("excerpt")
    return location + (f" ({', '.join(flags)})" if flags else "")


def _match_section(report: ScanReport, kind: str, title: str) -> list[str]:
    """Render one detailed source-kind section."""
    lines = ["", f"## {title}", ""]
    selected = [match for match in report.matches if match.kind == kind]
    if not selected:
        return [*lines, "None."]
    for match in selected:
        rendered_line = json.dumps(match.line, ensure_ascii=True)
        lines.append(
            f"- `{match.term}` — {_match_location(match)}: `{rendered_line}`",
        )
    return lines


def _markdown(report: ScanReport) -> str:
    """Render a complete contextual Markdown report."""
    lines = [
        "<!-- markdownlint-disable-file -->",
        "",
        "# Sensitive Git history scan",
        "",
        f"Repository: `{report.root}`",
        "",
        f"Reachable objects: {report.object_count}; unique blobs: {report.blob_count}.",
    ]
    if report.validation_term:
        lines.extend(
            [
                "",
                (
                    f"Scanner validation: `{report.validation_term}` appears in "
                    f"{report.validation_blob_count} historical blob(s)."
                ),
            ],
        )
    lines.extend(["", *_summary_lines(report)])
    for kind, title in (
        ("commit", "Commit-message lines"),
        ("tag", "Tag-message lines"),
        ("path", "Historical paths"),
        ("blob", "Historical blob lines"),
    ):
        lines.extend(_match_section(report, kind, title))
    return "\n".join(lines) + "\n"


def _patterns(args: argparse.Namespace, root: Path) -> list[PatternSpec]:
    """Resolve all explicit inputs or the conventional local rules file."""
    term_patterns = patterns_from_terms(args.terms)
    file_patterns = patterns_from_terms_file(args.terms_file) if args.terms_file else []
    rules_path = args.rules
    if not args.terms and not args.terms_file and rules_path is None:
        conventional = root / "a.sensitive.replacements.local.txt"
        if conventional.is_file():
            rules_path = conventional
    rule_patterns = patterns_from_replacement_file(rules_path) if rules_path else []
    return merge_patterns(term_patterns, file_patterns, rule_patterns)


def _validate_output(repository: GitRepository, output: Path) -> Path:
    """Refuse a report inside the worktree unless Git ignores it."""
    resolved = output.resolve()
    if resolved.is_relative_to(repository.root) and not repository.is_ignored(resolved):
        message = f"output inside the repository must be Git-ignored: {resolved}"
        raise HistoryScanError(message)
    return resolved


def _validate_line_limit(max_line_chars: int | None) -> None:
    """Reject excerpt sizes too small to preserve useful context."""
    if max_line_chars is not None and max_line_chars < MIN_LINE_CHARS:
        message = f"--max-line-chars must be at least {MIN_LINE_CHARS}"
        raise HistoryScanError(message)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the scanner CLI."""
    args = _parser().parse_args(argv)
    root = args.root.resolve()
    try:
        patterns = _patterns(args, root)
        max_line_chars = None if args.full_lines else args.max_line_chars
        _validate_line_limit(max_line_chars)
        report = scan_repository(
            root,
            patterns,
            max_line_chars=max_line_chars,
            validation_term=args.validation_term,
        )
        output = (
            json.dumps(report.to_dict(), indent=2, ensure_ascii=True) + "\n"
            if args.json
            else _markdown(report)
        )
        if args.output:
            destination = _validate_output(GitRepository(root), args.output)
            destination.write_text(output, encoding="utf-8")
            sys.stdout.write(f"Wrote {len(report.matches)} matches to {destination}\n")
        else:
            sys.stdout.write(output)
        return int(args.fail_on_match and bool(report.matches))
    except HistoryScanError as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return 2


if __name__ == "__main__":  # pragma: no cover - script entry point
    raise SystemExit(main())


# eof
