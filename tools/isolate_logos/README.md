# isolate_logos tool

Split one AI-generated logo sheet (a uniform grid of logos on a near-white
background) into per-logo PNG files: for each kept cell, an opaque square
version on white and a matching `-transparent` version.

Workflow documentation: [`../../instructions/isolate-logos.md`](../../instructions/isolate-logos.md).

## Run the isolation

```text
uv run --with pillow python tools/isolate_logos/isolate_logos.py sheet.png \
    --out-dir wiki/assets --cols 3 \
    --names download,bridge,forge,-,ship,combined=logo-cplx \
    --prefix logo-cplx
```

## Flags of isolate_logos.py

| Flag | Default | Role |
| --- | --- | --- |
| `sheet` | required | the grid image to split |
| `--out-dir` | required | destination folder for the PNG files |
| `--cols` | required | grid columns; rows are derived from the name count |
| `--names` | required | cell names in reading order; `-` skips a cell; `name=basename` overrides the output base |
| `--prefix` | `logo` | base names default to `<prefix>-<name>` |
| `--margin` | `0.06` | margin around the logo on its square canvas |
| `--white-threshold` | `242` | channel value from which a pixel counts as background |
| `--col-splits` | uniform | interior column split fractions (cols-1 values, e.g. `0.31,0.70`) for non-uniform grids |
| `--row-splits` | uniform | interior row split fractions (rows-1 values) for non-uniform grids |

## What each cell produces

| Output | Content |
| --- | --- |
| `<base>.png` | logo auto-cropped, centered on a white square canvas |
| `<base>-transparent.png` | same, background flood-filled to alpha 0 from the borders |

The transparency pass only clears background connected to the cell borders,
so white areas inside the artwork (paper, checkmarks, highlights) survive.

The content crop groups non-background pixels into connected components and
drops small components touching the cell border: a sliver of a neighboring
logo bleeding into the cell is ignored instead of widening the crop. A large
component touching the border is kept — that is a logo wider than its
uniform cell, which calls for explicit `--col-splits`/`--row-splits`.
