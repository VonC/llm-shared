"""Spell-check files outside VS Code, with the findings Code Spell Checker shows.

The streetsidesoftware Code Spell Checker extension shows its unknown words in
the VS Code Problems panel only, and offers no API to read them from outside.
It is built on ``cspell-lib``, the engine of the ``cspell`` command line, so
cspell reports the same words once it gets the same settings. VS Code merges
the ``cSpell.*`` settings of the user settings, of the checkout's
``.code-workspace`` files and of its ``.vscode/settings.json``; cspell reads
none of them. ``check`` merges those levels into one temporary cspell
configuration, imports the dictionary of every installed language extension
(such as the French one), runs a pinned cspell with Node, and lists each
unknown word with its locations and cSpell suggestions.

``add-words`` inserts accepted words into the ``cSpell.words`` list of the
checkout's ``.vscode/settings.json``, at their place in its order, so the
words the user chooses to accept are added in one call. Every other word is
replaced in the text: no ignore pattern or comment hides a finding.

Only Markdown files are checked (user decision of 2026-11-08): ``check``
drops every other file it is given, and needs no Node when none remains.

Fix: a client stopped at its commit gate because the check demanded a Node
22.18 that its machine could not install. The check now finds Node by itself
(the PATH, then the senv ``%PRGS%/nodes/node<N>`` links), puts it first on
the PATH of npm and cspell, and runs cspell 10 on a Node 22.18 or later, else
cspell 9 on a Node 20.18 or later.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import unquote, urlparse

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    Runner = Callable[..., subprocess.CompletedProcess[str]]

# The cspell release pinned for each minimum Node, newest first: cspell 10 is
# the engine of the VS Code extension; cspell 9, which gives the same findings
# on Markdown, runs on the Node 20.18 to 22.17 that machines still carry.
CSPELL_RELEASES: tuple[tuple[tuple[int, int], str], ...] = (((22, 18), "10.4.1"), ((20, 18), "9.8.0"))
EXTENSION_PREFIX = "streetsidesoftware.code-spell-checker-"
LIST_KEYS = ("words", "userWords", "flagWords", "ignoreWords", "ignorePaths", "ignoreRegExpList")
SCALAR_KEYS = ("language", "allowCompoundWords", "caseSensitive", "minWordLength")
MAX_SUGGESTIONS = 5
MARKDOWN_SUFFIX = ".md"
EXIT_CLEAN = 0
EXIT_WORDS = 1
EXIT_ERROR = 2
LLM_SHARED_DIR = Path(__file__).resolve().parents[1]
CSPELL_ROOT = LLM_SHARED_DIR / "venvs"

_STRING = r'"(?:\\.|[^"\\])*"'
_COMMENTS = re.compile(rf"{_STRING}|//[^\n]*|/\*.*?\*/", re.DOTALL)
_TRAILING_COMMAS = re.compile(rf"{_STRING}|,(?=\s*[\]}}])")
_WORDS_BLOCK = re.compile(r'"cSpell\.words"\s*:\s*\[(?P<body>.*?)\]', re.DOTALL)


class SpellCheckError(Exception):
    """An operational failure: settings, Node, cspell or its report cannot be used."""


@dataclass(frozen=True, slots=True)
class SettingsSources:
    """Where VS Code keeps the user settings and the installed extensions."""

    user_settings: Path | None
    extensions_dir: Path | None


@dataclass(frozen=True, slots=True)
class UnknownWord:
    """One word cSpell does not know, where it occurs and what it suggests."""

    word: str
    locations: tuple[str, ...]
    suggestions: tuple[str, ...]


def _keep_strings(match: re.Match[str]) -> str:
    """Keep a JSON string token, drop a comment or a trailing comma."""
    token = match.group()
    return token if token.startswith('"') else ""


def load_jsonc(text: str) -> object:
    """Parse JSON with comments and trailing commas, as VS Code settings allow."""
    without_comments = _COMMENTS.sub(_keep_strings, text)
    return json.loads(_TRAILING_COMMAS.sub(_keep_strings, without_comments))


def _parse_settings_text(text: str, path: Path) -> dict[str, Any]:
    """Parse settings text read from or written to ``path``, or fail with the file named."""
    try:
        settings = load_jsonc(text)
    except ValueError as error:
        message = f"unreadable VS Code settings {path}: {error}"
        raise SpellCheckError(message) from error
    if not isinstance(settings, dict):
        message = f"VS Code settings {path} hold no JSON object"
        raise SpellCheckError(message)
    return cast("dict[str, Any]", settings)


def _read_settings(path: Path) -> dict[str, Any]:
    """Read one VS Code settings object, or fail with the file named."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        message = f"unreadable VS Code settings {path}: {error}"
        raise SpellCheckError(message) from error
    return _parse_settings_text(text, path)


