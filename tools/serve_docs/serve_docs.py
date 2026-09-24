"""Serve one markdown folder as a local website (MkDocs Material).

The shared render_contract supplies the scaffold and navigation. A configured
external mode dispatches before any local renderer or server work.
The script scaffolds a temporary MkDocs configuration around the given
folder (nothing is written inside the served project), starts
``uvx --with mkdocs-material mkdocs serve`` on the configured port, and
opens the default browser once the server answers. Stop it with Ctrl-C.

The default port lives in ``serve_docs.ini`` next to this script;
``--port`` overrides it for one run.
"""

from __future__ import annotations

import argparse
import configparser
import logging
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

if not __package__:
    # The documented file entry point also works outside the checkout root.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.serve_docs import external_client, render_contract

# Preserve the public scaffold imports for callers of the local server.
DIATAXIS_SECTION_ORDER = render_contract.DIATAXIS_SECTION_ORDER
HOOK_FILENAME = render_contract.HOOK_FILENAME
HOOK_TEMPLATE = render_contract.HOOK_TEMPLATE
MKDOCS_TEMPLATE = render_contract.MKDOCS_TEMPLATE
SECTION_LABELS = render_contract.SECTION_LABELS
write_config = render_contract.write_config

LOGGER = logging.getLogger("serve_docs")

FALLBACK_PORT = 8000
BROWSER_WAIT_SECONDS = 180.0  # the first run downloads mkdocs-material
POLL_INTERVAL_SECONDS = 0.5
def read_default_port() -> int:
    """Read the default port from serve_docs.ini next to this script."""
    ini_path = Path(__file__).with_name("serve_docs.ini")
    parser = configparser.ConfigParser()
    parser.read(ini_path, encoding="utf-8")
    return parser.getint("serve_docs", "port", fallback=FALLBACK_PORT)


def read_docs_config(
    docs_dir: Path,
) -> tuple[str | None, int | None, list[Path], list[Path]]:
    """Read the optional serve_docs.ini colocated with the served folder.

    A project can pin its site name, port, include list, and root-include
    list next to its
    docs (one include path per line, relative to the folder), so a plain
    ``serve_docs.py <folder>`` call serves the full combined set without
    long command lines.
    """
    parser = configparser.ConfigParser()
    parser.read(docs_dir / "serve_docs.ini", encoding="utf-8")
    if not parser.has_section("serve_docs"):
        return None, None, [], []
    name = parser.get("serve_docs", "name", fallback=None)
    port = parser.getint("serve_docs", "port", fallback=None)
    raw_includes = parser.get("serve_docs", "include", fallback="")
    includes = [
        (docs_dir / line.strip()).resolve()
        for line in raw_includes.splitlines()
        if line.strip()
    ]
    raw_root_includes = parser.get("serve_docs", "root_include", fallback="")
    root_includes = [
        (docs_dir / line.strip()).resolve()
        for line in raw_root_includes.splitlines()
        if line.strip()
    ]
    return name, port, includes, root_includes


def find_runner() -> list[str]:
    """Return the command prefix that can run mkdocs through uv."""
    uvx = shutil.which("uvx")
    if uvx:
        return [uvx]
    uv = shutil.which("uv")
    if uv:
        return [uv, "tool", "run"]
    message = (
        "Neither 'uvx' nor 'uv' was found on PATH. Install uv "
        "(https://docs.astral.sh/uv/) or run from a shell whose PATH "
        "holds the venv Scripts folder."
    )
    raise SystemExit(message)


def open_browser_when_up(url: str, port: int) -> None:
    """Poll the server port, then open the default browser on the url."""
    deadline = time.monotonic() + BROWSER_WAIT_SECONDS
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                break
        except OSError:
            time.sleep(POLL_INTERVAL_SECONDS)
    else:
        return
    webbrowser.open(url)


def build_combined_root(
    docs_dir: Path,
    includes: list[Path],
    work_dir: Path,
) -> Path:
    """Copy docs_dir and the included paths into one snapshot root.

    The snapshot keeps the on-disk layout below the common ancestor of
    every path, so the relative links between the served folders resolve
    exactly as they do in the repository. A copy (never a link) is used,
    so cleaning the temporary folder can never touch the originals; the
    served content is a snapshot taken at start time.
    """
    paths = [docs_dir, *includes]
    root = Path(os.path.commonpath([str(path) for path in paths]))
    combined = work_dir / "docs"
    for path in paths:
        destination = combined / path.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(path, destination)
    return combined


_RELATIVE_MARKDOWN_TARGET = re.compile(
    r"(?P<opening>\]\()(?P<parents>(?:\.\./)+)(?P<target>[^)\s]+)(?P<closing>\))",
)


def _rewrite_flattened_repository_links(source_root: Path, snapshot_root: Path) -> None:
    """Adjust links that escaped the primary folder before it moved to ``/``."""
    for source in source_root.rglob("*.md"):
        relative = source.relative_to(source_root)
        nesting_depth = len(relative.parent.parts) if relative.parent != Path() else 0
        snapshot = snapshot_root / relative
        content = snapshot.read_text(encoding="utf-8")

        def replace(
            match: re.Match[str],
            depth: int = nesting_depth,
        ) -> str:
            parents = match.group("parents")
            if parents.count("../") <= depth:
                return match.group(0)
            return (
                f"{match.group('opening')}{parents.removeprefix('../')}"
                f"{match.group('target')}{match.group('closing')}"
            )

        snapshot.write_text(
            _RELATIVE_MARKDOWN_TARGET.sub(replace, content),
            encoding="utf-8",
        )


