---
name: review-and-update-project-docs
description: 'Review code and update project markdown documentation files (README.md, ARCHITECTURE.md, docs/architecture/**). If no specific markdown target is mentioned in the prompt, all documentation files are updated. If no specific code is mentioned, a global code review is performed first to inform the documentation updates.'
argument-hint: 'Optionally specify which docs to update (e.g. "README.md only") and/or which code to review (e.g. "tools/git_batch_commit.py").'
---

## Step 1 — Parse the prompt

Check the prompt for two optional pieces of information:

1. **Target docs**: Is any specific markdown file mentioned?
   - Accepted targets: `README.md`, `ARCHITECTURE.md`, any file matching `docs/architecture/**/*.md`.
   - If one or more specific files are named → restrict updates to those files only.
   - If nothing is specified → update **all** target docs: `README.md`, `ARCHITECTURE.md`, and every file found under `docs/architecture/`.

2. **Code scope**: Is any specific file, folder, module, or symbol mentioned as the subject of the review?
   - If one or more specific items are named → review only those items.
   - If nothing is specified → perform a **global code review** covering all source files (see Step 2).

---

## Step 2 — Perform the code review

### 2a — If a specific code scope was provided

Read the named files or modules. For each one, note:

- Public API surface (exported functions, classes, constants).
- Key behaviors, algorithms, and notable constraints.
- Dependencies on other internal modules.
- Any patterns, conventions, or design decisions visible in the code.

### 2b — If no code scope was provided (global review)

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

### README.md

- Keep the project purpose, install / usage, and contributing sections consistent with what the code actually does.
- Update any command-line examples, environment-variable names, or script names that changed.
- Do **not** add architectural or design-level content to the README; that belongs in ARCHITECTURE.md or docs/architecture/.

### ARCHITECTURE.md

- Reflect the actual module boundaries, layering, and data-flow visible in the code.
- Update component diagrams or textual descriptions when module names or responsibilities changed.
- Do **not** include step-by-step usage instructions; those belong in README.md.

### docs/architecture/\*.md

- Each file in this folder covers one architectural concern (e.g. a subsystem, an ADR, a data model).
- Update only the files whose subject was touched by the reviewed code.
- If the review reveals that a new architectural concern now warrants its own doc, create a new file under `docs/architecture/` and note it explicitly in your output.

---

## Step 5 — Report

After all updates, provide a short summary listing:

- Which docs were updated and why.
- Which docs were left unchanged and why.
- Any new docs created.
- Any open questions about intent or design that the code review could not resolve from the code alone, formatted as a bullet list.
