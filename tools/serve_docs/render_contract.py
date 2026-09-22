"""Share the Material scaffold and stable documentation navigation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

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


# eof
