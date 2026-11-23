"""Use real A/B repositories, linked worktrees and junctions for boundaries.

Share a worker with the configuration matrix to build its session template
once, avoiding concurrent copies of identical native Git initialization.
Read-only authorization cases share validated roots and real junctions;
discovery reuses immutable template metadata; mutation cases stay independent.
The equivalent-root fixture creates only its own junction, so its timeout does
not include unrelated boundary construction and duplicate root validation.
The explicit outside-Git case asserts its fixture's real captured failure;
both native probes still run and their setup duration is recorded.
Textual escapes and file ancestors reuse the same validated boundary matrix,
removing three repository copies and six native probes from those cases.
Linked Git-file rejection shares one native validated identity for both targets.

Step 8 of v0.14.0 git-cliff-provisioning adds `find_worktree`, used only by
`gcliff`: the configuration inspection first, then one presence query; a
plain directory, a bare repository and a `.git` directory give None, inside
a worktree it returns what `discover_project` returns, and every other
failure is a discovery failure. The `discover_project` cases stay unchanged.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow.git import GitCommandError, WorktreePresence
from tools.release_workflow.paths import (
    ProjectPathError,
    authorize_path,
    discover_project,
    find_worktree,
    validate_project,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.git import GitExecutionContext
    from tools.release_workflow.paths import ProjectIdentity

pytestmark = [pytest.mark.timeout(10), pytest.mark.xdist_group("release_git")]


def context(sandbox: GitSandbox, **overrides: str) -> GitExecutionContext:
    """Create an isolated invocation from the sandbox's controlled fixture env."""
    return sandbox.context(**overrides)


