"""Pin Git once, isolate child state and retain original command failures."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow.git import GitCommandError, GitExecutionContext
from tools.release_workflow.git_environment import GitPolicyError

if TYPE_CHECKING:
    from collections.abc import Sequence

_CHILD_FAILURE = 23


class RecordingGit:
    """Record native process boundaries with configurable version and result."""

    def __init__(self, version: str = "git version 2.31.0.windows.1\n") -> None:
        """Start with the minimum supported Git and successful empty config."""
        self.version = version
        self.calls: list[tuple[list[str], dict[str, object]]] = []
        self.result = subprocess.CompletedProcess[bytes]([], 0, b"", b"")

    def __call__(self, args: Sequence[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        """Keep arguments and process policy visible to assertions."""
        self.calls.append((list(args), kwargs))
        if args[-1] == "--version":
            return subprocess.CompletedProcess(args, 0, self.version.encode("utf-8"), b"")
        self.result.args = args
        return self.result


@pytest.fixture
def selected_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[GitExecutionContext, RecordingGit]:
    """Prepare a selected absolute executable without starting a process."""
    installed = tmp_path / "installed"
    installed.mkdir()
    (installed / "git.exe").touch()
    recorder = RecordingGit()
    monkeypatch.setattr(subprocess, "run", recorder)
    context = GitExecutionContext.create({"PATH": str(installed)}, original_cwd=tmp_path, non_interactive=True)
    return context, recorder


def test_select_first_eligible_executable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Cwd, empty and relative entries and PATHEXT shims cannot win selection."""
    directories = [tmp_path / name for name in ("cwd", "shims", "first", "second")]
    for directory in directories:
        directory.mkdir()
    cwd, shims, first, second = directories
    for directory in (cwd, first, second):
        (directory / "git.exe").touch()
    (shims / "git.cmd").touch()
    (shims / "git.bat").touch()
    recorder = RecordingGit()
    monkeypatch.setattr(subprocess, "run", recorder)
    source = {"Path": os.pathsep.join(("", ".", "relative", str(cwd), str(shims), str(first), str(second))), "PATHEXT": ".CMD;.BAT;.EXE"}
    context = GitExecutionContext.create(source, original_cwd=cwd, non_interactive=True)
    assert context.executable == first / "git.exe"
    assert context.version == (2, 31, 0)
    assert len(recorder.calls) == 1
    assert recorder.calls[0][1]["cwd"] == cwd
    assert source["PATHEXT"] == ".CMD;.BAT;.EXE"


