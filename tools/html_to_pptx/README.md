# HTML deck to editable PowerPoint

<img src="../../wiki/assets/logo-llm-shared-trail-transparent.png" alt="" height="90" align="right">

This folder rebuilds a browser HTML slide deck as a native Microsoft
PowerPoint file whose every element stays editable: real text boxes and real
vector shapes, no pictures. It exists so the method used to convert
`docs/llm-shared_presentation.html` is not lost and can be reused for any
other HTML deck.

## 🎯 The one rule for this tool

Text and vector shapes only. No slide is ever a screenshot or an embedded
image. A reader must be able to click any title, bullet or box in PowerPoint
and change the words, the color or the position.

This rules out the quick path (screenshot each HTML slide, drop the PNG on a
slide). That path looks identical to the browser but freezes the content:
nobody can fix a typo or reflow a box. The whole point here is the opposite.

## 📐 Why the pixel coordinates transfer for free

An HTML deck authored on a fixed pixel canvas maps one-to-one onto a
PowerPoint slide of the same aspect ratio:

- the HTML slides are `1280 x 720` px (a `.slide` block in the source CSS).
- the target PowerPoint slide is `13.333in x 7.5in`, the 16:9 widescreen
  size.
- `1 px = 13.333/1280 in` across and `7.5/720 in` down. For a matched 16:9
  ratio those two factors are equal (`0.010416...`).

So the `x`, `y`, `width`, `height` read straight out of the HTML become slide
coordinates with a single multiply. No re-layout, no eyeballing. `Theme.inx`
and `Theme.iny` in `pptx_helpers.py` do that multiply.

## 🗂️ Files in this folder

| File | Role |
| --- | --- |
| `pptx_helpers.py` | Generic, deck-agnostic drawing primitives and components. Import these. |
| `build_llm_shared_pptx.py` | Worked example: the full 16-slide llm-shared deck built on the helpers. Copy this per new deck. |
| `make_pptx.ps1` | One-line wrapper: installs `python-pptx` if missing, then rebuilds the `.pptx` (with brand env vars applied). |
| `make_pdf.ps1` | One-line wrapper: runs `make_pptx.ps1`, then exports the deck to `.pdf` through PowerPoint. |
| `export_preview.ps1` | Verification aid: export the finished `.pptx` back to PNG through PowerPoint to compare against the HTML. |
| `__init__.py` | Marks the folder as a package. |

## 📦 Prerequisites for the conversion

- Python with the `python-pptx` library: `python -m pip install python-pptx`.
- To verify the look afterwards, Microsoft PowerPoint installed (only for
  `export_preview.ps1`; not needed to build the deck).

## ▶️ Rebuild the llm-shared deck

From the repository root, one line per format:

```bat
powershell -File tools\html_to_pptx\make_pptx.ps1
powershell -File tools\html_to_pptx\make_pdf.ps1
```

`make_pptx.ps1` installs `python-pptx` when it is missing, then runs
`build_llm_shared_pptx.py`, which writes `docs\llm-shared_presentation.pptx`
(16 slides) and prints the slide count and file size. `make_pdf.ps1` runs
`make_pptx.ps1` first, then drives the installed PowerPoint through COM
(SaveAs format 32 = ppSaveAsPDF) to write
`docs\llm-shared_presentation.pdf`, so the PDF pages match the editable deck
one for one. Both scripts resolve their own paths, so the working directory
does not matter. The underlying direct call still works:

```bat
python tools\html_to_pptx\build_llm_shared_pptx.py
```

Both outputs are generated files and are gitignored (`docs/llm-shared_presentation.pptx`
explicitly, the PDF through the top-level `*.pdf` rule): do not commit them,
rebuild them on demand from the HTML source of truth.

## 🏷️ Branding through environment variables

The build reads two environment variables and falls back to the neutral
placeholders when they are not set:

| Variable | Replaces | Fallback |
| --- | --- | --- |
| `LLM_SHARED_BRAND` | the brand line on every slide | `Organization name` |
| `LLM_SHARED_BRAND_SUB` | the small line under the brand | `ORGANIZATION SUBTITLE` |