def cspell_settings(settings: Mapping[str, Any]) -> dict[str, Any]:
    """Return the ``cSpell.*`` entries of one settings level without their prefix."""
    prefix = "cSpell."
    return {key[len(prefix):]: value for key, value in settings.items() if key.startswith(prefix)}


def read_levels(root: Path, user_settings: Path | None) -> list[dict[str, Any]]:
    """Return the cSpell settings of each level VS Code merges, least specific first."""
    levels: list[dict[str, Any]] = []
    if user_settings is not None and user_settings.is_file():
        levels.append(cspell_settings(_read_settings(user_settings)))
    for workspace in sorted((root / ".vscode").glob("*.code-workspace")):
        workspace_settings = _read_settings(workspace).get("settings", {})
        if isinstance(workspace_settings, dict):
            levels.append(cspell_settings(cast("dict[str, Any]", workspace_settings)))
    folder = root / ".vscode" / "settings.json"
    if folder.is_file():
        levels.append(cspell_settings(_read_settings(folder)))
    return levels


def merge_settings(levels: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Join the word and pattern lists of all levels; the most specific scalar wins."""
    config: dict[str, Any] = {"version": "0.2", "language": "en"}
    for level in levels:
        for key in LIST_KEYS:
            values = level.get(key)
            if isinstance(values, list):
                config.setdefault(key, []).extend(cast("list[object]", values))
        for key in SCALAR_KEYS:
            if key in level:
                config[key] = level[key]
    return config


def _version_key(text: str) -> tuple[int, ...]:
    """Return the numbers of a version text, such as ``(22, 9, 0)`` for ``v22.9.0``."""
    return tuple(int(number) for number in re.findall(r"\d+", text))


def language_imports(extensions_dir: Path | None) -> list[str]:
    """Return the cspell configuration of each installed language extension, newest version."""
    if extensions_dir is None or not extensions_dir.is_dir():
        return []
    newest: dict[str, tuple[tuple[int, ...], Path]] = {}
    for folder in extensions_dir.glob(f"{EXTENSION_PREFIX}*"):
        config = folder / "static" / "cspell-ext.json"
        if not config.is_file():
            continue
        name, _, version = folder.name.rpartition("-")
        key = _version_key(version)
        if name not in newest or key > newest[name][0]:
            newest[name] = (key, config)
    return [newest[name][1].as_posix() for name in sorted(newest)]


def build_config(root: Path, sources: SettingsSources) -> dict[str, Any]:
    """Return the cspell configuration equal to what VS Code gives the extension."""
    config = merge_settings(read_levels(root, sources.user_settings))
    imports = language_imports(sources.extensions_dir)
    if imports:
        config["import"] = imports
    return config


def default_sources(environ: Mapping[str, str]) -> SettingsSources:
    """Locate the VS Code user settings and extensions folder of this user."""
    appdata = environ.get("APPDATA")
    profile = environ.get("USERPROFILE") or environ.get("HOME")
    return SettingsSources(
        Path(appdata, "Code", "User", "settings.json") if appdata else None,
        Path(profile, ".vscode", "extensions") if profile else None,
    )


def node_candidates(environ: Mapping[str, str]) -> list[Path]:
    r"""Return ``node`` from the PATH, then each senv ``%PRGS%\nodes\node<N>`` link, newest first."""
    found = shutil.which("node", path=environ.get("PATH"))
    candidates = [Path(found)] if found else []
    prgs = environ.get("PRGS")
    if prgs:
        linked = Path(prgs, "nodes").glob("node*/node.exe")
        candidates.extend(sorted(linked, key=lambda node: _version_key(node.parent.name), reverse=True))
    return candidates


def find_node(environ: Mapping[str, str], run: Runner) -> tuple[Path, str]:
    """Return a Node and the newest pinned cspell it runs, preferring cspell 10."""
    found: list[tuple[Path, tuple[int, ...]]] = []
    for node in node_candidates(environ):
        completed = run([str(node), "--version"], capture_output=True, text=True, check=False)
        found.append((node, _version_key(completed.stdout) if completed.returncode == 0 else ()))
    for minimum, cspell in CSPELL_RELEASES:
        for node, version in found:
            if version >= minimum:
                return node, cspell
    seen = ", ".join(f"{node} ({'.'.join(map(str, version)) or 'unknown version'})" for node, version in found)
    lowest = ".".join(map(str, CSPELL_RELEASES[-1][0]))
    message = (
        f"cspell needs Node {lowest} or later; found: {seen or 'none'}. "
        "Install one with the senv tools (dwl_inst_ver node 22), then rerun."
    )
    raise SpellCheckError(message)


def node_environment(node: Path, environ: Mapping[str, str]) -> dict[str, str]:
    """Return the environment with ``node``'s folder first on the PATH, for npm and cspell."""
    path = environ.get("PATH", "")
    return {**environ, "PATH": f"{node.parent}{os.pathsep}{path}" if path else str(node.parent)}


def ensure_cspell(node: Path, cspell: str, env: Mapping[str, str], run: Runner) -> Path:
    """Return the pinned cspell entry point, installing it with Node's own npm when missing."""
    home = CSPELL_ROOT / f"cspell_{cspell}"
    entry = home / "node_modules" / "cspell" / "bin.mjs"
    if entry.is_file():
        return entry
    npm = node.parent / "node_modules" / "npm" / "bin" / "npm-cli.js"
    completed = run(
        [
            str(node), str(npm), "install", "--prefix", str(home),
            "--no-save", "--no-audit", "--no-fund", f"cspell@{cspell}",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=dict(env),
    )
    if completed.returncode != 0 or not entry.is_file():
        message = f"npm could not install cspell {cspell} into {home}: {completed.stderr.strip()}"
        raise SpellCheckError(message)
    return entry


def run_cspell(
    command: Sequence[str],
    root: Path,
    env: Mapping[str, str],
    run: Runner,
) -> dict[str, Any]:
    """Run one cspell lint with the JSON reporter and return its parsed report."""
    completed = run(
        list(command), capture_output=True, text=True, encoding="utf-8", check=False, cwd=root, env=dict(env),
    )
    if completed.returncode not in {0, 1}:
        message = f"cspell failed with exit code {completed.returncode}: {completed.stderr.strip()}"
        raise SpellCheckError(message)
    try:
        report = json.loads(completed.stdout)
    except ValueError as error:
        message = f"cspell returned no JSON report: {error}"
        raise SpellCheckError(message) from error
    if not isinstance(report, dict):
        message = "cspell returned a JSON report that is not an object"
        raise SpellCheckError(message)
    return cast("dict[str, Any]", report)


def lint_command(node: Path, entry: Path, root: Path, config: Path, files: Sequence[str]) -> list[str]:
    """Return the cspell lint call for the given files under ``root``."""
    return [
        str(node), str(entry), "lint", "--root", str(root), "--config", str(config),
        "--no-progress", "--no-summary", "--no-must-find-files", "--show-suggestions",
        "--reporter", "@cspell/cspell-json-reporter", *files,
    ]


def word_key(word: str) -> tuple[str, str]:
    """Order words as VS Code sorts ``cSpell.words``: accents and case ignored, lowercase first."""
    plain = "".join(char for char in unicodedata.normalize("NFD", word) if not unicodedata.combining(char))
    return plain.casefold(), word.swapcase()


def _display_path(uri: str, root: Path) -> str:
    """Return a reported file URI as a path relative to ``root`` when it lies under it."""
    path = Path(unquote(urlparse(uri).path).lstrip("/")) if uri.startswith("file:") else Path(uri)
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _suggestions(issue: Mapping[str, Any]) -> list[str]:
    """Return an issue's suggestions, the preferred ones first."""
    detailed = cast("list[dict[str, Any]]", issue.get("suggestionsEx") or [])
    preferred = [str(entry["word"]) for entry in detailed if entry.get("isPreferred")]
    plain = [str(word) for word in cast("list[object]", issue.get("suggestions") or [])]
    return preferred + [word for word in plain if word not in preferred]


def unknown_words(report: Mapping[str, Any], root: Path) -> list[UnknownWord]:
    """Group a cspell JSON report by word, in settings order."""
    grouped: dict[str, tuple[list[str], list[str]]] = {}
    for issue in cast("list[dict[str, Any]]", report.get("issues") or []):
        locations, suggestions = grouped.setdefault(str(issue["text"]), ([], []))
        locations.append(f"{_display_path(str(issue['uri']), root)}:{issue['row']}:{issue['col']}")
        suggestions.extend(word for word in _suggestions(issue) if word not in suggestions)
    return [
        UnknownWord(word, tuple(locations), tuple(suggestions[:MAX_SUGGESTIONS]))
        for word, (locations, suggestions) in sorted(grouped.items(), key=lambda item: word_key(item[0]))
    ]


def render_markdown(words: Sequence[UnknownWord]) -> str:
    """Render the unknown words as a compact Markdown table, or a clean verdict."""
    if not words:
        return "cSpell: no unknown word."
    lines = [
        f"cSpell: {len(words)} unknown word(s).",
        "",
        "| Word | Where | cSpell suggestions |",
        "| --- | --- | --- |",
    ]
    for entry in words:
        where = ", ".join(f"`{location}`" for location in entry.locations)
        suggestions = ", ".join(entry.suggestions) or "none"
        lines.append(f"| `{entry.word}` | {where} | {suggestions} |")
    return "\n".join(lines)


def render_json(words: Sequence[UnknownWord]) -> str:
    """Render the unknown words as JSON for another tool."""
    return json.dumps(
        [{"word": e.word, "locations": e.locations, "suggestions": e.suggestions} for e in words],
        ensure_ascii=False,
        indent=2,
    )


def markdown_files(files: Sequence[str]) -> list[str]:
    """Keep the Markdown files: spelling is checked on documentation, never on source code."""
    return [name for name in files if name.lower().endswith(MARKDOWN_SUFFIX)]


def check(
    root: Path,
    files: Sequence[str],
    *,
    environ: Mapping[str, str],
    run: Runner,
) -> list[UnknownWord]:
    """Spell-check the Markdown ``files`` under ``root`` as VS Code would; return the unknown words."""
    files = markdown_files(files)
    if not files:
        return []
    config = build_config(root, default_sources(environ))
    node, cspell = find_node(environ, run)
    env = node_environment(node, environ)
    entry = ensure_cspell(node, cspell, env, run)
    handle, name = tempfile.mkstemp(prefix="a.spell-check.", suffix=".json")
    config_path = Path(name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(config, stream, ensure_ascii=False)
        report = run_cspell(lint_command(node, entry, root, config_path, files), root, env, run)
    finally:
        config_path.unlink(missing_ok=True)
    return unknown_words(report, root)


def _render_block(words: Sequence[str], indent: str, newline: str, closing: str) -> str:
    """Render the ``cSpell.words`` items, one per line, with the file's layout."""
    items = f",{newline}".join(f"{indent}{json.dumps(word, ensure_ascii=False)}" for word in words)
    return f"{newline}{items}{newline}{closing}"


def _merge_words(existing: object, words: Sequence[str]) -> tuple[list[str], list[str]]:
    """Insert each missing word before the first listed word that sorts after it."""
    merged = [str(word) for word in cast("list[object]", existing)] if isinstance(existing, list) else []
    added: list[str] = []
    for word in words:
        if word in merged:
            continue
        position = next((i for i, current in enumerate(merged) if word_key(current) > word_key(word)), len(merged))
        merged.insert(position, word)
        added.append(word)
    return merged, added


def _with_words(text: str, merged: Sequence[str]) -> str:
    """Return the settings text with its ``cSpell.words`` list replaced, or appended last."""
    newline = "\r\n" if "\r\n" in text else "\n"
    match = _WORDS_BLOCK.search(text)
    if match is None:
        end = text.rstrip().rfind("}")
        head = text[:end].rstrip()
        separator = "" if head.endswith("{") else ","
        block = _render_block(merged, "    ", newline, "  ")
        return f'{head}{separator}{newline}  "cSpell.words": [{block}]{newline}{text[end:]}'
    body = match.group("body")
    indent = re.search(r"\n([ \t]*)\"", body)
    closing = re.search(r"\n([ \t]*)$", body)
    block = _render_block(
        merged,
        indent.group(1) if indent else "    ",
        newline,
        closing.group(1) if closing else "  ",
    )
    return f"{text[:match.start('body')]}{block}{text[match.end('body'):]}"


def add_words(settings_path: Path, words: Sequence[str]) -> list[str]:
    """Insert the missing ``words`` into ``cSpell.words`` at their place; return those added."""
    if any(not word.strip() for word in words):
        message = "add-words needs non-empty words"
        raise SpellCheckError(message)
    text = settings_path.read_bytes().decode("utf-8") if settings_path.is_file() else "{\n}\n"
    existing = cspell_settings(_parse_settings_text(text, settings_path)).get("words")
    merged, added = _merge_words(existing, words)
    if not added:
        return added
    text = _with_words(text, merged)
    _parse_settings_text(text, settings_path)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_bytes(text.encode("utf-8"))
    return added


def build_parser() -> argparse.ArgumentParser:
    """Return the ``check`` and ``add-words`` command line."""
    parser = argparse.ArgumentParser(prog="spellcheck", description=__doc__.splitlines()[0] if __doc__ else None)
    commands = parser.add_subparsers(dest="command", required=True)
    checking = commands.add_parser("check", help="list the words cSpell does not know in the Markdown FILES")
    checking.add_argument("--root", default=".", help="checkout root (default: current folder)")
    checking.add_argument("--format", choices=("markdown", "json"), default="markdown")
    checking.add_argument("files", nargs="+", help="files relative to the root")
    adding = commands.add_parser("add-words", help="add WORDS to the checkout's .vscode/settings.json")
    adding.add_argument("--root", default=".", help="checkout root (default: current folder)")
    adding.add_argument("words", nargs="+")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    run: Runner = subprocess.run,
) -> int:
    """Run one command: 0 clean or words added, 1 unknown words listed, 2 operational error."""
    arguments = build_parser().parse_args(argv)
    environment = os.environ if environ is None else environ
    root = Path(arguments.root).resolve()
    try:
        if arguments.command == "add-words":
            added = add_words(root / ".vscode" / "settings.json", arguments.words)
            sys.stdout.write(f"cSpell words added: {', '.join(added) or 'none (already listed)'}\n")
            return EXIT_CLEAN
        words = check(root, arguments.files, environ=environment, run=run)
    except SpellCheckError as error:
        sys.stderr.write(f"spellcheck: {error}\n")
        return EXIT_ERROR
    sys.stdout.write((render_json(words) if arguments.format == "json" else render_markdown(words)) + "\n")
    return EXIT_WORDS if words else EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(main())


# eof
