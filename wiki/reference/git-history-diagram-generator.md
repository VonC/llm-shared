# Git-history diagram generator

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📊 Exact interface and output contract for the deterministic SVG generator in
`tools/git_history_diagrams/`.

![The generator's feature-integration scenario uses a dashed rebase arrow followed by a solid merge arrow.](../assets/prepare-release/feature-to-develop.svg)

## Invocation model

This generator is normally run directly by a documentation maintainer, or by the
AI when asked to update the Git-history documentation. It is not called by the
release workflow itself. Direct invocation is useful for regenerating one or all
stable SVG assets during visual iteration.

## Entry points

| Entry point | Meaning |
| --- | --- |
| `bin\git_history_diagrams.bat` | Self-locating launcher; preferred from scripts and agents |
| `ghdiag` | Interactive Doskey alias loaded by `senv.bat` |
| `tools\git_history_diagrams\generate_git_history_diagrams.py` | Python implementation; use for development, not from consuming projects |

## Options

| Option | Meaning |
| --- | --- |
| `--output-dir PATH` | Override the default `wiki/assets/prepare-release/` destination |
| `--check` | Write nothing; return nonzero when an expected SVG is missing or stale |
| `--list` | Print scenario slugs and write nothing |

## Scenarios and outputs

| Scenario | SVG |
| --- | --- |
| Feature rebased and integrated into develop | `feature-to-develop.svg` |
| Stale main-based feature promoted directly | `feature-direct-to-main.svg` |
| One develop-tested feature isolated and promoted | `feature-from-develop-to-main.svg` |
| Every validated develop topic promoted together | `develop-to-main.svg` |

## Stable visual contract

| Visual | Meaning |
| --- | --- |
| Blue / orange / green / purple | main / develop / feature / promotion-copy roles |
| Thin solid line | ordinary ancestry |
| Thick solid arrow | `merge --no-ff` |
| Dashed arrow | rebase or exact-range replay; destination commits have new identities |

![The selective-release scenario distinguishes the develop integration merge from the main release merge.](../assets/prepare-release/feature-from-develop-to-main.svg)

Each SVG has an accessible `title` and `desc`, a fixed `viewBox`, an embedded
legend, and no external font, script, stylesheet, or image dependency.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Generation, listing, or freshness check succeeded |
| `1` | `--check` found one or more missing or stale SVGs |
| `2` | Invalid command-line input |

Related, in Diátaxis order: [visual rationale](../explanation/why-git-history-diagrams-use-explicit-arrows.md),
[generation tutorial](../tutorials/07-generate-git-history-diagrams.md), and
[update guide](../how-to/update-git-history-diagrams.md).
