"""Input reading keeps UTF-8 file/stdin ownership explicit and bounded."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import inputs

if TYPE_CHECKING:
    from pathlib import Path


def test_utf8_file(tmp_path: Path) -> None:
    """File payloads preserve Unicode, metacharacters and original newlines."""
    path = tmp_path / "input.txt"
    payload = 'éléphant %PATH% ^!& "quoted"\r\n'
    path.write_bytes(payload.encode("utf-8"))
    assert inputs.read_payload(path, use_stdin=False, text=None, source="INPUT", required=True, non_interactive=True) == payload


def test_invalid_utf8(tmp_path: Path) -> None:
    """Decode failures identify the selector and supplied path."""
    path = tmp_path / "invalid.txt"
    path.write_bytes(b"\xff")
    with pytest.raises(ValueError, match=r"SELECTED.*invalid.txt"):
        inputs.read_payload(path, use_stdin=False, text=None, source=f"SELECTED={path}", required=True, non_interactive=True)


def test_console_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Console classification uses the Win32 API independently of isatty."""
    class Kernel:
        """Fake API exposes a non-console stdin handle, as NUL can be."""

        @staticmethod
        def GetStdHandle(_kind: int) -> int:  # noqa: N802
            return 123

        @staticmethod
        def GetConsoleMode(_handle: int, _mode: object) -> int:  # noqa: N802
            return 0

    monkeypatch.setattr(inputs, "_kernel", Kernel)
    assert not inputs.stdin_is_console()


@pytest.mark.parametrize("required", [False, True])
def test_native_text(*, required: bool) -> None:
    """Explicit empty text is supplied input, never a request to prompt."""
    assert inputs.read_payload(None, use_stdin=False, text="", source="native", required=required, non_interactive=True) == ""


def test_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stdin is decoded from bytes even when the ambient text encoding differs."""
    monkeypatch.setattr(inputs.sys, "stdin", io.TextIOWrapper(io.BytesIO("é\r\n".encode()), encoding="ascii"))
    assert inputs.read_payload(None, use_stdin=True, text=None, source="stdin", required=True, non_interactive=True) == "é\r\n"


def test_text_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """An injected text stream is already decoded and retains its original text."""
    monkeypatch.setattr(inputs.sys, "stdin", io.StringIO("fixture"))
    assert inputs.read_payload(None, use_stdin=True, text=None, source="stdin", required=True, non_interactive=True) == "fixture"


def test_invalid_utf8_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """A stdin decoding error identifies the channel, not an absent file."""
    monkeypatch.setattr(inputs.sys, "stdin", io.TextIOWrapper(io.BytesIO(b"\xff"), encoding="ascii"))
    with pytest.raises(ValueError, match=r"Cannot read stdin:.*utf-8"):
        inputs.read_payload(None, use_stdin=True, text=None, source="input file=None", required=True, non_interactive=True)


def test_optional_missing() -> None:
    """An optional absent payload stays absent without any stdin read."""
    assert inputs.read_payload(None, use_stdin=False, text=None, source="none", required=False, non_interactive=True) is None


def test_interactive_prompt(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Only a confirmed console policy permits Python prompting on stderr."""
    monkeypatch.setattr("builtins.input", lambda: "confirmed")
    assert inputs.read_payload(None, use_stdin=False, text=None, source="console", required=True, non_interactive=False) == "confirmed"
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Release input: "


def test_actual_redirected_handle() -> None:
    """The current test worker has no console; call actual pointer-safe signatures."""
    assert not inputs.stdin_is_console()


def test_missing_noninteractive_input(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """An absent required channel never consumes redirected data or prompts."""
    stream = io.StringIO("not consent")
    monkeypatch.setattr(inputs.sys, "stdin", stream)
    with pytest.raises(ValueError, match="Missing required input"):
        inputs.read_payload(None, use_stdin=False, text=None, source="none", required=True, non_interactive=True)
    assert stream.tell() == 0
    assert capsys.readouterr().err == ""

# eof
