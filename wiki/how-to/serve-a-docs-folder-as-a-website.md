# Serve a markdown folder as a local website

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

🤖 Browse a folder of markdown files (a project wiki, a docs tree) as a
rendered website in the browser, with working relative links, images,
raw HTML and Mermaid diagrams. The server runs locally, installs
nothing permanently, and writes nothing inside the served project.

## Invocation model

This is primarily a human-run local preview command: start it when you want to
browse the rendered documentation and stop it with Ctrl+C. The AI may start or
configure it when explicitly asked, but it is not an implicit phase of the
documentation-review skills. Direct invocation is therefore the normal choice
for visual inspection, link checking, and authoring feedback.

## When to reach for the docs server

- Reviewing documentation the way readers will see it, instead of as
  raw markdown in an editor.
- Checking that relative links, right-aligned logo images and Mermaid
  diagrams actually render. Each Mermaid diagram gets a
  "⛶ full screen" link that opens it alone in a new tab for zooming.
- Walking someone through a wiki on a call, from a plain browser tab.

## Start the server on a folder

From a shell that has Python (a project senv console):

```text
python "%LLM_SHARED_DIR%\tools\serve_docs\serve_docs.py" path\to\docs
```

From any other shell, the `mds.ps1` launcher self-locates the bundled
Python (a PowerShell wrapper on purpose: interrupting a `.bat` makes
cmd ask "Terminate batch job (Y/N)?", while this one stops cleanly):

```text
powershell -ExecutionPolicy Bypass -File "%LLM_SHARED_DIR%\bin\mds.ps1" path\to\docs
```

The tool scaffolds a temporary MkDocs Material configuration around the
folder, starts `mkdocs serve` on `http://127.0.0.1:8000/`, and opens
the browser once the server answers. The first run downloads
`mkdocs-material` into the uv cache and takes a moment; later runs
start in seconds. Stop with Ctrl-C.

`README.md` files are served as folder indexes, and the navigation
sidebar is derived from the folder structure.

## Change the port or the site name

The default port lives in `tools\serve_docs\serve_docs.ini`
(`port = 8000`). For one run:

```text
python "%LLM_SHARED_DIR%\tools\serve_docs\serve_docs.py" path\to\docs --port 8123 --name "my wiki"
```

`--no-browser` starts the server without opening a browser tab.

## Serve several folders that link to each other

When the docs folder links to sibling folders or to files at the
repository root (a wiki pointing at `../architecture/` pages or at the
root `README.md`), pull those targets in with repeatable `--include`
flags. The tool assembles a start-time snapshot that keeps the on-disk
layout below the common ancestor, so every relative link between the
included parts resolves:

```text
python "%LLM_SHARED_DIR%\tools\serve_docs\serve_docs.py" docs\wiki --include docs\architecture --include README.md
```

With `--include` the served content is a snapshot: restart the server
to pick up edits. Without it, the folder is served in place and edits
rebuild live.

Use `--root-include` when the primary folder must remain at the site
root but selected sibling assets need their repository-relative URL.
For example, serving `wiki` with the following mount keeps its
`README.md` at `/` and exposes the presentation at `/docs/deck.html`:

```text
python "%LLM_SHARED_DIR%\tools\serve_docs\serve_docs.py" wiki --root-include docs\deck.html
```

`--include` and `--root-include` are two different snapshot layouts and
cannot be combined in one invocation.

When a root snapshot flattens the primary folder from `wiki/` to `/`, the tool
adjusts only the copied Markdown links that originally escaped `wiki/`. The
checked-in links therefore remain correct in the repository, while MkDocs can
validate the mounted targets without warnings. Mounted Markdown is available as
a link target but does not acquire an extra sidebar section.

Rather than typing the flags each time, pin them in a
`serve_docs.ini` inside the docs folder itself (one include path per
line, relative to the folder); a plain call then serves the full set:

```ini
[serve_docs]
name = my docs
include =
    ../architecture
    ../../README.md
```

The equivalent configuration for repository-relative root mounts is:

```ini
[serve_docs]
name = my wiki
root_include =
    ../docs/deck.html
    ../docs/logo.png
```

When the served folder contains the four Diátaxis directories, the
generated left navigation always orders them as Explanation, Tutorials,
How-to guides, then Reference. Pages inside each section remain sorted by
filename.

## Add a project alias

A project can pin its own docs tree behind a Doskey alias in its
`senv.doskey`, so one short command serves the right set (the include
list living in the folder's `serve_docs.ini`). Call the script through
`python` directly, never through a `.bat`: Ctrl-C then stops the
server cleanly instead of asking cmd's "Terminate batch job (Y/N)?"
question:

```text
wserve=python "%LLM_SHARED_DIR%\tools\serve_docs\serve_docs.py" "%PRJ_DIR%\docs\wiki" $*
```

## Limits to know about

- Links pointing outside the served content stay unresolved: MkDocs
  warns on the console and keeps serving everything else. Include the
  targets that matter with `--include`, or use `--root-include` when the
  primary docs folder must remain at `/`.
- The rendering is MkDocs Material, close to but not identical to the
  GitHub/Gitea style. One notable difference: python-markdown treats a
  literal `#` at the start of a list item as a heading even without a
  space, so avoid emojis that begin with the `#` character.

Related: [Aliases and bin launchers](../reference/aliases-and-launchers.md) and
[automation versus direct invocation](../reference/automation-and-direct-invocation.md).
