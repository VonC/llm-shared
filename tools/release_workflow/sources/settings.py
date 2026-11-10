"""Validate and read the version domain of `.release.ini`.

Step 3 of v0.14.0 version-sources. `[source:<name>]` either overrides the form
of a registered built-in adapter, within that adapter's forms, for every
participating root (design decision Q14), or declares a pattern source with
`file`, `pattern` (exactly one capture group) and `form`; `anchor` and
`pattern` are reserved names. `[component:<id>]` declares one participating
root (design decision Q13): a managed directory below the project root, never
the root itself, never under an excluded directory name and never declared
twice. Item 1's loader has already rejected unknown sections and keys and
authorized every managed path. The validator reads no file, so detection
checks that declared files and directories exist. The project root is the
directory of the `.release.ini` the loader read: it is the only root the
validator's mappings carry, and `read_settings` uses the same one. Step 5
adds `VersionSettings.participant`, backed by an index of the participating
roots built once per settings value.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import cached_property
from types import MappingProxyType
from typing import TYPE_CHECKING, cast

from tools.release_workflow.sources import ADAPTERS, anchor, pattern
from tools.release_workflow.sources.model import (
    Form,
    PatternDeclaration,
    SourceError,
    participant_names,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from pathlib import Path

    from tools.release_workflow.configuration import Configuration
    from tools.release_workflow.schemas import ConfigSections, ConfigValue
    from tools.release_workflow.sources.model import Adapter

# Shared with candidate filtering; changing it is a change to llm-shared, not a project setting.
EXCLUDED_DIRECTORIES = frozenset({"node_modules", "venvs", ".venv", ".git", "target", "vendor", "sample", "samples", "example", "examples"})
_RESERVED = frozenset({anchor.ADAPTER.name, pattern.ADAPTER.name})
_SOURCE = "source:"
_COMPONENT = "component:"
_PATTERN_KEYS = ("file", "pattern", "form")


class SettingsError(ValueError):
    """An invalid version declaration: a configuration failure, status 2."""

    exit_code = 2


@dataclass(frozen=True)
class VersionSettings:
    """The validated version domain: form overrides, pattern sources and component roots.

    Step 5 adds `participant`: the participating roots are indexed once per
    settings value, so the python adapter names a local link's destination in
    one lookup.
    """

    project_root: Path
    forms: Mapping[str, Form]
    patterns: tuple[PatternDeclaration, ...]
    components: Mapping[str, Path]

    @cached_property
    def _participants(self) -> dict[str, str]:
        """Index the project root and the component roots once."""
        return participant_names(self.project_root, self.components)

    def participant(self, path: Path) -> str | None:
        """Name the participating root a physical path is, or return `None`."""
        return self._participants.get(os.path.normcase(str(path)))


@dataclass
class _Declarations:
    """Declarations gathered in one pass over the sections, in declaration order."""

    forms: dict[str, Form] = field(default_factory=dict[str, Form])
    patterns: list[PatternDeclaration] = field(default_factory=list[PatternDeclaration])
    components: dict[str, Path] = field(default_factory=dict[str, "Path"])
    roots: dict[str, str] = field(default_factory=dict[str, str])


def excluded_directory(parts: Iterable[str]) -> str | None:
    """Return the first directory name that is excluded, compared by the filesystem's case rules."""
    return next((part for part in parts if os.path.normcase(part) in EXCLUDED_DIRECTORIES), None)


def _form(name: str, value: ConfigValue, adapter: Adapter) -> Form:
    """Read a configured form and require one the adapter allows."""
    try:
        form = Form.parse(value.raw)
    except SourceError as exc:
        msg = f"[{name}] form={value.raw!r}: {exc}"
        raise SettingsError(msg) from exc
    if form not in adapter.forms:
        msg = f"[{name}] form={value.raw!r}: {adapter.name} allows only {', '.join(sorted(adapter.forms))}"
        raise SettingsError(msg)
    return form


def _pattern_source(name: str, values: Mapping[str, ConfigValue]) -> PatternDeclaration:
    """Require the three keys, one capture group and an allowed form."""
    for key in _PATTERN_KEYS:
        if key not in values:
            msg = f"[{name}] {key}: a pattern source requires file, pattern and form"
            raise SettingsError(msg)
    raw = values["pattern"].raw
    try:
        expression = re.compile(raw, re.MULTILINE)
    except re.error as exc:
        msg = f"[{name}] pattern={raw!r}: does not compile: {exc}"
        raise SettingsError(msg) from exc
    if expression.groups != 1:
        msg = f"[{name}] pattern={raw!r}: needs exactly one capture group, found {expression.groups}"
        raise SettingsError(msg)
    form = _form(name, values["form"], pattern.ADAPTER)
    return PatternDeclaration(name.removeprefix(_SOURCE), cast("Path", values["file"].value), expression, form)


def _source(declared: _Declarations, name: str, values: Mapping[str, ConfigValue], built_in: Mapping[str, Adapter]) -> None:
    """Record a built-in form override or a pattern source; reject reserved names."""
    instance = name.removeprefix(_SOURCE)
    if instance in _RESERVED:
        msg = f"[{name}]: {instance} is reserved for the built-in {instance} adapter and cannot be declared; give the pattern source another name"
        raise SettingsError(msg)
    adapter = built_in.get(instance)
    if adapter is None:
        declared.patterns.append(_pattern_source(name, values))
        return
    for key, value in values.items():
        if key != "form":
            msg = f"[{name}] {key}={value.raw!r}: the built-in {instance} source accepts only form"
            raise SettingsError(msg)
    if "form" in values:
        declared.forms[instance] = _form(name, values["form"], adapter)


def _component(declared: _Declarations, name: str, values: Mapping[str, ConfigValue]) -> None:
    """Record a component root below the project root, outside excluded names, declared once."""
    value = values["root"]
    root = cast("Path", value.value)
    project_root = value.source.parent
    location = f"[{name}] root={value.raw!r}"
    if root == project_root:
        msg = f"{location}: a component root is a directory below the project root, not the project root itself"
        raise SettingsError(msg)
    excluded = excluded_directory(root.relative_to(project_root).parts)
    if excluded is not None:
        msg = f"{location}: a component root cannot lie under the excluded directory {excluded}"
        raise SettingsError(msg)
    key = os.path.normcase(str(root))
    previous = declared.roots.get(key)
    if previous is not None:
        msg = f"{location}: names the same directory as [{previous}]"
        raise SettingsError(msg)
    declared.roots[key] = name
    declared.components[name.removeprefix(_COMPONENT)] = root


def _declarations(sections: ConfigSections, adapters: Sequence[Adapter]) -> _Declarations:
    """Apply the per-instance rules to every version section in one pass."""
    built_in = {adapter.name: adapter for adapter in adapters if adapter.name not in _RESERVED}
    declared = _Declarations()
    for name, values in sections.items():
        if name.startswith(_SOURCE):
            _source(declared, name, values, built_in)
        elif name.startswith(_COMPONENT):
            _component(declared, name, values)
    return declared


def validate_settings(sections: ConfigSections, adapters: Sequence[Adapter] = ADAPTERS) -> None:
    """Validate the version sections, with built-in forms read from the registered adapters."""
    _declarations(sections, adapters)


def read_settings(configuration: Configuration, adapters: Sequence[Adapter] = ADAPTERS) -> VersionSettings:
    """Return the validated version settings of a loaded configuration."""
    declared = _declarations(configuration.sections, adapters)
    return VersionSettings(configuration.source.parent, MappingProxyType(declared.forms), tuple(declared.patterns),
                           MappingProxyType(declared.components))


# eof
