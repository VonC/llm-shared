"""Serve one markdown folder as a local website (MkDocs Material).

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
import json
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

LOGGER = logging.getLogger("serve_docs")

FALLBACK_PORT = 8000
BROWSER_WAIT_SECONDS = 180.0  # the first run downloads mkdocs-material
POLL_INTERVAL_SECONDS = 0.5
DIATAXIS_SECTION_ORDER = ("explanation", "tutorials", "how-to", "reference")
SECTION_LABELS = {
    "explanation": "Explanation",
    "tutorials": "Tutorials",
    "how-to": "How-to guides",
    "reference": "Reference",
}

# use_directory_urls false keeps one .html page per source file, so the
# relative paths inside raw HTML tags (right-aligned <img> logos) resolve
# exactly as they do on disk and on Git hosting web views.
MKDOCS_TEMPLATE = """site_name: {site_name}
docs_dir: {docs_dir}
site_dir: {site_dir}
use_directory_urls: false
{navigation}
hooks:
  - fullscreen_hook.py
theme:
  name: material
  # font false keeps the system font stack (Consolas/Menlo for code)
  # instead of the Roboto Mono webfont, which has no box-drawing glyphs
  # and misaligns ASCII diagrams; it also avoids external font fetches.
  font: false
  features:
    - content.code.copy
markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - tables
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
"""


# MkDocs hook written next to the generated mkdocs.yml. It appends a script
# to every page that puts a "full screen" link above each rendered Mermaid
# diagram; the link opens the diagram's SVG alone in a new tab, where it
# fills the window and can be zoomed. Material renders Mermaid into a
# CLOSED shadow root on a div.mermaid host (see its bundle: it calls
# attachShadow({mode:"closed"}) and replaces the pre), so the script wraps
# Element.prototype.attachShadow early to keep a reference to each root.
# Material also themes the SVG through var(--md-mermaid-*) page variables,
# so the standalone tab inlines their resolved values.
HOOK_FILENAME = "fullscreen_hook.py"
HOOK_TEMPLATE = r'''"""MkDocs hook: add a full-screen link above each Mermaid diagram."""

SCRIPT = r"""<script>
(function () {
  var captured = [];
  var original = Element.prototype.attachShadow;
  Element.prototype.attachShadow = function (init) {
    var root = original.call(this, init);
    captured.push({ host: this, root: root });
    return root;
  };
  function svgOf(block) {
    var svg = block.querySelector("svg");
    if (svg) { return svg; }
    var i, entry;
    for (i = 0; i < captured.length; i += 1) {
      entry = captured[i];
      if (entry.host === block || block.contains(entry.host)) {
        svg = entry.root.querySelector("svg");
        if (svg) { return svg; }
      }
    }
    return null;
  }
  function themeVariables(markup) {
    var names = markup.match(/var\((--[A-Za-z0-9-]+)/g) || [];
    var style = getComputedStyle(document.body);
    var seen = {};
    var out = "";
    names.forEach(function (raw) {
      var name = raw.slice(4);
      if (seen[name]) { return; }
      seen[name] = true;
      var value = style.getPropertyValue(name);
      if (value) { out += name + ":" + value + ";"; }
    });
    return out ? ":root{" + out + "}" : "";
  }
  function viewer() {
    var wrap = document.getElementById("wrap");
    var svg = wrap.querySelector("svg");
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    var box = svg.viewBox.baseVal;
    var naturalWidth = box && box.width ? box.width : 800;
    var naturalHeight = box && box.height ? box.height : 600;
    var fit = Math.min(
      window.innerWidth / naturalWidth,
      window.innerHeight / naturalHeight);
    var scale = fit;
    function apply() {
      svg.style.width = naturalWidth * scale + "px";
      svg.style.height = naturalHeight * scale + "px";
    }
    apply();
    wrap.addEventListener("wheel", function (event) {
      event.preventDefault();
      var factor = event.deltaY < 0 ? 1.2 : 1 / 1.2;
      var pointX = (wrap.scrollLeft + event.clientX) / scale;
      var pointY = (wrap.scrollTop + event.clientY) / scale;
      scale = Math.max(0.05, Math.min(40, scale * factor));
      apply();
      wrap.scrollLeft = pointX * scale - event.clientX;
      wrap.scrollTop = pointY * scale - event.clientY;
    }, { passive: false });
    var panning = null;
    wrap.addEventListener("mousedown", function (event) {
      panning = {
        x: event.clientX, y: event.clientY,
        left: wrap.scrollLeft, top: wrap.scrollTop
      };
      wrap.style.cursor = "grabbing";
      event.preventDefault();
    });
    window.addEventListener("mousemove", function (event) {
      if (!panning) { return; }
      wrap.scrollLeft = panning.left - (event.clientX - panning.x);
      wrap.scrollTop = panning.top - (event.clientY - panning.y);
    });
    window.addEventListener("mouseup", function () {
      panning = null;
      wrap.style.cursor = "grab";
    });
    wrap.addEventListener("dblclick", function () {
      scale = fit;
      apply();
      wrap.scrollLeft = 0;
      wrap.scrollTop = 0;
    });
  }
  function openFullScreen(svg) {
    var clone = svg.cloneNode(true);
    clone.removeAttribute("style");
    var markup = clone.outerHTML;
    var page = "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
      + "<title>diagram</title>"
      + "<style>" + themeVariables(markup)
      + "html,body{margin:0;height:100%;background:#fff;overflow:hidden}"
      + "#wrap{width:100vw;height:100vh;overflow:auto;cursor:grab}"
      + "#hint{position:fixed;right:8px;bottom:8px;font:12px sans-serif;"
      + "color:#888;background:#fffc;padding:2px 8px;border-radius:4px}"
      + "</style></head><body>"
      + "<div id=\"wrap\">" + markup + "</div>"
      + "<div id=\"hint\">wheel: zoom &#183; drag: pan &#183; "
      + "double-click: fit</div>"
      + "<scr" + "ipt>(" + viewer.toString() + ")();</scr" + "ipt>"
      + "</body></html>";
    var blob = new Blob([page], { type: "text/html;charset=utf-8" });
    window.open(URL.createObjectURL(blob), "_blank");
  }
  function attach() {
    var blocks = document.querySelectorAll("div.mermaid, pre.mermaid");
    blocks.forEach(function (block) {
      if (block.dataset.serveDocsFs) { return; }
      var svg = svgOf(block);
      if (!svg) { return; }
      block.dataset.serveDocsFs = "1";
      var link = document.createElement("a");
      link.textContent = "⛶ full screen";
      link.href = "#";
      link.title = "Open this diagram alone in a new tab (zoom and pan)";
      link.style.cssText =
        "display:block;text-align:right;font-size:.72rem;margin:.2em 0;";
      link.addEventListener("click", function (event) {
        event.preventDefault();
        openFullScreen(svgOf(block) || svg);
      });
      block.parentNode.insertBefore(link, block);
    });
  }
  window.setInterval(attach, 800);
})();
</script>"""


def on_post_page(output, page, config):  # noqa: ARG001
    """Inject the full-screen script before the closing body tag."""
    return output.replace("</body>", SCRIPT + "</body>")
'''


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


def _markdown_title(path: Path) -> str:
    """Return the first H1, falling back to a readable filename."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return path.stem.replace("-", " ").title()


def _section_key(path: Path) -> tuple[int, str]:
    """Put Diátaxis sections first in the repository's required order."""
    try:
        priority = DIATAXIS_SECTION_ORDER.index(path.name)
    except ValueError:
        priority = len(DIATAXIS_SECTION_ORDER)
    return priority, path.name.casefold()


def _yaml_string(value: str) -> str:
    """Quote a YAML string without splitting non-BMP Unicode into surrogates."""
    return json.dumps(value, ensure_ascii=False)


def _navigation_yaml(docs_dir: Path) -> str:
    """Build explicit navigation with stable Diátaxis section ordering."""
    lines = ["nav:"]
    home = docs_dir / "README.md"
    if home.is_file():
        lines.append(f"  - {_yaml_string('Home')}: {_yaml_string('README.md')}")
    root_pages = sorted(
        path for path in docs_dir.glob("*.md") if path.name != "README.md"
    )
    lines.extend(
        f"  - {_yaml_string(_markdown_title(page))}: {_yaml_string(page.name)}"
        for page in root_pages
    )
    sections = sorted(
        (path for path in docs_dir.iterdir() if path.is_dir()),
        key=_section_key,
    )
    for section in sections:
        pages = sorted(section.rglob("*.md"))
        if not pages:
            continue
        label = SECTION_LABELS.get(section.name, section.name.replace("-", " ").title())
        lines.append(f"  - {_yaml_string(label)}:")
        for page in pages:
            relative = page.relative_to(docs_dir).as_posix()
            lines.append(
                f"      - {_yaml_string(_markdown_title(page))}: {_yaml_string(relative)}",
            )
    return "\n".join(lines)


def write_config(
    docs_dir: Path,
    site_name: str,
    work_dir: Path,
    navigation_root: Path | None = None,
) -> Path:
    """Write the scaffolded mkdocs.yml and hook, return the config path."""
    config_path = work_dir / "mkdocs.yml"
    config_path.write_text(
        MKDOCS_TEMPLATE.format(
            site_name=_yaml_string(site_name),
            docs_dir=_yaml_string(docs_dir.as_posix()),
            site_dir=_yaml_string((work_dir / "site").as_posix()),
            navigation=_navigation_yaml(navigation_root or docs_dir),
        ),
        encoding="utf-8",
    )
    (work_dir / HOOK_FILENAME).write_text(HOOK_TEMPLATE, encoding="utf-8")
    return config_path


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


def main(argv: list[str]) -> int:
    """Scaffold the config, start the server, open the browser."""
    _configure_logging()
    args = parse_args(argv)
    docs_dir = Path(args.docs_dir).resolve()
    if not docs_dir.is_dir():
        message = f"Not a directory: {docs_dir}"
        raise SystemExit(message)
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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


# eof
