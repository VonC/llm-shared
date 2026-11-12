"""Observe exclusive complete transfers, console encoding and delayed expansion."""

from __future__ import annotations

import runpy
import sys
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import pytest_plugin_environment as env
from tools import pytest_plugin_shell as shell


def expand_delayed(text: str) -> str:
    """Interpret cmd's documented caret/expansion scan for one FOR value token."""
    if "!" not in text:
        return text
    result: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "^":
            index += 1
            result.append(text[index])
        else:
            assert text[index] != "!", "Unescaped delayed expansion"
            result.append(text[index])
        index += 1
    return "".join(result)


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("value", ['space and %PATH% !bang! ^caret &amp |pipe <in >out "quote" (paren)', "only^^caret", "==leading equals", "", "!", "^!", r"C:\Users\Rémi\!café!^"])
def test_for_transfer_preserves_metacharacters(value: str, *, enabled: bool) -> None:
    """FOR substitution avoids reparsing percent/quote/control characters."""
    result = shell.serialize_result({env.SELECTION: value}, delayed_expansion=enabled)
    records = result.splitlines()
    assert len(records) == len(shell.OWNED_KEYS)
    record = next(line for line in records if line.startswith(env.SELECTION + "="))
    assert (expand_delayed(record) if enabled else record) == f"{env.SELECTION}={value}"
    assert all(line.split("=", 1)[0] in shell.OWNED_KEYS for line in records)


