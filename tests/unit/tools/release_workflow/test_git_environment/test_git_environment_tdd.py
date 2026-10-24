"""Enumerate supported Git overrides and reject untrusted config scopes."""

from __future__ import annotations

from typing import cast

import pytest

from tools.release_workflow.git_environment import (
    GitPolicyError,
    controlled_environment,
    validate_config,
)

REMOVED = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_IMPLICIT_WORK_TREE",
    "GIT_REPLACE_REF_BASE", "GIT_NO_REPLACE_OBJECTS", "GIT_GRAFT_FILE", "GIT_SHALLOW_FILE",
    "GIT_QUARANTINE_PATH", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0",
    "GIT_EXEC_PATH", "GIT_TEMPLATE_DIR", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS", "GIT_ICASE_PATHSPECS",
    "GIT_EXTERNAL_DIFF", "GIT_DIFF_OPTS", "GIT_TRACE", "GIT_TRACE2_EVENT", "GIT_FLUSH", "GIT_PROGRESS_DELAY",
    "GIT_REDIRECT_STDIN", "GIT_REDIRECT_STDOUT", "GIT_REDIRECT_STDERR",
)
PRESERVED = (
    "GIT_CONFIG_SYSTEM", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG",
    "HOME", "XDG_CONFIG_HOME", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE",
    "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "GIT_COMMITTER_DATE", "EMAIL",
    "GIT_SSH", "GIT_SSH_COMMAND", "SSH_AUTH_SOCK", "GIT_SSL_CAINFO", "GIT_ASKPASS",
)
ROUTING_KEYS = ("core.worktree", "CoRe.BaRe", "extensions.worktreeConfig")


@pytest.mark.parametrize("name", REMOVED)
def test_remove_conflicting_input_without_mutating_parent(name: str) -> None:
    """Each routing/injection/execution/output input is removed and diagnosed."""
    source = {name: "caller-value", "PATH": "absolute-search", "ordinary": "keep"}
    child = controlled_environment(source, non_interactive=False)
    assert name not in child.values
    assert any(name in diagnostic for diagnostic in child.diagnostics)
    assert source[name] == "caller-value"
    assert child.values["ordinary"] == "keep"


@pytest.mark.parametrize("name", PRESERVED)
def test_preserve_config_selection_identity_and_helpers(name: str) -> None:
    """Configuration selection and compatible user settings survive isolation."""
    child = controlled_environment({name: "keep"}, non_interactive=False)
    assert child.values[name] == "keep"
    assert not child.diagnostics


def test_machine_policy_and_noninteractive_prompts() -> None:
    """Explicit output and interaction policy wins case-insensitively."""
    source = {"git_dir": "other", "git_pager": "less", "git_redirect_stderr": "off", "LC_ALL": "fr_FR", "GIT_ASKPASS": "gui"}
    child = controlled_environment(source, non_interactive=True)
    assert not {"git_dir", "git_pager", "git_redirect_stderr"} & child.values.keys()
    expected = {
        "GIT_LITERAL_PATHSPECS": "1", "LC_ALL": "C", "GIT_PAGER": "",
        "GIT_EDITOR": "false", "GIT_SEQUENCE_EDITOR": "false", "GIT_TERMINAL_PROMPT": "0",
        "GIT_ASKPASS": "false", "SSH_ASKPASS": "false", "GCM_INTERACTIVE": "never",
    }
    assert {name: child.values[name] for name in expected} == expected
    assert source["GIT_ASKPASS"] == "gui"
    with pytest.raises(TypeError):
        cast("dict[str, str]", child.values)["PATH"] = "changed"


@pytest.mark.parametrize("key", ROUTING_KEYS)
@pytest.mark.parametrize("scope", ["system", "global", "command", "local", "worktree"])
def test_routing_configuration_scope_matrix(key: str, scope: str) -> None:
    """Only repository-owned routing settings are accepted, including includes."""
    output = f"{scope}\0file:included.cfg\0{key}\nvalue\0"
    if scope in {"local", "worktree"}:
        assert validate_config(output)[0].key == key
    else:
        with pytest.raises(GitPolicyError, match=f"{scope}.*included.cfg.*{key}"):
            validate_config(output)


@pytest.mark.parametrize("key", ["user.name", "credential.helper", "commit.gpgsign", "gpg.program", "core.editor", "color.ui"])
@pytest.mark.parametrize("scope", ["system", "global", "local", "worktree", "command"])
def test_benign_config_and_surviving_command_scope(key: str, scope: str) -> None:
    """Benign values survive; every surviving command-scope setting is rejected."""
    output = f"{scope}\0file:chosen.cfg\0{key}\nvalue\0"
    if scope == "command":
        with pytest.raises(GitPolicyError, match="command"):
            validate_config(output)
    else:
        entry = validate_config(output)[0]
        assert (entry.scope, entry.origin, entry.value) == (scope, "file:chosen.cfg", "value")


@pytest.mark.parametrize("output", ["local\0file:a\0key\nvalue", "local\0file:a\0", "local\0file:a\0\0"])
def test_malformed_config_cannot_be_trusted(output: str) -> None:
    """A truncated or nameless machine record is a preflight error."""
    with pytest.raises(GitPolicyError, match="configuration"):
        validate_config(output)


def test_empty_config_and_boolean_values() -> None:
    """Empty configuration and valueless booleans are valid native formats."""
    assert validate_config("") == ()
    assert validate_config("local\0file:a\0feature.enabled\0")[0].value is None


# eof
