"""The network client verifies certificates, streams under an exact size cap and classifies every failure.

Step 4 of v0.14.0 git-cliff-provisioning (design "Network path", "Archive
verification" and "Time budgets and retries"; design decisions Q06 and Q08;
requirement clarification Q07). The opener comes from the standard proxies
and the default certificate context, untouched. An archive streams into its
target with its SHA-256 and stops at the first byte beyond the expected size;
a short body is returned for the parent's digest check, and a stalled read
raises the socket timeout. Metadata is read whole within its limit. A
connection error, a reset, a timeout, HTTP 429 or 5xx is retryable; another
HTTP 4xx, a certificate failure or a size overflow is fatal. Every case runs
through a real `urllib` opener over canned answers, with no socket.
"""

from __future__ import annotations

import hashlib
import http.client
import socket
import ssl
import urllib.error
import urllib.request
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import Canned, CannedWeb
from tools.release_workflow.git_cliff import network
from tools.release_workflow.git_cliff.network import (
    Received,
    SizeOverflowError,
    build_opener,
    classify,
    fetch_metadata,
    stream_archive,
)

if TYPE_CHECKING:
    from pathlib import Path

_ASSET = "https://github.com/orhun/git-cliff/releases/download/v2.14.2/git-cliff-2.14.2-x86_64-pc-windows-msvc.zip"
_STORED = "https://release-assets.githubusercontent.com/github-production-release-asset/2149-asset"
_RELEASE = "https://api.github.com/repos/orhun/git-cliff/releases/tags/v2.7.0"
_PROXIES = {"https": "http://proxy.example:8080", "no": "localhost"}
_BODY = bytes(range(256)) * 40
_LARGE = bytes(range(256)) * 300


def _context() -> ssl.SSLContext:
    """Build a verifying client context that loads no certificate."""
    return ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


def _handler[T: urllib.request.BaseHandler](opener: urllib.request.OpenerDirector, kind: type[T]) -> T:
    """Find the opener's handler of one kind."""
    handlers: list[urllib.request.BaseHandler] = vars(opener)["handlers"]
    return next(handler for handler in handlers if isinstance(handler, kind))


def _digest(content: bytes) -> str:
    """Hash bytes as the client does."""
    return hashlib.sha256(content).hexdigest()


def test_the_opener_uses_the_declared_proxies_and_context() -> None:
    """The declared proxies and context are used as they are, verification included."""
    context = _context()
    opener = build_opener(proxies=_PROXIES, context=context)
    assert vars(_handler(opener, urllib.request.ProxyHandler))["proxies"] == _PROXIES
    assert vars(_handler(opener, urllib.request.HTTPSHandler))["_context"] is context
    assert (context.verify_mode, context.check_hostname) == (ssl.CERT_REQUIRED, True)