This mirrors the HTML deck, which swaps the same two values at render time
through `llm-shared_presentation.local.js`. A static `.pptx` or `.pdf` runs no
script, so the substitution happens at build time instead: set the variables
(or pass `-Brand` / `-BrandSub` to either wrapper script) and rebuild.

```bat
powershell -File tools\html_to_pptx\make_pptx.ps1 -Brand "ACME" -BrandSub "IT DIVISION"
powershell -File tools\html_to_pptx\make_pdf.ps1 -Brand "ACME" -BrandSub "IT DIVISION"
```

## ✅ Check the result against the HTML

```bat
powershell -File tools\html_to_pptx\export_preview.ps1
```

This exports every slide to PNG in a temp folder and lists them. Open the
folder, open the HTML in a browser, and walk both side by side. The PNGs are
only for your eyes during the check -- the deck you ship stays fully editable.

## 🧱 Building blocks in pptx_helpers.py

The helpers split into four groups. A run is one styled span of text; a
paragraph holds several runs, which is how a black sentence carries an orange
`/slash-command` in the middle (the HTML inline `<code>` look).

- Geometry and scaffolding: `Theme`, `rgb`, `make_presentation`,
  `blank_slide`, `fill_background`.
- Text: `run`, `add_paragraph`, `textbox`.
- Shapes: `rect` (square or rounded, filled or outlined), `oval` (step
  badges), `box` (a rounded box with a centered main line and optional
  caption), `arrow` (a small connector glyph).
- Ready-made components and page chrome: `card`, `feature_item`,
  `feature_row`, `header` (brand line, topic tag, two-tone accent bar),
  `title` (title plus subtitle), `footer` (caption plus page number).

## 🧭 Method for converting a new HTML deck

1. Read the source. Note the canvas size (the `.slide` width and height in
   the CSS) and the brand colors (often CSS `:root` variables).
2. Copy `build_llm_shared_pptx.py` to `build_<yourdeck>_pptx.py`. Set the
   output path, the palette constants, and a `Theme`. If the canvas is not
   `1280 x 720`, pass `canvas_px_w` and `canvas_px_h` to `Theme`.
3. Write one function per slide. For each HTML element, read its pixel
   `x/y/width/height` and its colors, then draw the matching primitive at the
   same numbers. Straight text becomes `textbox` + `add_paragraph`; a colored
   panel becomes `rect`; a flow box becomes `box`; a numbered badge becomes
   `oval`.
4. For a diagram the primitives do not cover directly (a flow column, a step
   row), write a small local composition, the way `loop_col`, `wf_row` and
   `step_row` do in the example. Keep such compositions in the per-deck build
   script, not in `pptx_helpers.py`, so the shared module stays generic.
5. Run the build script, then run `export_preview.ps1` and compare against
   the HTML. Nudge coordinates or font sizes until the two match.

## 🔤 Font sizing note

The HTML font sizes are pixel values scaled by a root `rem` base. In the
example they are carried over as point sizes picked for readability rather
than by a strict formula (a title around `21 pt`, body text around `10 pt`).
A workable starting rule is `point size = html_px * 0.8`; adjust per slide
during the visual check.

## 📎 Two carried-over details

- Brand placeholders. The HTML swaps `Organization name` and its subtitle at
  runtime through `llm-shared_presentation.local.js`. A static `.pptx` runs no
  script, so the build script reads `LLM_SHARED_BRAND` and
  `LLM_SHARED_BRAND_SUB` at build time instead (see "Branding through
  environment variables" above). When neither is set, the placeholders stay as
  plain editable text: Find and Replace in PowerPoint remains a last-resort
  option on an already-built deck.
- Omitted logo. The HTML title slide shows a product logo image. Because this
  tool draws no pictures, the example leaves it out. Add it back by hand in
  PowerPoint if a logo is wanted on the title and closing slides.

## 💯 Coverage gate

The build and preview scripts are a rendering seam that needs `python-pptx`
and PowerPoint to exercise, so `pyproject.toml` omits `*/html_to_pptx/*` from
the coverage source, the same way `groundhog/render.py` is omitted. They are
run on demand, not part of the tested library surface.
