"""Tests for coverage gap helper CLI and entry-point branches.

Fix: Cover logging, clipboard helpers, CLI dispatch, clipboard dispatch,
analysis routing, fatal exits, and `__main__` execution in
`tools.coverage_gap_functions`.
"""

from __future__ import annotations

import argparse
import logging
import runpy
import subprocess
import sys
from pathlib import Path
from typing import cast

import pytest

from tools import coverage_gap_functions as gap_functions

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

_CLI_EXIT_CODE = 11
_CLIPBOARD_EXIT_CODE = 22
_FATAL_EXIT_CODE = 2


class _ClipboardParser:
    def __init__(self) -> None:
        self.parsed_args: list[list[str]] = []

    def parse_args(self, args: list[str]) -> argparse.Namespace:
        self.parsed_args.append(args)
        if args[0] == "invalid.py":
            raise SystemExit(2)
        return argparse.Namespace(
            file=args[0],
            ranges=args[1:],
            root=None,
            coverage_json=None,
            debug=False,
        )


class _HelpParser:
    def __init__(self) -> None:
        self.help_calls = 0

    def print_help(self) -> None:
        self.help_calls += 1


def test_configure_logging_resets_root_logger() -> None:
    """Logging setup should replace handlers and switch the root logger level."""
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level

    try:
        root_logger.addHandler(logging.StreamHandler(sys.stderr))
        gap_functions._configure_logging(debug=True)

        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) == 1
        assert getattr(root_logger.handlers[0], "stream", None) is sys.stdout
    finally:
        root_logger.handlers.clear()
        for handler in original_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(original_level)


