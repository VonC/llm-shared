"""Tests for coverage gap helper core branches.

Fix: Cover exception messages, line-range parsing, project-root lookup, AST
helpers, branch collection, JSON helpers, mapping helpers, and rendering in
`tools.coverage_gap_functions`.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from tools import coverage_gap_functions as gap_functions

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

_BRANCH_BLOCK_SIZE = 3
_SECOND_LINE = 2
_ANCHOR_LINE = 3


def _control_flow_source() -> str:
    return (
        "def sample(value):\n"
        "    if value:\n"
        "        then_line = 1\n"
        "    else:\n"
        "        else_line = 2\n"
        "\n"
        "    for item in [1, 2]:\n"
        "        item += 1\n"
        "    else:\n"
        "        item = 0\n"
        "\n"
        "    while value:\n"
        "        break\n"
        "    else:\n"
        "        value = 0\n"
        "\n"
        "    try:\n"
        "        risky = value / 1\n"
        "    except ZeroDivisionError as err:\n"
        "        value = 1\n"
        "    else:\n"
        "        value = risky\n"
        "    finally:\n"
        "        value += 1\n"
        "\n"
        "    match value:\n"
        "        case 1:\n"
        "            value = 2\n"
        "        case _:\n"
        "            value = 3\n"
        "\n"
        "    return value\n"
    )


def _sample_function_node() -> tuple[list[str], ast.FunctionDef]:
    module = ast.parse(_control_flow_source())
    function_node = module.body[0]
    assert isinstance(function_node, ast.FunctionDef)
    return _control_flow_source().splitlines(), function_node


def test_exception_messages_are_stable(tmp_path: Path) -> None:
    """Exception helpers should keep their user-facing messages stable."""
    assert str(gap_functions.InvalidRangeError("bad")) == (
        "Invalid range 'bad' (expected N or N-M)"
    )
    assert str(gap_functions.InputFileNotFoundError(tmp_path / "missing.py")) == (
        f"File not found: {tmp_path / 'missing.py'}"
    )
    assert str(gap_functions.CoverageJsonNotFoundError(tmp_path / "coverage.json")) == (
        f"Coverage JSON not found: {tmp_path / 'coverage.json'}"
    )
    assert str(gap_functions.CoverageJsonFormatError("broken")) == (
        "coverage.json format error: broken"
    )
    assert str(gap_functions.CoverageJsonFileMatchError("ambiguous")) == (
        "coverage.json file match error: ambiguous"
    )


def test_line_range_helpers_cover_single_swap_invalid_and_compression() -> None:
    """Line-range helpers should parse single values, swapped ranges, and compress runs."""
    assert gap_functions.LineRange.parse("7,") == gap_functions.LineRange(7, 7)
    assert gap_functions.LineRange.parse("9-3,") == gap_functions.LineRange(3, 9)
    assert gap_functions.LineRange(2, 6).covers(3, 5) is True
    assert gap_functions.LineRange(2, 6).covers(1, 5) is False

    with pytest.raises(gap_functions.InvalidRangeError, match="expected N or N-M"):
        gap_functions.LineRange.parse("oops")

    assert gap_functions.compress_lines_to_ranges([]) == []
    assert gap_functions.compress_lines_to_ranges([1, 2, 4, 7, 8]) == [
        gap_functions.LineRange(1, 2),
        gap_functions.LineRange(4, 4),
        gap_functions.LineRange(7, 8),
    ]


def test_branch_block_contains_and_size() -> None:
    """Branch blocks should report containment and span size."""
    branch_block = gap_functions.BranchBlock("if flag", 2, 5)
    assert branch_block.contains(4) is True
    assert branch_block.contains(6) is False
    assert branch_block.size == _BRANCH_BLOCK_SIZE


def test_find_project_root_handles_git_file_markers_and_fallback(
    tmp_path: Path,
) -> None:
    """Project-root lookup should accept directory markers, file markers, and fallback to the start path."""
    git_root = tmp_path / "git-root"
    git_start = git_root / "nested" / "deeper"
    git_start.mkdir(parents=True)
    (git_root / ".git").mkdir()
    assert gap_functions.find_project_root(git_start) == git_root.resolve()

    file_root = tmp_path / "file-root"
    file_start = file_root / "child"
    file_start.mkdir(parents=True)
    (file_root / "pyproject.toml").write_text(
        "[project]\nname = 'demo'\n", encoding="utf-8",
    )
    assert gap_functions.find_project_root(file_start) == file_root.resolve()

    fallback_start = tmp_path / "plain" / "nested"
    fallback_start.mkdir(parents=True)
    assert gap_functions.find_project_root(fallback_start) == fallback_start.resolve()


def test_ast_text_helpers_cover_compact_unparse_and_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AST text helpers should normalize whitespace, unparse expressions, and detect header lines."""
    assert gap_functions._compact(" alpha\n  beta\tgamma ") == "alpha beta gamma"

    expression_stmt = ast.parse("value + 1").body[0]
    assert isinstance(expression_stmt, ast.Expr)
    assert gap_functions._unparse(expression_stmt.value) == "value + 1"

    def fake_unparse(_node: ast.AST) -> str:
        msg = "cannot unparse"
        raise TypeError(msg)

    monkeypatch.setattr(gap_functions.ast, "unparse", fake_unparse)
    assert gap_functions._unparse(expression_stmt.value) == "<expr>"

    assert gap_functions._stmt_list_span([]) is None
    statements = ast.parse("first = 1\nsecond = 2\n").body
    assert gap_functions._stmt_list_span(statements) == (1, 2)
    assert gap_functions._maybe_prev_header_line(["line"], 1, keywords=("else",)) == 1
    assert (
        gap_functions._maybe_prev_header_line(
            ["else:", "    value = 1"],
            2,
            keywords=("else",),
        )
        == 1
    )
    assert (
        gap_functions._maybe_prev_header_line(
            ["plain:", "    value = 1"],
            2,
            keywords=("else",),
        )
        == _SECOND_LINE
    )


