"""Run scenario variants through the real CLI without repeated Python startup.

Each invocation gets a fresh CLI runtime, caller directory, host environment
and captured streams. Lifecycle ownership takeover and concurrent waiters keep
real process boundaries; surrounding orchestration reuses imported modules.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tools.review_exchange_cli import main

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.git_test_double import GitTestDouble


def run_inline(arguments: tuple[str, ...], root: Path,
               environment: dict[str, str], git: GitTestDouble | None) -> subprocess.CompletedProcess[str]:
    """Invoke the public parser and dispatch with restored process state."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        patch.chdir(root)
        for name in os.environ.keys() - environment.keys():
            patch.delenv(name)
        for name, value in environment.items():
            patch.setenv(name, value)
        patch.setattr(sys, "stdout", stdout)
        patch.setattr(sys, "stderr", stderr)
        if git is not None:
            patch.setattr(subprocess, "run", git.run)
        code = main(arguments)
    return subprocess.CompletedProcess(arguments, code, stdout.getvalue(), stderr.getvalue())


# eof
