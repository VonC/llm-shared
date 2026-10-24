"""Retain real routing probes while separating setup and assertion timings.

Native Git still inspects the actual selected files and repository metadata.
The duration inventory includes fixture cost; moving it does not save total time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.paths import ProjectPathError, validate_project

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.git_environment import ConfigEntry
    from tools.release_workflow.paths import ProjectIdentity


@pytest.fixture
def external_routing_rejection(
    selector: str, routing: tuple[str, str, str], git_sandbox: GitSandbox,
) -> pytest.ExceptionInfo[ProjectPathError]:
    """Capture the real included-file failure for each routing parameter."""
    section, key, value = routing
    selected = git_sandbox.home / "chosen.cfg"
    included = git_sandbox.home / "included.cfg"
    selected.write_text("[include]\n path = included.cfg\n", encoding="utf-8")
    included.write_text(f"[{section}]\n {key} = {value}\n", encoding="utf-8")
    git = git_sandbox.context(**{selector: str(selected)})
    with pytest.raises(ProjectPathError) as caught:
        validate_project(git_sandbox.home / "B", git)
    return caught


@pytest.fixture
def repository_routing_result(
    git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, ProjectIdentity, tuple[ConfigEntry, ...]]:
    """Retain the identity and config entries from actual local/worktree Git."""
    root = git_sandbox.home / "B"
    with (root / ".git" / "config").open("a", encoding="utf-8") as config:
        config.write("[extensions]\n worktreeConfig = true\n[core]\n worktree = ..\n bare = false\n")
    (root / ".git" / "config.worktree").write_text("[core]\n bare = false\n worktree = ..\n", encoding="utf-8")
    entries: list[ConfigEntry] = []
    inspect_config = GitExecutionContext.inspect_config

    def observe_config(self: GitExecutionContext, *, cwd: Path) -> tuple[ConfigEntry, ...]:
        """Retain the actual config result used by root validation."""
        result = inspect_config(self, cwd=cwd)
        entries.extend(result)
        return result

    monkeypatch.setattr(GitExecutionContext, "inspect_config", observe_config)
    identity = validate_project(root, git_sandbox.context())
    return root, identity, tuple(entries)


# eof
