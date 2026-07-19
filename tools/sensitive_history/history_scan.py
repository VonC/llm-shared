"""Scan commit metadata and unique historical blobs for sensitive terms."""

from __future__ import annotations

import re
import subprocess
import threading
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence
    from pathlib import Path
    from typing import IO

MatchKind = Literal["commit", "tag", "path", "blob"]


class HistoryScanError(RuntimeError):
    """Report an invalid input or failed Git history scan."""


@dataclass(frozen=True)
class PatternSpec:
    """One named case-insensitive search expression."""

    label: str
    expression: str
    regex: re.Pattern[str]


@dataclass(frozen=True)
class HistoryMatch:
    """One matching line or historical path."""

    term: str
    kind: MatchKind
    oid: str
    ref: str | None
    paths: tuple[str, ...]
    line_number: int | None
    line: str
    forms: tuple[str, ...]
    binary: bool = False
    truncated: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {
            "term": self.term,
            "kind": self.kind,
            "oid": self.oid,
            "ref": self.ref,
            "paths": list(self.paths),
            "line_number": self.line_number,
            "line": self.line,
            "forms": list(self.forms),
            "binary": self.binary,
            "truncated": self.truncated,
        }


@dataclass(frozen=True)
class ScanReport:
    """Complete read-only result for one repository."""

    root: str
    object_count: int
    blob_count: int
    terms: tuple[str, ...]
    matches: tuple[HistoryMatch, ...]
    validation_term: str | None = None
    validation_blob_count: int | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {
            "root": self.root,
            "object_count": self.object_count,
            "blob_count": self.blob_count,
            "terms": list(self.terms),
            "matches": [match.to_dict() for match in self.matches],
            "validation_term": self.validation_term,
            "validation_blob_count": self.validation_blob_count,
        }

    def kind_counts(self, term: str) -> Counter[str]:
        """Count matching lines by source kind for one term."""
        return Counter(match.kind for match in self.matches if match.term == term)

    def blob_counts(self, term: str) -> int:
        """Count unique matching blobs for one term."""
        return len(
            {
                match.oid
                for match in self.matches
                if match.term == term and match.kind == "blob"
            },
        )

    def casing_counts(self, term: str) -> Counter[str]:
        """Count the exact matched casing forms for one term."""
        return Counter(
            form
            for match in self.matches
            if match.term == term
            for form in match.forms
        )


@dataclass(frozen=True)
class _MessageRecord:
    oid: str
    ref: str | None
    text: str


@dataclass(frozen=True)
class _MatchSource:
    """Source metadata shared by every line in one scanned value."""

    kind: MatchKind
    oid: str
    ref: str | None
    paths: tuple[str, ...]
    text: str
    binary: bool = False


def _compile(label: str, expression: str) -> PatternSpec:
    """Compile one expression with case-insensitive Unicode matching."""
    normalized = expression.removeprefix("(?i)")
    try:
        compiled = re.compile(normalized, re.IGNORECASE)
    except re.error as error:
        message = f"invalid pattern {label!r}: {error}"
        raise HistoryScanError(message) from error
    return PatternSpec(label=label, expression=normalized, regex=compiled)


def patterns_from_terms(terms: Iterable[str]) -> list[PatternSpec]:
    """Build literal case-insensitive patterns from user-provided terms."""
    patterns: list[PatternSpec] = []
    for raw_term in terms:
        term = raw_term.strip()
        if not term:
            message = "terms must not be empty"
            raise HistoryScanError(message)
        patterns.append(_compile(term, re.escape(term)))
    return patterns


def patterns_from_terms_file(path: Path) -> list[PatternSpec]:
    """Read one literal term per line, allowing blank lines and comments."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        message = f"cannot read terms file {path}: {error}"
        raise HistoryScanError(message) from error
    return patterns_from_terms(
        line for line in lines if line.strip() and not line.lstrip().startswith("#")
    )


def patterns_from_replacement_file(path: Path) -> list[PatternSpec]:
    """Read the left-hand patterns of a git-filter-repo replacement file."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        message = f"cannot read replacement file {path}: {error}"
        raise HistoryScanError(message) from error
    patterns: list[PatternSpec] = []
    for line_number, line in enumerate(lines, start=1):
        if not line:
            message = (
                f"replacement file line {line_number} is blank; "
                "rules files cannot contain blanks"
            )
            raise HistoryScanError(message)
        source = line.split("==>", 1)[0]
        if source.startswith("regex:"):
            expression = source.removeprefix("regex:")
            label = expression.removeprefix("(?i)")
        elif source.startswith("literal:"):
            label = source.removeprefix("literal:")
            expression = re.escape(label)
        elif source.startswith("glob:"):
            message = (
                f"replacement file line {line_number} uses unsupported glob syntax"
            )
            raise HistoryScanError(message)
        else:
            label = source
            expression = re.escape(source)
        patterns.append(_compile(label, expression))
    return patterns


