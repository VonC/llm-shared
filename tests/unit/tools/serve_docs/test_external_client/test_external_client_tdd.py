"""Verify generic command watching, opening, and failure isolation."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING
from unittest.mock import patch

from tools.serve_docs import external_client, serve_docs

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _write_config(folder: Path) -> None:
    folder.mkdir()
    (folder / "README.md").write_text("# Example\n", encoding="utf-8")
    (folder / "serve_docs.ini").write_text(
        "[serve_docs]\nmode = external\nexternal_command =\n"
        "    sample-tool\n    refresh\nexternal_watch =\n    .\n"
        "external_open =\n    https://manual.example.test/guide/\n"
        "external_debounce_seconds = 2\n",
        encoding="utf-8",
    )


def test_configured_command_invocation_opens_opaque_returned_url(tmp_path: Path) -> None:
    """The external client passes only configured argv and opens returned URLs."""
    folder = tmp_path / "notes"
    _write_config(folder)
    config = external_client.read_config(folder)
    assert config is not None
    opened: list[str] = []
    calls: list[list[str]] = []
    options: list[dict[str, object]] = []

    def invoke(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        options.append(kwargs)
        return subprocess.CompletedProcess(argv, 0, '{"open_urls":["https://manual.example.test/current/"]}', "")

    client = external_client.ExternalClient(config, invoke=invoke, opener=opened.append)
    client.refresh(open_pages=True)
    assert calls == [["sample-tool", "refresh"]]
    assert options[0]["stdout"] == subprocess.PIPE
    assert options[0]["stderr"] == subprocess.DEVNULL
    assert opened == ["https://manual.example.test/current/"]


def test_configured_browser_url_preserves_percent_encoded_path(tmp_path: Path) -> None:
    """Configured browser targets are read literally, including URL escapes."""
    folder = tmp_path / "notes"
    _write_config(folder)
    path = folder / "serve_docs.ini"
    path.write_text(
        path.read_text(encoding="utf-8").replace("/guide/", "/guide/first%20steps/"),
        encoding="utf-8",
    )
    config = external_client.read_config(folder)
    assert config is not None
    assert config.open_urls == ("https://manual.example.test/guide/first%20steps/",)


def test_watch_coalesces_changes_using_injected_clock(tmp_path: Path) -> None:
    """Several edits inside one deadline result in one command call."""
    folder = tmp_path / "notes"
    _write_config(folder)
    config = external_client.read_config(folder)
    assert config is not None
    calls: list[list[str]] = []

    def invoke(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")

    client = external_client.ExternalClient(config, invoke=invoke, opener=lambda _url: None)
    client.poll(now=0.0)
    page = folder / "README.md"
    page.write_text("# First\n", encoding="utf-8")
    client.poll(now=1.0)
    page.write_text("# Second revision\n", encoding="utf-8")
    client.poll(now=2.0)
    client.poll(now=3.9)
    assert calls == []
    client.poll(now=4.0)
    assert calls == [["sample-tool", "refresh"]]


def test_failure_opens_reachable_retained_target_and_reports_neutral_guidance(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """A failed command does not suppress a configured readable target."""
    folder = tmp_path / "notes"
    _write_config(folder)
    config = external_client.read_config(folder)
    assert config is not None
    opened: list[str] = []

    def invoke(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 1, "", "private failure detail")

    client = external_client.ExternalClient(config, invoke=invoke, opener=opened.append)
    client.refresh(open_pages=True)
    assert opened == ["https://manual.example.test/guide/"]
    assert "private failure detail" not in caplog.text
    assert "configured service" in caplog.text


def test_external_dispatch_never_starts_local_renderer_or_server(tmp_path: Path) -> None:
    """A configured external mode exits before local serving is prepared."""
    folder = tmp_path / "notes"
    _write_config(folder)
    with patch.object(external_client, "run", return_value=0) as external_run, patch.object(
        serve_docs, "write_config", side_effect=AssertionError("local render"),
    ), patch.object(serve_docs, "find_runner", side_effect=AssertionError("local tool")), patch.object(
        serve_docs.subprocess, "call", side_effect=AssertionError("local server"),
    ):
        assert serve_docs.main([str(folder)]) == 0
    external_run.assert_called_once()


# eof
