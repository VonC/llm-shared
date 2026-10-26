"""Observe a real CLI wait reaching its notification boundary without output.

The parent must not mutate an exchange while a child's initial status scan is
still running. A fixture-owned marker outside the repository signals that the
startup gate and initial discovery completed. The real notification wait, Git,
claim logic and terminal streams remain unchanged.

Fix: the marker is published by renaming a complete pending file, so the
parent never sees a marker whose handle is still open, and it carries this
interpreter's own pid. The parent started this driver through the virtual
environment's launcher stub, so that pid is the only way to stop exactly this
process. A daemon thread also ends the driver as soon as the test process that
started it (``REVIEW_RESUME_WAITER_PARENT_PID``) or its direct parent is gone,
so an interrupted test can no longer leave a waiter polling.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Final
from unittest.mock import patch

from tests.acceptance.review_resume.waiter_processes import TrackedProcess
from tools.review_exchange_cli import main as exchange_main
from tools.review_resume_notifications import WatchdogNotificationAdapter

# The test process that started this driver, set by its parent fixture.
PARENT_VARIABLE: Final = "REVIEW_RESUME_WAITER_PARENT_PID"
# Seconds between two checks of the parents.
_WATCH_SECONDS: Final = 0.1
# The exit code of a driver whose parent is gone.
_ORPHANED_EXIT: Final = 3


def _exit_when_orphaned() -> None:
    """End this process once its direct parent or its test process is gone."""
    parents = [TrackedProcess(os.getppid())]
    started_by = os.environ.get(PARENT_VARIABLE)
    if started_by:
        parents.append(TrackedProcess(int(started_by)))

    def watch() -> None:
        while all(parent.alive() for parent in parents):
            time.sleep(_WATCH_SECONDS)
        os._exit(_ORPHANED_EXIT)

    threading.Thread(target=watch, name="waiter-orphan-watch", daemon=True).start()


def main() -> int:
    """Signal the first idle boundary, then run the unmodified wait method."""
    _exit_when_orphaned()
    ready = Path(sys.argv[1])
    original_wait = WatchdogNotificationAdapter.wait
    signalled = False

    def observed_wait(adapter: WatchdogNotificationAdapter, seconds: float) -> bool:
        nonlocal signalled
        if not signalled:
            # Existence is the parent's signal, so publish only a complete,
            # closed marker; it names this interpreter for the parent's cleanup.
            pending = ready.with_suffix(".pending")
            pending.write_text(str(os.getpid()), encoding="utf-8")
            pending.replace(ready)
            signalled = True
        return original_wait(adapter, seconds)

    with patch.object(WatchdogNotificationAdapter, "wait", observed_wait):
        return exchange_main(sys.argv[2:])


if __name__ == "__main__":
    raise SystemExit(main())

# eof
