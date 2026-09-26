# Review and update project documentation

## Step 1 — Parse the prompt

Check the prompt for two optional pieces of information:

1. **Target docs**: Is any specific markdown file or documentation root mentioned?
   - Accepted targets: `README.md`, `ARCHITECTURE.md`, files matching
     `docs/architecture/**/*.md`, and existing Diataxis roots under `wiki/`
     or `docs/wiki/`.
   - A named `wiki/` or `docs/wiki/` directory selects every Markdown page
     under that root.
   - If one or more specific targets are named → restrict updates to those
     targets only.
   - If nothing is specified → update **all** existing target docs, including
     both Diataxis roots when both are present.

2. **Review scope**: Is a Git range or any specific file, folder, module, or
   symbol mentioned as the subject of the review?
   - If a Git range such as `v1.2.3..HEAD` is named → review every commit and
     the resulting tree change in that range.
   - If one or more specific items are named → review only those items.
   - If nothing is specified → perform a **global code review** covering all source files (see Step 2).

---

## Step 2 — Perform the code review

### 2a — If a Git range was provided

Read the commit subjects, changed-file list, and relevant diffs for every
commit in the range. Build a topic inventory that records:

- user-visible behavior and workflow changes;
- commands, configuration, file formats, and compatibility changes;
- fixes whose old behavior may still be described in the docs;
- documentation already changed by the commits.

Review the final state at the range tip before writing. Do not document a
change that a later commit in the same range reverted or replaced.

### 2b — If a specific code scope was provided

Read the named files or modules. For each one, note:

- Public API surface (exported functions, classes, constants).
- Key behaviors, algorithms, and notable constraints.
- Dependencies on other internal modules.
- Any patterns, conventions, or design decisions visible in the code.

### 2c — If no review scope was provided (global review)

Scan the full source tree. Cover at minimum:

- Every non-test Python file under `tools/` and `src/` (if present).
- Entry-point scripts at the project root.
- `pyproject.toml` / `setup.cfg` / `setup.py` for declared dependencies, scripts, and metadata.
- Test tree layout under `tests/` to understand feature coverage.

For each area, capture the same items as in 2a. Build a **structured summary** that groups related modules into functional areas (e.g. CLI layer, core logic, shared utilities, models, git helpers, …).

---

## Step 3 — Cross-reference the current documentation

Read each target markdown file that exists on disk. For every section or claim in the doc, compare it to the code-review findings and flag:

- **Outdated**: content that no longer matches the code.
- **Missing**: features, modules, or behaviors present in the code but absent from the doc.
- **Inaccurate**: descriptions that are misleading or incomplete.
- **Correct**: content that already matches and needs no change.

---

## Step 4 — Update the target documentation

For each target doc, rewrite only the sections that are outdated, missing, or inaccurate. Preserve all sections already marked correct and all editorial choices (tone, structure, heading hierarchy) that are not contradicted by the code.

Specific rules per doc:

### README.md content rules

- Keep the project purpose, install / usage, and contributing sections consistent with what the code actually does.
- Update any command-line examples, environment-variable names, or script names that changed.
- Do **not** add architectural or design-level content to the README; that belongs in ARCHITECTURE.md or docs/architecture/.

### ARCHITECTURE.md content rules

- Reflect the actual module boundaries, layering, and data-flow visible in the code.
- Update component diagrams or textual descriptions when module names or responsibilities changed.
- Do **not** include step-by-step usage instructions; those belong in README.md.

### docs/architecture/\*.md content rules

- Each file in this folder covers one architectural concern (e.g. a subsystem, an ADR, a data model).
- Update only the files whose subject was touched by the reviewed code.
- If the review reveals that a new architectural concern now warrants its own doc, create a new file under `docs/architecture/` and note it explicitly in your output.

### Diataxis wiki content rules

- Work only in a `wiki/` or `docs/wiki/` root that already exists. Do not
  create a new wiki root as part of an ordinary project-docs review.
- Keep every page focused on one purpose: explanation, tutorial, how-to guide,
  or reference.
- Present and link categories in this order: explanation, tutorials, how-to
  guides, then reference.
- Update the smallest set of pages that covers the reviewed behavior. A change
  does not need a page in all four categories.
- Prefer an existing page with the matching purpose. Create a new page only
  when no existing page can cover the topic without mixing purposes.
- For a Git-range review, account for every topic in the inventory and report
  any topic that has no suitable wiki coverage.

---

## Step 5 — Validate

- Check that changed relative links resolve.
- Check that each changed wiki page still serves one Diataxis purpose.
- Check wiki navigation and cross-links for the required category order.
- Run focused documentation or structure tests when the project provides them.

---

## Step 6 — Report

After all updates, provide a short summary listing:

- Which docs were updated and why.
- Which docs were left unchanged and why.
- Any new docs created.
- For a Git-range review, which release topics were mapped to which wiki pages.
- Any open questions about intent or design that the code review could not resolve from the code alone, formatted as a bullet list.

When `a.prepare-release.active` exists in the review artifact home (`.reviews`
unless `.review-artifacts.ini` declares another home), return this report
to the calling `prepare-release` workflow. Do not end with a standalone next
step.
