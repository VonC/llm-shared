"""Bounded Git probe double for invocation policy and handler tests.

Only version, empty configuration and physical metadata queries are supported.
The unchanged real-Git and launcher tests retain process-boundary evidence.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from tools.release_workflow.git import GitCommandError

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.git import GitExecutionContext


def probe_result(sandbox: GitSandbox, context: GitExecutionContext, arguments: Sequence[str], *, cwd: Path, check: bool) -> subprocess.CompletedProcess[str]:
    """Serve only the read-only probes needed by the copied empty repositories."""
    command = tuple(arguments)
    config = ("--no-pager", "config", "--null", "--list", "--includes", "--show-origin", "--show-scope")
    metadata = ("--no-pager", "--literal-pathspecs", "-c", "color.ui=false", "-c", "core.quotepath=false",
                "rev-parse", "--path-format=absolute", "--show-toplevel", "--absolute-git-dir", "--git-common-dir")
    status, output, error = 0, "", ""
    if command == ("--version",):
        output = "git version " + ".".join(str(part) for part in sandbox.verified_git.version) + "\n"
    elif command == config:
        pass
    elif command == metadata:
        directory = cwd.resolve()
        root = next((sandbox.home / name for name in ("A/nested", "A", "B") if directory.is_relative_to(sandbox.home / name)), None)
        if root is None:
            status, error = 128, "not a git repository"
        else:
            output = f"{root}\n{root / '.git'}\n{root / '.git'}\n"
    else:
        msg = f"Unmodeled invocation Git probe: {arguments!r}"
        raise AssertionError(msg)
    result = subprocess.CompletedProcess([str(context.executable), *arguments], status, output, error)
    if check and status:
        raise GitCommandError(result)
    return result


# eof
