"""Pin one Windows Git executable and run explicit native subprocesses.

The release adapter does not change the legacy cross-platform Git helper.
Every invocation, including version/config probes, has a fixed executable,
copied environment and absolute cwd. Child failures retain status and stderr.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.git_environment import (
    ConfigEntry,
    GitEnvironment,
    GitPolicyError,
    controlled_environment,
    validate_config,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_MINIMUM_VERSION = (2, 31, 0)
_VERSION = re.compile(r"git version (\d+)\.(\d+)\.(\d+)(?:\.windows\.\d+)?\s*")


class GitCommandError(GitPolicyError):
    """A failed child with its status and losslessly decoded output attached."""

    def __init__(self, result: subprocess.CompletedProcess[str]) -> None:
        """Keep the return code, stdout and stderr for the public result boundary."""
        self.result = result
        super().__init__(f"Git exited {result.returncode}: {result.stderr.rstrip()}")


def _absolute_directory(path: Path) -> Path:
    """Reject an implicit or invalid process cwd before invoking Git."""
    if not path.is_absolute() or not path.is_dir():
        msg = f"Git cwd must be an existing absolute directory: {path}"
        raise GitPolicyError(msg)
    return path.resolve(strict=True)


def _select_executable(source: Mapping[str, str], original_cwd: Path) -> Path:
    """Select the first eligible git.exe without cwd or PATHEXT fallback."""
    search = next((value for key, value in source.items() if key.upper() == "PATH"), "")
    for entry in search.split(os.pathsep):
        directory = Path(entry)
        if not entry or not directory.is_absolute():
            continue
        try:
            if not directory.is_dir() or directory.samefile(original_cwd):
                continue
            candidate = directory / "git.exe"
            if candidate.is_file():
                return candidate.resolve(strict=True)
        except OSError:
            # An inaccessible PATH entry is not an eligible executable.
            continue
    msg = "No eligible git.exe in absolute PATH directories outside the original cwd"
    raise GitPolicyError(msg)


def _decode_stream(output: bytes | None, *, arguments: Sequence[str], name: str, lossless: bool) -> str:
    """Decode on the calling thread so a reader failure cannot become success."""
    if output is None:
        msg = f"Missing captured Git {name} for {arguments!r}"
        raise GitPolicyError(msg)
    try:
        return output.decode("utf-8", errors="surrogateescape" if lossless else "strict")
    except UnicodeDecodeError as exc:
        msg = f"Git {name} is not valid UTF-8 for {arguments!r}"
        raise GitPolicyError(msg) from exc


@dataclass(frozen=True)
class GitExecutionContext:
    """Immutable executable/version/environment selected once per operation."""

    executable: Path
    version: tuple[int, int, int]
    environment: GitEnvironment
    original_cwd: Path
    non_interactive: bool

    @property
    def diagnostics(self) -> tuple[str, ...]:
        """Return ignored-input diagnostics without exposing caller secrets."""
        return self.environment.diagnostics

    @classmethod
    def create(cls, source: Mapping[str, str], *, original_cwd: Path, non_interactive: bool) -> GitExecutionContext:
        """Select and verify the first eligible executable; never try a fallback."""
        cwd = _absolute_directory(original_cwd)
        executable = _select_executable(source, cwd)
        environment = controlled_environment(source, non_interactive=non_interactive)
        probe = cls(executable, (0, 0, 0), environment, cwd, non_interactive)
        result = probe._execute(["--version"], cwd=cwd)
        match = _VERSION.fullmatch(result.stdout)
        if match is None:
            msg = f"Cannot establish Git version from {executable}: {result.stdout!r}"
            raise GitPolicyError(msg)
        version = (int(match[1]), int(match[2]), int(match[3]))
        if version < _MINIMUM_VERSION:
            msg = f"Git version {version} at {executable} is older than required 2.31.0"
            raise GitPolicyError(msg)
        return cls(executable, version, environment, cwd, non_interactive)

    def _execute(self, arguments: Sequence[str], *, cwd: Path, check: bool = True, lossless_stdout: bool = False) -> subprocess.CompletedProcess[str]:
        """Own the sole subprocess boundary, including startup/config probes."""
        directory = _absolute_directory(cwd)
        try:
            captured = subprocess.run(  # noqa: S603 - pinned absolute executable, native trusted arguments
                [str(self.executable), *arguments], cwd=directory,
                env=dict(self.environment.values), stdin=subprocess.DEVNULL if self.non_interactive else None,
                shell=False, check=False, capture_output=True, text=False,
            )
        except OSError as exc:
            msg = f"Cannot execute selected Git {self.executable}: {exc}"
            raise GitPolicyError(msg) from exc
        # Diagnostics and failed-command output retain every original byte.
        stdout = _decode_stream(captured.stdout, arguments=captured.args, name="stdout", lossless=lossless_stdout or captured.returncode != 0)
        stderr = _decode_stream(captured.stderr, arguments=captured.args, name="stderr", lossless=True)
        result = subprocess.CompletedProcess(captured.args, captured.returncode, stdout, stderr)
        if check and result.returncode:
            raise GitCommandError(result)
        return result

    def inspect_config(self, *, cwd: Path) -> tuple[ConfigEntry, ...]:
        """Inspect genuine scopes before adding our own output-only options."""
        result = self._execute(["--no-pager", "config", "--null", "--list", "--includes", "--show-origin", "--show-scope"], cwd=cwd, lossless_stdout=True)
        entries = validate_config(result.stdout)
        # Even an empty command-scoped selected file hides the normal config
        # chain. No emitted entry does not mean that chain was inspected.
        selector = next((value for key, value in self.environment.values.items() if key.upper() == "GIT_CONFIG"), None)
        if selector is not None:
            msg = f"Rejected Git configuration: command scope, file:{selector}, GIT_CONFIG selector"
            raise GitPolicyError(msg)
        return entries

    def run(self, arguments: Sequence[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
        """Run a trusted domain command with explicit output and literal paths.

        Callers select the command's machine format (for example `-z` or
        porcelain). Internal color/quoting settings are added only after the
        independent effective-configuration inspection used by root validation.
        """
        return self._execute([
            "--no-pager", "--literal-pathspecs", "-c", "color.ui=false",
            "-c", "core.quotepath=false", *arguments,
        ], cwd=cwd, check=check)


# eof
