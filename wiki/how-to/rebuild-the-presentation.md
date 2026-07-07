# How to rebuild the presentation as PPTX and PDF

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📊 Goal: regenerate `docs\llm-shared_presentation.pptx` and
`docs\llm-shared_presentation.pdf` from the HTML slide deck, with your own
branding.

## 🎞️ What the converter produces

The source of truth is `docs\llm-shared_presentation.html`, a
self-contained 16-slide deck telling the workflow story from raw idea to
tagged release. `tools\html_to_pptx\` rebuilds it as a native, editable
PowerPoint: real text boxes and vector shapes, no screenshots. Both
outputs are gitignored and rebuilt on demand.

## 📋 One-line generators

From the repository root:

```powershell
powershell -File tools\html_to_pptx\make_pptx.ps1
powershell -File tools\html_to_pptx\make_pdf.ps1
```

`make_pptx.ps1` installs `python-pptx` if missing, runs
`build_llm_shared_pptx.py`, and prints the slide count and file size.
`make_pdf.ps1` runs the pptx build first, then drives an installed
PowerPoint through COM (`SaveAs` format 32) to write the PDF. Direct call,
when the environment is already set:

```cmd
python tools\html_to_pptx\build_llm_shared_pptx.py
```

## 🏷️ Branding the outputs

The HTML deck brands itself at render time: it loads
`docs\llm-shared_presentation.local.js` (seed it from the checked-in
`.local.js.example`) and reads `brand_name` and `brand_subtitle` from
`llmSharedPresentationLocal`, falling back to placeholder text.

The static PPTX and PDF run no JavaScript, so the same values are passed
at build time instead, either as environment variables or as wrapper
parameters:

```powershell
powershell -File tools\html_to_pptx\make_pptx.ps1 -Brand "My Company" -BrandSub "My Motto"
```

`LLM_SHARED_BRAND` and `LLM_SHARED_BRAND_SUB` are the matching variables.

## 🧱 Reusing the drawing layer

`tools\html_to_pptx\pptx_helpers.py` is deck-agnostic: a `Theme` with the
px-to-inch mapping (1280x720 px to 13.333x7.5 in) and primitives such as
`textbox`, `card`, `arrow`, `header` and `footer`.
`build_llm_shared_pptx.py` is the worked example that mirrors the 16 HTML
slides with them; copy its pattern to build another deck.

## ✅ Check the outputs

The PPTX opens with 16 editable slides carrying your brand name in the
headers; the PDF matches it page for page.

Related: [Repository layout](../reference/repository-layout.md).
