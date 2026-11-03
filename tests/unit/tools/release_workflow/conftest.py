"""Data-only runtime and repository fixtures for production release contracts.

Step 6 (2026-11-02): integrated acceptance adds consumer projects A and B with
version data, ignored output and legacy scratch, plus declared lock process
facts; the transition mutex is uncontended, as in the lock contract tests.
"""

from __future__ import annotations

import sys
from contextlib import nullcontext
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.acceptance_support import (
    LockFacts,
    consumer,
    handlers,
)
from tests.unit.tools.release_workflow.git_test_support import (
    GitSandbox,
    copy_template,
    create_template,
)
from tests.unit.tools.release_workflow.invocation_test_support import probe_result
from tests.unit.tools.release_workflow.launcher_simulation import (
    ToolingSimulation,
    tooling,
)
from tests.unit.tools.release_workflow.test_support import prepared_runtime
from tools.release_workflow import operation_lock
from tools.release_workflow.git import GitExecutionContext

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from pathlib import Path
    from subprocess import CompletedProcess

    from tools.release_workflow import cli


@pytest.fixture
def bootstrap_state() -> Iterator[None]:
    """Restore bytecode, import path and private helper state after each check."""
    bytecode = sys.dont_write_bytecode
    search_path = list(sys.path)
    private = {name: module for name, module in sys.modules.items() if name.startswith("_release_bootstrap_")}
    yield
    sys.dont_write_bytecode = bytecode
    sys.path[:] = search_path
    for name in list(sys.modules):
        if name.startswith("_release_bootstrap_"):
            del sys.modules[name]
    sys.modules.update(private)


@pytest.fixture
def runtime(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Provide a tooling root, measured executable and measured prefix."""
    executable, prefix = prepared_runtime(tmp_path)
    return tmp_path, executable, prefix


@pytest.fixture(scope="session")
def git_template(tmp_path_factory: pytest.TempPathFactory) -> GitSandbox:
    """Declare minimal repository metadata and a non-executable Git port."""
    return create_template(tmp_path_factory.mktemp("release-git-template"))


@pytest.fixture
def git_sandbox(git_template: GitSandbox, tmp_path: Path) -> GitSandbox:
    """Give each case independent copies of the small empty repository."""
    return copy_template(git_template, tmp_path)


@pytest.fixture
def read_only_git(git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid process startup in composition cases that do not test Git itself."""
    def execute(context: GitExecutionContext, arguments: Sequence[str], *, cwd: Path,
                check: bool = True, lossless_stdout: bool = False) -> CompletedProcess[str]:
        del lossless_stdout
        return probe_result(git_sandbox, context, arguments, cwd=cwd, check=check)

    monkeypatch.setattr(GitExecutionContext, "_execute", execute)


@pytest.fixture(scope="session")
def linked_sandbox(git_template: GitSandbox, tmp_path_factory: pytest.TempPathFactory) -> GitSandbox:
    """Share read-only linked metadata between config and identity checks."""
    sandbox = copy_template(git_template, tmp_path_factory.mktemp("release-linked"))
    sandbox.linked_worktree()
    return sandbox


@pytest.fixture(scope="session")
def launcher_tooling(tmp_path_factory: pytest.TempPathFactory) -> ToolingSimulation:
    """Prepare runtime data without copying code or creating an interpreter."""
    return tooling(tmp_path_factory.mktemp("release-launchers") / "tooling é % ^ ! & space")


@pytest.fixture(scope="session")
def alternate_launcher_tooling(tmp_path_factory: pytest.TempPathFactory) -> ToolingSimulation:
    """Provide another independent tooling designation for dispatch."""
    return tooling(tmp_path_factory.mktemp("release-alternate") / "alternate é % ^ ! & space")


@pytest.fixture
def consumers(git_sandbox: GitSandbox) -> tuple[Path, Path]:
    """Give projects A and B version data, ignored output and legacy scratch."""
    return consumer(git_sandbox.home / "A"), consumer(git_sandbox.home / "B")


@pytest.fixture
def lock_facts(monkeypatch: pytest.MonkeyPatch) -> LockFacts:
    """Declare lock owner identities and states; no native process or mutex call."""
    facts = LockFacts()

    def uncontended(_name: str) -> nullcontext[None]:
        return nullcontext()

    monkeypatch.setattr(operation_lock, "current_identity", facts.identity)
    monkeypatch.setattr(operation_lock, "transition_mutex", uncontended)
    return facts


@pytest.fixture
def acceptance_registry(lock_facts: LockFacts) -> dict[str, cli.Handler]:
    """Return the in-process acceptance handlers bound to this case's lock facts."""
    return handlers(lock_facts)

# eof
