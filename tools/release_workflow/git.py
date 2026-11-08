"""Pin one Windows Git executable and run explicit native subprocesses.

The release adapter does not change the legacy cross-platform Git helper.
Every invocation, including version/config probes, has a fixed executable,
copied environment and absolute cwd. Child failures retain status and stderr.

Step 1 of v0.14.0 version-sources adds typed release observations, each one
`run` call: tag records with their peeled commit and own annotation,
independent tips, tag names between two revisions, a commit count and the
candidate listing. A reachability filter naming no object raises
`GitRevisionNotFoundError` from that same call, and the tips query refuses a
command line longer than Windows accepts before any process starts.

The Git floor is 2.44.0 since that step: range selection reads every tag with
its commit in one `for-each-ref` call, and only from Git 2.44 does `%(*...)`
peel a tag of a tag to its commit (older Git stops at the inner tag object,
which no listing row explains once the inner ref is deleted). An older Git is
refused at selection with that reason, and a record still dereferenced to a
tag fails closed with it.
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
    validate_entry,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_MINIMUM_VERSION = (2, 44, 0)
_FLOOR_REASON = (
    "release range selection reads every tag with its commit in one `git for-each-ref` call, "
    "and only Git 2.44 or later peels a tag of a tag to its commit there (older Git stops at the inner tag)"
)
_METADATA_PATH_COUNT = 3
_VERSION = re.compile(r"git version (\d+)\.(\d+)\.(\d+)(?:\.windows\.\d+)?\s*")
# Output-only options of every domain command, also measured by the tips guard.
_RUN_OPTIONS = ("--no-pager", "--literal-pathspecs", "-c", "color.ui=false", "-c", "core.quotepath=false")
# CreateProcess accepts 32,767 UTF-16 code units, the terminating NUL included.
_COMMAND_LINE_LIMIT = 32_767
_USAGE_STATUS = 129
_TAG_FIELDS = ("%(refname:strip=2)", "%(objecttype)", "%(objectname)", "%(*objecttype)", "%(*objectname)", "%(contents)")
_TAG_FORMAT = "".join(f"{name}%00" for name in _TAG_FIELDS)


class GitCommandError(GitPolicyError):
    """A failed child with its status and losslessly decoded output attached."""

    def __init__(self, result: subprocess.CompletedProcess[str]) -> None:
        """Keep the return code, stdout and stderr for the public result boundary."""
        self.result = result
        super().__init__(f"Git exited {result.returncode}: {result.stderr.rstrip()}")


class GitRevisionNotFoundError(GitCommandError):
    """A reachability filter names no object: a missing target, not a Git failure."""

    exit_code = 2

    def __init__(self, result: subprocess.CompletedProcess[str], revision: str) -> None:
        """Keep the missing revision beside the original failed command."""
        self.revision = revision
        super().__init__(result)


class GitCommandLineTooLongError(GitPolicyError):
    """A query whose Windows command line would exceed the process limit."""

    exit_code = 1

    def __init__(self, units: int, candidates: int) -> None:
        """Name the limit, the measured length and the candidate count."""
        self.units = units
        self.candidates = candidates
        super().__init__(
            f"Git command line of {units} UTF-16 code units exceeds the Windows limit of "
            f"{_COMMAND_LINE_LIMIT} for {candidates} candidate commits",
        )


@dataclass(frozen=True)
class TagRecord:
    """One tag ref: its name, object type, peeled commit and own annotation.

    A lightweight tag has no annotation (`None`); Git would otherwise report
    the message of the commit it names.
    """

    name: str
    object_type: str
    commit: str
    annotation: str | None


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


def _tag_records(output: str) -> tuple[TagRecord, ...]:
    """Split NUL-terminated six-field records, each followed by a newline.

    The commit of an annotated tag is its dereferenced object, which Git 2.44
    or later peels fully, through a tag of a tag too. A dereferenced type
    `tag` means an older Git stopped at the inner tag object, so the record
    cannot name its commit and the listing is refused with the floor's reason.
    """
    *fields, tail = output.split("\0")
    width = len(_TAG_FIELDS)
    if (tail, len(fields) % width) != ("\n" if fields else "", 0):
        msg = f"Git did not report NUL-terminated tag records: {output[:80]!r}"
        raise GitPolicyError(msg)
    records: list[TagRecord] = []
    for start in range(0, len(fields), width):
        raw_name, object_type, target, kind, peeled, contents = fields[start:start + width]
        # The newline closing the previous record starts each later record's name.
        name = raw_name.removeprefix("\n")
        if object_type != "tag":
            records.append(TagRecord(name, object_type, target, None))
            continue
        if kind == "tag":
            msg = f"Git did not peel tag {name} to its commit (it reported the inner tag {peeled}); {_FLOOR_REASON}"
            raise GitPolicyError(msg)
        records.append(TagRecord(name, object_type, peeled, contents))
    return tuple(records)


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
        version = probe.read_version(cwd=cwd)
        if version < _MINIMUM_VERSION:
            required, found = (".".join(map(str, numbers)) for numbers in (_MINIMUM_VERSION, version))
            msg = f"Git version {found} at {executable} is older than required {required}: {_FLOOR_REASON}. Upgrade Git to 2.44 or later."
            raise GitPolicyError(msg)
        return cls(executable, version, environment, cwd, non_interactive)

    def read_version(self, *, cwd: Path) -> tuple[int, int, int]:
        """Read the native version once at the executable adapter boundary."""
        result = self._execute(["--version"], cwd=cwd)
        match = _VERSION.fullmatch(result.stdout)
        if match is None:
            msg = f"Cannot establish Git version from {self.executable}: {result.stdout!r}"
            raise GitPolicyError(msg)
        return (int(match[1]), int(match[2]), int(match[3]))

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

    def effective_config(self, *, cwd: Path) -> tuple[ConfigEntry, ...]:
        """Read effective values through the native config parser."""
        result = self._execute(["--no-pager", "config", "--null", "--list", "--includes", "--show-origin", "--show-scope"], cwd=cwd, lossless_stdout=True)
        return validate_config(result.stdout)

    def inspect_config(self, *, cwd: Path) -> tuple[ConfigEntry, ...]:
        """Inspect genuine scopes before adding our own output-only options."""
        entries = tuple(validate_entry(entry) for entry in self.effective_config(cwd=cwd))
        # Even an empty command-scoped selected file hides the normal config
        # chain. No emitted entry does not mean that chain was inspected.
        selector = next((value for key, value in self.environment.values.items() if key.upper() == "GIT_CONFIG"), None)
        if selector is not None:
            msg = f"Rejected Git configuration: command scope, file:{selector}, GIT_CONFIG selector"
            raise GitPolicyError(msg)
        return entries

    def metadata(self, *, cwd: Path) -> tuple[Path, Path, Path]:
        """Read typed worktree and Git metadata from the native adapter."""
        result = self.run(["rev-parse", "--path-format=absolute", "--show-toplevel", "--absolute-git-dir", "--git-common-dir"], cwd=cwd)
        lines = result.stdout.splitlines()
        if len(lines) != _METADATA_PATH_COUNT or any(not Path(line).is_absolute() for line in lines):
            msg = "Git did not report three absolute project metadata paths"
            raise GitPolicyError(msg)
        return Path(lines[0]), Path(lines[1]), Path(lines[2])

    def index(self, *, cwd: Path, directory: str | None = None) -> tuple[str, ...]:
        """Return tracked names without exposing NUL-delimited command output."""
        arguments = ["ls-files", "-z"]
        if directory is not None:
            arguments.extend(["--", directory])
        return tuple(filter(None, self.run(arguments, cwd=cwd).stdout.split("\0")))

    def tag_records(self, *, cwd: Path, merged: str | None = None) -> tuple[TagRecord, ...]:
        """List every tag ref, or those reachable from one revision, in one call.

        Exit 129 reporting a malformed object name for the supplied filter is a
        missing target (`GitRevisionNotFoundError`); every other failure stays a
        `GitCommandError`, so the selector needs no second query.
        """
        selected = [] if merged is None else [f"--merged={merged}"]
        result = self.run(["for-each-ref", f"--format={_TAG_FORMAT}", *selected, "refs/tags"], cwd=cwd, check=False)
        if result.returncode:
            if merged is not None and result.returncode == _USAGE_STATUS and f"malformed object name {merged}" in result.stderr:
                raise GitRevisionNotFoundError(result, merged)
            raise GitCommandError(result)
        return _tag_records(result.stdout)

    def _independent_arguments(self, commits: Sequence[str]) -> list[str]:
        """Build the tips query, refusing a command line Windows cannot start.

        The measure is the exact line `_execute` would pass to CreateProcess:
        the selected executable, the fixed `run` options and the arguments,
        quoted by `subprocess.list2cmdline`, in UTF-16 units plus the NUL.
        """
        arguments = ["merge-base", "--independent", *commits]
        line = subprocess.list2cmdline([str(self.executable), *_RUN_OPTIONS, *arguments])
        units = len(line.encode("utf-16-le")) // 2 + 1
        if units > _COMMAND_LINE_LIMIT:
            raise GitCommandLineTooLongError(units, len(commits))
        return arguments

    def independent_commits(self, commits: Sequence[str], *, cwd: Path) -> tuple[str, ...]:
        """Return the candidates that are not ancestors of another, in one call."""
        return tuple(self.run(self._independent_arguments(commits), cwd=cwd).stdout.split())

    def tag_names(self, *, cwd: Path, merged: str, not_merged: str) -> tuple[str, ...]:
        """Name the tags reachable from one revision and not from another."""
        arguments = ["for-each-ref", "--format=%(refname:strip=2)", f"--merged={merged}", f"--no-merged={not_merged}", "refs/tags"]
        return tuple(self.run(arguments, cwd=cwd).stdout.splitlines())

    def commit_count(self, revision_range: str, *, cwd: Path) -> int:
        """Ask Git for the number of commits in a revision range."""
        output = self.run(["rev-list", "--count", revision_range], cwd=cwd).stdout.strip()
        if not output.isdigit():
            msg = f"Git did not report a commit count for {revision_range}: {output!r}"
            raise GitPolicyError(msg)
        return int(output)

    def listing(self, *, cwd: Path) -> tuple[str, ...]:
        """List tracked and unignored untracked names, without embedded repositories.

        Git reports an untracked nested repository as one name ending with
        `/`; it is dropped. A tracked gitlink stays an ordinary name.
        """
        output = self.run(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=cwd).stdout
        return tuple(name for name in output.split("\0") if name and not name.endswith("/"))

    def run(self, arguments: Sequence[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
        """Run a trusted domain command with explicit output and literal paths.

        Callers select the command's machine format (for example `-z` or
        porcelain). Internal color/quoting settings are added only after the
        independent effective-configuration inspection used by root validation.
        """
        return self._execute([*_RUN_OPTIONS, *arguments], cwd=cwd, check=check)


# eof
