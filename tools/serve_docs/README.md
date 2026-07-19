# serve_docs tool

Serve one folder of markdown files as a local website, rendered by
MkDocs Material through `uvx --with mkdocs-material mkdocs serve`, and
open the default browser on it. Nothing is installed permanently and
nothing is written inside the served project: the MkDocs configuration
is scaffolded in a temporary folder for the lifetime of the server.

Workflow documentation:
[`../../wiki/how-to/serve-a-docs-folder-as-a-website.md`](../../wiki/how-to/serve-a-docs-folder-as-a-website.md).

## Run the docs server

```text
python tools/serve_docs/serve_docs.py path/to/docs --name "my wiki"
powershell -ExecutionPolicy Bypass -File "%LLM_SHARED_DIR%\bin\mds.ps1" path\to\docs
```

Stop the server with Ctrl-C. Prefer the direct `python` call in a shell
that already has the environment (a `senv.bat` console). The `mds.ps1`
launcher covers shells with no Python on PATH; it is a PowerShell
script on purpose: a `.bat` wrapper would make cmd ask
"Terminate batch job (Y/N)?" on Ctrl-C, while PowerShell stops
cleanly.

## Flags of serve_docs.py

| Flag | Default | Role |
| --- | --- | --- |
| `docs_dir` | required | the folder of markdown files to serve |
| `--include` | none | extra folder or file served next to `docs_dir`, keeping the on-disk layout below their common ancestor; repeatable |
| `--root-include` | none | sibling file or folder mounted below its path relative to `docs_dir`'s parent while the primary folder stays at `/`; repeatable |
| `--name` | folder name | site name shown in the header |
| `--port` | from `serve_docs.ini` | server port for this run |
| `--no-browser` | off | do not open the browser once the server answers |

With `--include`, the served content is a snapshot copied at start time
(never links, so cleanup can never touch the originals): restart the
server to pick up file edits. Without `--include`, the folder is served
in place and edits rebuild live.

`--root-include` is also a start-time snapshot. It is useful when a wiki
must stay at `/` while a sibling presentation is expected at a URL such
as `/docs/deck.html`. Root includes must stay below `docs_dir`'s parent,
and cannot be combined with `--include`. Repository-relative Markdown links
that escape the primary folder are adjusted in the snapshot only, so MkDocs
validates their mounted targets while the checked-in sources remain correct.
Mounted Markdown stays outside the generated sidebar navigation.

## Per-folder configuration

A `serve_docs.ini` placed inside the served folder pins the site name,
port, and include list (one path per line, relative to the folder), so
a plain `serve_docs.py <folder>` call serves the full combined set:

```ini
[serve_docs]
name = my docs
include =
    ../architecture
    ../../README.md
```

Or preserve the primary folder at the site root and mount selected
sibling assets at repository-relative paths:

```ini
[serve_docs]
name = my wiki
root_include =
    ../docs/deck.html
    ../docs/logo.png
```

Command-line flags win over the per-folder file; the per-folder file
wins over the tool-level `serve_docs.ini` (port only).

## Port configuration

The default port lives in [`serve_docs.ini`](serve_docs.ini) next to the
script:

```ini
[serve_docs]
port = 8000
```

`--port` overrides it for one run without touching the file.

## What the rendering supports

- GitHub-flavored markdown: tables, fenced code blocks, emoji characters.
- ASCII and box-drawing diagrams stay aligned: the theme runs with
  `font: false`, so code blocks use the system monospace stack
  (Consolas, Menlo) whose box-drawing glyphs are monowidth, instead of
  the Roboto Mono webfont which lacks them. No external font is
  fetched.
- Raw inline HTML, so right-aligned `<img align="right">` logos render.
  Pages are served as one `.html` file per source file
  (`use_directory_urls: false`), so the relative paths inside raw HTML
  tags resolve exactly as they do on disk.
- Mermaid diagrams in ` ```mermaid ` fences (wired through
  `pymdownx.superfences`). Each rendered diagram gets a
  "⛶ full screen" link above it that opens the diagram alone in a new
  tab with mouse-wheel zoom around the pointer, drag to pan, and
  double-click to fit (injected by a scaffolded MkDocs hook, no file
  added to the served folder; the page theme colors are inlined so the
  standalone diagram keeps its look).
- Relative links and images between the served pages; `README.md` is
  served as the folder index (`index.html`). Links pointing outside the
  served content stay unresolved (MkDocs warns and keeps serving); pull
  their targets in with `--include` or `--root-include` when they matter.
- Explicit Diátaxis navigation when the conventional directories exist:
  Explanation, Tutorials, How-to guides, then Reference. Other folders
  follow alphabetically.
- One rendering difference from GitHub: python-markdown treats a line
  content starting with a literal `#` as a heading even without a
  following space, so an emoji such as the keycap `#`-sign at the start
  of a list item breaks the layout. Prefer emojis that do not start
  with `#`.

## Requirements of the tool

Only `uvx` (or `uv`) on PATH; the `bin\mds.ps1` launcher runs the
bundled venv Python, whose Scripts folder carries `uvx`. The first run
downloads
`mkdocs-material` into the uv cache, so the browser can take a moment
to open; later runs start in seconds.