def test_the_default_opener_reads_the_standard_proxies_and_certificates(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without declarations, `getproxies()` and `ssl.create_default_context()` supply the opener."""
    context = _context()
    monkeypatch.setattr(network.urllib.request, "getproxies", lambda: dict(_PROXIES))
    monkeypatch.setattr(network.ssl, "create_default_context", lambda: context)
    opener = build_opener()
    assert vars(_handler(opener, urllib.request.ProxyHandler))["proxies"] == _PROXIES
    assert vars(_handler(opener, urllib.request.HTTPSHandler))["_context"] is context


def test_an_archive_streams_into_its_target_with_size_and_digest(tmp_path: Path) -> None:
    """The bytes land in the target and the received size and SHA-256 describe them."""
    web, target = CannedWeb({_ASSET: Canned(body=_BODY)}), tmp_path / "archive.zip"
    received = stream_archive(web.opener(), _ASSET, target, expected_size=len(_BODY), socket_timeout=30)
    assert (received, target.read_bytes(), web.opened) == (Received(len(_BODY), _digest(_BODY)), _BODY, [(_ASSET, 30)])


def test_the_redirect_to_the_release_asset_host_is_followed(tmp_path: Path) -> None:
    """GitHub answers 302 to `release-assets.githubusercontent.com`, which serves the bytes."""
    web = CannedWeb({_ASSET: Canned(status=302, location=_STORED), _STORED: Canned(body=_BODY)})
    received = stream_archive(web.opener(), _ASSET, tmp_path / "archive.zip", expected_size=len(_BODY), socket_timeout=30)
    assert (received.size, web.opened) == (len(_BODY), [(_ASSET, 30), (_STORED, 30)])


def test_a_longer_body_stops_at_the_first_extra_byte(tmp_path: Path) -> None:
    """Exactly one byte past the expected size is read, and nothing past the size is written."""
    expected = len(_LARGE)
    web, target = CannedWeb({_ASSET: Canned(body=_LARGE + b"!" * 50)}), tmp_path / "archive.zip"
    with pytest.raises(SizeOverflowError, match=f"more than the expected {expected} bytes"):
        stream_archive(web.opener(), _ASSET, target, expected_size=expected, socket_timeout=30)
    assert sum(web.reads) == expected + 1
    assert _LARGE.startswith(target.read_bytes())


def test_a_short_body_is_returned_for_the_digest_check(tmp_path: Path) -> None:
    """A body shorter than expected is not an error here: the parent compares size and digest."""
    web = CannedWeb({_ASSET: Canned(body=_BODY)})
    received = stream_archive(web.opener(), _ASSET, tmp_path / "archive.zip", expected_size=len(_BODY) + 5, socket_timeout=30)
    assert received == Received(len(_BODY), _digest(_BODY))


def test_a_stalled_read_raises_the_socket_timeout(tmp_path: Path) -> None:
    """A read that never gets data ends with the socket timeout, which is retryable."""
    web = CannedWeb({_ASSET: Canned(stall=True)})
    with pytest.raises(TimeoutError) as caught:
        stream_archive(web.opener(), _ASSET, tmp_path / "archive.zip", expected_size=len(_BODY), socket_timeout=30)
    assert classify(caught.value) == "retryable"


@pytest.mark.parametrize("status", [403, 404, 410, 429, 500, 503])
def test_an_http_error_creates_no_target(tmp_path: Path, status: int) -> None:
    """An error status raises before the target file is created."""
    web, target = CannedWeb({_ASSET: Canned(status=status)}), tmp_path / "archive.zip"
    with pytest.raises(urllib.error.HTTPError) as caught:
        stream_archive(web.opener(), _ASSET, target, expected_size=len(_BODY), socket_timeout=30)
    assert (caught.value.code, target.exists()) == (status, False)


def test_metadata_is_read_whole_within_its_limit() -> None:
    """The release metadata body comes back as bytes, with the socket timeout given."""
    body = b'{"tag_name": "v2.7.0", "assets": []}'
    web = CannedWeb({_RELEASE: Canned(body=body)})
    assert (fetch_metadata(web.opener(), _RELEASE, socket_timeout=12.5), web.opened) == (body, [(_RELEASE, 12.5)])


def test_metadata_beyond_its_limit_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """A metadata body larger than the limit is a size overflow, never kept in memory whole."""
    monkeypatch.setattr(network, "METADATA_LIMIT", 16)
    web = CannedWeb({_RELEASE: Canned(body=b"x" * 17)})
    with pytest.raises(SizeOverflowError, match="more than 16 bytes of release metadata"):
        fetch_metadata(web.opener(), _RELEASE, socket_timeout=30)


@pytest.mark.parametrize(("code", "kind"), [
    (429, "retryable"), (500, "retryable"), (502, "retryable"), (503, "retryable"), (599, "retryable"),
    (400, "fatal"), (403, "fatal"), (404, "fatal"), (410, "fatal"),
])
def test_http_statuses_are_classified(code: int, kind: str) -> None:
    """Throttling and server errors are retried once; every other HTTP error is final."""
    error = urllib.error.HTTPError(_ASSET, code, "canned", http.client.HTTPMessage(), None)
    assert classify(error) == kind


@pytest.mark.parametrize(("error", "kind"), [
    (urllib.error.URLError(ConnectionRefusedError(10061, "refused")), "retryable"),
    (urllib.error.URLError(socket.gaierror(11001, "getaddrinfo failed")), "retryable"),
    (ConnectionResetError(10054, "reset by peer"), "retryable"),
    (http.client.RemoteDisconnected("closed without response"), "retryable"),
    (http.client.IncompleteRead(b"partial", 10), "retryable"),
    (TimeoutError("timed out"), "retryable"),
    (ssl.SSLEOFError(8, "EOF occurred in violation of protocol"), "retryable"),
    (urllib.error.URLError(ssl.SSLCertVerificationError(1, "certificate verify failed")), "fatal"),
    (SizeOverflowError("too long"), "fatal"),
    (PermissionError(13, "write denied"), "fatal"),
    (ValueError("unexpected"), "fatal"),
])
def test_other_failures_are_classified(error: Exception, kind: str) -> None:
    """Connection errors, resets and timeouts are retried; certificate, size and local failures are final."""
    assert classify(error) == kind


# eof
