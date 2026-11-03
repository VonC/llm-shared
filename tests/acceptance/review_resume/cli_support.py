"""Run scenario variants through the real CLI without repeated Python startup.

Each invocation gets a fresh CLI runtime, caller directory, host environment
and captured streams. Ownership recovery and scheduled competing claims use
the same production entry points without child processes.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow, review_exchange_cli, review_status_cli

if TYPE_CHECKING:
    from pathlib import Path


def run_inline(arguments: tuple[str, ...], root: Path,
               environment: dict[str, str], *, entry: str = "exchange") -> subprocess.CompletedProcess[str]:
    """Invoke the public CLI using the package's declared repository observations."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        patch.chdir(root)
        patch.setattr(os, "environ", dict(environment))
        patch.setattr(sys, "stdout", stdout)
        patch.setattr(sys, "stderr", stderr)
        main = {"exchange": review_exchange_cli.main, "status": review_status_cli.main,
                "workflow": prompt_workflow.main}[entry]
        code = main(list(arguments))
    return subprocess.CompletedProcess(arguments, code, stdout.getvalue(), stderr.getvalue())


# eof
