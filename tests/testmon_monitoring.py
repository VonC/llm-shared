"""Retain per-test dependency evidence with Python's low-overhead monitoring.

Testmon switches coverage contexts explicitly before each test protocol.
Coverage's monitoring collector disables each visited line until restarted;
re-arm it after that context switch so shared code belongs to every consumer.
No source filtering, dependency selection or duration boundary changes here.

Testmon's Git hash shortcut can run while the process audit is active during
reporting. Use its ordinary source-reading fallback instead, preserving source
hashes and dependency evidence without launching Git inside a test lifecycle.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from coverage import collector
from testmon import process_code, testmon_core

if TYPE_CHECKING:
    from collections.abc import Generator


def collector_origin() -> str:
    """Format collector diagnostics from frames without loading source files."""
    frames = [f"{frame.f_code.co_name} : {frame.f_code.co_filename}:{line}"
              for frame, line in traceback.walk_stack(None)]
    return "\n".join(reversed(frames))


def source_sha(directory: str, filename: str) -> tuple[str | None, str | None]:
    """Read Testmon's source and blob hash without its optional Git shortcut."""
    return cast("tuple[str | None, str | None]", process_code.read_source_sha(str(Path(directory) / filename)))


def pytest_configure(config: pytest.Config) -> None:
    """Keep diagnostics cheap and dependency hashing free of child processes."""
    patch = pytest.MonkeyPatch()
    patch.setattr(collector, "short_stack", collector_origin)
    patch.setattr(process_code, "get_source_sha", source_sha)
    # Testmon imports the function directly, so patch that binding as well.
    patch.setattr(testmon_core, "get_source_sha", source_sha)
    config.add_cleanup(patch.undo)


@pytest.hookimpl(wrapper=True, trylast=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None) -> Generator[None, object, object]:
    """Run inside testmon's context switch and before fixture setup."""
    del nextitem
    if getattr(getattr(item.config, "testmon_config", None), "collect", False):
        sys.monitoring.restart_events()
    return (yield)


# eof
