r"""Validate the llm-shared Codex skill package.

``validate`` checks the manifest and every ``skills/<name>/SKILL.md`` wrapper:
no BOM, closed front matter limited to ``name``, ``description``, a
``metadata`` mapping and the ``llm_nature: codex`` adapter hint. It uses the
standard library only, so ``llmup`` runs it with the llm-shared Python,
without PyYAML or an isolated ``uv`` environment, and it never writes.

Fix: decoded JSON values go through ``_json_object``, which types an object as
``dict[str, object]`` and returns None for anything else, so strict pyright
sees no partially unknown manifest value.

Fix: Codex now reads the skills through the ``%USERPROFILE%\.agents\skills``
link to this package in the clone, not from an installed plugin cache. The
``bump-version`` command, which rewrote the tracked manifest with a
``+codex.<timestamp>`` cachebuster on every ``llmup``, and the
``marketplace-name`` command, which only the plugin install needed, are gone.
The manifest keeps a fixed version.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import cast

_KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_SEMVER = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?")
_SKILL_KEYS = frozenset({"name", "description", "metadata", "llm_nature"})
_MAX_NAME = 64
_MAX_DESCRIPTION = 1024
_BOM = b"\xef\xbb\xbf"
_FENCE = "---"


def _json_object(value: object) -> dict[str, object] | None:
    """Return a decoded JSON object with typed keys, or None for any other value."""
    return cast("dict[str, object]", value) if isinstance(value, dict) else None


def _scalar(text: str) -> str:
    """Return one YAML scalar written plain, single-quoted or double-quoted."""
    text = text.strip()
    if len(text) > 1 and text[0] == text[-1] == '"':
        try:
            return json.loads(text)
        except ValueError as error:
            message = f"invalid double-quoted value {text}"
            raise ValueError(message) from error
    if len(text) > 1 and text[0] == text[-1] == "'":
        return text[1:-1].replace("''", "'")
    return text


def _entry(line: str, *, nested: bool) -> tuple[str, str]:
    """Split one ``key: value`` line; a nested line needs a value, never a mapping."""
    key, separator, value = (line[2:] if nested else line).partition(":")
    if not separator or not key or key != key.strip() or (nested and not value.strip()):
        message = f"unsupported front matter line {line!r}"
        raise ValueError(message)
    return key, value


def _header_lines(text: str) -> list[str]:
    """Return the lines between the opening --- fence and its closing fence."""
    lines = text.splitlines()
    if not lines or lines[0] != _FENCE or _FENCE not in lines[1:]:
        message = "SKILL.md must start with closed --- front matter"
        raise ValueError(message)
    return lines[1 : lines.index(_FENCE, 1)]


def _frontmatter(text: str) -> dict[str, object]:
    """Parse the closed front matter subset the wrappers use, rejecting the rest.

    Top-level ``key: value`` scalars are supported, and a key without a value
    opens a one-level mapping whose lines are indented by exactly two spaces.
    The next top-level key closes that mapping.
    """
    fields: dict[str, object] = {}
    mapping: dict[str, object] | None = None
    for line in _header_lines(text):
        nested = mapping is not None and line.startswith("  ")
        key, value = _entry(line, nested=nested)
        target = mapping if nested and mapping is not None else fields
        if key in target:
            message = f"duplicate front matter key {key!r}"
            raise ValueError(message)
        if nested:
            target[key] = _scalar(value)
        elif value.strip():
            fields[key], mapping = _scalar(value), None
        else:
            mapping = fields[key] = {}
    return fields


def _name_problems(name: object, folder: str) -> list[str]:
    """Check one hyphen-case skill name against its folder."""
    if not isinstance(name, str) or not _KEBAB.fullmatch(name) or len(name) > _MAX_NAME:
        return [f"name must be hyphen-case, at most {_MAX_NAME} characters"]
    if name != folder:
        return [f"name {name!r} differs from its folder {folder!r}"]
    return []


def _description_problems(description: object) -> list[str]:
    """Check the one-line description Codex shows in its skill registry."""
    if not isinstance(description, str) or not description.strip():
        return ["description must be a non-empty string"]
    if len(description) > _MAX_DESCRIPTION or "<" in description or ">" in description:
        return [f"description must be at most {_MAX_DESCRIPTION} characters, without < or >"]
    return []


def _optional_problems(fields: dict[str, object]) -> list[str]:
    """Check the keys a wrapper may add beyond its name and description."""
    problems = [f"unexpected front matter key {key!r}" for key in sorted(set(fields) - _SKILL_KEYS)]
    if not isinstance(fields.get("metadata", {}), dict):
        problems.append("metadata must be a mapping")
    if fields.get("llm_nature", "codex") != "codex":
        problems.append("llm_nature must be codex in the Codex plugin")
    return problems


def _skill_errors(folder: Path) -> list[str]:
    """Return every problem of one skills/<name>/SKILL.md wrapper."""
    skill = folder / "SKILL.md"
    if not skill.is_file():
        return [f"missing SKILL.md: {skill}"]
    data = skill.read_bytes()
    if data.startswith(_BOM):
        return [f"UTF-8 BOM: {skill}"]
    try:
        fields = _frontmatter(data.decode("utf-8"))
    except UnicodeDecodeError:
        return [f"not UTF-8: {skill}"]
    except ValueError as error:
        problems = [str(error).removeprefix("SKILL.md must start with ")]
    else:
        problems = (
            _name_problems(fields.get("name"), folder.name)
            + _description_problems(fields.get("description"))
            + _optional_problems(fields)
        )
    return [f"{problem}: {skill}" for problem in problems]


def _read_manifest(root: Path) -> dict[str, object]:
    """Load .codex-plugin/plugin.json as one JSON object."""
    manifest = root / ".codex-plugin" / "plugin.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        message = f"unreadable manifest {manifest}: {error}"
        raise ValueError(message) from error
    fields = _json_object(data)
    if fields is None:
        message = f"manifest must be a JSON object: {manifest}"
        raise ValueError(message)
    return fields


def _skills_root(data: dict[str, object], root: Path) -> Path:
    """Resolve the manifest skills path, which must stay inside the package."""
    skills = data.get("skills")
    if not isinstance(skills, str) or not skills.startswith("./"):
        message = "manifest skills must be a ./ relative path"
        raise ValueError(message)
    folder = (root / skills).resolve()
    if not folder.is_relative_to(root):
        message = f"manifest skills must stay inside the plugin root: {skills}"
        raise ValueError(message)
    if not folder.is_dir():
        message = f"manifest skills folder is not a directory: {folder}"
        raise ValueError(message)
    return folder


def _manifest_problems(data: dict[str, object], folder: str) -> list[str]:
    """Check the manifest name against its folder and its semantic version."""
    problems: list[str] = []
    name = data.get("name")
    if not isinstance(name, str) or not _KEBAB.fullmatch(name):
        problems.append("manifest name must be hyphen-case")
    elif name != folder:
        problems.append(f"manifest name {name!r} differs from its folder {folder!r}")
    version = data.get("version")
    if not isinstance(version, str) or not _SEMVER.fullmatch(version):
        problems.append(f"manifest version must be a semantic version, not {version!r}")
    return problems


def validate_package(plugin_root: Path) -> tuple[list[str], int]:
    """Return every package problem and the number of skill folders checked."""
    root = plugin_root.resolve()
    try:
        data = _read_manifest(root)
        skills = _skills_root(data, root)
    except ValueError as error:
        return [str(error)], 0
    errors = _manifest_problems(data, root.name)
    folders = sorted(path for path in skills.iterdir() if path.is_dir())
    if not folders:
        errors.append(f"no skill folder under {skills}")
    for folder in folders:
        errors.extend(_skill_errors(folder))
    return errors, len(folders)


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and run validate, the only command."""
    parser = argparse.ArgumentParser(description="Validate the llm-shared Codex skill package.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate").add_argument("plugin_root", type=Path)
    args = parser.parse_args(argv)
    errors, count = validate_package(args.plugin_root)
    for error in errors:
        sys.stderr.write(f"ERROR: {error}\n")
    if errors:
        return 1
    sys.stdout.write(f"Validated {count} skills in plugin package: {args.plugin_root}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
