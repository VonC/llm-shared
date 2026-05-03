"""coverage_gap_functions.py.

Map uncovered line ranges (or missing lines from coverage.json) to the enclosing
function/method name, and optionally to a nearby branch context (if/else/except/etc).

Output is emitted via logging (logger.info) with a formatter that prints only the message.

Fix: Build the clipboard text in one helper so optional follow-up lines are only
appended when the report actually contains uncovered lines to cover.

Fix (complexity): split the CLI and clipboard dispatch paths out of `main()` so
the entry point stays small while preserving the same behavior.

Arg parsing note (Windows):
Some launchers can inject placeholder arguments containing '%' (for example '%VAR%').
If any arg contains '%', this script drops that arg and all args before it, and only
parses the args that follow.
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NoReturn, TypeGuard, cast

LOGGER = logging.getLogger("coverage_gap_functions")

ROOT_MARKERS_DIR: tuple[str, ...] = (".git",)
ROOT_MARKERS_FILE: tuple[str, ...] = (
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "tox.ini",
)
POST_COVERAGE_LINES: tuple[str, ...] = (
    "Make sure check.bat is passing, it can be called from anywhere, Python venv is already activated.",
    "Make sure affected tests are passing.",
    "Prefer `pytest --testmon --cov-append --no-header --cov-report term-missing:skip-covered test_file1.py test_file2.py ...`",
    "to run affected test while preserving existing coverage reports.",
)

# ----------------------------
# Exceptions
# ----------------------------


class CoverageGapError(Exception):
    """Base exception for this tool."""


class InvalidRangeError(CoverageGapError, ValueError):
    """Raised when a line range cannot be parsed."""

    def __init__(self, raw: str) -> None:
        """Create an InvalidRangeError for the raw range string provided by the user."""
        msg = f"Invalid range {raw!r} (expected N or N-M)"
        super().__init__(msg)


class InputFileNotFoundError(CoverageGapError, FileNotFoundError):
    """Raised when the target Python file cannot be located."""

    def __init__(self, file_path: Path) -> None:
        """Create an InputFileNotFoundError for a missing target source file."""
        msg = f"File not found: {file_path}"
        super().__init__(msg)


class CoverageJsonNotFoundError(CoverageGapError, FileNotFoundError):
    """Raised when the coverage JSON file cannot be located."""

    def __init__(self, json_path: Path) -> None:
        """Create a CoverageJsonNotFoundError for a missing coverage JSON file."""
        msg = f"Coverage JSON not found: {json_path}"
        super().__init__(msg)


class CoverageJsonFormatError(CoverageGapError):
    """Raised when coverage.json does not match the expected structure."""

    def __init__(self, detail: str) -> None:
        """Create a CoverageJsonFormatError describing the invalid coverage.json structure."""
        msg = f"coverage.json format error: {detail}"
        super().__init__(msg)


class CoverageJsonFileMatchError(CoverageGapError):
    """Raised when matching a file entry in coverage.json fails."""

    def __init__(self, detail: str) -> None:
        """Create a CoverageJsonFileMatchError describing why file matching failed."""
        msg = f"coverage.json file match error: {detail}"
        super().__init__(msg)


# ----------------------------
# Data model
# ----------------------------


@dataclass(frozen=True, order=True)
class LineRange:
    """A 1-based inclusive line range."""

    start: int
    end: int

    @classmethod
    def parse(cls, raw: str) -> LineRange:
        """Parse 'N' or 'N-M' into a LineRange."""
        if re.fullmatch(r"\d+,?", raw):
            # remove , from raw
            raw = raw.rstrip(",")
            n = int(raw)
            return cls(n, n)

        match = re.fullmatch(r"(\d+)-(\d+),?", raw)
        if match is None:
            raise InvalidRangeError(raw)

        raw = raw.rstrip(",")
        a = int(match.group(1))
        b = int(match.group(2))
        if b < a:
            a, b = b, a
        return cls(a, b)

    def covers(self, start: int, end: int) -> bool:
        """Return True if this range fully covers [start, end]."""
        return self.start <= start and self.end >= end


@dataclass(frozen=True)
class FuncInfo:
    """Information about a discovered function/method."""

    qualname: str
    start: int
    end: int
    node: ast.AST
    is_method: bool  # NEW


@dataclass(frozen=True)
class Detail:
    """Extra detail for a partial uncovered range."""

    kind: Literal["branch", "code"]
    text: str


@dataclass(frozen=True)
class BranchBlock:
    """A block of lines corresponding to a branch-like structure."""

    label: str
    start: int
    end: int

    def contains(self, line: int) -> bool:
        """Return True if 'line' is within this block."""
        return self.start <= line <= self.end

    @property
    def size(self) -> int:
        """Block size in lines (inclusive end not accounted; used for ordering)."""
        return self.end - self.start


# ----------------------------
# Project root detection
# ----------------------------


def find_project_root(start: Path) -> Path:
    """Scan upward for project root markers and return the discovered root path."""
    cur = start.resolve()
    while True:
        for d in ROOT_MARKERS_DIR:
            if (cur / d).is_dir():
                return cur
        for f in ROOT_MARKERS_FILE:
            if (cur / f).is_file():
                return cur
        if cur == cur.parent:
            return start.resolve()
        cur = cur.parent


# ----------------------------
# AST utilities
# ----------------------------


def _compact(s: str) -> str:
    return " ".join(s.split())


def _unparse(node: ast.AST) -> str:
    """Return a compact one-line expression string.

    Falls back to "<expr>" if the node cannot be unparsed.
    """
    try:
        return _compact(ast.unparse(node))
    except (TypeError, ValueError, AttributeError, RecursionError):
        return "<expr>"


def _stmt_list_span(stmts: list[ast.stmt]) -> tuple[int, int] | None:
    if not stmts:
        return None
    start = min(getattr(s, "lineno", 10**9) for s in stmts)
    end = max(getattr(s, "end_lineno", getattr(s, "lineno", 0)) for s in stmts)
    return (start, end)


def _maybe_prev_header_line(
    source_lines: list[str],
    start_line_1based: int,
    *,
    keywords: tuple[str, ...],
) -> int:
    """If the previous physical line starts with a keyword (else/finally/case/etc), include it in the block span for better mapping."""
    if start_line_1based <= 1:
        return start_line_1based

    prev = source_lines[start_line_1based - 2].lstrip()
    for kw in keywords:
        if prev.startswith(kw):
            return start_line_1based - 1
    return start_line_1based


class _FuncCollector(ast.NodeVisitor):
    """Collect function/method spans and qualified names."""

    def __init__(self) -> None:
        self._class_stack: list[str] = []
        self._func_stack: list[str] = []
        self.funcs: list[FuncInfo] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._func_stack.append(node.name)
        qual = ".".join(self._class_stack + self._func_stack)
        end = getattr(node, "end_lineno", node.lineno)
        is_method = bool(self._class_stack)  # NEW
        self.funcs.append(FuncInfo(qual, node.lineno, end, node, is_method))  # UPDATED
        self.generic_visit(node)
        self._func_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._func_stack.append(node.name)
        qual = ".".join(self._class_stack + self._func_stack)
        end = getattr(node, "end_lineno", node.lineno)
        is_method = bool(self._class_stack)  # NEW
        self.funcs.append(FuncInfo(qual, node.lineno, end, node, is_method))  # UPDATED
        self.generic_visit(node)
        self._func_stack.pop()


def collect_functions(tree: ast.AST) -> list[FuncInfo]:
    """Collect all (async) functions with their qualified names and line spans."""
    v = _FuncCollector()
    v.visit(tree)
    return v.funcs


class BranchCollector:
    """Collect branch blocks (if/else/except/etc) inside a function."""

    def __init__(self, source_lines: list[str]) -> None:
        """Initialize a collector bound to the module's source lines for header lookups."""
        self._source_lines = source_lines
        self._blocks: list[BranchBlock] = []

    def collect(self, func_node: ast.AST) -> list[BranchBlock]:
        """Collect and return all branch blocks under the given function node."""
        self._blocks.clear()
        for stmt in getattr(func_node, "body", []):
            self._walk(stmt)
        return list(self._blocks)

    def _add(self, label: str, start: int | None, end: int | None) -> None:
        if start is None or end is None:
            return
        a, b = (start, end) if end >= start else (end, start)
        self._blocks.append(BranchBlock(label=label, start=a, end=b))

    def _walk(self, node: ast.AST) -> None:
        if isinstance(node, ast.If):
            self._handle_if(node)
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            self._handle_for(node)
            return
        if isinstance(node, ast.While):
            self._handle_while(node)
            return
        if isinstance(node, ast.Try):
            self._handle_try(node)
            return
        if isinstance(node, ast.Match):
            self._handle_match(node)
            return

        for child in ast.iter_child_nodes(node):
            self._walk(child)

    def _handle_if(self, node: ast.If) -> None:
        cond = _unparse(node.test)

        body_span = _stmt_list_span(node.body)
        if body_span:
            self._add(f"if {cond} (then)", node.lineno, body_span[1])
        else:
            self._add(f"if {cond} (then)", node.lineno, node.lineno)

        if node.orelse:
            orelse_span = _stmt_list_span(node.orelse)
            if orelse_span:
                orelse_start = _maybe_prev_header_line(
                    self._source_lines,
                    orelse_span[0],
                    keywords=("else", "elif"),
                )
                self._add(f"else of if {cond}", orelse_start, orelse_span[1])

        for s in node.body:
            self._walk(s)
        for s in node.orelse:
            self._walk(s)

    def _handle_for(self, node: ast.For | ast.AsyncFor) -> None:
        tgt = _unparse(node.target)
        it = _unparse(node.iter)
        kind = "async for" if isinstance(node, ast.AsyncFor) else "for"

        body_span = _stmt_list_span(node.body)
        if body_span:
            self._add(f"{kind} {tgt} in {it}", node.lineno, body_span[1])

        if node.orelse:
            orelse_span = _stmt_list_span(node.orelse)
            if orelse_span:
                orelse_start = _maybe_prev_header_line(
                    self._source_lines,
                    orelse_span[0],
                    keywords=("else",),
                )
                self._add(f"else of {kind} {tgt} in {it}", orelse_start, orelse_span[1])

        for s in node.body:
            self._walk(s)
        for s in node.orelse:
            self._walk(s)

    def _handle_while(self, node: ast.While) -> None:
        cond = _unparse(node.test)

        body_span = _stmt_list_span(node.body)
        if body_span:
            self._add(f"while {cond}", node.lineno, body_span[1])

        if node.orelse:
            orelse_span = _stmt_list_span(node.orelse)
            if orelse_span:
                orelse_start = _maybe_prev_header_line(
                    self._source_lines,
                    orelse_span[0],
                    keywords=("else",),
                )
                self._add(f"else of while {cond}", orelse_start, orelse_span[1])

        for s in node.body:
            self._walk(s)
        for s in node.orelse:
            self._walk(s)

    def _handle_try(self, node: ast.Try) -> None:
        def _add_stmt_block(
            label: str,
            stmts: list[ast.stmt],
            *,
            kw: tuple[str, ...] = (),
        ) -> None:
            span = _stmt_list_span(stmts)
            if not span:
                return
            start = (
                _maybe_prev_header_line(self._source_lines, span[0], keywords=kw)
                if kw
                else span[0]
            )
            self._add(label, start, span[1])

        def _walk_stmts(stmts: list[ast.stmt]) -> None:
            for stmt in stmts:
                self._walk(stmt)

        def _add_handlers(handlers: list[ast.ExceptHandler]) -> None:
            for h in handlers:
                span = _stmt_list_span(h.body)
                if span:
                    start = min(h.lineno, span[0])
                    typ = "*" if h.type is None else _unparse(h.type)
                    nm = f" as {h.name}" if getattr(h, "name", None) else ""
                    self._add(f"except {typ}{nm}", start, span[1])
                _walk_stmts(h.body)

        _add_stmt_block("try", node.body, kw=())
        _add_handlers(node.handlers)

        if node.orelse:
            _add_stmt_block("else of try", node.orelse, kw=("else",))
            _walk_stmts(node.orelse)

        if node.finalbody:
            _add_stmt_block("finally", node.finalbody, kw=("finally",))
            _walk_stmts(node.finalbody)

        _walk_stmts(node.body)

    def _handle_match(self, node: ast.Match) -> None:
        subj = _unparse(node.subject)
        for case in node.cases:
            case_span = _stmt_list_span(case.body)
            if not case_span:
                continue

            pat = _unparse(case.pattern)
            guard = f" if {_unparse(case.guard)}" if case.guard else ""
            case_start = _maybe_prev_header_line(
                self._source_lines,
                case_span[0],
                keywords=("case",),
            )
            self._add(f"case {pat}{guard} (match {subj})", case_start, case_span[1])

            for s in case.body:
                self._walk(s)


