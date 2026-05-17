#!/usr/bin/env python3
"""Cert-aware ``uv`` launcher for personal and corporate environments.

``uv`` honours the ``SSL_CERT_FILE`` environment variable. Behind a
corporate TLS-intercepting proxy that variable must point at the
corporate CA bundle, or every PyPI request fails with
``invalid peer certificate: UnknownIssuer``. On a personal network the
variable must be absent, or that same corporate bundle rejects the
genuine PyPI certificate.

This wrapper picks a TLS strategy from the current environment, runs
``uv``, and -- when a run fails with a certificate error -- retries with
the remaining strategies. The same alias therefore works unchanged on a
personal machine and on a corporate one.

Usage::

    python uv_run.py <uv arguments...>
    python uv_run.py lock --upgrade
    python uv_run.py sync

The real ``uv`` executable is taken from the ``UV_BIN`` environment
variable when set, otherwise from ``PATH``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# Substrings (lower-cased) that identify a TLS failure in uv's output.
_CERT_ERROR_MARKERS: tuple[str, ...] = (
    "invalid peer certificate",
    "unknownissuer",
    "certificate verify failed",
    "self-signed certificate",
    "ssl error",
)


@dataclass(frozen=True)
class TlsStrategy:
    """One way of presenting trust roots to ``uv``.

    Attributes:
        label: Human-readable name shown in the progress note.
        cert_file: Value forced into ``SSL_CERT_FILE`` for the child
            process, or ``None`` to remove that variable entirely.
        extra_args: Extra ``uv`` arguments appended to the command line.
    """

    label: str
    cert_file: Path | None
    extra_args: tuple[str, ...]


def _resolve_uv() -> str:
    """Locate the real ``uv`` executable.

    Returns:
        Path to ``uv``, from ``UV_BIN`` when set, otherwise from
        ``PATH``.

    Raises:
        SystemExit: When no ``uv`` executable can be found.
    """
    override = os.environ.get("UV_BIN")
    if override:
        return override
    found = shutil.which("uv")
    if found is None:
        sys.stderr.write(
            "uv_run: no 'uv' on PATH; install it with "
            "'python -m pip install uv' or set UV_BIN.\n",
        )
        raise SystemExit(127)
    return found


def _corporate_bundle() -> Path | None:
    """Return the corporate CA bundle currently in effect, if usable.

    Returns:
        The ``SSL_CERT_FILE`` path when it is set and points at an
        existing file (the corporate-machine case); ``None`` otherwise
        (the personal-machine case, or a stale override).
    """
    raw = os.environ.get("SSL_CERT_FILE")
    if not raw:
        return None
    bundle = Path(raw)
    return bundle if bundle.is_file() else None


def _strategies() -> list[TlsStrategy]:
    """Build the ordered list of TLS strategies to attempt.

    The first entry is the one detected from the environment; the
    remainder are fallbacks tried only after a certificate error.

    Returns:
        Strategies in the order they should be attempted.
    """
    system = TlsStrategy("system trust store", None, ("--system-certs",))
    default = TlsStrategy("default trust roots", None, ())
    bundle = _corporate_bundle()
    if bundle is not None:
        # Corporate machine: the explicit bundle is the primary path.
        explicit = TlsStrategy(f"corporate bundle ({bundle.name})", bundle, ())
        return [explicit, system, default]
    # Personal machine: the public roots bundled with uv work directly.
    return [default, system]


def _run(uv: str, strategy: TlsStrategy, args: Sequence[str]) -> tuple[int, bool]:
    """Run ``uv`` once under a given TLS strategy.

    Args:
        uv: Path to the ``uv`` executable.
        strategy: TLS strategy applied for this attempt.
        args: ``uv`` arguments supplied by the caller.

    Returns:
        The process exit code and whether the output showed a
        certificate error.
    """
    env = dict(os.environ)
    if strategy.cert_file is None:
        env.pop("SSL_CERT_FILE", None)
        env.pop("SSL_CERT_DIR", None)
    else:
        env["SSL_CERT_FILE"] = str(strategy.cert_file)
    command = [uv, *args, *strategy.extra_args]
    sys.stdout.write(f"uv_run: TLS strategy = {strategy.label}\n")
    sys.stdout.flush()
    captured: list[str] = []
    with subprocess.Popen(  # noqa: S603
        command,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    ) as process:
        for line in process.stdout or []:
            sys.stdout.write(line)
            sys.stdout.flush()
            captured.append(line)
    output = "".join(captured).lower()
    is_cert_error = any(marker in output for marker in _CERT_ERROR_MARKERS)
    return process.returncode, is_cert_error


def main(argv: Sequence[str]) -> int:
    """Run ``uv`` with automatic TLS-strategy fallback.

    Args:
        argv: ``uv`` arguments (everything after the script name). When
            empty, ``uv`` is run bare, which prints its own help.

    Returns:
        The exit code of the last ``uv`` attempt.
    """
    uv = _resolve_uv()
    strategies = _strategies()
    last_code = 0
    for index, strategy in enumerate(strategies):
        last_code, is_cert_error = _run(uv, strategy, argv)
        if last_code == 0 or not is_cert_error:
            return last_code
        if index + 1 < len(strategies):
            sys.stderr.write(
                f"uv_run: certificate error with {strategy.label}; "
                "retrying with the next strategy.\n",
            )
    sys.stderr.write("uv_run: every TLS strategy failed with a certificate error.\n")
    return last_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
