# Add scaffolding for another LLM

Use this guide when your preferred LLM host is absent from the
[compatibility list](../reference/repository-layout.md#llm-compatibility), or
when you want native discovery instead of explicitly loading a shared file.
You need the llm-shared checkout and the host's current integration
documentation. For the concepts, read
[What scaffolding means here](../explanation/one-body-many-agents.md#what-scaffolding-means-here).

## 1. Choose the host's actual entry point

Check how the application loads custom instructions: a skill file, prompt,
workflow, plugin, or explicitly supplied document. Confirm the required folder,
metadata, registration scope, command syntax, and refresh behavior from that
host's documentation. Do not assume that a `.grok/`, `.claude/`, or `.agents/`
convention applies to another application using the same model.

Confirm that the host can access both the llm-shared clone and the consuming
project. Check the capabilities needed by your first skill, such as reading
and writing files or running shell tools. If it only accepts text, supply the
canonical instruction and its required references manually; describe that as
explicit loading rather than native skill discovery.

## 2. Select the shared instruction

Find the command in the [skills catalog](../reference/skills-catalog.md).
Read its canonical file and identify the rules, templates, supporting files,
and tools it requires. Start with one command, such as
[pause-session](../../instructions/pause-session.md).

Reuse these shared files. If the task itself needs a change, make that change
in its canonical instruction, rule, template, or tool. Follow
[llm-specific-adapters.md](../../rules/llm-specific-adapters.md); the new host's
adapter must not contain a copied or summarized version of the workflow.

## 3. Write a direct redirect with the required metadata

Create the file at the location required by your host. The following example
assumes an illustrative `.preferred/skills/pause-session/SKILL.md` inside the
llm-shared clone. `.preferred/` is not a real discovery convention; replace it
with the verified host layout and adjust the metadata to its schema.

```markdown
---
name: pause-session
description: Save the current session context for later continuation.
---

Read and follow [the canonical instruction](../../../instructions/pause-session.md).
```

The Markdown body is only the redirect. Link directly to the canonical file,
never through another provider's adapter. Keep host-required names,
descriptions, and invocation settings in metadata or the host registration.
Do not add shell commands, template copies, or alternate approval rules there.

Resolve the link from the path the host actually reads. Plugin caches and
copied adapters can have a different depth from the source tree; a link that
works in the clone may fail after installation. Use the host's documented
resource mechanism when appropriate and verify the installed target. Avoid
committing personal absolute paths in shared scaffolding; keep machine-specific
registration local.

## 4. Register it and exercise it in a scratch checkout

Perform the host's required registration and refresh. If the selected command
uses executable helpers, first
[set up the shared Python tools](set-up-shared-python-tools.md). Keep the
consuming checkout explicit and follow the shared shell-execution rule when
the skill calls a launcher.

Verify the integration with a small task in a disposable Git checkout:

1. Invoke the new entry point using the host's documented syntax. Confirm it
   reads the canonical instruction and the references that instruction needs.
2. For a pause adapter, give it a simple task to resume, such as reporting the
   current branch. Invoke pause and check the generated prompt is in the
   checkout's ignored artifact home, with the correct project root.
3. Add the equivalent resume redirect. Resume once and check the usage receipt
   appears before the saved task runs. Invoke resume again and check it stops
   as already used; then explicitly test `--force` rereading.
4. Confirm pending human decisions stay pending and that neither generated
   private artifact is staged. Use the
   [session guide](pause-and-resume-a-session.md) for the expected behavior.

If discovery fails, check registration, refresh state, installed paths, and
metadata before changing the shared instruction. If a required capability is
missing, report that limit instead of claiming the skill ran successfully.

## 5. Extend and document the coverage

Add redirects only for commands you intend to expose. Compare their targets
with the catalog, including aliases and commands whose filenames differ from
their names. Keep any required plugin manifest consistent with those files.

When contributing a new provider directory to llm-shared, include it in the
adapter inventory in
[`test_codex_plugin_structure_tdd.py`](../../tests/unit/tools/test_instruction_structure/test_codex_plugin_structure_tdd.py)
and follow the adapter rule's duplication check. Run the project's existing
Markdown and relevant structure checks; confirm that every redirect resolves
in the installed layout as well as in the source tree.

Update the README compatibility table and
[repository-layout reference](../reference/repository-layout.md#llm-compatibility)
with the host, entry-point location, command coverage, and what you actually
verified. Mark explicit loading separately from native discovery. For review
commands, retain the existing identity and ownership gates; do not invent a
recognized host identity or allow an agent to start its review counterpart.
