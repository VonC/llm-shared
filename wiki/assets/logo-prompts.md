# Logo prompts for the llm-shared themes

<img src="logo-llm-shared-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Five image-generation prompts: one flat 2D logo per theme, plus one
combined llm-shared logo. The shared style block keeps the five outputs
consistent; the palette reuses the presentation brand colors (deep blue
`#00566f`, orange `#ec6608`).

## 🎨 Shared style block appended to every prompt

> Flat 2D vector logo, sticker style, no text, no letters. Bold rounded
> outlines, simple geometric shapes, minimal detail, crisp edges. Vibrant
> palette built on deep teal-blue #00566f and warm orange #ec6608, with a
> light cream accent and one soft green highlight. Plain white background,
> centered composition, square canvas, suitable at 64x64 pixels.

## 1. 📝 The document pipeline

> A vertical cascade of three overlapping rounded document pages, each
> page marked with a small colored version tag shaped like a git tag
> (v1, v2, v3 as abstract dots, not letters), linked top to bottom by one
> bold arrow that starts as a scribble on the first page and ends as a
> neat numbered checklist on the last page — a raw idea maturing into a
> plan.

## 2. 🔁 Self-review and handoff

> Two thick arrows forming a circular loop around a single document. On
> the left of the loop, a speech bubble holding a large question mark; on
> the right, a speech bubble holding a check mark; at the bottom, a small
> round human figure placing a token into the loop — the machine asks,
> the human answers, the loop continues by itself.

## 3. 🧪 The groundhog test gate

> A cute round groundhog popping out of its burrow hole, facing a rising
> sun drawn as a circular gauge filled to the top, with three small
> stepping stones in front of the burrow each carrying a tiny check mark
> — the same day relived until the walk is flawless, one hundred percent
> reached.

## 4. 📊 The shared trail

> A git commit graph — a line of connected dots with one branch merging
> back — whose dots transform, left to right, into the bars of a rising
> bar chart, with a small release tag hanging from the tallest bar and a
> subtle paper-trail of tiny pages following the line — the history that
> tells its own story.

## 5. 🤖 llm-shared, the four themes combined

> A rounded chat-window frame (title bar with three dots) containing four
> mini-icons arranged in a two-by-two grid: a stack of versioned pages
> (top left), a circular review loop with a check mark (top right), a
> small groundhog in front of a filled gauge (bottom left), and a commit
> graph turning into a bar chart (bottom right), all four connected by a
> thin continuous line that flows from one quadrant to the next in
> reading order — one workflow, four movements, inside one conversation
> with the machine.

## 🏷️ Naming convention for the generated files

Mirror the senv wiki assets so each page can embed its theme logo:

| Theme | File |
| --- | --- |
| combined | `logo-llm-shared-transparent.png` |
| 📝 document pipeline | `logo-llm-shared-documents-transparent.png` |
| 🔁 self-review and handoff | `logo-llm-shared-review-transparent.png` |
| 🧪 groundhog test gate | `logo-llm-shared-groundhog-transparent.png` |
| 📊 shared trail | `logo-llm-shared-trail-transparent.png` |
