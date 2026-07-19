# How to split a large file

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🧪 Goal: bring a Python file over the line budget (big means more than 650
lines; aim under 550) back under it, by splitting it into files with
single responsibilities — never by trimming content.

## Invocation model

The AI normally invokes the split-large-file skill after a size threshold or an
implementation review identifies the need. It performs the extraction and
validation while preserving behavior. Use this guide directly when refactoring
without the skill or when checking the AI's proposed boundaries.

## 🚨 When the split triggers

Three callers reach for `/split-large-file`: the check step of a
`ghog day` walk ("Big files found" — ghog reports over-limit files, never
splits), an `/implementation-check` that flags a file doing too many
unrelated things, and a direct request.

## 📋 Steps of the split

1. Run the skill with the file in context:

   ```txt
   /split-large-file
   ```

2. The skill writes a short analysis first: the responsibilities it sees
   and the split it intends.

3. It then creates one file per responsibility, named
   `<original>_<xxx>.py` (test files keep their `_tdd.py` or `_pbt.py`
   suffix, with `_xxx` inserted before it). Every class is written in
   full, comments and docstrings preserved; the original becomes a thin
   shell or disappears.

4. `__init__.py` files are updated for the new modules, and imports are
   checked against the DDD-Hexagonal layering.

5. The skill verifies with a `ghog day` loop — a "Big files found" stop
   midway through a split is expected, and clears once every piece is
   under budget.

6. It ends by writing (not committing) a commit message covering only the
   modified files.

## ✅ Check after the split

Every new file is under 550 lines, `ghog day` runs green, and no assertion
or docstring was lost — the split moved code, it did not rewrite it.

Related: [Fix a red groundhog walk](fix-a-red-groundhog-walk.md),
[Writing rules](../reference/writing-rules.md) for the preserve-code rule.
