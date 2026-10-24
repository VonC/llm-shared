"""Isolate Git targeting while retaining compatible user configuration.

Repository routing, command injection, execution search and output shaping
are separate, explicit policies. Configuration-file selectors remain intact;
their effective scopes and origins are inspected before discovery is trusted.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

# These names are Git's environment spellings, including less common routing
# controls that `git -C` alone cannot neutralize.
_ROUTING = frozenset({
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_IMPLICIT_WORK_TREE", "GIT_REPLACE_REF_BASE", "GIT_NO_REPLACE_OBJECTS",
    "GIT_GRAFT_FILE", "GIT_SHALLOW_FILE", "GIT_QUARANTINE_PATH",
    "GIT_INTERNAL_SUPER_PREFIX", "GIT_PREFIX",
})
_INJECTION = frozenset({"GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT"})
_EXECUTION = frozenset({"GIT_EXEC_PATH", "GIT_TEMPLATE_DIR"})
_OUTPUT = frozenset({
    "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS", "GIT_ICASE_PATHSPECS",
    "GIT_EXTERNAL_DIFF", "GIT_DIFF_OPTS", "GIT_DIFF_PATH_COUNTER",
    "GIT_DIFF_PATH_TOTAL", "GIT_FLUSH", "GIT_PROGRESS_DELAY",
    "GIT_PAGER_IN_USE", "GIT_MERGE_VERBOSITY",
    "GIT_REDIRECT_STDIN", "GIT_REDIRECT_STDOUT", "GIT_REDIRECT_STDERR",
})
_REMOVED = _ROUTING | _INJECTION | _EXECUTION | _OUTPUT
_REMOVED_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_", "GIT_TRACE", "GIT_TEST_")
_MACHINE = {
    "GIT_LITERAL_PATHSPECS": "1", "LC_ALL": "C", "LANG": "C", "LANGUAGE": "C",
    "GIT_PAGER": "", "PAGER": "", "GIT_EDITOR": "false",
    "GIT_SEQUENCE_EDITOR": "false", "EDITOR": "false", "VISUAL": "false",
}
_NONINTERACTIVE = {
    "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "false", "SSH_ASKPASS": "false",
    "GCM_INTERACTIVE": "never", "GCM_GUI_PROMPT": "false",
}
_ROUTING_KEYS = frozenset({"core.worktree", "core.bare", "extensions.worktreeconfig"})


class GitPolicyError(ValueError):
    """Git selection, inherited policy or machine output cannot be trusted."""


@dataclass(frozen=True)
class GitEnvironment:
    """A read-only child environment and safe ignored-input diagnostics."""

    values: Mapping[str, str]
    diagnostics: tuple[str, ...]


@dataclass(frozen=True)
class ConfigEntry:
    """One effective Git value with its original scope, origin and key."""

    scope: str
    origin: str
    key: str
    value: str | None


def controlled_environment(source: Mapping[str, str], *, non_interactive: bool) -> GitEnvironment:
    """Copy caller state without leaking routing or modifying the parent.

    Config selectors (including GIT_CONFIG) are deliberately preserved. Git
    reports a GIT_CONFIG override in command scope, which inspection rejects;
    system/global selectors and includes retain their genuine file scope.
    Diagnostics name ignored inputs without exposing identity or helper secrets.
    """
    overrides = dict(_MACHINE)
    if non_interactive:
        overrides.update(_NONINTERACTIVE)
    child: dict[str, str] = {}
    diagnostics: list[str] = []
    for name, value in source.items():
        normalized = name.upper()
        if normalized in _REMOVED or normalized.startswith(_REMOVED_PREFIXES):
            diagnostics.append(f"Ignored inherited Git input {name}")
        elif normalized in overrides:
            if value != overrides[normalized]:
                diagnostics.append(f"Overrode inherited Git input {name}")
        else:
            child[name] = value
    child.update(overrides)
    return GitEnvironment(MappingProxyType(child), tuple(diagnostics))


def validate_config(output: str) -> tuple[ConfigEntry, ...]:
    """Parse `config --null --show-scope --show-origin --list` and check policy.

    NUL separates scope/origin/value records; the first newline in the value
    record separates key from value. Embedded newlines in a value are data.
    Included files carry Git's reported origin and inherited configuration scope.
    """
    if not output:
        return ()
    fields = output.split("\0")
    if fields[-1] != "" or (len(fields) - 1) % 3:
        msg = "Malformed Git configuration record"
        raise GitPolicyError(msg)
    entries: list[ConfigEntry] = []
    for offset in range(0, len(fields) - 1, 3):
        scope, origin, record = fields[offset:offset + 3]
        entries.append(_validate_entry(scope, origin, record))
    return tuple(entries)


def _validate_entry(scope: str, origin: str, record: str) -> ConfigEntry:
    """Apply the closed routing-key and command-scope policy to one record."""
    key, separator, value = record.partition("\n")
    if not key or not origin or not scope:
        msg = "Malformed Git configuration identity"
        raise GitPolicyError(msg)
    if scope == "command" or (key.lower() in _ROUTING_KEYS and scope not in {"local", "worktree"}):
        msg = f"Rejected Git configuration: {scope} scope, {origin}, {key}"
        raise GitPolicyError(msg)
    return ConfigEntry(scope, origin, key, value if separator else None)


# eof
