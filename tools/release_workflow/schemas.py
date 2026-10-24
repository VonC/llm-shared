"""Compose shipped domain schemas with linear, indexed ownership checks.

Domain owners supply value converters, defaults and cross-section validators.
The foundation imports no consumer code and discovers no schema files. A trie
rejects overlapping fixed/family ownership without pairwise prefix scans.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pathlib import Path


class SchemaError(ValueError):
    """Shipped schema composition is incomplete or ambiguous before dispatch."""

    exit_code = 2


@dataclass(frozen=True)
class ValueRule:
    """One key's conversion, optional textual default and managed-path role.

    Converters and validators are trusted shipped code, never project inputs.
    Managed paths retain their original text and resolve through the common
    physical boundary; a custom converter cannot replace that authorization.
    """

    key: str
    parse: Callable[[str], object] = str
    default: str | None = None
    required: bool = False
    path_role: Literal["managed"] | None = None


@dataclass(frozen=True)
class SectionSchema:
    """A fixed section or nonempty-instance family claimed by one domain."""

    name: str
    rules: tuple[ValueRule, ...]
    family: bool = False


@dataclass(frozen=True)
class ConfigValue:
    """Retain source and original text alongside a validated value or default."""

    source: Path
    section: str
    key: str
    raw: str
    value: object
    defaulted: bool


type ConfigSections = Mapping[str, Mapping[str, ConfigValue]]


@dataclass(frozen=True)
class DomainSchema:
    """Shipped owner of declarations and optional whole-configuration checks."""

    name: str
    sections: tuple[SectionSchema, ...]
    validate: Callable[[ConfigSections], None] | None = None


@dataclass(frozen=True)
class RegisteredSection:
    """Indexed rules and ownership retained once for every section definition."""

    domain: str
    definition: SectionSchema
    rules: Mapping[str, ValueRule]


@dataclass
class _OwnershipNode:
    """A prefix node counts claims below it to reject overlap in one traversal."""

    children: dict[str, _OwnershipNode] = field(default_factory=dict[str, "_OwnershipNode"])
    exact: RegisteredSection | None = None
    family: RegisteredSection | None = None
    claims: int = 0

    def insert(self, section: RegisteredSection) -> None:
        """Reject duplicate fixed names and all overlapping family claims."""
        node = self
        ancestors: list[_OwnershipNode] = [node]
        for character in section.definition.name:
            if node.family is not None:
                self._conflict(section)
            node = node.children.setdefault(character, _OwnershipNode())
            ancestors.append(node)
        if node.exact is not None or node.family is not None or (section.definition.family and node.claims):
            self._conflict(section)
        if section.definition.family:
            node.family = section
        else:
            node.exact = section
        for ancestor in ancestors:
            ancestor.claims += 1

    @staticmethod
    def _conflict(section: RegisteredSection) -> None:
        """Describe the conflicting source declaration without inspecting files."""
        msg = f"Conflicting section ownership: {section.domain} [{section.definition.name}]"
        raise SchemaError(msg)

    def find(self, name: str) -> RegisteredSection | None:
        """Look up a section in time proportional only to its own name length."""
        node = self
        for character in name:
            if node.family is not None:
                return node.family
            child = node.children.get(character)
            if child is None:
                return None
            node = child
        return node.exact


TOOLING_SCHEMA = DomainSchema("tooling", (SectionSchema("tooling", (ValueRule("minimum-version"),)),))
SHIPPED_SCHEMAS = (TOOLING_SCHEMA,)


def _validate_section(domain: str, section: SectionSchema) -> None:
    """Reject names that INI would normalize or treat as structural syntax."""
    if not section.name or section.name != section.name.strip() or section.name == "DEFAULT" or any(character in section.name for character in "[]\r\n"):
        msg = f"Invalid section declaration in domain {domain}: {section.name!r}"
        raise SchemaError(msg)


def _rules(domain: str, section: SectionSchema) -> RegisteredSection:
    """Reject malformed declarations and index keys without normalization loss."""
    _validate_section(domain, section)
    rules: dict[str, ValueRule] = {}
    for rule in section.rules:
        if not re.fullmatch(r"[a-z][a-z0-9-]*", rule.key) or rule.key in rules:
            msg = f"Invalid or duplicate key in [{section.name}]: {rule.key!r}"
            raise SchemaError(msg)
        if rule.path_role not in (None, "managed") or (rule.path_role is not None and rule.parse is not str):
            msg = f"Invalid path role/converter for [{section.name}] {rule.key}"
            raise SchemaError(msg)
        rules[rule.key] = rule
    return RegisteredSection(domain, section, MappingProxyType(rules))


def _complete(schemas: tuple[DomainSchema, ...], shipped: tuple[DomainSchema, ...]) -> None:
    """Require one owner per domain and every exact shipped source declaration."""
    names: set[str] = set()
    for schema in schemas:
        if not schema.name or schema.name in names:
            msg = f"Invalid or duplicate domain owner: {schema.name!r}"
            raise SchemaError(msg)
        names.add(schema.name)
    if len(shipped) != len(schemas) or {id(schema) for schema in shipped} != {id(schema) for schema in schemas}:
        msg = "Registry does not match the complete shipped schema declarations"
        raise SchemaError(msg)


class SchemaRegistry:
    """Validate explicit source composition before accepting project declarations.

    The shipped tuple is the completeness manifest. Production uses the module
    constants; in-process tests may supply a synthetic manifest. Neither tuple
    can be selected from project configuration or dynamic plugin imports.
    """

    def __init__(self, schemas: tuple[DomainSchema, ...] = SHIPPED_SCHEMAS, *, shipped: tuple[DomainSchema, ...] = SHIPPED_SCHEMAS) -> None:
        """Check domain identity, manifest completeness and indexed ownership."""
        _complete(schemas, shipped)
        self.schemas = schemas
        self._ownership = _OwnershipNode()
        fixed: dict[str, RegisteredSection] = {}
        for schema in schemas:
            for definition in schema.sections:
                section = _rules(schema.name, definition)
                self._ownership.insert(section)
                if not definition.family:
                    fixed[definition.name] = section
        self.fixed: Mapping[str, RegisteredSection] = MappingProxyType(fixed)

    def section(self, name: str) -> RegisteredSection | None:
        """Resolve fixed or instantiated family ownership without a schema scan."""
        return self._ownership.find(name)


# eof
