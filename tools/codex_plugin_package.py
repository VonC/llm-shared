r"""Validate, version and locate the llm-shared Codex plugin package.

These commands replace the plugin-creator helper scripts that ``llmup`` used to
call from ``%USERPROFILE%\.codex\skills\.system\plugin-creator\scripts``.
Codex no longer installs them there, so ``llmup`` stopped before reinstalling
the plugin. They use the standard library only, so the launcher runs them with
the llm-shared Python, without PyYAML or an isolated ``uv`` environment:

- ``validate`` checks the manifest and every ``skills/<name>/SKILL.md``
  wrapper: no BOM, closed front matter limited to ``name``, ``description``,
  a ``metadata`` mapping and the ``llm_nature: codex`` adapter hint.
- ``bump-version`` replaces the manifest ``+codex.<cachebuster>`` suffix with
  a newer timestamp, so Codex installs a fresh cache copy.
- ``marketplace-name`` prints the personal marketplace name once it lists the
  plugin.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_SEMVER = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?")
_MARKETPLACE = re.compile(r"[A-Za-z0-9_.-]+")
_VERSION_FIELD = re.compile(rb'("version"\s*:\s*)"([^"\\]*)"')
_SKILL_KEYS = frozenset({"name", "description", "metadata", "llm_nature"})
_MAX_NAME = 64
_MAX_DESCRIPTION = 1024
_BOM = b"\xef\xbb\xbf"
_FENCE = "---"


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
    if not isinstance(data, dict):
        message = f"manifest must be a JSON object: {manifest}"
        raise ValueError(message)  # noqa: TRY004 - one error type for every manifest problem
    return data


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
    problems = []
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


def bump_version(plugin_root: Path, now: datetime | None = None) -> str:
    """Write a newer +codex.<timestamp> suffix, keeping every other manifest byte."""
    manifest = plugin_root / ".codex-plugin" / "plugin.json"
    content = manifest.read_bytes()
    matches = _VERSION_FIELD.findall(content)
    if len(matches) != 1:
        message = f"expected exactly one version field in {manifest}"
        raise ValueError(message)
    base, _, build = matches[0][1].decode("utf-8").partition("+")
    stamp = int((now or datetime.now(UTC)).strftime("%Y%m%d%H%M%S"))
    previous = build.removeprefix("codex.")
    if build.startswith("codex.") and previous.isdigit():
        stamp = max(stamp, int(previous) + 1)
    version = f"{base}+codex.{stamp}"
    manifest.write_bytes(
        _VERSION_FIELD.sub(lambda match: match[1] + f'"{version}"'.encode(), content, count=1),
    )
    return version


def marketplace_name(marketplace: Path, plugin: str) -> str:
    """Return the marketplace name once it lists the given plugin."""
    try:
        data = json.loads(marketplace.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        message = f"unreadable marketplace {marketplace}: {error}"
        raise ValueError(message) from error
    name = data.get("name") if isinstance(data, dict) else None
    if not isinstance(name, str) or not _MARKETPLACE.fullmatch(name):
        message = f"marketplace name must use letters, digits, '_', '.' or '-': {marketplace}"
        raise ValueError(message)
    entries = data.get("plugins")
    if not isinstance(entries, list) or not any(
        isinstance(entry, dict) and entry.get("name") == plugin for entry in entries
    ):
        message = f"marketplace {name} has no {plugin} entry: {marketplace}"
        raise ValueError(message)
    return name


def _run(args: argparse.Namespace) -> int:
    """Run one parsed command; ValueError reports a problem to the caller."""
    if args.command == "validate":
        errors, count = validate_package(args.plugin_root)
        for error in errors:
            sys.stderr.write(f"ERROR: {error}\n")
        if errors:
            return 1
        sys.stdout.write(f"Validated {count} skills in plugin package: {args.plugin_root}\n")
    elif args.command == "bump-version":
        sys.stdout.write(f"Plugin version: {bump_version(args.plugin_root)}\n")
    else:
        sys.stdout.write(f"{marketplace_name(args.marketplace, args.plugin)}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and run validate, bump-version or marketplace-name."""
    parser = argparse.ArgumentParser(description="Validate, version and locate the llm-shared Codex plugin.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate").add_argument("plugin_root", type=Path)
    commands.add_parser("bump-version").add_argument("plugin_root", type=Path)
    reader = commands.add_parser("marketplace-name")
    reader.add_argument("marketplace", type=Path)
    reader.add_argument("--plugin", default="llm-shared")
    try:
        return _run(parser.parse_args(argv))
    except ValueError as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


# eof
