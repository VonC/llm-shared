"""AST and rendering helpers for coverage gap analysis.

Fix: Split the AST traversal and report rendering logic out of
`tools.coverage_gap_functions` so the script hub stays smaller while the
mapping behavior stays unchanged.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Literal

from tools.coverage_gap_functions_shared import (
    BranchBlock,
    CoverageGapError,
    Detail,
    FuncInfo,
    LineRange,
)

if TYPE_CHECKING:
    from pathlib import Path


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
    start = min(getattr(stmt, "lineno", 10**9) for stmt in stmts)
    end = max(
        getattr(stmt, "end_lineno", getattr(stmt, "lineno", 0))
        for stmt in stmts
    )
    return (start, end)


def _maybe_prev_header_line(
    source_lines: list[str],
    start_line_1based: int,
    *,
    keywords: tuple[str, ...],
) -> int:
    """Include branch header lines such as else/finally/case in the block span."""
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
        is_method = bool(self._class_stack)
        self.funcs.append(FuncInfo(qual, node.lineno, end, node, is_method))
        self.generic_visit(node)
        self._func_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._func_stack.append(node.name)
        qual = ".".join(self._class_stack + self._func_stack)
        end = getattr(node, "end_lineno", node.lineno)
        is_method = bool(self._class_stack)
        self.funcs.append(FuncInfo(qual, node.lineno, end, node, is_method))
        self.generic_visit(node)
        self._func_stack.pop()


def collect_functions(tree: ast.AST) -> list[FuncInfo]:
    """Collect all (async) functions with their qualified names and line spans."""
    visitor = _FuncCollector()
    visitor.visit(tree)
    return visitor.funcs


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

        for stmt in node.body:
            self._walk(stmt)
        for stmt in node.orelse:
            self._walk(stmt)

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
                self._add(
                    f"else of {kind} {tgt} in {it}",
                    orelse_start,
                    orelse_span[1],
                )

        for stmt in node.body:
            self._walk(stmt)
        for stmt in node.orelse:
            self._walk(stmt)

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

        for stmt in node.body:
            self._walk(stmt)
        for stmt in node.orelse:
            self._walk(stmt)

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
            for handler in handlers:
                span = _stmt_list_span(handler.body)
                if span:
                    start = min(handler.lineno, span[0])
                    typ = "*" if handler.type is None else _unparse(handler.type)
                    nm = f" as {handler.name}" if getattr(handler, "name", None) else ""
                    self._add(f"except {typ}{nm}", start, span[1])
                _walk_stmts(handler.body)

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

            for stmt in case.body:
                self._walk(stmt)


# ----------------------------
# Mapping logic
# ----------------------------


def find_containing_func(funcs: list[FuncInfo], rng: LineRange) -> FuncInfo | None:
    """Find the smallest function that contains the given line range (or its start line)."""
    candidates = [func for func in funcs if func.start <= rng.start and func.end >= rng.end]
    if not candidates:
        candidates = [func for func in funcs if func.start <= rng.start <= func.end]
    if not candidates:
        return None
    return min(candidates, key=lambda func: (func.end - func.start, func.start))


def _parse_python_file(file_path: Path) -> tuple[list[str], ast.AST]:
    """Read a Python file and return (source_lines, parsed_ast)."""
    src = file_path.read_text(encoding="utf-8")
    source_lines = src.splitlines()
    try:
        tree = ast.parse(src, filename=str(file_path), type_comments=True)
    except SyntaxError as err:
        msg = f"Cannot parse {file_path}: {err.msg} at line {err.lineno}"
        raise CoverageGapError(msg) from err
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
    candidates = [block for block in branch_cache[qual] if block.contains(rng.start)]
    if not candidates:
        return None
    best = min(candidates, key=lambda block: (block.size, block.start))
    return best.label


def _truncate(s: str, limit: int = 160) -> str:
    s2 = " ".join(s.split())
    return (s2[: limit - 1] + "…") if len(s2) > limit else s2


def _md_inline_code(s: str) -> str:
    # Avoid breaking Markdown inline code.
    return s.replace("`", "'")


def _pick_anchor_line(rng: LineRange, source_lines: list[str]) -> int:
    """Pick the first non-empty, non-comment line within the range as the anchor."""
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
    """Return a short snippet for the smallest statement spanning `line`."""
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
        for rng, _full, detail in sorted(partials, key=lambda x: (x[0].start, x[0].end)):
            if detail is None:
                out_lines.append(f"  - `{rng.start}-{rng.end}`")
                continue

            if detail.kind == "branch":
                out_lines.append(
                    f"  - `{rng.start}-{rng.end}`: from the `{_md_inline_code(detail.text)}` path.",
                )
                continue

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
        func.qualname: ("method" if func.is_method else "function") for func in funcs
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


__all__ = [
    "BranchCollector",
    "_FuncCollector",
    "_best_branch_label_for_range",
    "_best_stmt_snippet_for_line",
    "_compact",
    "_format_grouped_mapping",
    "_map_range_to_group_item",
    "_maybe_prev_header_line",
    "_md_inline_code",
    "_parse_python_file",
    "_physical_line_snippet",
    "_physical_span_snippet",
    "_pick_anchor_line",
    "_pick_smallest_spanning_stmt",
    "_stmt_list_span",
    "_stmt_span",
    "_truncate",
    "_unparse",
    "collect_functions",
    "find_containing_func",
    "render_mapping",
]


# eof
