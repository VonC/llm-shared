r"""Check, and on request create, the link that shows the llm-shared skills to Codex.

Codex reads user skills from ``.agents\skills`` in the user's home folder
(``%USERPROFILE%`` on Windows) and follows a linked folder to its target.
``llmup`` (``bin\codex_skills_link.bat``) keeps that whole folder a link to
this clone's ``.agents\llm-shared\skills``, so every new Codex thread lists
the clone's current skills, named ``llm-shared:<skill>`` after the package
manifest: no plugin install, no plugin cache, no manifest version to bump.
Codex shows the resolved clone path as the skill root, so the clone-relative
wrapper links resolve. A link one level down, ``.agents\skills\llm-shared``,
keeps the link path instead and breaks them: only the whole folder is linked.

The tool never writes inside the clone. It runs three steps in order:

1. Validate the package, read-only: the manifest, every ``SKILL.md`` wrapper
   and every clone-relative redirect. An invalid package stops here.
2. Check the link: a junction or symbolic link whose target is this clone's
   skills folder. Only with ``--create``, an absent or empty folder becomes
   that link (a junction on Windows, which needs no elevation). A folder with
   any content, a file, a link to another folder, or a link that would sit
   inside the clone is refused and left unchanged.
3. Warn, without changing the exit code, when the Codex configuration still
   enables an ``llm-shared@<marketplace>`` plugin, whose skills would then be
   listed twice, and print the ``codex plugin remove`` command to run.

Exit codes:

- 0: the package is valid and the link targets this clone's skills
- 1: the package is invalid; the link is not checked
- 2: no link yet, the folder is absent or empty: run again with ``--create``
- 3: refused, the folder holds other content or links elsewhere: nothing changed
- 4: the link could not be created, or does not read back as created
- 5: usage error, or the launcher found no llm-shared Python
"""

from __future__ import annotations

import argparse
import os
import sys
import tomllib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn, cast

if __name__ == "__main__":
    # bin\codex_skills_link.bat runs this file in isolated mode (-I), which
    # puts neither the current folder nor this file's folder on sys.path: add
    # the llm-shared root so the package validators import as part of tools.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.codex_plugin_package import validate_package
from tools.codex_plugin_redirects import PACKAGE, validate_redirects

if TYPE_CHECKING:
    from collections.abc import Sequence

EXIT_READY = 0
EXIT_INVALID_PACKAGE = 1
EXIT_NO_LINK = 2
EXIT_REFUSED = 3
EXIT_LINK_FAILED = 4
EXIT_USAGE = 5

PLUGIN_PREFIX = "llm-shared@"
LAUNCHER = Path("bin") / "codex_skills_link.bat"
NEW_THREAD = (
    "New Codex threads list the clone's current skills, with no further command;"
    " restart Codex if a change does not appear.\n"
)


class LinkState(Enum):
    """What the user skills folder holds, observed without changing it."""

    LINKED = "a link to this clone's skills"
    ABSENT = "absent"
    EMPTY = "an empty folder"
    ELSEWHERE = "a link to another folder"
    OCCUPIED = "a folder or file with other content"


@dataclass(frozen=True, slots=True)
class Locations:
    """The clone whose skills are linked, and the user folders Codex reads."""

    clone: Path
    home: Path
    codex_home: Path

    @property
    def package(self) -> Path:
        """The Codex skill package inside the clone."""
        return self.clone / PACKAGE

    @property
    def skills(self) -> Path:
        """The link target: the package skills folder."""
        return self.package / "skills"

    @property
    def link(self) -> Path:
        """The user skills folder Codex scans."""
        return self.home / ".agents" / "skills"

    @property
    def config(self) -> Path:
        """The Codex configuration that may still enable the old plugin."""
        return self.codex_home / "config.toml"


def _say(text: str) -> None:
    """Print a result on stdout."""
    sys.stdout.write(text)


def _problem(text: str) -> None:
    """Print a problem on stderr, after the results already printed on stdout."""
    sys.stdout.flush()
    sys.stderr.write(text)


def _same_folder(first: Path, second: Path) -> bool:
    """Compare two folders after following every link, ignoring case on Windows."""
    return os.path.normcase(str(first.resolve())) == os.path.normcase(str(second.resolve()))


def link_state(link: Path, skills: Path) -> LinkState:
    """Classify the user skills folder; nothing is created or removed."""
    if link.is_junction() or link.is_symlink():
        return LinkState.LINKED if _same_folder(link, skills) else LinkState.ELSEWHERE
    if not link.exists():
        return LinkState.ABSENT
    if link.is_dir() and not any(link.iterdir()):
        return LinkState.EMPTY
    return LinkState.OCCUPIED


def create_link(link: Path, skills: Path, *, windows: bool = os.name == "nt") -> None:
    """Make ``link`` a folder link to ``skills``, creating its parent folder.

    Windows gets a junction, which any user may create; other systems get a
    symbolic link.
    """
    link.parent.mkdir(parents=True, exist_ok=True)
    if windows:
        import _winapi  # noqa: PLC0415 - Windows-only module

        _winapi.CreateJunction(str(skills), str(link))
    else:
        link.symlink_to(skills, target_is_directory=True)


