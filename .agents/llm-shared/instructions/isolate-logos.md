# isolate-logos instruction

Split one AI-generated logo sheet — a single image holding several logos in
a uniform grid on a near-white background — into individual PNG assets, one
opaque and one transparent file per logo. This is the full workflow behind
the `isolate-logos` skill.

## Goal for the logo isolation

From the sheet image and the list of cell names the user gives, produce in
the target assets folder, for each kept logo:

- `<base>.png`: the logo auto-cropped to its content, centered on a square
  white canvas with a small margin,
- `<base>-transparent.png`: the same, with the background made transparent
  by flood fill from the borders, so white inside the artwork survives.

## Collect the isolation inputs

Ask for (or infer from the conversation) what is not already given:

| Input | How to resolve it |
| --- | --- |
| sheet image path | given by the user (often a download or a pasted image saved to disk) |
| grid shape | count the logos per row on the image itself; pass `--cols` |
| cell names, in reading order | from the themes the logos represent; `-` for a duplicate or empty cell to skip |
| output folder | the project convention, for example `wiki/assets/` |
| filename prefix | the project convention, for example `logo-<project>` |

When one logo is the project-wide emblem combining the others, give it an
explicit base name with the `name=basename` form (for example
`combined=logo-cplx`) so it lands as `logo-<project>.png` instead of
`logo-<project>-combined.png`.

## Run the isolation script

Before running the command, read
[`../rules/run_commands.md`](../rules/run_commands.md).

```text
uv run --with pillow python <llm-shared>/tools/isolate_logos/isolate_logos.py \
    sheet.png --out-dir wiki/assets --cols 3 \
    --names download,bridge,forge,-,ship,combined=logo-cplx \
    --prefix logo-cplx
```

The script splits the sheet into `--cols` × (derived rows) cells, finds the
content bounding box of each kept cell, pads it square (6% margin by
default), and writes both PNG versions. Flags are described in
[`../tools/isolate_logos/README.md`](../tools/isolate_logos/README.md).

## Verify the produced assets

Always check the result visually — read each `-transparent.png` back:

- the crop holds one complete logo, nothing from a neighboring cell,
- white *inside* the artwork (paper, checkmarks, highlights) is still
  there: only the outer background may have disappeared,
- soft glows around shapes are artwork, not background; keep them.

If a logo bleeds into a neighboring cell on the sheet, the uniform grid
assumption is broken: crop that cell manually or regenerate the sheet.

## Adjust when the defaults fail

| Symptom | Adjustment |
| --- | --- |
| pale artwork areas turned transparent | raise `--white-threshold` (only nearly pure white counts as background) |
| faint specks or gray residue treated as content (bbox too wide, residue kept opaque) | lower `--white-threshold` so those pale pixels count as background |
| logos touching the canvas edge | raise `--margin` |
| "cell contains only background" error | the names list does not match the real grid; recount rows and columns |
| a wide logo clipped at its cell edge | the grid is not uniform: measure the split positions on the sheet and pass `--col-splits` (and `--row-splits`) as fractions, e.g. `--col-splits 0.31,0.70` |

A thin sliver of a neighboring logo inside a cell is handled automatically:
the crop drops small border-touching fragments, so only a genuinely clipped
(large, border-touching) logo requires the split overrides.

## Wire the assets into the documentation

When the assets back a wiki (Diátaxis-style, as in senv or cplx), the
naming convention is one square-ish image per theme plus one for the
project as a whole: `logo-<project>-<theme>[-transparent].png` and
`logo-<project>[-transparent].png`. Pages reference the transparent
variants with a right-aligned image of height 90:

```html
<img src="../assets/logo-<project>-<theme>-transparent.png" alt="" height="90" align="right">
```
