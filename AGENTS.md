# Agent instructions

## Running shell commands

Before any tool call that runs a shell command, follow `rules/run_commands.md`: read and search files with the harness file tools, never through an environment wrapper; when a wrapper is required, chain exactly one simple command with no nested shell quoting; read targeted slices, never whole-document dumps; and when a command fails with a quoting or parse error, rewrite it simpler instead of re-running or escalating it.

## groundhog (pytest reset loop)

To drive the test suite to its global objective (every test passing, coverage at the project gate), follow the instructions from `instructions/groundhog.md`. Trigger this whenever the user asks to run groundhog, ghog, or to fix tests and coverage.