def test_clipboard_helpers_cover_success_and_failure_paths(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Clipboard helpers should trim stdout, log preview text, and warn on subprocess failures."""
    get_calls: list[list[str]] = []
    set_calls: list[tuple[list[str], str]] = []

    def fake_which(_name: str) -> str:
        return "powershell"

    def fake_run_success(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if kwargs.get("capture_output"):
            get_calls.append(command)
            return subprocess.CompletedProcess(command, 0, stdout=" copied text \n")

        set_calls.append((command, cast("str", kwargs["input"])))
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(gap_functions.shutil, "which", fake_which)
    monkeypatch.setattr(gap_functions.subprocess, "run", fake_run_success)
    caplog.set_level("INFO")

    assert gap_functions._get_clipboard_text() == "copied text"
    gap_functions._set_clipboard_text("clipboard text")

    assert get_calls[0][0] == "powershell"
    assert set_calls[0][0][0] == "powershell"
    assert set_calls[0][1] == "clipboard text"
    assert "DEBUG: Setting clipboard" in caplog.text

    def fake_run_failure(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(gap_functions.subprocess, "run", fake_run_failure)
    caplog.clear()

    assert gap_functions._get_clipboard_text() == ""
    gap_functions._set_clipboard_text("clipboard text")
    assert "Failed to read clipboard" in caplog.text
    assert "Failed to write to clipboard" in caplog.text


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        ([], []),
        (["demo.py", "1-2"], ["demo.py", "1-2"]),
        (["%PLACEHOLDER%", "demo.py", "1-2"], ["demo.py", "1-2"]),
        (["python", "%PLACEHOLDER%", "demo.py", "1-2"], ["python", "demo.py", "1-2"]),
    ],
)
def test_strip_percent_prefixed_args_handles_empty_passthrough_and_suffix_cases(
    argv: list[str],
    expected: list[str],
) -> None:
    """Percent-prefixed launcher arguments should be removed while preserving the remaining suffix."""
    assert gap_functions._strip_percent_prefixed_args(argv) == expected


def test_get_arg_parser_accepts_supported_cli_options() -> None:
    """The CLI parser should expose the expected positional and optional arguments."""
    parser = gap_functions._get_arg_parser()

    parsed = parser.parse_args(
        [
            "demo.py",
            "1",
            "2-3",
            "--root",
            "C:/demo",
            "--coverage-json",
            "coverage.json",
            "--debug",
        ],
    )

    assert parsed.file == "demo.py"
    assert parsed.ranges == ["1", "2-3"]
    assert parsed.root == "C:/demo"
    assert parsed.coverage_json == "coverage.json"
    assert parsed.debug is True


def test_run_analysis_handles_ranges_coverage_json_and_error_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Analysis should route range and coverage-json inputs and raise stable errors for missing inputs."""
    demo_file = tmp_path / "demo.py"
    demo_file.write_text("value = 1\n", encoding="utf-8")
    coverage_json_path = tmp_path / "coverage.json"
    coverage_json_path.write_text(
        '{"files": {"demo.py": {"missing_lines": [1]}}}',
        encoding="utf-8",
    )

    configure_calls: list[bool] = []

    def fake_configure_logging(*, debug: bool) -> None:
        configure_calls.append(debug)

    def fake_render_mapping(
        file_path: Path,
        ranges: list[gap_functions.LineRange],
        *,
        root: Path,
    ) -> str:
        assert file_path == demo_file
        assert root == tmp_path
        return f"report:{[(rng.start, rng.end) for rng in ranges]}"

    monkeypatch.setattr(gap_functions, "_configure_logging", fake_configure_logging)
    monkeypatch.setattr(gap_functions, "render_mapping", fake_render_mapping)

    range_args = argparse.Namespace(
        file="demo.py",
        ranges=["1", "3-4"],
        root=str(tmp_path),
        coverage_json=None,
        debug=True,
    )
    assert gap_functions._run_analysis(range_args) == "report:[(1, 1), (3, 4)]"

    coverage_args = argparse.Namespace(
        file="demo.py",
        ranges=[],
        root=str(tmp_path),
        coverage_json="coverage.json",
        debug=False,
    )
    assert gap_functions._run_analysis(coverage_args) == "report:[(1, 1)]"
    assert configure_calls == [True, False]

    with pytest.raises(gap_functions.InputFileNotFoundError, match="File not found"):
        gap_functions._run_analysis(
            argparse.Namespace(
                file="missing.py",
                ranges=["1"],
                root=str(tmp_path),
                coverage_json=None,
                debug=False,
            ),
        )

    with pytest.raises(
        gap_functions.CoverageJsonNotFoundError, match="Coverage JSON not found",
    ):
        gap_functions._run_analysis(
            argparse.Namespace(
                file="demo.py",
                ranges=[],
                root=str(tmp_path),
                coverage_json="missing.json",
                debug=False,
            ),
        )

    with pytest.raises(gap_functions.CoverageGapError, match="Provide ranges"):
        gap_functions._run_analysis(
            argparse.Namespace(
                file="demo.py",
                ranges=[],
                root=str(tmp_path),
                coverage_json=None,
                debug=False,
            ),
        )


def test_clipboard_text_building_and_copying_logs_each_report(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Clipboard output should be skipped for empty reports and include follow-up lines for real reports."""
    assert gap_functions._build_final_clipboard_text(["", "   "]) is None

    final_text = gap_functions._build_final_clipboard_text(
        [" first report ", "second report"],
    )
    assert final_text is not None
    assert final_text.startswith(
        "Extend test coverage to cover:\n\nfirst report\n\nsecond report",
    )
    assert gap_functions.POST_COVERAGE_LINES[-1] in final_text

    captured_text: list[str] = []

    def fake_set_clipboard_text(text: str) -> None:
        captured_text.append(text)

    monkeypatch.setattr(gap_functions, "_set_clipboard_text", fake_set_clipboard_text)
    caplog.set_level("INFO")

    gap_functions._copy_reports_to_clipboard(["report one", "report two"])

    assert captured_text
    assert "report one" in captured_text[0]
    assert "report one" in caplog.text
    assert "report two" in caplog.text


def test_run_cli_mode_strips_args_runs_analysis_and_copies_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI mode should strip percent-prefixed args, run analysis, and copy one report."""
    parser = gap_functions._get_arg_parser()
    copied_reports: list[list[str]] = []

    def fake_run_analysis(args: argparse.Namespace) -> str:
        assert args.file == "demo.py"
        assert args.ranges == ["1-2"]
        return "rendered report"

    def fake_copy_reports_to_clipboard(reports: list[str]) -> None:
        copied_reports.append(reports)

    monkeypatch.setattr(gap_functions, "_run_analysis", fake_run_analysis)
    monkeypatch.setattr(
        gap_functions,
        "_copy_reports_to_clipboard",
        fake_copy_reports_to_clipboard,
    )

    assert gap_functions._run_cli_mode(parser, ["%PLACEHOLDER%", "demo.py", "1-2"]) == 0
    assert copied_reports == [["rendered report"]]


def test_collect_reports_from_clipboard_handles_success_gap_errors_and_invalid_lines(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Clipboard collection should keep valid reports and warn when parsing or analysis fails."""
    parser = _ClipboardParser()

    def fake_run_analysis(args: argparse.Namespace) -> str:
        if args.file == "error.py":
            msg = "analysis failed"
            raise gap_functions.CoverageGapError(msg)
        return f"report:{args.file}:{args.ranges}"

    monkeypatch.setattr(gap_functions, "_run_analysis", fake_run_analysis)
    caplog.set_level("WARNING")

    reports = gap_functions._collect_reports_from_clipboard(
        cast("argparse.ArgumentParser", parser),
        "demo.py 87% detail\n"
        "error.py 66% detail\n"
        "invalid.py 55% detail\n"
        "not-a-match\n",
    )

    assert reports == ["report:demo.py:['detail']"]
    assert parser.parsed_args == [
        ["demo.py", "detail"],
        ["error.py", "detail"],
        ["invalid.py", "detail"],
    ]
    assert "Skipping line 'error.py 66% detail': analysis failed" in caplog.text
    assert "Skipping invalid line args 'invalid.py 55% detail'" in caplog.text


def test_run_clipboard_mode_prints_help_without_clipboard_and_copies_reports_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clipboard mode should print help for empty clipboard text and copy collected reports otherwise."""
    help_parser = _HelpParser()

    monkeypatch.setattr(gap_functions, "_get_clipboard_text", lambda: "")
    assert (
        gap_functions._run_clipboard_mode(cast("argparse.ArgumentParser", help_parser))
        == 0
    )
    assert help_parser.help_calls == 1

    copied_reports: list[list[str]] = []

    def fake_get_clipboard_text() -> str:
        return "demo.py 87% detail"

    def fake_collect_reports_from_clipboard(
        parser: argparse.ArgumentParser,
        clipboard_content: str,
    ) -> list[str]:
        del parser
        assert clipboard_content == "demo.py 87% detail"
        return ["report"]

    def fake_copy_reports_to_clipboard(reports: list[str]) -> None:
        copied_reports.append(reports)

    monkeypatch.setattr(gap_functions, "_get_clipboard_text", fake_get_clipboard_text)
    monkeypatch.setattr(
        gap_functions,
        "_collect_reports_from_clipboard",
        fake_collect_reports_from_clipboard,
    )
    monkeypatch.setattr(
        gap_functions,
        "_copy_reports_to_clipboard",
        fake_copy_reports_to_clipboard,
    )

    parser = gap_functions._get_arg_parser()
    assert gap_functions._run_clipboard_mode(parser) == 0
    assert copied_reports == [["report"]]


def test_main_dispatches_to_cli_and_clipboard_modes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The entry point should dispatch to CLI mode when args exist and to clipboard mode otherwise."""
    cli_calls: list[list[str]] = []
    clipboard_calls = 0

    def fake_run_cli_mode(parser: argparse.ArgumentParser, raw_argv: list[str]) -> int:
        del parser
        cli_calls.append(raw_argv)
        return _CLI_EXIT_CODE

    def fake_run_clipboard_mode(parser: argparse.ArgumentParser) -> int:
        del parser
        nonlocal clipboard_calls
        clipboard_calls += 1
        return _CLIPBOARD_EXIT_CODE

    monkeypatch.setattr(gap_functions, "_run_cli_mode", fake_run_cli_mode)
    monkeypatch.setattr(gap_functions, "_run_clipboard_mode", fake_run_clipboard_mode)
    monkeypatch.setattr(sys, "argv", ["coverage_gap_functions.py", "demo.py", "1-2"])

    assert gap_functions.main() == _CLI_EXIT_CODE
    assert cli_calls == [["demo.py", "1-2"]]
    assert gap_functions.main([]) == _CLIPBOARD_EXIT_CODE
    assert clipboard_calls == 1


def test_log_fatal_and_script_main_convert_failures_into_exit_code_two(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Fatal error logging and `__main__` execution should convert coverage errors into exit code 2."""
    with pytest.raises(SystemExit) as excinfo:
        gap_functions._log_fatal(gap_functions.CoverageGapError("boom"))
    assert excinfo.value.code == _FATAL_EXIT_CODE

    script_path = Path(gap_functions.__file__)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(script_path), "missing.py", "1", "--root", str(tmp_path)],
    )

    with pytest.raises(SystemExit) as script_excinfo:
        runpy.run_path(str(script_path), run_name="__main__")

    assert script_excinfo.value.code == _FATAL_EXIT_CODE


# eof