def test_func_collector_and_collect_functions_capture_methods_and_async_functions() -> (
    None
):
    """Function collection should keep qualified names and method flags for class members."""
    tree = ast.parse(
        "class Example:\n"
        "    def method(self):\n"
        "        return 1\n"
        "\n"
        "    async def async_method(self):\n"
        "        return 2\n"
        "\n"
        "def top():\n"
        "    return 3\n",
    )

    collector = gap_functions._FuncCollector()
    collector.visit(tree)

    assert [func.qualname for func in collector.funcs] == [
        "Example.method",
        "Example.async_method",
        "top",
    ]
    assert [func.is_method for func in collector.funcs] == [True, True, False]
    assert collector._class_stack == []
    assert collector._func_stack == []

    collected = gap_functions.collect_functions(tree)
    assert [func.qualname for func in collected] == [
        "Example.method",
        "Example.async_method",
        "top",
    ]


def _collected_branch_labels() -> tuple[gap_functions.BranchCollector, set[str]]:
    source_lines, function_node = _sample_function_node()
    collector = gap_functions.BranchCollector(source_lines)
    collector._blocks.append(gap_functions.BranchBlock("stale", 0, 0))

    blocks = collector.collect(function_node)
    return collector, {block.label for block in blocks}


def test_branch_collector_collects_if_for_and_while_labels() -> None:
    """Branch collection should emit labels for `if`, `for`, and `while` blocks."""
    collector, labels = _collected_branch_labels()

    assert collector._source_lines == _control_flow_source().splitlines()
    assert "stale" not in labels
    assert "if value (then)" in labels
    assert "else of if value" in labels
    assert "for item in [1, 2]" in labels
    assert "else of for item in [1, 2]" in labels
    assert "while value" in labels
    assert "else of while value" in labels


def test_branch_collector_collects_try_and_match_labels() -> None:
    """Branch collection should emit labels for `try` and `match` blocks."""
    _, labels = _collected_branch_labels()

    assert "try" in labels
    assert "except ZeroDivisionError as err" in labels
    assert "else of try" in labels
    assert "finally" in labels
    assert "case 1 (match value)" in labels
    assert "case _ (match value)" in labels


def test_branch_collector_add_ignores_missing_bounds_and_normalizes_order() -> None:
    """Direct block insertion should ignore missing bounds and normalize reversed spans."""
    collector = gap_functions.BranchCollector([])

    collector._add("ignored", None, 4)
    collector._add("normalized", 5, 2)

    assert collector._blocks == [gap_functions.BranchBlock("normalized", 2, 5)]


