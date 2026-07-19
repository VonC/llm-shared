# Why Git history diagrams use explicit arrows

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

This is a documentation-maintenance tool, not a hidden prepare-release step.
A human maintainer—or an AI asked to update the documentation—runs `ghdiag`
after scenario changes. Direct execution is the normal path; `--check` is the
non-writing freshness gate.

📊 A release diagram must distinguish two operations that can produce the
same final files but very different histories. A rebase copies commits and
changes their identities; a merge connects existing histories and records a
selection decision.

## The visual grammar

The diagrams deliberately use a small, stable vocabulary:

- blue is `main`, the release and tag branch;
- orange is `develop`, the long-lived integration branch;
- green is feature work;
- purple is a temporary promotion copy;
- a dashed arrow is a rebase or exact-range replay that creates new commits;
- a thick solid arrow is a `merge --no-ff` that preserves both parents;
- a thin solid line is ordinary first-parent or branch ancestry.

![A develop-tested feature is isolated, replayed onto main with a dashed arrow, and accepted by a solid merge.](../assets/prepare-release/feature-from-develop-to-main.svg)

Colors identify roles; line styles identify Git semantics. The meaning does
not depend on color alone, so the SVG remains readable in monochrome and for
readers with color-vision differences.

## Why the diagram is generated

Hand-edited pictures drift easily: a caption says "no rebase" while an old
arrow still implies one, or two pages silently use different colors for the
same branch. The declarative scenarios under `tools/git_history_diagrams/`
are rendered into deterministic, accessible SVG files. A freshness check can
then prove that the committed assets still match their source.

The renderer is intentionally specific to Git histories, not a general
drawing package. Its job is to make branch roles, commit identity changes,
and release-selection boundaries unambiguous in workflow documentation.

![When every validated topic is ready, develop is merged into main without any rebase arrow.](../assets/prepare-release/develop-to-main.svg)

Related, in Diátaxis order: [generate the diagrams for the first time](../tutorials/07-generate-git-history-diagrams.md),
[update a scenario](../how-to/update-git-history-diagrams.md), and the
[generator reference](../reference/git-history-diagram-generator.md).