def build_root_snapshot(
    docs_dir: Path,
    root_includes: list[Path],
    work_dir: Path,
) -> Path:
    """Copy the primary docs at site root and mount selected sibling assets.

    Every included path must stay below the primary folder's parent. Its
    repository-relative path below that parent becomes its site path. This
    keeps the primary README at ``/`` while allowing a sibling ``docs/file``
    to be served at ``/docs/file``.
    """
    combined = work_dir / "docs"
    shutil.copytree(docs_dir, combined, dirs_exist_ok=True)
    _rewrite_flattened_repository_links(docs_dir, combined)
    repository_root = docs_dir.parent
    for source in root_includes:
        destination = combined / source.relative_to(repository_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)
    return combined


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the CLI arguments for the docs server."""
    parser = argparse.ArgumentParser(
        description=(
            "Serve a folder of markdown files as a local website "
            "(MkDocs Material with Mermaid support), and open the browser."
        ),
    )
    parser.add_argument(
        "docs_dir",
        type=str,
        help="Folder holding the markdown files to serve.",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Site name shown in the header. Defaults to the folder name.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Server port. Defaults to the value in serve_docs.ini.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Extra folder or file to serve next to docs_dir, keeping the "
            "on-disk layout below their common ancestor so relative links "
            "between them resolve. Repeatable. With --include the served "
            "content is a start-time snapshot copy."
        ),
    )
    parser.add_argument(
        "--root-include",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Extra file or folder mounted below the site root using its path "
            "relative to docs_dir's parent. Repeatable. Cannot be combined "
            "with --include."
        ),
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the browser once the server answers.",
    )
    return parser.parse_args(argv)


def _configure_logging() -> None:
    """Configure stdout logging with message-only formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def _unique_resolved_paths(
    cli_values: list[str],
    configured: list[Path],
) -> list[Path]:
    """Resolve CLI paths and remove duplicates while preserving order."""
    paths: list[Path] = []
    for path in [Path(value).resolve() for value in cli_values] + configured:
        if path not in paths:
            paths.append(path)
    return paths


def _require_existing(paths: list[Path], option_name: str) -> None:
    """Reject configured paths that do not exist."""
    for path in paths:
        if not path.exists():
            message = f"{option_name} path not found: {path}"
            raise SystemExit(message)


def _validate_root_includes(root_includes: list[Path], docs_dir: Path) -> None:
    """Keep root mounts inside the repository area copied into the snapshot."""
    _require_existing(root_includes, "root-include")
    for include in root_includes:
        if not include.is_relative_to(docs_dir.parent):
            message = f"root-include must stay below {docs_dir.parent}: {include}"
            raise SystemExit(message)


def resolve_settings(
    args: argparse.Namespace,
    docs_dir: Path,
) -> tuple[str, int, list[Path], list[Path]]:
    """Merge the CLI flags, the per-folder ini, and the tool-level ini."""
    ini_name, ini_port, ini_includes, ini_root_includes = read_docs_config(docs_dir)
    includes = _unique_resolved_paths(args.include, ini_includes)
    _require_existing(includes, "include")
    root_includes = _unique_resolved_paths(args.root_include, ini_root_includes)
    if includes and root_includes:
        message = "--include and --root-include cannot be combined"
        raise SystemExit(message)
    _validate_root_includes(root_includes, docs_dir)
    port = args.port if args.port is not None else ini_port
    port = port if port is not None else read_default_port()
    site_name = args.name or ini_name or docs_dir.name
    return site_name, port, includes, root_includes


def _run_local(args: argparse.Namespace, docs_dir: Path) -> int:
    """Scaffold and serve a local folder when external mode is absent."""
    if not any(docs_dir.rglob("*.md")):
        message = f"No markdown file found under: {docs_dir}"
        raise SystemExit(message)
    site_name, port, includes, root_includes = resolve_settings(args, docs_dir)
    url = f"http://127.0.0.1:{port}/"

    with tempfile.TemporaryDirectory(prefix="serve_docs_") as work:
        served_root = docs_dir
        if includes:
            served_root = build_combined_root(docs_dir, includes, Path(work))
        elif root_includes:
            served_root = build_root_snapshot(docs_dir, root_includes, Path(work))
        navigation_root = docs_dir if root_includes else served_root
        config_path = write_config(
            served_root,
            site_name,
            Path(work),
            navigation_root=navigation_root,
        )
        command = [
            *find_runner(),
            # Pin the tool environment to this interpreter so uv never
            # downloads a standalone Python (blocked on TLS-intercepting
            # networks); package downloads follow the shell's uv settings.
            "--python",
            sys.executable,
            "--with",
            "mkdocs-material",
            "mkdocs",
            "serve",
            "-f",
            str(config_path),
            "-a",
            f"127.0.0.1:{port}",
        ]
        if not args.no_browser:
            opener = threading.Thread(
                target=open_browser_when_up,
                args=(url, port),
                daemon=True,
            )
            opener.start()
        LOGGER.info("Serving %s on %s (Ctrl-C to stop)", docs_dir, url)
        if includes:
            LOGGER.info(
                "Combined snapshot with %d included path(s); restart to "
                "pick up file edits.",
                len(includes),
            )
        elif root_includes:
            LOGGER.info(
                "Root snapshot with %d mounted path(s); restart to pick up "
                "file edits.",
                len(root_includes),
            )
        try:
            return subprocess.call(command)  # noqa: S603
        except KeyboardInterrupt:
            return 0


def main(argv: list[str]) -> int:
    """Dispatch configured external mode or scaffold the local server."""
    _configure_logging()
    args = parse_args(argv)
    docs_dir = Path(args.docs_dir).resolve()
    if not docs_dir.is_dir():
        message = f"Not a directory: {docs_dir}"
        raise SystemExit(message)
    external = external_client.read_config(docs_dir)
    if external is not None:
        return external_client.run(external, no_browser=args.no_browser)
    return _run_local(args, docs_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


# eof