def test_branch_collector_handles_sparse_manual_nodes_for_uncommon_paths() -> None:
    """Manual AST nodes should cover the fallback branches in each branch handler."""
    collector = gap_functions.BranchCollector(["if flag:", "match subject:"])

    empty_if = ast.If(test=ast.Name(id="flag", ctx=ast.Load()), body=[], orelse=[])
    empty_if.lineno = 5
    empty_if.end_lineno = 5
    collector._handle_if(empty_if)

    empty_try = ast.Try(body=[], handlers=[], orelse=[], finalbody=[])
    empty_try.lineno = 6
    empty_try.end_lineno = 6
    collector._handle_try(empty_try)

    empty_match = ast.Match(
        subject=ast.Name(id="subject", ctx=ast.Load()),
        cases=[ast.match_case(pattern=ast.MatchAs(), guard=None, body=[])],
    )
    empty_match.lineno = 7
    empty_match.end_lineno = 7
    collector._handle_match(empty_match)

    assert collector._blocks == [gap_functions.BranchBlock("if flag (then)", 5, 5)]


def test_json_shape_helpers_validate_dicts_lists_and_keys() -> None:
    """JSON shape helpers should accept valid containers and reject invalid key types."""
    assert gap_functions._is_obj_dict({}) is True
    assert gap_functions._is_obj_dict([]) is False
    assert gap_functions._is_obj_list([]) is True
    assert gap_functions._is_obj_list({}) is False

    assert gap_functions._ensure_dict({"key": "value"}, "root") == {"key": "value"}
    with pytest.raises(
        gap_functions.CoverageJsonFormatError, match="root is not a dict",
    ):
        gap_functions._ensure_dict([], "root")

    assert gap_functions._ensure_str_dict({"a": 1}, "ctx") == {"a": 1}
    with pytest.raises(gap_functions.CoverageJsonFormatError, match="non-string key"):
        gap_functions._ensure_str_dict({1: "bad"}, "ctx")

    assert gap_functions._ensure_str_obj_dict({"a": 1}, "ctx") == {"a": 1}
    with pytest.raises(gap_functions.CoverageJsonFormatError, match="non-string key"):
        gap_functions._ensure_str_obj_dict({1: "bad"}, "ctx")


def test_coverage_json_helpers_parse_match_and_load_ranges(tmp_path: Path) -> None:
    """Coverage JSON helpers should read files, normalize paths, and load missing ranges."""
    assert gap_functions._parse_json_root_obj('{"files": {}}') == {"files": {}}
    with pytest.raises(gap_functions.CoverageJsonFormatError, match="invalid JSON"):
        gap_functions._parse_json_root_obj("{")

    assert gap_functions._normalize_rel_path("./pkg\\module.py") == "pkg/module.py"

    single_match = gap_functions._find_matching_file_entries(
        {"other/pkg/module.py": {"missing_lines": [2, 3, 5]}},
        "pkg/module.py",
    )
    assert single_match[0][0] == "other/pkg/module.py"

    with pytest.raises(gap_functions.CoverageJsonFileMatchError, match="no entry for"):
        gap_functions._pick_single_file_entry(
            [],
            target_rel_file="pkg/module.py",
            coverage_json_path=tmp_path / "coverage.json",
        )

    with pytest.raises(
        gap_functions.CoverageJsonFileMatchError, match="ambiguous match",
    ):
        gap_functions._pick_single_file_entry(
            [
                ("one/pkg/module.py", {"missing_lines": [1]}),
                ("two/pkg/module.py", {"missing_lines": [2]}),
            ],
            target_rel_file="pkg/module.py",
            coverage_json_path=tmp_path / "coverage.json",
        )

    assert gap_functions._extract_missing_lines({"missing_lines": [2, 3]}) == [2, 3]
    with pytest.raises(gap_functions.CoverageJsonFormatError, match="not a list"):
        gap_functions._extract_missing_lines({"missing_lines": "bad"})
    with pytest.raises(gap_functions.CoverageJsonFormatError, match="non-integer"):
        gap_functions._extract_missing_lines({"missing_lines": [1, "two"]})

    with pytest.raises(
        gap_functions.CoverageJsonNotFoundError, match="Coverage JSON not found",
    ):
        gap_functions._read_text_or_raise(tmp_path / "missing.json")

    coverage_json_path = tmp_path / "coverage.json"
    coverage_json_path.write_text(
        json.dumps(
            {
                "files": {
                    "pkg/module.py": {"missing_lines": [2, 3, 5]},
                },
            },
        ),
        encoding="utf-8",
    )

    assert gap_functions.load_missing_ranges_from_coverage_json(
        coverage_json_path,
        "pkg/module.py",
    ) == [
        gap_functions.LineRange(2, 3),
        gap_functions.LineRange(5, 5),
    ]