def merge_patterns(*groups: Sequence[PatternSpec]) -> list[PatternSpec]:
    """Combine input groups while keeping the first equivalent pattern."""
    merged: list[PatternSpec] = []
    seen: set[str] = set()
    for group in groups:
        for pattern in group:
            key = pattern.expression.casefold()
            if key not in seen:
                merged.append(pattern)
                seen.add(key)
    if not merged:
        message = "provide terms, a terms file, or a replacement file"
        raise HistoryScanError(message)
    return merged


class GitRepository:
    """Read Git metadata and blobs without checking out historical trees."""

    def __init__(self, root: Path) -> None:
        """Open one existing Git working tree without modifying it."""
        self.root = root.resolve()
        if self._run("rev-parse", "--is-inside-work-tree").strip() != b"true":
            message = f"not a Git working tree: {self.root}"
            raise HistoryScanError(message)

    def _run(
        self,
        *args: str,
        input_bytes: bytes | None = None,
        check: bool = True,
    ) -> bytes:
        """Run Git and return stdout bytes."""
        result = subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607
            cwd=self.root,
            input=input_bytes,
            capture_output=True,
            check=False,
        )
        if check and result.returncode:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            message = f"git {' '.join(args)} failed: {detail}"
            raise HistoryScanError(message)
        return result.stdout

    def is_ignored(self, path: Path) -> bool:
        """Return whether Git ignores a path inside this worktree."""
        relative = path.resolve().relative_to(self.root)
        result = subprocess.run(  # noqa: S603
            ["git", "check-ignore", "--quiet", "--", str(relative)],  # noqa: S607
            cwd=self.root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0

    def object_inventory(self) -> tuple[list[str], dict[str, tuple[str, ...]]]:
        """Return reachable object ids and their representative historical paths."""
        object_ids: set[str] = set()
        paths: dict[str, set[str]] = defaultdict(set)
        text = self._run("rev-list", "--all", "--objects").decode(
            "utf-8", errors="surrogateescape",
        )
        for line in text.splitlines():
            oid, separator, path = line.partition(" ")
            object_ids.add(oid)
            if separator:
                paths[oid].add(path)
        return sorted(object_ids), {
            oid: tuple(sorted(values)) for oid, values in paths.items()
        }

    def blob_ids(self, object_ids: Sequence[str]) -> list[str]:
        """Filter reachable objects to unique blob ids in one Git process."""
        if not object_ids:
            return []
        checked = self._run(
            "cat-file",
            "--batch-check=%(objectname) %(objecttype)",
            input_bytes=("\n".join(object_ids) + "\n").encode("ascii"),
        )
        return [
            line.split()[0].decode("ascii")
            for line in checked.splitlines()
            if line.endswith(b" blob")
        ]

    @staticmethod
    def _require_pipe[T](pipe: T | None, name: str) -> T:
        """Return a configured subprocess pipe."""
        if pipe is None:  # pragma: no cover - subprocess.PIPE contract
            message = f"git cat-file {name} is unavailable"
            raise HistoryScanError(message)
        return pipe

    @staticmethod
    def _feed_blob_ids(
        stdin: IO[bytes],
        blob_ids: Sequence[str],
        errors: list[Exception],
    ) -> None:
        """Feed object ids while the caller drains the batch output."""
        try:
            stdin.writelines(oid.encode("ascii") + b"\n" for oid in blob_ids)
            stdin.close()
        except Exception as error:  # noqa: BLE001  # pragma: no cover
            errors.append(error)

    @staticmethod
    def _read_blob(stdout: IO[bytes], expected_oid: str) -> bytes:
        """Read one complete blob from a cat-file batch stream."""
        header = stdout.readline().rstrip(b"\n")
        parts = header.split(b" ")
        expected_header_parts = 3
        if len(parts) != expected_header_parts:  # pragma: no cover - corrupt stream
            message = f"unexpected git cat-file header: {header!r}"
            raise HistoryScanError(message)
        oid_bytes, kind, size_bytes = parts
        if (  # pragma: no cover - corrupt Git stream
            oid_bytes.decode("ascii") != expected_oid or kind != b"blob"
        ):
            message = f"unexpected git cat-file header: {header!r}"
            raise HistoryScanError(message)
        remaining = int(size_bytes)
        chunks: list[bytes] = []
        while remaining:
            chunk = stdout.read(remaining)
            if not chunk:  # pragma: no cover - corrupt Git stream
                message = "git cat-file returned a truncated blob"
                raise HistoryScanError(message)
            chunks.append(chunk)
            remaining -= len(chunk)
        if stdout.read(1) != b"\n":  # pragma: no cover - corrupt Git stream
            message = "git cat-file omitted the blob delimiter"
            raise HistoryScanError(message)
        return b"".join(chunks)

    @staticmethod
    def _finish_blob_process(
        process: subprocess.Popen[bytes],
        writer: threading.Thread,
        writer_errors: Sequence[Exception],
    ) -> None:
        """Join the feeder and validate the Git batch process."""
        writer.join()
        stderr = process.stderr.read() if process.stderr is not None else b""
        return_code = process.wait()
        if writer_errors:  # pragma: no cover - broken subprocess pipe
            message = f"cannot feed git cat-file: {writer_errors[0]}"
            raise HistoryScanError(message)
        if return_code:  # pragma: no cover - Git process failure
            detail = stderr.decode("utf-8", errors="replace").strip()
            message = f"git cat-file --batch failed: {detail}"
            raise HistoryScanError(message)

    def iter_blobs(self, blob_ids: Sequence[str]) -> Iterator[tuple[str, bytes]]:
        """Stream every requested blob through one git cat-file process."""
        if not blob_ids:
            return
        process = subprocess.Popen(
            ["git", "cat-file", "--batch"],  # noqa: S607
            cwd=self.root,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdin = self._require_pipe(process.stdin, "stdin")
        stdout = self._require_pipe(process.stdout, "stdout")
        writer_errors: list[Exception] = []
        writer = threading.Thread(
            target=self._feed_blob_ids,
            args=(stdin, blob_ids, writer_errors),
            daemon=True,
        )
        writer.start()
        for expected_oid in blob_ids:
            yield expected_oid, self._read_blob(stdout, expected_oid)
        self._finish_blob_process(process, writer, writer_errors)

    def commit_messages(self) -> list[_MessageRecord]:
        """Return all commit messages reachable from all refs."""
        fields = self._run("log", "--all", "--format=%H%x00%B%x00").split(b"\0")
        records: list[_MessageRecord] = []
        for index in range(0, len(fields) - 1, 2):
            oid = fields[index].strip().decode("ascii")
            if oid:
                records.append(
                    _MessageRecord(
                        oid=oid,
                        ref=None,
                        text=fields[index + 1].decode("utf-8", errors="surrogateescape"),
                    ),
                )
        return records

    def tag_messages(self) -> list[_MessageRecord]:
        """Return tag names, object ids, and annotated contents."""
        fields = self._run(
            "for-each-ref",
            "--format=%(refname:short)%00%(objectname)%00%(contents)%00",
            "refs/tags",
        ).split(b"\0")
        records: list[_MessageRecord] = []
        for index in range(0, len(fields) - 2, 3):
            ref = fields[index].lstrip(b"\r\n").decode("utf-8", errors="surrogateescape")
            oid = fields[index + 1].decode("ascii")
            if ref:
                records.append(
                    _MessageRecord(
                        oid=oid,
                        ref=ref,
                        text=fields[index + 2].decode(
                            "utf-8", errors="surrogateescape",
                        ),
                    ),
                )
        return records


def _display_line(
    line: str,
    regex: re.Pattern[str],
    max_line_chars: int | None,
) -> tuple[str, bool]:
    """Return a full line or a bounded excerpt centered on its first match."""
    if max_line_chars is None or len(line) <= max_line_chars:
        return line, False
    match = regex.search(line)
    if match is None:
        return line[:max_line_chars], True
    allowance = max_line_chars - len(match.group())
    start = max(0, match.start() - allowance // 2)
    end = min(len(line), start + max_line_chars)
    start = max(0, end - max_line_chars)
    prefix = "…" if start else ""
    suffix = "…" if end < len(line) else ""
    return f"{prefix}{line[start:end]}{suffix}", True


def _line_matches(
    source: _MatchSource,
    patterns: Sequence[PatternSpec],
    max_line_chars: int | None,
) -> list[HistoryMatch]:
    """Return one result per matching term and source line."""
    matches: list[HistoryMatch] = []
    for line_number, line in enumerate(
        source.text.splitlines() or [source.text], start=1,
    ):
        for pattern in patterns:
            occurrences = tuple(found.group() for found in pattern.regex.finditer(line))
            if not occurrences:
                continue
            rendered, truncated = _display_line(line, pattern.regex, max_line_chars)
            matches.append(
                HistoryMatch(
                    term=pattern.label,
                    kind=source.kind,
                    oid=source.oid,
                    ref=source.ref,
                    paths=source.paths,
                    line_number=line_number,
                    line=rendered,
                    forms=occurrences,
                    binary=source.binary,
                    truncated=truncated,
                ),
            )
    return matches


def _message_matches(
    records: Sequence[_MessageRecord],
    kind: Literal["commit", "tag"],
    patterns: Sequence[PatternSpec],
    max_line_chars: int | None,
) -> list[HistoryMatch]:
    """Scan commit or tag message records."""
    matches: list[HistoryMatch] = []
    for record in records:
        source = _MatchSource(kind, record.oid, record.ref, (), record.text)
        matches.extend(_line_matches(source, patterns, max_line_chars))
    return matches


def _path_matches(
    paths_by_oid: dict[str, tuple[str, ...]],
    patterns: Sequence[PatternSpec],
    max_line_chars: int | None,
) -> list[HistoryMatch]:
    """Scan representative historical object paths."""
    matches: list[HistoryMatch] = []
    for oid, paths in paths_by_oid.items():
        for path in paths:
            source = _MatchSource("path", oid, None, (path,), path)
            matches.extend(_line_matches(source, patterns, max_line_chars))
    return matches


def _blob_matches(  # noqa: PLR0913
    repository: GitRepository,
    blob_ids: Sequence[str],
    paths_by_oid: dict[str, tuple[str, ...]],
    patterns: Sequence[PatternSpec],
    max_line_chars: int | None,
    validation_regex: re.Pattern[str] | None,
) -> tuple[list[HistoryMatch], int | None]:
    """Scan unique blobs and count the positive-control blobs."""
    matches: list[HistoryMatch] = []
    validation_count = 0 if validation_regex else None
    for oid, content in repository.iter_blobs(blob_ids):
        text = content.decode("utf-8", errors="surrogateescape")
        if validation_regex and validation_regex.search(text):
            validation_count = (validation_count or 0) + 1
        source = _MatchSource(
            "blob",
            oid,
            None,
            paths_by_oid.get(oid, ()),
            text,
            b"\0" in content,
        )
        matches.extend(_line_matches(source, patterns, max_line_chars))
    return matches, validation_count


def scan_repository(
    root: Path,
    patterns: Sequence[PatternSpec],
    *,
    max_line_chars: int | None = 500,
    validation_term: str | None = None,
) -> ScanReport:
    """Scan all refs, paths, commit/tag messages, and unique historical blobs."""
    repository = GitRepository(root)
    object_ids, paths_by_oid = repository.object_inventory()
    blobs = repository.blob_ids(object_ids)
    validation_regex = (
        re.compile(re.escape(validation_term), re.IGNORECASE)
        if validation_term
        else None
    )
    blob_matches, validation_blob_count = _blob_matches(
        repository,
        blobs,
        paths_by_oid,
        patterns,
        max_line_chars,
        validation_regex,
    )
    matches = [
        *_message_matches(
            repository.commit_messages(), "commit", patterns, max_line_chars,
        ),
        *_message_matches(repository.tag_messages(), "tag", patterns, max_line_chars),
        *_path_matches(paths_by_oid, patterns, max_line_chars),
        *blob_matches,
    ]
    if validation_term and not validation_blob_count:
        message = (
            f"scanner validation failed: {validation_term!r} matched no historical blob"
        )
        raise HistoryScanError(message)
    return ScanReport(
        root=str(repository.root),
        object_count=len(object_ids),
        blob_count=len(blobs),
        terms=tuple(pattern.label for pattern in patterns),
        matches=tuple(matches),
        validation_term=validation_term,
        validation_blob_count=validation_blob_count,
    )


# eof
