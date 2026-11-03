"""Retain per-test dependency evidence with Python's low-overhead monitoring.

Testmon switches coverage contexts explicitly before each test protocol.
Coverage's monitoring collector disables each visited line until restarted;
re-arm it after that context switch so shared code belongs to every consumer.
No source filtering, dependency selection or duration boundary changes here.
"""

from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING

import pytest
from coverage import collector

if TYPE_CHECKING:
    from collections.abc import Generator


def collector_origin() -> str:
    """Format collector diagnostics from frames without loading source files."""
    frames = [f"{frame.f_code.co_name} : {frame.f_code.co_filename}:{line}"
              for frame, line in traceback.walk_stack(None)]
    return "\n".join(reversed(frames))


def pytest_configure(config: pytest.Config) -> None:
    """Keep coverage's origin diagnostic without inspect.stack's filesystem IO."""
    patch = pytest.MonkeyPatch()
    patch.setattr(collector, "short_stack", collector_origin)
    config.add_cleanup(patch.undo)


@pytest.hookimpl(wrapper=True, trylast=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None) -> Generator[None, object, object]:
    """Run inside testmon's context switch and before fixture setup."""
    del nextitem
    if getattr(getattr(item.config, "testmon_config", None), "collect", False):
        sys.monitoring.restart_events()
    return (yield)


# eof
