"""Atomic migration journal snapshots with bounded transient-sharing retries."""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Final

_REPLACE_ATTEMPTS: Final = 5
_REPLACE_DELAY_SECONDS: Final = 0.01


def _commit_snapshot(prepared: Path, target: Path) -> None:
    """Retry permission failures without exposing a partial journal snapshot."""
    for attempt in range(_REPLACE_ATTEMPTS):
        try:
            prepared.replace(target)
        except PermissionError:
            if attempt + 1 == _REPLACE_ATTEMPTS:
                raise
            time.sleep(_REPLACE_DELAY_SECONDS * (2**attempt))
        else:
            return


def write_journal(path: Path, payload: dict[str, object]) -> None:
    """Synchronize one complete snapshot and atomically publish it or clean up."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=".review-artifact-migration-", suffix=".tmp", dir=path.parent,
    )
    prepared = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        _commit_snapshot(prepared, path)
    except OSError:
        prepared.unlink(missing_ok=True)
        raise


# eof
