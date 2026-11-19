"""Reach the GitHub release hosts through the standard proxies and the system certificates, under an exact size cap.

Step 4 of v0.14.0 git-cliff-provisioning (design "Network path", "Archive
verification" and "Time budgets and retries"; design decisions Q06 and Q08;
requirement clarification Q07). Only the download worker calls this module,
inside its own process, so that its parent can end a call that never returns.

- `build_opener` uses `urllib.request.getproxies()` (`HTTPS_PROXY`,
  `HTTP_PROXY` and `NO_PROXY`, else the static Windows proxy setting) and
  `ssl.create_default_context()` (the Windows certificate store), unchanged:
  certificate and host name verification are never turned off. Redirects,
  such as GitHub's 302 to `release-assets.githubusercontent.com`, are
  followed by the standard handler.
- `stream_archive` writes the body into its target while hashing it. It never
  reads more than one byte past the expected size, and that byte raises
  `SizeOverflowError` before anything beyond the size is written. A shorter
  body is returned as received: the parent compares size and digest.
- `fetch_metadata` reads a release metadata body whole, within
  `METADATA_LIMIT`.
- `classify` sorts a failure: a connection error, a reset, a timeout, a TLS
  failure other than certificate verification, HTTP 429 or 5xx is
  `retryable`; another HTTP status, a certificate failure, a size overflow or
  a local error is `fatal`.

A socket timeout bounds each blocking operation, never the whole transfer;
the caller's deadline does that. No response header is read, so a server's
retry delay extends no budget.
"""

from __future__ import annotations

import hashlib
import http.client
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

METADATA_LIMIT = 1 << 22
_CHUNK = 1 << 16
_TOO_MANY_REQUESTS = 429
_SERVER_ERRORS = range(500, 600)


class SizeOverflowError(ValueError):
    """The body is longer than its expected size; a repeated download would not change it."""


@dataclass(frozen=True)
class Received:
    """What one archive attempt received: its size in bytes and its SHA-256."""

    size: int
    sha256: str


def build_opener(*, proxies: Mapping[str, str] | None = None, context: ssl.SSLContext | None = None) -> urllib.request.OpenerDirector:
    """Build the opener from the standard proxies and the verifying default context, or from declared ones."""
    chosen = urllib.request.getproxies() if proxies is None else dict(proxies)
    secure = ssl.create_default_context() if context is None else context
    return urllib.request.build_opener(urllib.request.ProxyHandler(chosen), urllib.request.HTTPSHandler(context=secure))


def stream_archive(opener: urllib.request.OpenerDirector, url: str, target: Path, *, expected_size: int,
                   socket_timeout: float) -> Received:
    """Stream an archive into its target, stopping at the first byte beyond the expected size.

    Args:
        opener: The opener of `build_opener`, or a test double.
        url: The asset URL; redirects are followed.
        target: The staging file, created only once the response arrived.
        expected_size: The manifest size; one more byte is an overflow.
        socket_timeout: The bound of each blocking socket operation.

    Returns:
        The received size and SHA-256, for the parent's comparison.

    Raises:
        SizeOverflowError: The body holds more bytes than expected.
    """
    digest, size = hashlib.sha256(), 0
    with opener.open(url, timeout=socket_timeout) as response, target.open("wb") as stream:
        while chunk := response.read(min(_CHUNK, expected_size - size + 1)):
            if size + len(chunk) > expected_size:
                msg = f"{url}: more than the expected {expected_size} bytes"
                raise SizeOverflowError(msg)
            stream.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    return Received(size, digest.hexdigest())


def fetch_metadata(opener: urllib.request.OpenerDirector, url: str, *, socket_timeout: float) -> bytes:
    """Read a release metadata body whole, refusing one larger than `METADATA_LIMIT`."""
    with opener.open(url, timeout=socket_timeout) as response:
        body: bytes = response.read(METADATA_LIMIT + 1)
    if len(body) > METADATA_LIMIT:
        msg = f"{url}: more than {METADATA_LIMIT} bytes of release metadata"
        raise SizeOverflowError(msg)
    return body


def classify(error: BaseException) -> Literal["retryable", "fatal"]:
    """Tell whether one more attempt could succeed: connection-level and server-side failures only."""
    if isinstance(error, urllib.error.HTTPError):
        return "retryable" if error.code == _TOO_MANY_REQUESTS or error.code in _SERVER_ERRORS else "fatal"
    cause = error.reason if isinstance(error, urllib.error.URLError) else error
    if isinstance(cause, ssl.SSLCertVerificationError):
        return "fatal"
    if isinstance(error, urllib.error.URLError) or isinstance(cause, ConnectionError | TimeoutError | ssl.SSLError | http.client.HTTPException):
        return "retryable"
    return "fatal"


# eof
