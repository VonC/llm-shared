# How to install or verify sensitive commit hooks

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Normally ask the agent to invoke `install-sensitive-git-hooks` from the
repository to protect. Run the installer directly only for maintenance or
diagnosis when all resolved paths are already known.

📊 Goal: protect the current repository's staged blob updates and commit
messages with shared tooling, without requiring that repository to maintain a
Python environment.

## Use the skill

From the repository to protect, invoke `install-sensitive-git-hooks` through
Copilot, Codex, Claude, or Antigravity. The target is always the current Git
worktree.

The skill:

1. locates the current, sibling, or submodule `llm-shared`;
2. selects the newest `llm-shared` virtualenv Python;
3. resolves the configured shared rules or the file beside `llm-shared`;
4. validates the project-local rules and ignore state;
5. runs the installer for only the current repository;
6. verifies the managed markers and reports Installed, Repaired, Already
   installed, or Blocked.

## Run the installer directly

Resolve these values first:

- `<TARGET_REPO>`: `git rev-parse --show-toplevel`;
- `<LLM_SHARED_DIR>`: the shared clone;
- `<LLM_SHARED_PYTHON>`: the newest matching interpreter under
  `<LLM_SHARED_DIR>/venvs`;
- `<SHARED_RULES>`: normally
  `<LLM_SHARED_DIR>/../a.sensitive.replacements.local.txt`.

Then run:

```text
<LLM_SHARED_PYTHON> <LLM_SHARED_DIR>/tools/sensitive_history/install_hooks.py <TARGET_REPO> --shared-root <LLM_SHARED_DIR> --shared-rules <SHARED_RULES>
```

Omit `--shared-rules` only when the project-local file intentionally contains
the complete non-empty rule set.

A correct repeat prints:

```text
HOOK: sensitive hooks already installed
```

## Check the installation

From the target repository, verify the configured shared path:

```sh
git config --path --get sensitive.sharedRulesFile
```

Resolve the Git hook directory portably:

```sh
git rev-parse --git-path hooks
```

It must contain:

```text
pre-commit
pre-commit.d/90-sensitive
commit-msg
commit-msg.d/90-sensitive
```

The main files carry the managed dispatcher marker. The `90-sensitive`
entries carry the managed sensitive marker and reference `llm-shared`'s
interpreter and tracked adapters.

Run the installer rather than comparing files by hand when checking drift. It
updates stale managed paths and returns the already-installed result when
everything matches.

## Preserve another hook

When an unmanaged `pre-commit` or `commit-msg` already exists, the installer
moves it to `<hook>.d/50-existing` and installs the dispatcher. The sensitive
check runs as `90-sensitive`, after earlier hooks have had a chance to update
the index or message.

If `50-existing` is already occupied and another unmanaged main hook appears,
the installer stops. Resolve that collision manually; do not discard either
hook.

## Diagnose a blocked installation

- **No llm-shared interpreter**: initialize the `llm-shared` environment; do
  not use the target project's Python.
- **No effective rules**: add at least one shared or local rule.
- **Rules not ignored**: add an appropriate `a.*` or exact filename rule to
  the project's `.gitignore`.
- **Exit 2 from the check**: repair the missing rules, Git config, repository,
  or interpreter path. The hook fails closed.
- **Sensitive finding**: edit the staged blob or pending message. Output is
  redacted and identifies only its location.

Related: [Rationale](../explanation/why-sensitive-commit-protection-uses-two-hooks.md),
[first-repository tutorial](../tutorials/08-protect-your-first-repository.md),
[rules reference](../reference/sensitive-replacement-rules.md), and
[hook reference](../reference/sensitive-commit-hooks.md).