def enabled_plugins(config: Path) -> list[str]:
    """Return the ``llm-shared@<marketplace>`` plugins the Codex config enables.

    A plugin entry counts as enabled unless it says ``enabled = false``. A
    missing configuration enables nothing.

    Raises:
        OSError: The configuration exists but cannot be read.
        ValueError: The configuration is not UTF-8 TOML.
    """
    if not config.is_file():
        return []
    data = tomllib.loads(config.read_text(encoding="utf-8-sig"))
    plugins = data.get("plugins")
    if not isinstance(plugins, dict):
        return []
    names: list[str] = []
    for name, entry in cast("dict[str, object]", plugins).items():
        settings = cast("dict[str, object]", entry) if isinstance(entry, dict) else {}
        if name.startswith(PLUGIN_PREFIX) and settings.get("enabled") is not False:
            names.append(name)
    return sorted(names)


def _plugin_warning(config: Path) -> str:
    """Return the warning about a still-enabled llm-shared plugin, or nothing."""
    try:
        names = enabled_plugins(config)
    except (OSError, ValueError) as error:
        return (
            f"WARNING: cannot read {config} ({error}); check yourself that no "
            f'[plugins."{PLUGIN_PREFIX}<marketplace>"] entry is enabled there.\n'
        )
    if not names:
        return ""
    commands = "".join(f"  codex plugin remove {name}\n" for name in names)
    return (
        f"WARNING: {config} still enables {', '.join(names)}: Codex would list"
        f" every llm-shared skill twice. Remove the plugin with:\n{commands}"
    )


def _create(locations: Locations, state: LinkState) -> int:
    """Turn an absent or empty user skills folder into the link, then read it back."""
    link, skills = locations.link, locations.skills
    if link.parent.resolve().is_relative_to(locations.clone.resolve()):
        _problem(
            f"REFUSED: {link} is inside the clone {locations.clone}, where llmup"
            " never writes. Nothing changed.\n",
        )
        return EXIT_REFUSED
    try:
        if state is LinkState.EMPTY:
            link.rmdir()
        create_link(link, skills)
    except OSError as error:
        _problem(f"FAILED: cannot create {link}: {error}\n")
        return EXIT_LINK_FAILED
    if link_state(link, skills) is not LinkState.LINKED:
        _problem(f"FAILED: {link} was created but does not link to {skills}\n")
        return EXIT_LINK_FAILED
    _say(f"CREATED: {link} links to {skills}\n{NEW_THREAD}")
    return EXIT_READY


def check_link(locations: Locations, *, create: bool) -> int:
    """Report the user skills folder, creating the link only when asked and free."""
    link, skills = locations.link, locations.skills
    state = link_state(link, skills)
    if state is LinkState.LINKED:
        _say(f"OK: {link} links to {skills}\n{NEW_THREAD}")
        return EXIT_READY
    if state is LinkState.ELSEWHERE:
        _problem(
            f"REFUSED: {link} links to {link.resolve()}, not to {skills}."
            f' Remove that link first (rmdir "{link}" removes the link only),'
            " then run again with --create. Nothing changed.\n",
        )
        return EXIT_REFUSED
    if state is LinkState.OCCUPIED:
        _problem(
            f"REFUSED: {link} is {state.value}. Move it away, then run again"
            " with --create. Nothing changed.\n",
        )
        return EXIT_REFUSED
    if create:
        return _create(locations, state)
    _problem(
        f"MISSING: {link} is {state.value}, not a link to {skills}. Create the"
        f' link with: "{locations.clone / LAUNCHER}" --create (llmup --create)\n',
    )
    return EXIT_NO_LINK


def run(locations: Locations, *, create: bool) -> int:
    """Validate the package, check or create the link, then warn about the plugin."""
    errors, count = validate_package(locations.package)
    errors += validate_redirects(locations.clone)
    if errors:
        for error in errors:
            _problem(f"ERROR: {error}\n")
        _problem(
            "The skill package is invalid: fix the clone, then run again."
            " The link was not checked.\n",
        )
        return EXIT_INVALID_PACKAGE
    _say(
        f"OK: {count} skills and their clone-relative redirects are valid in {locations.package}\n",
    )
    code = check_link(locations, create=create)
    _problem(_plugin_warning(locations.config))
    return code


class _Parser(argparse.ArgumentParser):
    """An argument parser whose usage errors exit with the documented code 5."""

    def error(self, message: str) -> NoReturn:
        """Print the usage and the problem, then exit with EXIT_USAGE."""
        self.print_usage(sys.stderr)
        self.exit(EXIT_USAGE, f"{self.prog}: error: {message}\n")


def _parser() -> argparse.ArgumentParser:
    """Build the llmup command line."""
    parser = _Parser(
        prog="codex_skills_link",
        description=(
            "Check that the user skills folder Codex reads links to this clone's"
            " llm-shared skills; create it with --create. Never writes inside the clone."
        ),
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="create the link when the user skills folder is absent or empty",
    )
    parser.add_argument(
        "--home",
        type=Path,
        help=r"home folder holding .agents\skills (default: the current user's home)",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        help=r"folder holding the Codex config.toml (default: CODEX_HOME, else <home>\.codex)",
    )
    return parser


def main(argv: Sequence[str] | None = None, *, clone: Path | None = None) -> int:
    """Run llmup for one clone, the clone holding this file by default."""
    args = _parser().parse_args(argv)
    home = (cast("Path | None", args.home) or Path.home()).absolute()
    environment_home = os.environ.get("CODEX_HOME")
    codex_home = cast("Path | None", args.codex_home) or (
        Path(environment_home) if environment_home else home / ".codex"
    )
    root = clone or Path(__file__).resolve().parent.parent
    return run(Locations(root, home, codex_home), create=args.create)


if __name__ == "__main__":
    raise SystemExit(main())


# eof