@pytest.mark.parametrize("version", ["git version 2.30.9", "unknown", "git version 2.31", "git version 2.31.0oops"])
def test_bad_version_never_falls_back(version: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An unverified first candidate is an error, not permission to try later Git."""
    for name in ("first", "second"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "git.exe").touch()
    recorder = RecordingGit(version)
    monkeypatch.setattr(subprocess, "run", recorder)
    with pytest.raises(GitPolicyError, match="version"):
        GitExecutionContext.create({"PATH": os.pathsep.join(str(tmp_path / name) for name in ("first", "second"))}, original_cwd=tmp_path, non_interactive=True)
    assert len(recorder.calls) == 1


def test_no_eligible_git(tmp_path: Path) -> None:
    """Missing or relative PATH entries fail without consulting bare Git."""
    with pytest.raises(GitPolicyError, match=r"git\.exe"):
        GitExecutionContext.create({"PATH": ".;relative;;"}, original_cwd=tmp_path, non_interactive=True)


def test_all_calls_pin_cwd_environment_and_native_arguments(selected_git: tuple[GitExecutionContext, RecordingGit], tmp_path: Path) -> None:
    """A later cwd and shell metacharacters remain data in a pinned child call."""
    context, recorder = selected_git
    context.inspect_config(cwd=tmp_path)
    result = context.run(["ls-files", "-z", "--", "a & b!.txt"], cwd=tmp_path)
    assert result.returncode == 0
    for args, kwargs in recorder.calls:
        assert args[0] == str(context.executable)
        assert (kwargs["cwd"], kwargs["shell"], kwargs["stdin"]) == (tmp_path, False, subprocess.DEVNULL)
        assert kwargs["env"] is not os.environ
        assert (kwargs["text"], "encoding" in kwargs) == (False, False)
    assert recorder.calls[-1][0][-1] == "a & b!.txt"
    assert {"--null", "--show-origin", "--show-scope"} <= set(recorder.calls[1][0])
    assert "-c" not in recorder.calls[1][0]


def test_failure_retains_child_status_and_stderr(selected_git: tuple[GitExecutionContext, RecordingGit], tmp_path: Path) -> None:
    """Failures expose the original child result for the later public boundary."""
    context, recorder = selected_git
    recorder.result = subprocess.CompletedProcess([], _CHILD_FAILURE, b"partial \xe9", b"fatal: original \xe9\n")
    with pytest.raises(GitCommandError, match="original") as caught:
        context.run(["status", "--porcelain=v1", "-z"], cwd=tmp_path)
    assert caught.value.result.returncode == _CHILD_FAILURE
    assert caught.value.result.stdout.encode("utf-8", errors="surrogateescape") == recorder.result.stdout
    assert caught.value.result.stderr.encode("utf-8", errors="surrogateescape") == recorder.result.stderr
    unchecked = context.run(["check-ignore", "absent"], cwd=tmp_path, check=False)
    assert unchecked.returncode == _CHILD_FAILURE
    assert unchecked.stdout == caught.value.result.stdout
    assert unchecked.stderr == caught.value.result.stderr


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_missing_capture_cannot_pass_configuration_policy(stream: str, selected_git: tuple[GitExecutionContext, RecordingGit], tmp_path: Path) -> None:
    """A missing stream is an explicit failure, even when the child exits zero."""
    context, recorder = selected_git
    setattr(recorder.result, stream, None)
    with pytest.raises(GitPolicyError, match=r"Missing.*config"):
        context.inspect_config(cwd=tmp_path)


def test_invalid_utf8_metadata_is_rejected(selected_git: tuple[GitExecutionContext, RecordingGit], tmp_path: Path) -> None:
    """Successful path output must decode strictly rather than be guessed."""
    context, recorder = selected_git
    recorder.result = subprocess.CompletedProcess([], 0, b"C:/project/\xff", b"")
    with pytest.raises(GitPolicyError, match=r"UTF-8.*rev-parse"):
        context.run(["rev-parse", "--show-toplevel"], cwd=tmp_path)


def test_relative_cwd_is_rejected(selected_git: tuple[GitExecutionContext, RecordingGit]) -> None:
    """No command may silently borrow the engine's process cwd."""
    context, recorder = selected_git
    with pytest.raises(GitPolicyError, match="cwd"):
        context.run(["status"], cwd=Path("relative"))
    assert len(recorder.calls) == 1


def test_selected_executable_launch_failure(selected_git: tuple[GitExecutionContext, RecordingGit], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A selected but unusable executable fails without a PATH retry."""
    context, _ = selected_git

    def fail(_args: Sequence[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        msg = "not executable"
        raise OSError(msg)

    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(GitPolicyError, match="selected Git"):
        context.run(["status"], cwd=tmp_path)


def test_inaccessible_path_entry_is_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An inaccessible directory cannot become an eligible executable."""
    (tmp_path / "blocked").mkdir()
    (tmp_path / "installed").mkdir()
    (tmp_path / "installed" / "git.exe").touch()
    original = Path.samefile

    def samefile(path: Path, other: str | Path) -> bool:
        if path.name == "blocked":
            raise PermissionError
        return original(path, other)

    monkeypatch.setattr(Path, "samefile", samefile)
    monkeypatch.setattr(subprocess, "run", RecordingGit())
    source = {"PATH": os.pathsep.join(str(tmp_path / name) for name in ("blocked", "installed"))}
    context = GitExecutionContext.create(source, original_cwd=tmp_path, non_interactive=False)
    assert context.executable.parent.name == "installed"


def test_interactive_policy_retains_stdin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Interactive callers retain stdin while editors and pagers stay disabled."""
    installed = tmp_path / "installed"
    installed.mkdir()
    (installed / "git.exe").touch()
    recorder = RecordingGit()
    monkeypatch.setattr(subprocess, "run", recorder)
    GitExecutionContext.create({"PATH": str(installed)}, original_cwd=tmp_path, non_interactive=False)
    assert recorder.calls[0][1]["stdin"] is None


# eof