def test_parse_python_file_handles_success_and_syntax_errors(tmp_path: Path) -> None:
    """Python-file parsing should return source lines on success and wrap syntax errors."""
    python_file = tmp_path / "demo.py"
    python_file.write_text(
        "if flag:\n    value = 1\nelse:\n    value = 2\n",
        encoding="utf-8",
    )

    source_lines, tree = gap_functions._parse_python_file(python_file)
    assert source_lines[0] == "if flag:"
    assert isinstance(tree, ast.AST)

    broken_file = tmp_path / "broken.py"
    broken_file.write_text("def broken(:\n", encoding="utf-8")
    with pytest.raises(gap_functions.CoverageGapError, match="Cannot parse"):
        gap_functions._parse_python_file(broken_file)


def test_snippet_helpers_cover_truncate_md_and_anchor_selection() -> None:
    """Snippet helpers should normalize whitespace and select a stable anchor line."""
    assert gap_functions._truncate(" alpha\n beta ", limit=20) == "alpha beta"
    assert gap_functions._truncate("word " * 20, limit=10).endswith("…")
    assert gap_functions._md_inline_code("`quoted`") == "'quoted'"
    assert (
        gap_functions._pick_anchor_line(
            gap_functions.LineRange(1, 3),
            ["", "    # comment", "value = 1"],
        )
        == _ANCHOR_LINE
    )
    assert (
        gap_functions._pick_anchor_line(
            gap_functions.LineRange(1, 2),
            ["", "   # comment"],
        )
        == 1
    )


def test_physical_snippet_helpers_cover_line_and_span_fallbacks() -> None:
    """Physical snippet helpers should join spans, trim lines, and fall back when no AST statement exists."""
    assert gap_functions._physical_span_snippet([], start=1, end=2) is None
    assert (
        gap_functions._physical_span_snippet(
            [" first = 1 ", " second = 2 "],
            start=1,
            end=2,
        )
        == "first = 1 second = 2"
    )
    assert gap_functions._physical_line_snippet(["  value = 1  "], 1) == "value = 1"
    assert gap_functions._physical_line_snippet(["value = 1"], _SECOND_LINE) is None
    assert gap_functions._best_stmt_snippet_for_line(
        ast.parse(""), 1, ["  value = 1  "],
    ) == ("value = 1")


