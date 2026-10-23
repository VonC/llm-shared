"""Observe a real CLI wait reaching its notification boundary without output.

The parent must not mutate an exchange while a child's initial status scan is
still running. A fixture-owned marker outside the repository signals that the
startup gate and initial discovery completed. The real notification wait, Git,
claim logic and terminal streams remain unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from tools.review_exchange_cli import main as exchange_main
from tools.review_resume_notifications import WatchdogNotificationAdapter


def main() -> int:
    """Signal the first idle boundary, then run the unmodified wait method."""
    ready = Path(sys.argv[1])
    original_wait = WatchdogNotificationAdapter.wait
    signalled = False

    def observed_wait(adapter: WatchdogNotificationAdapter, seconds: float) -> bool:
        nonlocal signalled
        if not signalled:
            ready.touch()
            signalled = True
        return original_wait(adapter, seconds)

    with patch.object(WatchdogNotificationAdapter, "wait", observed_wait):
        return exchange_main(sys.argv[2:])


if __name__ == "__main__":
    raise SystemExit(main())

# eof
