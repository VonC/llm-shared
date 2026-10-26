"""Atomic side-file publication that rides out a transient Windows lock.

On-access virus scanning holds a freshly written file open for a few
milliseconds; an ``os.replace`` onto it in that window fails with
``PermissionError`` (WinError 5). groundhog then lost a lifecycle ``done``
line, so the next run read its own finished run as live and refused to start
(exit 6). Every groundhog side-file publication now goes through
:func:`replace`, which retries that one error a few times with a short
doubling backoff before letting it through.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# Attempts of one publication; the waits between them total about 0.3s.
ATTEMPTS: Final = 6
# The first wait, doubled after each refused attempt.
FIRST_DELAY_SECONDS: Final = 0.01


def replace(side: Path, path: Path, sleep: Callable[[float], None] = time.sleep) -> None:
    """Move a complete side file over its target, retrying a transient lock.

    Args:
        side: The fully written side file.
        path: The published target it replaces.
        sleep: The pause between two attempts, injectable for tests.

    Raises:
        PermissionError: When the target stays locked through every attempt.
    """
    for attempt in range(ATTEMPTS):
        try:
            side.replace(path)
        except PermissionError:
            if attempt + 1 == ATTEMPTS:
                raise
            sleep(FIRST_DELAY_SECONDS * 2**attempt)
        else:
            return


# eof