def test_statement_selection_helpers_cover_smallest_stmt_and_unparse_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Statement selection should prefer the smallest statement and fall back when unparsing yields `<expr>`."""
    python_file = tmp_path / "demo.py"
    python_file.write_text(
        "if flag:\n    value = 1\nelse:\n    value = 2\n",
        encoding="utf-8",
    )
    source_lines, tree = gap_functions._parse_python_file(python_file)

    dummy_statement = ast.Pass()
    assert gap_functions._stmt_span(dummy_statement, default_line=7) == (7, 7)

    smallest_statement = gap_functions._pick_smallest_spanning_stmt(tree, 2)
    assert isinstance(smallest_statement, ast.Assign)
    assert gap_functions._pick_smallest_spanning_stmt(tree, 99) is None

    assert (
        gap_functions._best_stmt_snippet_for_line(tree, 2, source_lines) == "value = 1"
    )

    def fake_unparse(_node: ast.AST) -> str:
        return "<expr>"

    monkeypatch.setattr(gap_functions, "_unparse", fake_unparse)
    assert (
        gap_functions._best_stmt_snippet_for_line(tree, 2, source_lines) == "value = 1"
    )


def test_find_containing_func_prefers_smallest_match_and_falls_back() -> None:
    """Function containment should prefer the narrowest containing span and fall back to start-line matches."""
    outer_node = ast.parse("pass")
    inner_node = ast.parse("pass")
    funcs = [
        gap_functions.FuncInfo("outer", 1, 20, outer_node, is_method=False),
        gap_functions.FuncInfo("inner", 5, 10, inner_node, is_method=False),
    ]
    assert (
        gap_functions.find_containing_func(funcs, gap_functions.LineRange(6, 7))
        == funcs[1]
    )
    assert (
        gap_functions.find_containing_func(funcs, gap_functions.LineRange(11, 11))
        == funcs[0]
    )
    assert (
        gap_functions.find_containing_func(funcs, gap_functions.LineRange(30, 30))
        is None
    )


def test_map_range_to_group_item_covers_module_full_branch_and_code_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Range mapping should handle module fallbacks, full coverage, branch labels, and code snippets."""
    source_lines, function_node = _sample_function_node()
    collector = gap_functions.BranchCollector(source_lines)
    function_info = gap_functions.FuncInfo(
        "sample",
        function_node.lineno,
        getattr(function_node, "end_lineno", function_node.lineno),
        function_node,
        is_method=False,
    )
    branch_cache: dict[str, list[gap_functions.BranchBlock]] = {}

    assert (
        gap_functions._best_branch_label_for_range(
            gap_functions.LineRange(3, 3),
            qual="sample",
            fi=function_info,
            collector=collector,
            branch_cache=branch_cache,
        )
        == "if value (then)"
    )
    assert (
        gap_functions._best_branch_label_for_range(
            gap_functions.LineRange(99, 99),
            qual="sample",
            fi=function_info,
            collector=collector,
            branch_cache=branch_cache,
        )
        is None
    )
    assert "sample" in branch_cache

    module_mapping = gap_functions._map_range_to_group_item(
        gap_functions.LineRange(1, 1),
        funcs=[],
        collector=collector,
        branch_cache={},
        source_lines=["value = 1"],
    )
    assert module_mapping[0] == "<module>"
    assert module_mapping[2] is False
    assert module_mapping[3] == gap_functions.Detail("code", "value = 1")

    full_mapping = gap_functions._map_range_to_group_item(
        gap_functions.LineRange(function_info.start, function_info.end),
        funcs=[function_info],
        collector=collector,
        branch_cache={},
        source_lines=source_lines,
    )
    assert full_mapping == (
        "sample",
        gap_functions.LineRange(function_info.start, function_info.end),
        True,
        None,
    )

    branch_mapping = gap_functions._map_range_to_group_item(
        gap_functions.LineRange(3, 3),
        funcs=[function_info],
        collector=collector,
        branch_cache={},
        source_lines=source_lines,
    )
    assert branch_mapping[3] == gap_functions.Detail("branch", "if value (then)")

    def fake_best_branch_label_for_range(
        rng: gap_functions.LineRange,
        *,
        qual: str,
        fi: gap_functions.FuncInfo,
        collector: gap_functions.BranchCollector,
        branch_cache: dict[str, list[gap_functions.BranchBlock]],
    ) -> str | None:
        del rng, qual, fi, collector, branch_cache
        return None

    def fake_best_stmt_snippet_for_line(
        scope: ast.AST,
        line: int,
        source_lines_arg: list[str],
    ) -> str:
        del scope, line, source_lines_arg
        return "value = 1"

    monkeypatch.setattr(
        gap_functions,
        "_best_branch_label_for_range",
        fake_best_branch_label_for_range,
    )
    monkeypatch.setattr(
        gap_functions,
        "_best_stmt_snippet_for_line",
        fake_best_stmt_snippet_for_line,
    )

    code_mapping = gap_functions._map_range_to_group_item(
        gap_functions.LineRange(3, 3),
        funcs=[function_info],
        collector=collector,
        branch_cache={},
        source_lines=source_lines,
    )
    assert code_mapping[3] == gap_functions.Detail("code", "value = 1")


def test_format_grouped_mapping_and_render_mapping_produce_expected_text(
    tmp_path: Path,
) -> None:
    """Grouped mapping text should render module, method, branch, and file-relative output."""
    formatted = gap_functions._format_grouped_mapping(
        {
            "<module>": [(gap_functions.LineRange(1, 1), False, None)],
            "demo": [
                (
                    gap_functions.LineRange(2, 2),
                    False,
                    gap_functions.Detail("branch", "if flag (then)"),
                ),
                (
                    gap_functions.LineRange(3, 3),
                    False,
                    gap_functions.Detail("code", "value = 1"),
                ),
                (
                    gap_functions.LineRange(4, 5),
                    False,
                    gap_functions.Detail("code", "value = 2"),
                ),
            ],
        },
        header_path=Path("pkg/demo.py"),
        qual_kind={"demo": "method"},
    )
    assert f"In `{Path('pkg/demo.py')}`:" in formatted
    assert "- In the module scope" in formatted
    assert "- In the `demo()` method" in formatted
    assert "from the `if flag (then)` path." in formatted
    assert "the line `value = 1`" in formatted
    assert "the lines starting with `value = 2`" in formatted

    render_file = tmp_path / "demo.py"
    render_file.write_text(
        "def render_demo(flag):\n"
        "    if flag:\n"
        "        return 1\n"
        "    return 0\n",
        encoding="utf-8",
    )
    rendered = gap_functions.render_mapping(
        render_file,
        [gap_functions.LineRange(2, 3)],
        root=tmp_path,
    )
    assert "In `demo.py`:" in rendered
    assert "render_demo()" in rendered


# eof
