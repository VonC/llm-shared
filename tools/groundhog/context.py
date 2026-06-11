"""Injectable seams and parsed invocation of the groundhog CLI.

Split out of ``cli.py`` so the entry point stays under the repo line
budget: this module carries the two dataclasses every command executor
receives — the ``Deps`` seams faked by the tests, and the ``Invocation``
parsed from the command line.
"""

from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.groundhog import render, runner

if TYPE_CHECKING:
    import subprocess
    from collections.abc import Callable

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
    """

    popen_factory: Callable[[list[str], Path], subprocess.Popen[str]] = (
        runner.default_popen_factory
    )
    clock: Callable[[], float] = time.monotonic
    bar_factory: Callable[[int, str], ProgressBar] = render.make_bar
    which: Callable[[str], str | None] = shutil.which
    home: Callable[[], Path] = Path.home


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
    """

    sub: str
    files: tuple[str, ...]
    no_cov: bool
    mode: Mode
    root: Path
    force: bool = False


# eof