# ----------------------------
# Coverage JSON helpers
# ----------------------------


def compress_lines_to_ranges(lines: list[int]) -> list[LineRange]:
    """Compress a list of line numbers into consecutive LineRanges."""
    if not lines:
        return list[LineRange]()
    sorted_lines = sorted(set(lines))
    out: list[LineRange] = []

    start = prev = sorted_lines[0]
    for n in sorted_lines[1:]:
        if n == prev + 1:
            prev = n
            continue
        out.append(LineRange(start, prev))
        start = prev = n
    out.append(LineRange(start, prev))
    return out


def _is_obj_dict(obj: object) -> TypeGuard[dict[object, object]]:
    """Narrow an arbitrary object to a plain dict with object keys/values."""
    return isinstance(obj, dict)


def _ensure_dict(obj: object, ctx: str) -> dict[object, object]:
    """Return obj as a dict[object, object], or raise with context."""
    if _is_obj_dict(obj):
        return obj
    msg = f"{ctx} is not a dict"
    raise CoverageJsonFormatError(msg)


def _ensure_str_dict(obj: object, ctx: str) -> dict[str, object]:
    """Return obj as a dict[str, object] after validating all keys are strings."""
    d = _ensure_dict(obj, ctx)  # dict[object, object]
    for k in d:
        if not isinstance(k, str):
            msg = f"{ctx} has a non-string key: {k!r}"
            raise CoverageJsonFormatError(msg)
    return cast("dict[str, object]", d)


