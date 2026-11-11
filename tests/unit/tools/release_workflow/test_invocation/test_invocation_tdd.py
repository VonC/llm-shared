"""Invocation policy composes production services with declared repository facts.

Step 1 of v0.14.0 version-sources: the parsed operation tokens are copied into
the context, and the batch-character rule still covers every one of them.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import invocation
from tools.release_workflow.runtime_identity import RuntimeIdentity

pytestmark = pytest.mark.usefixtures("read_only_git")

if TYPE_CHECKING:
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox


def context(sandbox: GitSandbox, request: invocation.InvocationRequest, *, entry: str = "explicit-native", **environment: str) -> invocation.InvocationContext:
    """Compose real project services against independent minimal repositories."""
    return invocation.create_context(
        request, runtime=RuntimeIdentity(sandbox.home, "venvs/prepared"),
        entry_kind=entry, original_argv=("probe",), original_cwd=sandbox.home / "B" / "sub",
        environment=dict(sandbox.environment, **environment), stdin_console=False,
    )


def test_fixed_context(git_sandbox: GitSandbox) -> None:
    """Selectors choose B, warn about A and remove inherited location variables."""
    root = git_sandbox.home / "B"
    value = context(git_sandbox, invocation.InvocationRequest(project_root_env="SELECTED"),
                    SELECTED=str(root), PRJ_DIR=str(git_sandbox.home / "A"),
                    VERSION_TXT_FILE="foreign", PRJ_DIR_NAME="foreign")
    assert value.project.root == root.resolve()
    assert (value.project_name, value.root_windows, value.root_posix) == ("B", str(root.resolve()), root.resolve().as_posix())
    assert (value.version_file, value.pom_file, value.package_file, value.changelog_header, value.dev_workflow) == (
        root / "version.txt", root / "pom.xml", root / "package.json", root / "changelog-header.md", root / "tools/dev_workflow",
    )
    assert value.non_interactive
    assert not (root / ".reviews").exists()
    assert any(str(root) in warning and str(git_sandbox.home / "A") in warning for warning in value.diagnostics)
    assert not {"PRJ_DIR", "PRJ_DIR_NAME", "VERSION_TXT_FILE"}.intersection(value.git.environment.values)
    with pytest.raises(FrozenInstanceError):
        setattr(value, "project_name", "wrong")


@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch"])
def test_explicit_root_required(git_sandbox: GitSandbox, entry: str) -> None:
    """Valid cwd and inherited PRJ_DIR never supply an explicit root."""
    with pytest.raises(ValueError, match="explicit project root"):
        context(git_sandbox, invocation.InvocationRequest(), entry=entry, PRJ_DIR=str(git_sandbox.home / "A"))


@pytest.mark.usefixtures("read_only_git")
def test_alias_discovers_from_original_cwd(git_sandbox: GitSandbox) -> None:
    """Alias entry alone discovers B from its subfolder."""
    value = context(git_sandbox, invocation.InvocationRequest(), entry="alias-batch")
    assert value.project.root == (git_sandbox.home / "B").resolve()


@pytest.mark.parametrize("supplied", [None, ""])
def test_missing_selector(git_sandbox: GitSandbox, supplied: str | None) -> None:
    """A named but missing or empty selector fails with provenance."""
    environment = {} if supplied is None else {"SELECTED": supplied}
    with pytest.raises(ValueError, match="SELECTED"):
        context(git_sandbox, invocation.InvocationRequest(project_root_env="SELECTED"), **environment)


def test_conflicting_roots(git_sandbox: GitSandbox) -> None:
    """Even equivalent sources cannot silently override one another."""
    with pytest.raises(ValueError, match="Conflicting"):
        context(git_sandbox, invocation.InvocationRequest(project_root="B", project_root_env="SELECTED"), SELECTED="B")


def test_input_locator_uses_root(git_sandbox: GitSandbox) -> None:
    """Input selectors resolve relative to the root, retaining arbitrary text."""
    value = context(git_sandbox, invocation.InvocationRequest(project_root="..", input_file_env="PAYLOAD"), PAYLOAD="title %^!&.txt")
    assert value.input_file == (git_sandbox.home / "B" / "title %^!&.txt").resolve()


def test_invalid_selector_root_names_value(git_sandbox: GitSandbox) -> None:
    """Physical-root rejection retains the selected variable and its value."""
    with pytest.raises(ValueError, match=r"SELECTED.*does-not-exist"):
        context(git_sandbox, invocation.InvocationRequest(project_root_env="SELECTED"), SELECTED="does-not-exist")


@pytest.mark.parametrize("token", ["a%b", "a^b", "a!b", 'a"b'])
def test_batch_grammar_only(token: str) -> None:
    """Surviving forbidden characters fail only at batch-origin boundaries."""
    invocation.validate_arguments("explicit-native", (token,))
    with pytest.raises(ValueError, match="batch"):
        invocation.validate_arguments("explicit-batch", (token,))


def test_operation_tokens_reach_context(git_sandbox: GitSandbox) -> None:
    """The context carries the parsed operation tokens unchanged."""
    value = context(git_sandbox, invocation.InvocationRequest(project_root="..", operation=("set", "0.14.0")))
    assert value.operation == ("set", "0.14.0")
    assert context(git_sandbox, invocation.InvocationRequest(project_root="..")).operation == ()


@pytest.mark.parametrize("token", ["0.14.0%", "0.14.0^", "0.14.0!", '0.14.0"'])
def test_batch_rule_covers_operation_tokens(git_sandbox: GitSandbox, token: str) -> None:
    """A batch caller cannot pass an unsafe character inside an operation token."""
    with pytest.raises(ValueError, match="batch"):
        invocation.create_context(
            invocation.InvocationRequest(project_root="..", operation=("set", token)),
            runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared"), entry_kind="explicit-batch",
            original_argv=("versions", "set", token), original_cwd=git_sandbox.home / "B" / "sub",
            environment=dict(git_sandbox.environment), stdin_console=False,
        )


@pytest.mark.parametrize("console", [False, True])
@pytest.mark.parametrize("requested", [False, True])
@pytest.mark.usefixtures("read_only_git")
def test_interaction_policy(git_sandbox: GitSandbox, *, console: bool, requested: bool) -> None:
    """Redirected stdin cannot be made interactive by omitting the flag."""
    value = invocation.create_context(
        invocation.InvocationRequest(project_root=str(git_sandbox.home / "B"), non_interactive=requested),
        runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared"), entry_kind="explicit-native",
        original_argv=(), original_cwd=git_sandbox.home, environment=git_sandbox.environment, stdin_console=console,
    )
    assert value.non_interactive == (requested or not console)


@pytest.mark.usefixtures("read_only_git")
def test_selector_case(git_sandbox: GitSandbox) -> None:
    """Named variables retain Windows case-insensitive semantics in a frozen map."""
    value = context(git_sandbox, invocation.InvocationRequest(project_root_env="selected"), SELECTED=str(git_sandbox.home / "B"))
    assert value.project.root == (git_sandbox.home / "B").resolve()


@pytest.mark.parametrize("requested_input", [
    invocation.InvocationRequest(project_root="..", input_file=""),
    invocation.InvocationRequest(project_root="..", input_file="one", input_file_env="FILE"),
    invocation.InvocationRequest(project_root="..", input_file="one", text="two"),
    invocation.InvocationRequest(project_root="..", input_stdin=True, text="two"),
    invocation.InvocationRequest(project_root_env="invalid-name"),
])
@pytest.mark.usefixtures("read_only_git")
def test_invalid_input_combinations(requested_input: invocation.InvocationRequest, git_sandbox: GitSandbox) -> None:
    """Empty paths and multiple sources never choose a silent precedence."""
    with pytest.raises(ValueError, match=r"Empty|Conflicting|Invalid"):
        context(git_sandbox, requested_input)


def test_unknown_origin() -> None:
    """In-process callers cannot invent another discovery mode."""
    with pytest.raises(ValueError, match="entry kind"):
        invocation.validate_arguments("unknown", ())


@pytest.mark.usefixtures("read_only_git")
def test_legacy_equivalent_root(git_sandbox: GitSandbox) -> None:
    """Equivalent relative legacy spelling requires no stale-root warning."""
    value = context(git_sandbox, invocation.InvocationRequest(project_root=".."), PRJ_DIR="..")
    assert not any("stale PRJ_DIR" in diagnostic for diagnostic in value.diagnostics)


@pytest.mark.parametrize("inherited", [None, ""])
@pytest.mark.usefixtures("read_only_git")
def test_no_legacy_root(git_sandbox: GitSandbox, inherited: str | None) -> None:
    """Explicit project identity needs no inherited root or stale-root warning."""
    environment = {key: value for key, value in git_sandbox.environment.items() if key.upper() != "PRJ_DIR"}
    if inherited is not None:
        environment["PRJ_DIR"] = inherited
    root = git_sandbox.home / "B"
    value = invocation.create_context(
        invocation.InvocationRequest(project_root=str(root)), runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared"),
        entry_kind="explicit-native", original_argv=(), original_cwd=root / "sub",
        environment=environment, stdin_console=False,
    )
    assert value.project.root == root.resolve()
    assert not any("PRJ_DIR" in diagnostic for diagnostic in value.diagnostics)


@pytest.mark.usefixtures("read_only_git")
def test_absolute_input_path(git_sandbox: GitSandbox) -> None:
    """Read-only input files can be explicitly located outside the project."""
    path = git_sandbox.home / "input.txt"
    value = context(git_sandbox, invocation.InvocationRequest(project_root="..", input_file=str(path)))
    assert value.input_file == path


@pytest.mark.usefixtures("read_only_git")
def test_alias_outside_git(git_sandbox: GitSandbox) -> None:
    """Alias discovery outside a worktree cannot fall back to a valid PRJ_DIR."""
    with pytest.raises(ValueError, match="project root"):
        invocation.create_context(
            invocation.InvocationRequest(), runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared"),
            entry_kind="alias-batch", original_argv=(), original_cwd=git_sandbox.home,
            environment=dict(git_sandbox.environment, PRJ_DIR=str(git_sandbox.home / "B")), stdin_console=True,
        )

# eof
