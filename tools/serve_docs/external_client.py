"""Run a configured external documentation command without local serving.

The client watches configured paths, coalesces edits, and treats returned web
addresses as opaque browser targets. It does not interpret command output as
service diagnostics.
"""

from __future__ import annotations

import configparser
import json
import logging
import os
import subprocess
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from collections.abc import Callable


LOGGER = logging.getLogger("serve_docs.external")
COMMAND_TIMEOUT_SECONDS = 15
POLL_SECONDS = 0.5


@dataclass(frozen=True)
class ExternalConfig:
    """Hold generic command, watch, and browser settings for external mode."""

    command: tuple[str, ...]
    watch_paths: tuple[Path, ...]
    open_urls: tuple[str, ...]
    debounce_seconds: float


def _lines(value: str) -> list[str]:
    """Read one argument or path per configuration line."""
    return [line.strip() for line in value.splitlines() if line.strip()]


def _safe_web_url(value: str) -> bool:
    """Accept only absolute browser URLs without embedded credentials."""
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and parsed.username is None and parsed.password is None
    except ValueError:
        return False


def _read_watch(parser: configparser.ConfigParser, docs_dir: Path) -> tuple[Path, ...]:
    """Resolve configured watch roots once, retaining their first occurrence."""
    watch: list[Path] = []
    known: set[Path] = set()
    for item in _lines(parser.get("serve_docs", "external_watch", fallback=".")):
        values = _lines(parser.get("serve_docs", item[1:], fallback="")) if item in {"@include", "@assets"} else [item]
        for value in values:
            path = (docs_dir / value).resolve()
            if path not in known:
                known.add(path)
                watch.append(path)
    return tuple(watch)


def read_config(docs_dir: Path) -> ExternalConfig | None:
    """Read external mode from a folder's optional serve_docs.ini."""
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(docs_dir / "serve_docs.ini", encoding="utf-8")
    if not parser.has_section("serve_docs") or parser.get("serve_docs", "mode", fallback="local").strip() != "external":
        return None
    command = _lines(parser.get("serve_docs", "external_command", fallback=""))
    if not command:
        message = "external_command requires an executable"
        raise ValueError(message)
    if command[0].startswith((".", "/")):
        command[0] = str((docs_dir / command[0]).resolve())
    urls = _lines(parser.get("serve_docs", "external_open", fallback=""))
    if any(not _safe_web_url(url) for url in urls):
        message = "external_open requires absolute HTTP(S) URLs without credentials"
        raise ValueError(message)
    debounce = parser.getfloat("serve_docs", "external_debounce_seconds", fallback=1.0)
    if debounce < 0:
        message = "external_debounce_seconds must be nonnegative"
        raise ValueError(message)
    return ExternalConfig(tuple(command), _read_watch(parser, docs_dir), tuple(urls), debounce)


def _file_stamp(path: Path) -> tuple[int, int] | None:
    """Read a watched file's modification stamp when it remains available."""
    try:
        stat = path.stat()
    except OSError:
        return None
    return stat.st_mtime_ns, stat.st_size


def _scan_directory(root: Path, seen: dict[Path, tuple[int, int]]) -> None:
    """Add visible files below one watched directory in a linear walk."""
    for folder, children, files in os.walk(root):
        children[:] = [name for name in children if name not in {".git", ".venv", "venvs", "__pycache__"}]
        for name in files:
            path = Path(folder) / name
            stamp = _file_stamp(path)
            if stamp is not None:
                seen[path] = stamp


def _snapshot(paths: tuple[Path, ...]) -> dict[Path, tuple[int, int]]:
    """Observe watched file identity in one linear filesystem pass."""
    seen: dict[Path, tuple[int, int]] = {}
    directories = {path for path in paths if path.is_dir()}
    for root in paths:
        if any(parent in directories for parent in root.parents):
            continue
        if root.is_file():
            stamp = _file_stamp(root)
            if stamp is not None:
                seen[root] = stamp
        elif root in directories:
            _scan_directory(root, seen)
    return seen


def _returned_urls(stdout: str) -> tuple[str, ...]:
    """Extract only safe opaque browser URLs from one JSON response."""
    try:
        payload: object = json.loads(stdout)
    except (ValueError, TypeError):
        return ()
    if not isinstance(payload, dict):
        return ()
    values = cast("dict[str, object]", payload).get("open_urls")
    if not isinstance(values, list):
        return ()
    return tuple(value for value in cast("list[object]", values) if isinstance(value, str) and _safe_web_url(value))


class ExternalClient:
    """Coalesce edits and invoke configured argv without retaining diagnostics."""

    def __init__(
        self,
        config: ExternalConfig,
        *,
        invoke: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
        opener: Callable[[str], object] = webbrowser.open,
    ) -> None:
        """Capture trusted dependencies and the initial watch snapshot."""
        self.config = config
        self._invoke = invoke
        self._opener = opener
        self._last = _snapshot(config.watch_paths)
        self._deadline: float | None = None

    def refresh(self, *, open_pages: bool = False) -> None:
        """Request refresh and optionally open returned or configured pages."""
        urls = self.config.open_urls
        try:
            result = self._invoke(
                list(self.config.command),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            LOGGER.warning("The configured service could not be reached. Check or start it, then retry.")
        else:
            returned = _returned_urls(result.stdout)
            if returned:
                urls = returned
            if result.returncode != 0:
                LOGGER.warning("The configured service could not be reached. Check or start it, then retry.")
        if open_pages:
            for url in urls:
                self._opener(url)

    def poll(self, *, now: float) -> None:
        """Schedule one refresh after the latest observed edit settles."""
        current = _snapshot(self.config.watch_paths)
        if current != self._last:
            self._last = current
            self._deadline = now + self.config.debounce_seconds
        if self._deadline is not None and now >= self._deadline:
            self._deadline = None
            self.refresh()


def run(config: ExternalConfig, *, no_browser: bool = False) -> int:
    """Refresh once, then watch until interrupted without starting a server."""
    client = ExternalClient(config)
    client.refresh(open_pages=not no_browser)
    try:
        while True:
            client.poll(now=time.monotonic())
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        return 0


# eof
