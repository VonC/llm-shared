"""Read optional project INI once, strictly and without artifact preparation.

Parsing and the stable tooling minimum precede domain validation. All shipped
owners validate the resulting immutable mappings, even outside an operation's
immediate scope. Invalid declarations never fall back to domain defaults.
"""

from __future__ import annotations

import configparser
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from tools.release_workflow.paths import (
    ProjectIdentity,
    ProjectPathError,
    authorize_path,
)
from tools.release_workflow.schemas import ConfigValue, SchemaRegistry

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from tools.release_workflow.schemas import (
        ConfigSections,
        RegisteredSection,
        ValueRule,
    )


class ConfigurationError(ValueError):
    """Invalid project configuration is an input/preflight failure, status 2."""

    exit_code = 2


@dataclass(frozen=True)
class Configuration:
    """Validated values retain immutable section mappings and source provenance."""

    source: Path
    sections: ConfigSections


def _read(source: Path) -> str:
    """Only a truly absent directory entry permits defaults, never a broken link."""
    try:
        return source.read_text(encoding="utf-8-sig")
    except FileNotFoundError as exc:
        try:
            source.lstat()
        except FileNotFoundError:
            return ""
        msg = f"Cannot read configuration {source}: {exc}"
        raise ConfigurationError(msg) from exc


def _parse(source: Path) -> dict[str, dict[str, str]]:
    """Disable interpolation, inline comments and implicit DEFAULT inheritance."""
    parser = configparser.ConfigParser(interpolation=None, strict=True, default_section="", empty_lines_in_values=False)
    try:
        parser.read_string(_read(source), source=str(source))
    except (OSError, UnicodeError, configparser.Error) as exc:
        msg = f"Cannot read configuration {source}: {exc}"
        raise ConfigurationError(msg) from exc
    return {name: dict(parser.items(name, raw=True)) for name in parser.sections()}


def _minimum(source: Path, sections: Mapping[str, Mapping[str, str]]) -> None:
    """Fail closed until the compatibility owner supplies version comparison."""
    value = sections.get("tooling", {}).get("minimum-version")
    if value is None:
        return
    location = f"{source} [tooling] minimum-version={value!r}"
    if re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value) is None:
        msg = f"{location}: expected release MAJOR.MINOR.PATCH without a v prefix"
        raise ConfigurationError(msg)
    msg = f"{location}: tooling compatibility comparison is unavailable; use tooling that supports this minimum-version declaration"
    raise ConfigurationError(msg)


def _value(identity: ProjectIdentity, source: Path, section: str, rule: ValueRule, supplied: str | None) -> ConfigValue | None:
    """Validate supplied text or its owned default, keeping diagnostic context."""
    raw = rule.default if supplied is None else supplied
    location = f"{source} [{section}] {rule.key}"
    if raw is None:
        if rule.required:
            msg = f"{location}: required value is missing and has no default"
            raise ConfigurationError(msg)
        return None
    if rule.path_role == "managed" and not raw:
        msg = f"{location}={raw!r}: managed path must not be empty"
        raise ConfigurationError(msg)
    try:
        if rule.path_role == "managed":
            value = authorize_path(identity, raw)
        else:
            value = rule.parse(raw)
    except (ValueError, OSError, RuntimeError) as exc:
        msg = f"{location}={raw!r}: {exc}"
        raise ConfigurationError(msg) from exc
    return ConfigValue(source, section, rule.key, raw, value, supplied is None)


def _section(identity: ProjectIdentity, source: Path, name: str, owner: RegisteredSection, declared: Mapping[str, str]) -> Mapping[str, ConfigValue]:
    """Check every declaration then apply each rule once, including defaults."""
    instance = name[len(owner.definition.name):]
    if owner.definition.family and instance != instance.strip():
        msg = f"Invalid configuration section: {source} [{name}]: family instance must not have leading or trailing whitespace"
        raise ConfigurationError(msg)
    for key, raw in declared.items():
        if key not in owner.rules:
            msg = f"Unknown configuration key: {source} [{name}] {key}={raw!r}"
            raise ConfigurationError(msg)
    values: dict[str, ConfigValue] = {}
    for key, rule in owner.rules.items():
        value = _value(identity, source, name, rule, declared.get(key))
        if value is not None:
            values[key] = value
    return MappingProxyType(values)


def load_configuration(identity: ProjectIdentity, registry: SchemaRegistry | None = None) -> Configuration:
    """Load only the selected root's declaration and validate every shipped owner.

    No operation selector is accepted: unrelated declarations must also pass.
    This function creates no file or directory and performs no migration.
    """
    source = identity.root / ".release.ini"
    try:
        authorize_path(identity, source)
    except ProjectPathError as exc:
        msg = f"Cannot read configuration {source}: {exc}"
        raise ConfigurationError(msg) from exc
    declarations = _parse(source)
    _minimum(source, declarations)
    registry = SchemaRegistry() if registry is None else registry
    owners = dict(registry.fixed)
    for name in declarations:
        owner = registry.section(name)
        if owner is None:
            msg = f"Unknown configuration section: {source} [{name}]"
            raise ConfigurationError(msg)
        owners[name] = owner
    values = {name: _section(identity, source, name, owner, declarations.get(name, {})) for name, owner in owners.items()}
    sections: ConfigSections = MappingProxyType(values)
    for schema in registry.schemas:
        if schema.validate is not None:
            try:
                schema.validate(sections)
            except ValueError as exc:
                msg = f"{source}: domain {schema.name}: {exc}"
                raise ConfigurationError(msg) from exc
    return Configuration(source, sections)


# eof
