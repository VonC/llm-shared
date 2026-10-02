"""Injectable seams and parsed invocation of the groundhog CLI.

Split out of ``cli.py`` so the entry point stays under the repo line
budget: this module carries the two dataclasses every command executor
receives — the ``Deps`` seams faked by the tests, and the ``Invocation``
parsed from the command line.

Fix: the Q32 lifecycle adds two seams — the detached-walk spawn and the
handshake sleep — and the ``detach`` flag of the day walk to the
invocation.

Fix: the ``pytest_project`` seam tells the pytest steps whether the root
carries a pytest suite, so a project without one exits 9 before any pytest
lookup.

Fix (v0.13.0 full_suite_levels, Step 2): the ``environ`` seam is the one read
of the process environment (``GHOG_FULL``), so tests never touch the real
environment; the invocation carries its resolved full-suite ``level`` and
``level_source`` (``None`` meaning the command default, so a directly built
invocation keeps its old behavior: ``full`` at ``speed``, every other command
at ``none``), and ``in_walk`` tells a step derived by the day walk from a
standalone command, so a step report never prints the standalone next step.
The default survivor spawn now comes from ``detach.py``, split out of
``status.py``.
"""

from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.groundhog import detach, render, runner
from tools.groundhog.levels import LevelSource

if TYPE_CHECKING:
    import subprocess
    from collections.abc import Callable

    from tools.groundhog.levels import FullLevel
    from tools.groundhog.models import Mode
    from tools.groundhog.render import ProgressBar


@dataclass(frozen=True)
class Deps:
    """Injectable seams of the CLI, the single faked layer in tests.

    Attributes:
        popen_factory: Child-process factory (Q17).
        clock: Monotonic time source for the progress cadence (Q04).
        bar_factory: User-mode bar factory, the tqdm seam (Q20).
        which: Executable lookup for the project pytest.
        home: User home lookup, for the Codex prompt of init (Q25).
        detach_factory: Survivor spawn of the detached day walk (Q32).
        sleep: Handshake pause of the detached launch (Q32).
        pytest_project: Root probe for a pytest suite, gating the pytest
            steps before the pytest lookup.
        environ: Environment lookup, read only for ``GHOG_FULL`` when no
            ``--full`` parameter selects a level.
    """

    popen_factory: Callable[[list[str], Path], subprocess.Popen[str]] = (
        runner.default_popen_factory
    )
    clock: Callable[[], float] = time.monotonic
    bar_factory: Callable[[int, str], ProgressBar] = render.make_bar
    which: Callable[[str], str | None] = shutil.which
    home: Callable[[], Path] = Path.home
    detach_factory: Callable[[list[str], Path, str, Path], int] = (
        detach.default_detach_factory
    )
    sleep: Callable[[float], None] = time.sleep
    pytest_project: Callable[[Path], bool] = runner.is_pytest_project
    environ: Callable[[str], str | None] = os.environ.get


@dataclass(frozen=True)
class Invocation:
    """One parsed groundhog invocation.

    Attributes:
        sub: The subcommand name (Q15).
        files: The test files of a ``single`` run.
        no_cov: Whether coverage is disabled (the ptanc variant).
        mode: The picked output mode (Q03).
        root: The consuming project root.
        force: Whether a ``day`` walk runs even when the source matches
            the last green walk (Q28).
        detach: Whether a ``day`` walk runs as a survivor process,
            polled through ``ghog status`` (Q32).
        node: The pytest node id of an ``exclude`` run, the accepted-slow
            call written to the ``[exclusion]`` section (Q62).
        seconds: The measured call time of an ``exclude`` run, the recorded
            baseline the full run later holds the call to (Q56, Q62).
        level: The resolved full-suite level, ``None`` for the command
            default of a directly built invocation.
        level_source: Where the level came from: the parameter, the
            environment variable or the command default.
        in_walk: Whether this step was derived by the day walk, whose own
            report carries the next step and the closing evidence.
    """

    sub: str
    files: tuple[str, ...]
    no_cov: bool
    mode: Mode
    root: Path
    force: bool = False
    detach: bool = False
    node: str = ""
    seconds: float = 0.0
    level: FullLevel | None = None
    level_source: LevelSource = LevelSource.DEFAULT
    in_walk: bool = False


# eof
