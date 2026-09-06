# Agent instructions

## 🐚 Running shell commands

Before any tool call that runs a shell command, follow `rules/run_commands.md`: read and search files with the harness file tools, never through an environment wrapper; when a wrapper is required, chain exactly one simple command with no nested shell quoting; read targeted slices, never whole-document dumps; and when a command fails with a quoting or parse error, rewrite it simpler instead of re-running or escalating it.

## Review role isolation

Whenever acting in a review exchange, follow the role-session isolation rules
in `instructions/review-requestor.md`. A requestor publishes and then waits; it
must never spawn, start, delegate, invoke, or message a reviewer agent or
session. A reviewer reviews or waits and must never spawn, start, delegate,
invoke, or message a requestor agent or session. Each role rejects a task
initiated by the automated counterpart.

## groundhog (pytest reset loop)

To drive the test suite to its global objective (every test passing, coverage at the project gate), follow the instructions from `instructions/groundhog.md`. Trigger this whenever the user asks to run groundhog, ghog, or to fix tests and coverage.

A walk is finished only when `a.ghog.status` at the project root reads `state=done` - a growing `a.ghog.log` proves nothing. Poll with `ghog status` (never redirected, never replaced by a direct read of `a.ghog.status` - only the command probes the recorded pid: exit 6 while the walk is live, 7 when it was killed), and when the harness can kill long calls, run the walk detached (`ghog day --detach`, no redirect) as that instruction describes - never size a timeout around a walk, never rerun one that may still be alive.

## Diataxis documentation order

Whenever a task creates or maintains a Diataxis documentation set, present
and link its categories in this order: explanation, tutorials, how-to guides,
then reference. Keep every page focused on exactly one Diataxis purpose.

## LLM-specific Markdown adapters

When adding or modifying an LLM-specific skill, prompt, workflow, or other
Markdown adapter, follow `rules/llm-specific-adapters.md`.
