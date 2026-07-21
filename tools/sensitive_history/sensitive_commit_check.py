#!/usr/bin/env python3
"""Reject sensitive terms in pending commit messages and staged blob updates."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if __name__ == "__main__":  # pragma: no cover - script bootstrap
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from tools.sensitive_history.history_scan import (
    GitRepository,
    HistoryScanError,
    PatternSpec,
    patterns_from_repository_rules,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

BLOCKED = 1
ERROR = 2
RAW_FIELD_COUNT = 5


@dataclass(frozen=True)
class Finding:
    """One redacted sensitive-term location in the pending commit."""

    kind: Literal["blob", "message"]
    location: str


def _git(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    """Run one Git command and return its standard output."""
    try:
        result = subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607
            cwd=root,
            input=input_bytes,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = ""
        if isinstance(error, subprocess.CalledProcessError):
            detail = error.stderr.decode("utf-8", errors="replace").strip()
        suffix = f": {detail}" if detail else ""
        message = f"git {' '.join(args)} failed{suffix}"
        raise HistoryScanError(message) from error
    return result.stdout


def repository_root(root: Path) -> Path:
    """Resolve the worktree root used by the pending commit."""
    output = _git(root, "rev-parse", "--show-toplevel")
    return Path(output.decode("utf-8", errors="surrogateescape").strip()).resolve()


def _base_tree(root: Path) -> str:
    """Return HEAD, or Git's empty tree for an unborn branch."""
    try:
        return _git(root, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
    except HistoryScanError:
        return _git(root, "hash-object", "-t", "tree", "--stdin", input_bytes=b"").decode(
            "ascii",
        ).strip()


def staged_blob_paths(root: Path) -> dict[str, tuple[str, ...]]:
    """Map only changed/new staged blob IDs to their pending paths."""
    raw = _git(
        root,
        "diff",
        "--cached",
        "--raw",
        "-z",
        "--no-abbrev",
        "--find-renames",
        _base_tree(root),
        "--",
    )
    fields = raw.split(b"\0")
    paths_by_oid: dict[str, list[str]] = {}
    index = 0
    while index + 1 < len(fields) and fields[index]:
        metadata = fields[index].decode("ascii")
        parts = metadata.removeprefix(":").split()
        if len(parts) != RAW_FIELD_COUNT:  # pragma: no cover - Git --raw contract
            message = f"unexpected git diff --raw record: {metadata!r}"
            raise HistoryScanError(message)
        _old_mode, new_mode, old_oid, new_oid, status = parts
        path_index = index + 2 if status.startswith(("R", "C")) else index + 1
        path = fields[path_index].decode("utf-8", errors="surrogateescape")
        is_blob_update = (
            not status.startswith("D")
            and new_mode != "160000"
            and old_oid != new_oid
            and set(new_oid) != {"0"}
        )
        if is_blob_update:
            paths_by_oid.setdefault(new_oid, []).append(path)
        index = path_index + 1
    return {oid: tuple(paths) for oid, paths in paths_by_oid.items()}


def _matching_lines(text: str, patterns: Sequence[PatternSpec]) -> tuple[int, ...]:
    """Return matching line numbers without retaining or displaying secrets."""
    lines = text.splitlines() or [text]
    return tuple(
        line_number
        for line_number, line in enumerate(lines, start=1)
        if any(pattern.regex.search(line) for pattern in patterns)
    )


def check_staged_blobs(root: Path, patterns: Sequence[PatternSpec]) -> list[Finding]:
    """Check only blob versions introduced by the current index diff."""
    paths_by_oid = staged_blob_paths(root)
    findings: list[Finding] = []
    repository = GitRepository(root)
    for oid, content in repository.iter_blobs(tuple(paths_by_oid)):
        text = content.decode("utf-8", errors="surrogateescape")
        for line_number in _matching_lines(text, patterns):
            findings.extend(
                Finding("blob", f"{path}:{line_number}")
                for path in paths_by_oid[oid]
            )
    return findings


def check_message(path: Path, patterns: Sequence[PatternSpec]) -> list[Finding]:
    """Check the pending commit-message file supplied by Git."""
    try:
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
    except OSError as error:
        message = f"cannot read commit message {path}: {error}"
        raise HistoryScanError(message) from error
    return [
        Finding("message", f"commit message line {line_number}")
        for line_number in _matching_lines(text, patterns)
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sensitive-commit-check")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("staged", help="check changed/new staged blobs")
    message = subparsers.add_parser("message", help="check a pending commit message")
    message.add_argument("message_file", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected pending-commit check."""
    args = _parser().parse_args(argv)
    try:
        root = repository_root(args.root)
        patterns = patterns_from_repository_rules(root)
        findings = (
            check_staged_blobs(root, patterns)
            if args.command == "staged"
            else check_message(args.message_file, patterns)
        )
    except HistoryScanError as error:
        sys.stderr.write(f"ERROR: sensitive commit check could not run: {error}\n")
        return ERROR
    if not findings:
        return 0
    sys.stderr.write("ERROR: sensitive content found in the pending commit:\n")
    for finding in findings:
        sys.stderr.write(f"  - {finding.location}\n")
    sys.stderr.write("Commit blocked; sensitive content was not printed.\n")
    return BLOCKED


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
