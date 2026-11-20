r"""Run one archive attempt or one metadata lookup in a worker process its parent can end at the deadline.

Step 4 of v0.14.0 git-cliff-provisioning (design "Deadline enforcement" and
"Time budgets and retries"; design decision Q06; plan decisions Q10 and Q15).
A `urllib` timeout bounds one socket operation, not a transfer, and does not
cover name resolution, so each attempt runs in this worker: the parent starts
it through the bootstrap's internal `git-cliff-worker` entry kind with the
same runtime, as a contained and recorded child, and ends it job-wide at the
stage deadline. The parent owns the retry, its delay and the shared deadline,
and recomputes the archive digest from the staged file.

- `WorkerRequest`: `archive` mode (the URL, the staging file and the expected
  size) or `metadata` mode (the URL only; no file is written), plus the
  remaining seconds of the caller's budget. HTTPS only.
- `worker_arguments` and `parse_request` are inverse; anything the parent
  could not have built is refused.
- `worker_command(runtime, tooling_root, request)`: `-I -X utf8
  <tooling_root>\tools\release_workflow\bootstrap.py --entry-kind
  git-cliff-worker -- <arguments>`.
- `main` sets the socket timeout to `min(30, remaining)` and writes exactly
  one JSON line on its standard output, which the parent reads through its
  pipe: `{"outcome": "ok", "size", "sha256"}`, `{"outcome": "ok",
  "metadata"}`, or the failure class with its error. Nothing goes to standard
  error. The internal statuses 0, 75 and 65 stand for `ok`, `retryable` and
  `fatal`; the bootstrap passes them through unchanged and they never reach a
  caller of provisioning.

Since Step 5 (code review round 1), a local file failure, an `OSError` naming
a file that is not a URL error, such as a staging file the worker cannot
write, also reports that `path`, so the parent names the permission stage and
its directory instead of a network failure.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.error import URLError

from tools.release_workflow.git_cliff import network

if TYPE_CHECKING:
    import urllib.request
    from collections.abc import Sequence

ENTRY_KIND = "git-cliff-worker"
SOCKET_SECONDS = 30
STATUSES = {"ok": 0, "retryable": 75, "fatal": 65}
_MODES = ("archive", "metadata")
_OPTIONS = {"--mode": "mode", "--url": "url", "--target": "target", "--expected-size": "expected_size", "--remaining": "remaining"}
_REQUIRED = ("mode", "url", "remaining")


@dataclass(frozen=True, kw_only=True)
class WorkerRequest:
    """One attempt: its mode, its HTTPS URL, the staging file and expected size of an archive, the remaining seconds."""

    mode: str
    url: str
    target: Path | None = None
    expected_size: int | None = None
    remaining: float

    def __post_init__(self) -> None:
        """Refuse a request the parent would never build."""
        archive = self.mode == "archive"
        problem = next((text for text, failed in (
            (f"unknown mode {self.mode!r}", self.mode not in _MODES),
            ("the URL must use HTTPS", not self.url.startswith("https://")),
            ("--remaining must be a finite positive number of seconds", not (math.isfinite(self.remaining) and self.remaining > 0)),
            ("an archive attempt needs --target and --expected-size, a metadata lookup neither",
             archive != (self.target is not None) or archive != (self.expected_size is not None)),
            ("--expected-size must be positive", self.expected_size is not None and self.expected_size <= 0),
        ) if failed), None)
        if problem is not None:
            raise ValueError(problem)


def worker_arguments(request: WorkerRequest) -> list[str]:
    """Write the request as the worker's argument vector."""
    arguments = ["--mode", request.mode, "--url", request.url]
    if request.target is not None:
        arguments += ["--target", str(request.target)]
    if request.expected_size is not None:
        arguments += ["--expected-size", str(request.expected_size)]
    return [*arguments, "--remaining", repr(request.remaining)]


def _option_values(arguments: Sequence[str]) -> dict[str, str]:
    """Pair each known option with its one value, refusing an unknown, repeated, missing or valueless option."""
    if len(arguments) % 2:
        msg = "every option needs exactly one value"
        raise ValueError(msg)
    values: dict[str, str] = {}
    for option, value in zip(arguments[::2], arguments[1::2], strict=True):
        key = _OPTIONS.get(option)
        if key is None or key in values:
            msg = f"unknown or repeated option {option!r}"
            raise ValueError(msg)
        values[key] = value
    if any(key not in values for key in _REQUIRED):
        msg = "--mode, --url and --remaining are required"
        raise ValueError(msg)
    return values


def parse_request(arguments: Sequence[str]) -> WorkerRequest:
    """Read the argument vector `worker_arguments` writes, refusing every other form."""
    values = _option_values(arguments)
    size = values.get("expected_size")
    if size is not None and not (size.isascii() and size.isdigit()):
        msg = f"--expected-size {size!r} is not a whole number of bytes"
        raise ValueError(msg)
    target = values.get("target")
    return WorkerRequest(mode=values["mode"], url=values["url"], target=None if target is None else Path(target),
                         expected_size=None if size is None else int(size), remaining=float(values["remaining"]))


def worker_command(runtime: Path, tooling_root: Path, request: WorkerRequest) -> tuple[Path, list[str]]:
    """Give the executable and arguments that start the worker through the bootstrap with the same runtime."""
    bootstrap = tooling_root / "tools" / "release_workflow" / "bootstrap.py"
    return runtime, ["-I", "-X", "utf8", str(bootstrap), "--entry-kind", ENTRY_KIND, "--", *worker_arguments(request)]


def _attempt(request: WorkerRequest, opener: urllib.request.OpenerDirector) -> dict[str, object]:
    """Run the request with a socket timeout of at most 30 s, never beyond the remaining budget."""
    timeout = min(SOCKET_SECONDS, request.remaining)
    if request.target is not None and request.expected_size is not None:
        received = network.stream_archive(opener, request.url, request.target, expected_size=request.expected_size,
                                          socket_timeout=timeout)
        return {"outcome": "ok", "size": received.size, "sha256": received.sha256}
    body = network.fetch_metadata(opener, request.url, socket_timeout=timeout)
    return {"outcome": "ok", "metadata": body.decode("utf-8")}


def _emit(payload: dict[str, object]) -> int:
    """Write the one outcome line and return its internal status."""
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()
    return STATUSES[str(payload["outcome"])]


def main(arguments: Sequence[str], *, opener: urllib.request.OpenerDirector | None = None) -> int:
    """Run one attempt from its arguments and report its outcome line; the status is internal (0, 75 or 65)."""
    try:
        request = parse_request(arguments)
    except ValueError as error:
        return _emit({"outcome": "fatal", "error": f"invalid worker arguments: {error}"})
    payload: dict[str, object]
    try:
        payload = _attempt(request, network.build_opener() if opener is None else opener)
    except Exception as error:  # noqa: BLE001 - every failure of the attempt is reported with its class, never raised
        payload = {"outcome": network.classify(error), "error": f"{type(error).__name__}: {error}"}
        if isinstance(error, OSError) and not isinstance(error, URLError) and error.filename is not None:
            payload["path"] = str(error.filename)
    return _emit(payload)


# eof
