# LLM-specific Markdown adapters

Markdown under the root `instructions/`, `rules/`, `scripts/`, `templates/`,
`bin/`, `tools/`, `docs/`, and `wiki/` folders is canonical. Keep reusable
instruction, rule, skill, prompt, and documentation content only in those
folders.

Files registered for a particular LLM under `.agent/`, `.agents/`, `.claude/`,
`.github/`, `.grok/`, or another provider-specific folder are adapters, not sources.
They may keep front matter or other metadata required for discovery, but their
body must only direct the LLM to read and follow the canonical root file.

When adding or modifying an LLM-specific skill or prompt:

1. Add or update its canonical content in the appropriate root reference
   folder.
2. Keep the provider-specific file as a redirect to that root file. Point to
   the root file directly; do not route through another adapter.
3. Do not copy, summarize, or fork canonical content in the adapter.
4. Check all Markdown files for exact and substantially equivalent copies
   before finishing.