@pytest.mark.parametrize("value", ["bad\nline", "bad\rline", "bad\0line", "x" * 8200])
def test_invalid_record_prevents_any_publication(tmp_path: Path, value: str) -> None:
    """An unrepresentable complete result leaves no partial transfer file."""
    with pytest.raises(env.PreparationError, match="transport"):
        shell.publish_result({env.SELECTION: value}, delayed_expansion=False, code_page=850, directory=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_publish_result_is_complete_and_removes_temporary_output(tmp_path: Path) -> None:
    """Only a fully serialized result is exposed to the caller."""
    output = shell.publish_result({env.SELECTION: "process", "UNRELATED": "ignored"}, delayed_expansion=True, code_page=65001, directory=tmp_path)
    assert output.read_text(encoding="utf-8") == shell.serialize_result({env.SELECTION: "process"}, delayed_expansion=True)
    assert list(tmp_path.iterdir()) == [output]


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("code_page", [850, 65001])
def test_non_ascii_result_uses_callers_code_page(tmp_path: Path, code_page: int, *, enabled: bool) -> None:
    """The caller's FOR decoding preserves values in both expansion states."""
    value = r"C:\Users\Rémi\!café!^"
    output = shell.publish_result({env.ROOT: value}, delayed_expansion=enabled, code_page=code_page, directory=tmp_path)
    records = output.read_bytes().decode(f"cp{code_page}").splitlines()
    record = next(line for line in records if line.startswith(env.ROOT + "="))
    assert (expand_delayed(record) if enabled else record) == f"{env.ROOT}={value}"


@pytest.mark.parametrize("code_page", [850, 999999])
def test_encoding_failure_preserves_other_preparation(tmp_path: Path, code_page: int) -> None:
    """An unrepresentable value or invalid code page publishes no result."""
    first = shell.publish_result({env.ROOT: "first"}, delayed_expansion=False, code_page=850, directory=tmp_path)
    before = first.read_bytes()
    with pytest.raises(env.PreparationError, match="code page"):
        shell.publish_result({env.ROOT: "漢字"}, delayed_expansion=False, code_page=code_page, directory=tmp_path)
    second = shell.publish_result({env.ROOT: "second"}, delayed_expansion=False, code_page=850, directory=tmp_path)
    assert first != second
    assert first.read_bytes() == before
    assert set(tmp_path.iterdir()) == {first, second}


def test_unrepresentable_filename_cleans_only_own_file(tmp_path: Path) -> None:
    """A temp path the console cannot read never escapes as an applicable result."""
    directory = tmp_path / "漢字"
    directory.mkdir()
    with pytest.raises(UnicodeError):
        shell.publish_result({}, delayed_expansion=False, code_page=850, directory=directory)
    assert list(directory.iterdir()) == []


def test_cli_calls_shared_builder_and_reports_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The transport owns no duplicate selection or environment algorithm."""
    monkeypatch.setattr(shell.tempfile, "tempdir", str(tmp_path))
    seen: list[tuple[Path, Path]] = []
    def prepare(project: Path, shared: Path, _environment: object) -> dict[str, str]:
        seen.append((project, shared))
        return {env.SELECTION: "process"}
    monkeypatch.setattr(shell, "prepare_environment", prepare)
    args = ["--project-root", str(tmp_path), "--shared-root", str(tmp_path / "shared"), "--code-page", "65001", "--delayed-expansion", "on"]
    assert shell.main(args) == 0
    output = Path(capsys.readouterr().out.strip())
    assert seen == [(tmp_path, tmp_path / "shared")]
    assert output.exists()
    output.unlink()
    def fail(*_args: object) -> dict[str, str]:
        message = "selected policy unavailable"
        raise env.PreparationError(message)
    monkeypatch.setattr(shell, "prepare_environment", fail)
    assert shell.main(args) == pytest.ExitCode.USAGE_ERROR
    assert "selected policy unavailable" in capsys.readouterr().err
    assert not output.exists()


def test_write_failure_cleans_transfer_owned_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Interrupted publication cannot leave a result for a caller to apply."""
    first = shell.publish_result({}, delayed_expansion=False, code_page=850, directory=tmp_path)
    class FailedWrite(BytesIO):
        def write(self, _content: object, /) -> int:
            message = "write failure"
            raise OSError(message)
    def fail(descriptor: int, _mode: str) -> FailedWrite:
        shell.os.close(descriptor)
        return FailedWrite()
    monkeypatch.setattr(shell.os, "fdopen", fail)
    with pytest.raises(OSError, match="write failure"):
        shell.publish_result({}, delayed_expansion=False, code_page=850, directory=tmp_path)
    assert list(tmp_path.iterdir()) == [first]


def test_failed_path_publication_removes_complete_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If stdout fails, no abandoned success file remains for another caller."""
    class FailedOutput(BytesIO):
        def flush(self) -> None:
            message = "output failure"
            raise OSError(message)
    monkeypatch.setattr(shell.tempfile, "tempdir", str(tmp_path))
    def prepare(*_args: object) -> dict[str, str]:
        return {}
    monkeypatch.setattr(shell, "prepare_environment", prepare)
    monkeypatch.setattr(sys, "stdout", SimpleNamespace(buffer=FailedOutput()))
    args = ["--project-root", str(tmp_path), "--shared-root", str(tmp_path), "--code-page", "850", "--delayed-expansion", "off"]
    assert shell.main(args) == pytest.ExitCode.USAGE_ERROR
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("fragment", [
    'if "!"=="" goto delayed_on',
    '--project-root "%CD%\\." --shared-root "%~dp0.."',
    "--code-page %_LLM_PYTEST_CODE_PAGE% --delayed-expansion %_LLM_PYTEST_DELAYED%",
    'for /f "tokens=2 delims=:" %%C in (\'chcp\')',
    "if not defined _LLM_PYTEST_TRANSFER goto failed",
    'if not exist "%_LLM_PYTEST_TRANSFER%" goto failed',
    'endlocal & (for /f "usebackq delims=" %%V',
    ') & del /q "%_LLM_PYTEST_APPLY%" 2>nul',
    ':failed\nif defined _LLM_PYTEST_TRANSFER del /q "%_LLM_PYTEST_TRANSFER%" 2>nul',
    'set "_LLM_PYTEST_APPLY=%_LLM_PYTEST_APPLY:^=^^%"',
    'set "_LLM_PYTEST_APPLY=%_LLM_PYTEST_APPLY:!=^!%"',
])
def test_launcher_applies_only_success_and_cleans_both_paths(fragment: str) -> None:
    """Inspect the adapter's observed inputs and cleanup on both return paths."""
    launcher = (Path(shell.__file__).parent.parent / "bin/prepare_pytest_plugins.bat").read_text(encoding="utf-8")
    assert fragment in launcher
    assert launcher.count("setlocal DisableDelayedExpansion") == len(("on", "off"))
    assert launcher.index("if not defined _LLM_PYTEST_TRANSFER goto failed") < launcher.index('do set "%%V"')
    assert "%RANDOM%" not in launcher


def test_script_entrypoint_reports_io_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Direct invocation uses the builder and exits before publishing on IO errors."""
    def fail(*_args: object, **_kwargs: object) -> dict[str, str]:
        message = "source unavailable"
        raise OSError(message)
    monkeypatch.setattr(env, "prepare_environment", fail)
    monkeypatch.setattr(sys, "argv", ["prepare", "--project-root", str(tmp_path), "--shared-root", str(tmp_path / "shared"), "--code-page", "850", "--delayed-expansion", "off"])
    monkeypatch.setattr(sys, "path", sys.path[:])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(Path(shell.__file__)), run_name="__main__")
    assert error.value.code == pytest.ExitCode.USAGE_ERROR
    assert "source unavailable" in capsys.readouterr().err
    assert not (tmp_path / "result.env").exists()