def _ensure_str_obj_dict(obj: object, ctx: str) -> dict[str, object]:
    """Return obj as dict[str, object] after validating keys are strings."""
    d = _ensure_dict(obj, ctx)  # dict[object, object]
    for k in d:
        if not isinstance(k, str):
            msg = f"{ctx} has a non-string key: {k!r}"
            raise CoverageJsonFormatError(msg)
    return cast("dict[str, object]", d)


def _is_obj_list(obj: object) -> TypeGuard[list[object]]:
    """Return True if obj is a list (treated as list[object] for typing purposes)."""
    return isinstance(obj, list)


def _read_text_or_raise(path: Path) -> str:
    """Read a UTF-8 text file or raise CoverageJsonNotFoundError."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        raise CoverageJsonNotFoundError(path) from e


def _parse_json_root_obj(text: str) -> dict[object, object]:
    """Parse JSON text and return the root object as dict[object, object]."""
    try:
        parsed: object = json.loads(text)
    except json.JSONDecodeError as e:
        msg = "invalid JSON"
        raise CoverageJsonFormatError(msg) from e
    return _ensure_dict(parsed, "root")


def _normalize_rel_path(p: str) -> str:
    """Normalize a relative path for suffix matching in coverage.json."""
    return p.replace("\\", "/").lstrip("./")


def _find_matching_file_entries(
    files: dict[str, object],
    target_norm: str,
) -> list[tuple[str, dict[str, object]]]:
    """Return all coverage.json file entries matching the normalized target path."""
    matches: list[tuple[str, dict[str, object]]] = []
    for k, v in files.items():
        k_norm = k.replace("\\", "/")
        if k_norm == target_norm or k_norm.endswith("/" + target_norm):
            matches.append((k, _ensure_str_obj_dict(v, f"root.files[{k!r}]")))
    return matches


def _pick_single_file_entry(
    matches: list[tuple[str, dict[str, object]]],
    *,
    target_rel_file: str,
    coverage_json_path: Path,
) -> dict[str, object]:
    """Pick exactly one match or raise CoverageJsonFileMatchError."""
    if not matches:
        msg = f"no entry for {target_rel_file!r} in {coverage_json_path}"
        raise CoverageJsonFileMatchError(
            msg,
        )

    if len(matches) > 1:
        keys = "\n".join(f"  - {m[0]}" for m in matches)
        msg = (
            f"ambiguous match for {target_rel_file!r} in {coverage_json_path}:\n{keys}"
        )
        raise CoverageJsonFileMatchError(
            msg,
        )

    return matches[0][1]


def _extract_missing_lines(file_entry: dict[str, object]) -> list[int]:
    """Extract and validate missing_lines as list[int] from a file entry."""
    missing_obj = file_entry.get("missing_lines", [])
    if not _is_obj_list(missing_obj):
        msg = "missing_lines is not a list"
        raise CoverageJsonFormatError(msg)

    missing_lines: list[int] = []
    for item in missing_obj:  # item: object
        if not isinstance(item, int):
            msg = "missing_lines contains a non-integer item"
            raise CoverageJsonFormatError(msg)
        missing_lines.append(item)
    return missing_lines


def load_missing_ranges_from_coverage_json(
    coverage_json_path: Path,
    target_rel_file: str,
) -> list[LineRange]:
    """Load missing line ranges for a given file entry in coverage.json."""
    text = _read_text_or_raise(coverage_json_path)
    root_obj = _parse_json_root_obj(text)

    files = _ensure_str_dict(root_obj.get("files"), "root.files")  # dict[str, object]
    target_norm = _normalize_rel_path(target_rel_file)

    matches = _find_matching_file_entries(files, target_norm)
    file_entry = _pick_single_file_entry(
        matches,
        target_rel_file=target_rel_file,
        coverage_json_path=coverage_json_path,
    )

    missing_lines = _extract_missing_lines(file_entry)
    return compress_lines_to_ranges(missing_lines)


# ----------------------------
# Mapping logic
# ----------------------------


def find_containing_func(funcs: list[FuncInfo], rng: LineRange) -> FuncInfo | None:
    """Find the smallest function that contains the given line range (or its start line)."""
    candidates = [f for f in funcs if f.start <= rng.start and f.end >= rng.end]
    if not candidates:
        candidates = [f for f in funcs if f.start <= rng.start <= f.end]
    if not candidates:
        return None
    return min(candidates, key=lambda f: (f.end - f.start, f.start))


def _parse_python_file(file_path: Path) -> tuple[list[str], ast.AST]:
    """Read a Python file and return (source_lines, parsed_ast)."""
    src = file_path.read_text(encoding="utf-8")
    source_lines = src.splitlines()
    try:
        tree = ast.parse(src, filename=str(file_path), type_comments=True)
    except SyntaxError as e:
        msg = f"Cannot parse {file_path}: {e.msg} at line {e.lineno}"
        raise CoverageGapError(msg) from e
    return source_lines, tree


def _best_branch_label_for_range(
    rng: LineRange,
    *,
    qual: str,
    fi: FuncInfo,
    collector: BranchCollector,
    branch_cache: dict[str, list[BranchBlock]],
) -> str | None:
    """Return the best matching branch label (if any) for a range start line."""
    if qual not in branch_cache:
        branch_cache[qual] = collector.collect(fi.node)
    candidates = [b for b in branch_cache[qual] if b.contains(rng.start)]
    if not candidates:
        return None
    best = min(candidates, key=lambda b: (b.size, b.start))
    return best.label


def _truncate(s: str, limit: int = 160) -> str:
    s2 = " ".join(s.split())
    return (s2[: limit - 1] + "…") if len(s2) > limit else s2


def _md_inline_code(s: str) -> str:
    # Avoid breaking Markdown inline code.
    return s.replace("`", "'")


def _pick_anchor_line(rng: LineRange, source_lines: list[str]) -> int:
    """Pick the first non-empty, non-comment line within the range as the "anchor".

    (better than using rng.start when it points to a blank/comment line).
    """
    max_line = len(source_lines)
    start = max(1, min(rng.start, max_line))
    end = max(1, min(rng.end, max_line))
    for n in range(start, end + 1):
        t = source_lines[n - 1].strip()
        if t and not t.startswith("#"):
            return n
    return start


def _stmt_span(stmt: ast.stmt, *, default_line: int) -> tuple[int, int]:
    """Return (start, end) span for a statement, using defaults when missing."""
    start = getattr(stmt, "lineno", 10**9)
    end = getattr(stmt, "end_lineno", start)
    if start == 10**9:
        start = default_line
        end = default_line
    return start, end


def _pick_smallest_spanning_stmt(scope: ast.AST, line: int) -> ast.stmt | None:
    """Return the smallest ast.stmt in scope that spans `line`."""
    candidates: list[ast.stmt] = []
    for node in ast.walk(scope):
        if not isinstance(node, ast.stmt):
            continue
        s0, s1 = _stmt_span(node, default_line=line)
        if s0 <= line <= s1:
            candidates.append(node)

    if not candidates:
        return None

    def _key(stmt: ast.stmt) -> tuple[int, int]:
        s0, s1 = _stmt_span(stmt, default_line=line)
        return (s1 - s0, s0)

    return min(candidates, key=_key)


def _physical_span_snippet(
    source_lines: list[str],
    *,
    start: int,
    end: int,
) -> str | None:
    """Return a compact snippet from the physical lines [start, end]."""
    if not source_lines:
        return None
    b0 = max(1, start)
    b1 = max(b0, end)
    chunk = " ".join(source_lines[b0 - 1 : min(b1, len(source_lines))]).strip()
    return _truncate(chunk) if chunk else None


def _physical_line_snippet(source_lines: list[str], line: int) -> str | None:
    """Return a compact snippet from the physical line, if it exists."""
    if 1 <= line <= len(source_lines):
        physical = source_lines[line - 1].strip()
        return _truncate(physical) if physical else None
    return None


def _best_stmt_snippet_for_line(
    scope: ast.AST,
    line: int,
    source_lines: list[str],
) -> str | None:
    """Return a short snippet for the smallest statement spanning `line` (or the physical line)."""
    best = _pick_smallest_spanning_stmt(scope, line)
    if best is None:
        return _physical_line_snippet(source_lines, line)

    snippet = _truncate(_unparse(best))
    if snippet and snippet != "<expr>":
        return snippet

    s0, s1 = _stmt_span(best, default_line=line)
    return _physical_span_snippet(source_lines, start=s0, end=s1)


def _map_range_to_group_item(
    rng: LineRange,
    *,
    funcs: list[FuncInfo],
    collector: BranchCollector,
    branch_cache: dict[str, list[BranchBlock]],
    source_lines: list[str],
) -> tuple[str, LineRange, bool, Detail | None]:
    """Map a range to (qualname, range, full_coverage_of_func, detail_for_partial)."""
    anchor_line = _pick_anchor_line(rng, source_lines)

    fi = find_containing_func(funcs, rng)
    if fi is None:
        # Best-effort: show the physical line as detail
        snippet = _best_stmt_snippet_for_line(
            ast.parse("\n".join(source_lines)),
            anchor_line,
            source_lines,
        )
        return ("<module>", rng, False, Detail("code", snippet) if snippet else None)

    qual = fi.qualname
    full = rng.covers(fi.start, fi.end)
    if full:
        return (qual, rng, True, None)

    # 1) Prefer branch label (if/else/except/finally/case...)
    branch_label = _best_branch_label_for_range(
        LineRange(anchor_line, anchor_line),
        qual=qual,
        fi=fi,
        collector=collector,
        branch_cache=branch_cache,
    )
    if branch_label:
        return (qual, rng, False, Detail("branch", branch_label))

    snippet = _best_stmt_snippet_for_line(fi.node, anchor_line, source_lines)
    return (qual, rng, False, Detail("code", snippet) if snippet else None)


def _format_grouped_mapping(
    grouped: dict[str, list[tuple[LineRange, bool, Detail | None]]],
    *,
    header_path: Path,
    qual_kind: dict[str, Literal["function", "method"]],
) -> str:
    """Render the grouped mapping to Markdown with friendly wording."""
    out_lines: list[str] = [f"\nIn `{header_path}`:\n"]

    for qual in sorted(grouped.keys()):
        kind = qual_kind.get(qual, "function")
        if qual == "<module>":
            out_lines.append("- In the module scope")
        else:
            out_lines.append(f"- In the `{qual}()` {kind}")

        partials = [x for x in grouped[qual] if not x[1]]
        for rng, _full, detail in sorted(
            partials,
            key=lambda x: (x[0].start, x[0].end),
        ):
            if detail is None:
                out_lines.append(f"  - `{rng.start}-{rng.end}`")
                continue

            if detail.kind == "branch":
                out_lines.append(
                    f"  - `{rng.start}-{rng.end}`: from the `{_md_inline_code(detail.text)}` path.",
                )
                continue

            # detail.kind == "code" comment
            snippet = _md_inline_code(detail.text)
            if rng.start == rng.end:
                out_lines.append(f"  - `{rng.start}-{rng.end}`: the line `{snippet}`")
            else:
                out_lines.append(
                    f"  - `{rng.start}-{rng.end}`: the lines starting with `{snippet}`",
                )

    return "\n".join(out_lines) + "\n"


def render_mapping(file_path: Path, ranges: list[LineRange], *, root: Path) -> str:
    """Render a Markdown mapping for the provided uncovered ranges."""
    source_lines, tree = _parse_python_file(file_path)

    funcs = collect_functions(tree)
    collector = BranchCollector(source_lines)
    branch_cache: dict[str, list[BranchBlock]] = {}

    qual_kind: dict[str, Literal["function", "method"]] = {
        f.qualname: ("method" if f.is_method else "function") for f in funcs
    }

    grouped: dict[str, list[tuple[LineRange, bool, Detail | None]]] = {}
    for rng in ranges:
        qual, rr, full, detail = _map_range_to_group_item(
            rng,
            funcs=funcs,
            collector=collector,
            branch_cache=branch_cache,
            source_lines=source_lines,
        )
        grouped.setdefault(qual, []).append((rr, full, detail))

    header_path = file_path.relative_to(root) if file_path.is_absolute() else file_path
    return _format_grouped_mapping(
        grouped,
        header_path=header_path,
        qual_kind=qual_kind,
    )


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
    except subprocess.SubprocessError as e:
        LOGGER.warning("Failed to read clipboard: %s", e)
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
    except subprocess.SubprocessError as e:
        LOGGER.warning("Failed to write to clipboard: %s", e)


def _strip_percent_prefixed_args(argv: list[str]) -> list[str]:
    """If any arg contains '%', drop that arg and all args before it, except argv[0].

    This is meant to tolerate Windows launchers that inject placeholder args like
    '%VAR%'. When such an arg appears, we keep the first arg (argv[0]) and then
    keep only the args that follow the last percent-containing arg.
    """
    if not argv:
        return argv

    last_percent_index: int | None = None
    for i, a in enumerate(argv):
        if "%" in a:
            last_percent_index = i

    if last_percent_index is None:
        return argv

    # Drop the offending arg itself and everything before it, but keep argv[0].
    # If the offending arg is argv[0], we still drop it.
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
    """Run the gap analysis logic for the parsed arguments and return the report."""
    _configure_logging(debug=args.debug)

    start = Path(args.root).resolve() if args.root else Path.cwd()
    root = find_project_root(start)

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
        except (CoverageGapError, OSError) as e:
            # Log error but continue processing other lines
            LOGGER.warning("Skipping line '%s': %s", line, e)
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


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CoverageGapError, OSError) as err:
        _log_fatal(err)


# eof