def test_stale_a_environment_still_targets_b(git_sandbox: GitSandbox) -> None:
    """Root discovery ignores caller routing back to A."""
    root_a, root_b = git_sandbox.home / "A", git_sandbox.home / "B"
    git = context(git_sandbox, GIT_DIR=str(root_a / ".git"), GIT_WORK_TREE=str(root_a), GIT_INDEX_FILE=str(root_a / ".git" / "index"), GIT_COMMON_DIR=str(root_a / ".git"), GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.worktree", GIT_CONFIG_VALUE_0=str(root_a))
    identity = validate_project(root_b, git)
    assert identity.root.samefile(root_b)
    assert identity.git_dir.samefile(root_b / ".git")
    assert identity.common_dir == identity.git_dir
    assert any("GIT_DIR" in message for message in git.diagnostics)


def test_stale_a_index_still_reads_b(indexed_sandbox: GitSandbox) -> None:
    """Real tracked entries come from B even when the caller selects A's index."""
    root_a, root_b = indexed_sandbox.home / "A", indexed_sandbox.home / "B"
    git = context(indexed_sandbox, GIT_INDEX_FILE=str(root_a / ".git" / "index"))
    assert git.index(cwd=root_b) == ("B.txt",)


def test_linked_worktree_configuration_is_repository_owned(linked_sandbox: GitSandbox) -> None:
    """A real linked worktree reads its common repository's local settings."""
    entries = context(linked_sandbox).inspect_config(cwd=linked_sandbox.home / "linked")
    bare = next(entry for entry in entries if entry.key == "core.bare")
    assert bare.scope == "local"
    assert bare.value == "false"


def test_linked_worktree_metadata_is_separate(linked_sandbox: GitSandbox) -> None:
    """External linked metadata does not make the worktree an escaping path."""
    identity = validate_project(linked_sandbox.home / "linked", context(linked_sandbox))
    assert identity.root.name == "linked"
    assert identity.git_dir.samefile(linked_sandbox.home / "A" / ".git" / "worktrees" / "linked")
    assert identity.common_dir.samefile(linked_sandbox.home / "A" / ".git")
    assert authorize_path(identity, "future/release.txt") == identity.root / "future" / "release.txt"


@pytest.mark.parametrize("supplied", [None, "", "absent", "B/B.txt", "B/sub"])
def test_invalid_explicit_roots(supplied: str | None, git_sandbox: GitSandbox) -> None:
    """Missing, nonexistent, non-directory and subfolder inputs fail preflight."""
    with pytest.raises(ProjectPathError):
        validate_project(supplied, context(git_sandbox))


def test_alias_discovers_from_subfolder(git_template: GitSandbox, discovered_project: ProjectIdentity) -> None:
    """Alias discovery uses the same physical-root validation from a subfolder."""
    assert discovered_project.root.samefile(git_template.home / "B")


def test_equivalent_physical_roots(git_sandbox: GitSandbox, equivalent_alias: Path) -> None:
    """Case and directory-junction spellings retain the same physical root."""
    root = git_sandbox.home / "B"
    alias = equivalent_alias
    identity = validate_project(str(alias).upper(), context(git_sandbox))
    assert identity.root.samefile(root)
    assert identity.supplied_root == str(alias).upper()


def test_internal_junction_and_future_ancestors(boundary_matrix: tuple[GitSandbox, ProjectIdentity, ProjectIdentity]) -> None:
    """An internal junction authorizes its physical existing and future targets."""
    _, _, identity = boundary_matrix
    root = identity.root
    alias = root / "internal"
    assert authorize_path(identity, alias / "new" / "file") == root / "sub" / "new" / "file"
    assert authorize_path(identity, "B.txt") == root / "B.txt"


@pytest.mark.parametrize("target", ["A", "A/nested"])
def test_external_junction_is_rejected(target: str, boundary_matrix: tuple[GitSandbox, ProjectIdentity, ProjectIdentity]) -> None:
    """Existing and future targets cannot escape through a real junction."""
    _, _, identity = boundary_matrix
    alias = identity.root / ("external" if target == "A" else "external-nested")
    original = str(alias / "future" / "file")
    with pytest.raises(ProjectPathError) as caught:
        authorize_path(identity, original)
    assert original in str(caught.value)


@pytest.mark.parametrize("name", ["nested/B.txt", "nested/future/file", "shortcut/future"])
def test_nested_repository_is_rejected(name: str, boundary_matrix: tuple[GitSandbox, ProjectIdentity, ProjectIdentity]) -> None:
    """A nested repository remains foreign, including through an internal link."""
    _, identity, _ = boundary_matrix
    with pytest.raises(ProjectPathError, match="nested"):
        authorize_path(identity, name)


@pytest.mark.parametrize("name", ["../A/new", "../../elsewhere", "B.txt/child"])
def test_escape_or_file_ancestor_is_rejected(name: str, boundary_matrix: tuple[GitSandbox, ProjectIdentity, ProjectIdentity]) -> None:
    """Textual prefixes and existing file ancestors do not authorize a write."""
    _, _, identity = boundary_matrix
    with pytest.raises(ProjectPathError):
        authorize_path(identity, name)


def test_explicit_root_outside_git_is_rejected(explicit_outside_git: pytest.ExceptionInfo[ProjectPathError], git_sandbox: GitSandbox) -> None:
    """Explicit validation retains the real failure and original root context."""
    assert explicit_outside_git.match("Cannot validate")
    assert str(git_sandbox.home) in str(explicit_outside_git.value)


def test_alias_outside_git_is_rejected(git_sandbox: GitSandbox) -> None:
    """Alias discovery retains the original failed-root context."""
    with pytest.raises(ProjectPathError, match="Cannot discover"):
        discover_project(git_sandbox.home, context(git_sandbox))


def test_linked_nested_worktree_is_rejected(git_sandbox: GitSandbox) -> None:
    """Gitfile boundaries count as foreign even with metadata outside root."""
    root = git_sandbox.home / "B"
    foreign = root / "foreign"
    foreign.mkdir()
    (foreign / ".git").write_text(f"gitdir: {git_sandbox.home / 'A' / '.git'}\n", encoding="utf-8")
    identity = validate_project(root, context(git_sandbox))
    with pytest.raises(ProjectPathError, match="nested"):
        authorize_path(identity, foreign / "new")


@pytest.mark.parametrize("name", [".git", ".git/objects/new"])
def test_git_metadata_is_not_a_managed_destination(name: str, boundary_matrix: tuple[GitSandbox, ProjectIdentity, ProjectIdentity]) -> None:
    """Bare Git metadata under the project must not receive managed files."""
    _, _, identity = boundary_matrix
    with pytest.raises(ProjectPathError, match="Git metadata"):
        authorize_path(identity, name)


@pytest.mark.parametrize("name", [".git", ".git/child"])
def test_linked_gitfile_is_not_a_managed_destination(name: str, linked_identity: ProjectIdentity) -> None:
    """Protect a linked worktree's pointer file as both target and ancestor."""
    with pytest.raises(ProjectPathError, match="Git metadata"):
        authorize_path(linked_identity, name)


def test_find_worktree_returns_what_discovery_returns(git_sandbox: GitSandbox) -> None:
    """Step 8 of git-cliff-provisioning: from a nested folder, `find_worktree` gives the identity `discover_project` gives."""
    git = context(git_sandbox)
    found = find_worktree(git_sandbox.home / "B" / "sub", git)
    assert found == discover_project(git_sandbox.home / "B" / "sub", git)
    assert found is not None
    assert found.root == (git_sandbox.home / "B").resolve()


@pytest.mark.parametrize("place", ["plain", "bare.git", "B/.git"])
def test_a_directory_without_a_worktree_finds_none(place: str, git_sandbox: GitSandbox) -> None:
    """A plain directory, a bare repository and a `.git` directory are no worktree: None, not a failure."""
    directory = git_sandbox.home / place
    directory.mkdir(exist_ok=True)
    if place == "bare.git":
        git_sandbox.declare_presence(directory, WorktreePresence.NO_WORKTREE)
    assert find_worktree(directory, context(git_sandbox)) is None


def _recorded(calls: list[str], name: str, method: Callable[..., object]) -> Callable[..., object]:
    """Wrap one Git observation so its calls are listed in order."""
    def observe(self: GitExecutionContext, *, cwd: Path) -> object:
        calls.append(name)
        return method(self, cwd=cwd)
    return observe


def test_find_worktree_inspects_the_configuration_before_the_presence(git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    """The existing configuration inspection runs once, first; the metadata is read only inside a worktree."""
    calls: list[str] = []
    git = context(git_sandbox)
    for name in ("inspect_config", "worktree_presence", "metadata"):
        monkeypatch.setattr(type(git), name, _recorded(calls, name, getattr(type(git), name)))
    find_worktree(git_sandbox.home / "B", git)
    find_worktree(git_sandbox.home, git)
    assert calls == ["inspect_config", "worktree_presence", "metadata", "inspect_config", "worktree_presence"]


def test_a_rejected_configuration_or_another_git_failure_is_a_discovery_failure(git_sandbox: GitSandbox) -> None:
    """A rejected configuration, or a refusal such as a dubious ownership, fails with the discovery context."""
    selected = git_sandbox.home / "chosen.cfg"
    selected.write_text("", encoding="utf-8")
    with pytest.raises(ProjectPathError, match=r"Cannot discover project from .*GIT_CONFIG selector"):
        find_worktree(git_sandbox.home / "B", context(git_sandbox, GIT_CONFIG=str(selected)))
    refusal = subprocess.CompletedProcess(["git"], 128, "", "fatal: detected dubious ownership in repository at 'B'\n")
    git_sandbox.declare_presence(git_sandbox.home / "B", GitCommandError(refusal))
    with pytest.raises(ProjectPathError, match=r"Cannot discover project from .*dubious ownership"):
        find_worktree(git_sandbox.home / "B", context(git_sandbox))


# eof
