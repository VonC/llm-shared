"""Cross-platform Git subprocess execution for local batch commit tools.

Fix: Vendor the Git command helper into this repository so tools can run
without importing the `pdfss` package from another project.

Fix: Keep the cached platform dispatch so Linux always runs `command git`
through `/bin/sh -c`, while Windows runs `git` directly.

Fix: Avoid a login shell on Linux so Git subprocesses keep the Python process
environment instead of letting `/bin/sh -l` rebuild `PATH` before
`command git` runs.

Fix: Accept per-call environment overrides so callers can expose live Git
trace output for a single command without mutating the parent Python process.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

_IS_WINDOWS = os.name == "nt"
_GIT_COMMAND_PREFIX = "git" if _IS_WINDOWS else "command git"
_GIT_LINUX_SHELL = ("/bin/sh", "-c")


@dataclass(frozen=True)
class GitCommandOptions:
    """Options for one Git subprocess invocation."""

    check: bool = True
    capture_output: bool = False
    encoding: str | None = None
    env: dict[str, str] | None = None


def _build_linux_git_shell_command(git_args: Sequence[str]) -> str:
    """Build the Linux shell command used to invoke Git."""
    return f"{_GIT_COMMAND_PREFIX} {shlex.join(list(git_args))}"


def run_cross_platform_git_command(
    git_args: Sequence[str],
    *,
    cwd: Path | None = None,
    options: GitCommandOptions | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a Git command using the cached platform-specific invocation path.

    Args:
        git_args: Git subcommand arguments without the leading `git` token.
        cwd: Working directory for the subprocess.
        options: Optional subprocess execution settings.

    Returns:
        The completed subprocess result with text stdout/stderr.
    """
    git_options = options or GitCommandOptions()

    if _IS_WINDOWS:
        return subprocess.run(  # noqa: S603
            [_GIT_COMMAND_PREFIX, *git_args],
            cwd=cwd,
            check=git_options.check,
            capture_output=git_options.capture_output,
            text=True,
            encoding=git_options.encoding,
            env=git_options.env,
        )

    return subprocess.run(  # noqa: S603
        [*_GIT_LINUX_SHELL, _build_linux_git_shell_command(git_args)],
        cwd=cwd,
        check=git_options.check,
        capture_output=git_options.capture_output,
        text=True,
        encoding=git_options.encoding,
        env=git_options.env,
    )


# eof
