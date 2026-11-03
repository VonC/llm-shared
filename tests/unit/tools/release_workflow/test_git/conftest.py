"""Retain real routing probes while separating setup and assertion timings.

Native Git still inspects the actual selected files and repository metadata.
The duration inventory includes fixture cost; moving it does not save total time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.git_environment import ConfigEntry
from tools.release_workflow.paths import ProjectPathError, validate_project

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
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
    scope = "global" if selector == "GIT_CONFIG_GLOBAL" else "system"
    git_sandbox.configure(selected, ConfigEntry(scope, f"file:{included}", f"{section}.{key}".lower(), value))
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
    git_sandbox.configure(root,
        ConfigEntry("local", f"file:{root / '.git/config'}", "extensions.worktreeconfig", "true"),
        ConfigEntry("worktree", f"file:{root / '.git/config.worktree'}", "core.bare", "false"),
        ConfigEntry("worktree", f"file:{root / '.git/config.worktree'}", "core.worktree", ".."))
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
