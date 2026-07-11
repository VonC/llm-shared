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

# use_directory_urls false keeps one .html page per source file, so the
# relative paths inside raw HTML tags (right-aligned <img> logos) resolve
# exactly as they do on disk and on Git hosting web views.
MKDOCS_TEMPLATE = """site_name: {site_name}
docs_dir: {docs_dir}
site_dir: {site_dir}
use_directory_urls: false
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
) -> tuple[str | None, int | None, list[Path]]:
    """Read the optional serve_docs.ini colocated with the served folder.

    A project can pin its site name, port, and include list next to its
    docs (one include path per line, relative to the folder), so a plain
    ``serve_docs.py <folder>`` call serves the full combined set without
    long command lines.
    """
    parser = configparser.ConfigParser()
    parser.read(docs_dir / "serve_docs.ini", encoding="utf-8")
    if not parser.has_section("serve_docs"):
        return None, None, []
    name = parser.get("serve_docs", "name", fallback=None)
    port = parser.getint("serve_docs", "port", fallback=None)
    raw_includes = parser.get("serve_docs", "include", fallback="")
    includes = [
        (docs_dir / line.strip()).resolve()
        for line in raw_includes.splitlines()
        if line.strip()
    ]
    return name, port, includes


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


def write_config(docs_dir: Path, site_name: str, work_dir: Path) -> Path:
    """Write the scaffolded mkdocs.yml and hook, return the config path."""
    config_path = work_dir / "mkdocs.yml"
    config_path.write_text(
        MKDOCS_TEMPLATE.format(
            site_name=json.dumps(site_name),
            docs_dir=json.dumps(docs_dir.as_posix()),
            site_dir=json.dumps((work_dir / "site").as_posix()),
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


def resolve_settings(
    args: argparse.Namespace,
    docs_dir: Path,
) -> tuple[str, int, list[Path]]:
    """Merge the CLI flags, the per-folder ini, and the tool-level ini."""
    ini_name, ini_port, ini_includes = read_docs_config(docs_dir)
    includes: list[Path] = []
    for include in [Path(i).resolve() for i in args.include] + ini_includes:
        if include not in includes:
            includes.append(include)
    for include in includes:
        if not include.exists():
            message = f"include path not found: {include}"
            raise SystemExit(message)
    port = args.port if args.port is not None else ini_port
    port = port if port is not None else read_default_port()
    site_name = args.name or ini_name or docs_dir.name
    return site_name, port, includes


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
    site_name, port, includes = resolve_settings(args, docs_dir)
    url = f"http://127.0.0.1:{port}/"

    with tempfile.TemporaryDirectory(prefix="serve_docs_") as work:
        served_root = docs_dir
        if includes:
            served_root = build_combined_root(docs_dir, includes, Path(work))
        config_path = write_config(served_root, site_name, Path(work))
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
        try:
            return subprocess.call(command)  # noqa: S603
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


# eof
