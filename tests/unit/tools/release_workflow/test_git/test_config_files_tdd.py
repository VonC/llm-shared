"""Real Git config selectors/includes retain scopes and benign helpers.

Keep the shared repository template on one worker with the physical-path
matrix, so parallel collection never multiplies native Git fixture setup.
Observe validation's real config inspection instead of repeating its subprocess.
Routing fixtures retain real native results; setup/total time stays observable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.release_workflow.git_environment import GitPolicyError
from tools.release_workflow.paths import ProjectPathError, validate_project

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.git_environment import ConfigEntry
    from tools.release_workflow.paths import ProjectIdentity

pytestmark = [pytest.mark.timeout(10), pytest.mark.xdist_group("release_git")]


@pytest.mark.parametrize(("selector", "scope"), [("GIT_CONFIG_GLOBAL", "global"), ("GIT_CONFIG_SYSTEM", "system")])
@pytest.mark.parametrize("routing", [("core", "worktree", "../A"), ("core", "bare", "true"), ("extensions", "worktreeConfig", "true")])
def test_external_routing_include_is_rejected(scope: str, routing: tuple[str, str, str], external_routing_rejection: pytest.ExceptionInfo[ProjectPathError]) -> None:
    """Actual selected files/includes report their origin before discovery."""
    section, key, _value = routing
    message = str(external_routing_rejection.value)
    assert scope in message
    assert "included.cfg" in message
    assert f"{section}.{key}".lower() in message.lower()


def test_selected_files_preserve_identity_signing_and_credentials(git_sandbox: GitSandbox) -> None:
    """Real file configuration survives with the selected origin and scope."""
    selected = git_sandbox.home / "selected.cfg"
    included = git_sandbox.home / "benign.cfg"
    selected.write_text("[include]\n path = benign.cfg\n", encoding="utf-8")
    included.write_text("[user]\n name = Release User\n signingkey = test-key\n[commit]\n gpgsign = true\n[credential]\n helper = fixture-helper\n[gpg]\n program = fixture-signer\n", encoding="utf-8")
    git = git_sandbox.context(GIT_CONFIG_GLOBAL=str(selected), GIT_AUTHOR_NAME="Preserved Author")
    entries = {entry.key: entry for entry in git.inspect_config(cwd=git_sandbox.home / "B")}
    expected = {"user.name": "Release User", "user.signingkey": "test-key", "commit.gpgsign": "true", "credential.helper": "fixture-helper", "gpg.program": "fixture-signer"}
    assert {key: entries[key].value for key in expected} == expected
    assert all(entries[key].scope == "global" and "benign.cfg" in entries[key].origin for key in expected)
    assert git.environment.values["GIT_AUTHOR_NAME"] == "Preserved Author"


@pytest.mark.parametrize("content", ["", "[user]\n name = Benign\n"])
def test_config_selector_cannot_hide_repository_config(content: str, git_sandbox: GitSandbox) -> None:
    """Git's command-scope GIT_CONFIG selector is preserved then rejected."""
    selected = git_sandbox.home / "override.cfg"
    selected.write_text(content, encoding="utf-8")
    git = git_sandbox.context(GIT_CONFIG=str(selected))
    with pytest.raises(GitPolicyError, match="command"):
        git.inspect_config(cwd=git_sandbox.home / "B")


def test_legacy_config_encoding_cannot_hide_external_routing(git_sandbox: GitSandbox) -> None:
    """A cp1252 value cannot drop all records and bypass the origin policy."""
    selected = git_sandbox.home / "legacy.cfg"
    selected.write_bytes(b"[user]\n name = Jos\xe9\n[core]\n worktree = ../A\n")
    git = git_sandbox.context(GIT_CONFIG_GLOBAL=str(selected))
    with pytest.raises(ProjectPathError, match=r"global.*legacy\.cfg.*core\.worktree"):
        validate_project(git_sandbox.home / "B", git)


def test_legacy_benign_config_value_is_preserved(git_sandbox: GitSandbox) -> None:
    """Lossless decoding preserves legacy values without discarding records."""
    selected = git_sandbox.home / "legacy.cfg"
    selected.write_bytes(b"[user]\n name = Jos\xe9\n")
    git = git_sandbox.context(GIT_CONFIG_GLOBAL=str(selected))
    entries = git.inspect_config(cwd=git_sandbox.home / "B")
    name = next(entry for entry in entries if entry.key == "user.name")
    assert name.value is not None
    assert name.value.encode("utf-8", errors="surrogateescape") == b"Jos\xe9"
    assert name.scope == "global"


def test_repository_owned_routing_is_accepted(repository_routing_result: tuple[Path, ProjectIdentity, tuple[ConfigEntry, ...]]) -> None:
    """Real local/worktree routing keys remain valid for the chosen repository."""
    root, identity, entries = repository_routing_result
    assert identity.root.samefile(root)
    assert any(entry.scope == "worktree" for entry in entries)


# eof
