---
applyTo: "**"
---

# Preserve existing code

When writing or rewriting any file, write it in full — never use placeholder comments like `# ...existing code...` or `// ... existing code ...` to skip sections.

You MUST:

- write every file from top to bottom, including its header comment or docstring, its imports, any helper definitions, and the main content itself, in full.
- preserve all relevant comments, any small inline comments like `// Act`, `// Assert`, `// TODO`, etc: all MUST be preserved, unless they are no longer relevant in the current rewrite.
- preserve all relevant docstrings and block comments, trimming only those that are explicitly made obsolete by the change being applied.
