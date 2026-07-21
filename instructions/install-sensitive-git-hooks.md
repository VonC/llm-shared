# install-sensitive-git-hooks instruction

Install or verify the composable sensitive-content Git hooks in the repository
from which this skill is invoked. The consuming repository uses
`llm-shared`'s Python environment; it does not need its own Python.

The protection has two entry points:

- `pre-commit` checks only new or updated staged blob objects;
- `commit-msg` checks the final pending commit message.

Both use the configured shared replacement rules followed by the current
repository's project-local rules. They never scan old commits during a commit.

## Resolve the target and llm-shared

1. Resolve `<TARGET_REPO>` with `git rev-parse --show-toplevel` from the
   current directory. Stop if it is not a Git worktree. Do not silently select
   another repository.
2. Resolve `<LLM_SHARED_DIR>` in this order:
   - the target itself when it contains
     `tools/sensitive_history/install_hooks.py`;
   - a sibling `../llm-shared`;
   - a `llm-shared` submodule or workspace folder under the target.
3. Confirm that these files exist:
   - `<LLM_SHARED_DIR>/tools/sensitive_history/install_hooks.py`;
   - `<LLM_SHARED_DIR>/tools/sensitive_history/sensitive_pre_commit.py`;
   - `<LLM_SHARED_DIR>/tools/sensitive_history/sensitive_commit_msg.py`.
4. Select the newest matching llm-shared virtualenv interpreter:
   - Windows:
     `<LLM_SHARED_DIR>/venvs/python_3*llm-shared*/Scripts/python.exe`;
   - POSIX:
     `<LLM_SHARED_DIR>/venvs/python_3*llm-shared*/bin/python`.

Stop with a clear setup message when no interpreter exists. Do not fall back to
the consuming repository's Python or to an arbitrary `python` on `PATH`.

## Resolve the rules

The project-local file is always:

`<TARGET_REPO>/a.sensitive.replacements.local.txt`

Resolve the optional shared file in this order:

1. `git config --path --get sensitive.sharedRulesFile` in the target;
2. `<LLM_SHARED_DIR>/../a.sensitive.replacements.local.txt`.

The second location is `%PROG%\git\a.sensitive.replacements.local.txt` when
`llm-shared` is cloned as `%PROG%\git\llm-shared`.

Before installation:

1. Confirm the local file is ignored with
   `git check-ignore -v --no-index -- a.sensitive.replacements.local.txt`.
2. If a shared file exists, confirm it is outside the target or is itself
   ignored.
3. Parse both files using the format documented in
   `wiki/reference/sensitive-replacement-rules.md`.
4. Require at least one effective rule across the two files. An empty local
   file is valid when the shared file supplies rules.
5. Never print rule contents or matched sensitive text.
6. Never stage either rules file.

If neither file supplies a rule, stop and ask the user to define the watch
list. Do not install protection that can only fail later or silently scan
nothing.

## Install or verify

Run the installer with the exact llm-shared interpreter:

```text
<LLM_SHARED_PYTHON> <LLM_SHARED_DIR>/tools/sensitive_history/install_hooks.py <TARGET_REPO> --shared-root <LLM_SHARED_DIR> --shared-rules <SHARED_RULES>
```

Omit `--shared-rules` only when no shared file exists and the non-empty local
file is intentionally the complete rules source.

The installer is idempotent:

- it writes generic `.git/hooks/pre-commit` and `.git/hooks/commit-msg`
  dispatchers;
- it writes managed `90-sensitive` entries in each `.d` chain;
- it points those entries at the selected llm-shared interpreter and adapters;
- it stores the shared file in local Git config when supplied;
- it preserves an unmanaged existing hook as `50-existing`;
- it reports `HOOK: sensitive hooks already installed` when nothing changed.

If `50-existing` already exists while another unmanaged hook occupies the
main hook path, stop on the installer error. Never overwrite either copy.

## Verify the result

Check all of the following without displaying sensitive rules:

1. Both main hook files contain
   `# llm-shared managed hook dispatcher v1`.
2. Both `90-sensitive` entries contain
   `# llm-shared managed sensitive hook v1`.
3. The entries reference `<LLM_SHARED_PYTHON>` and the corresponding tracked
   adapter under `<LLM_SHARED_DIR>`.
4. When a shared file was supplied,
   `git config --path --get sensitive.sharedRulesFile` resolves to it.
5. Run the dedicated pre-commit adapter from `<TARGET_REPO>` with the exact
   llm-shared interpreter. It must return:
   - `0` when the staged update is clean;
   - `1` when sensitive content is found;
   - `2` when configuration or Git prevents a reliable check.

Do not alter the index merely to test the hook. The automated test suite covers
blocking message and blob commits with temporary repositories.

## Report

State one of these outcomes:

- **Already installed**: every managed file, interpreter path, and shared-rules
  config was already correct;
- **Installed**: no managed dispatcher existed and it was created;
- **Repaired**: stale managed files or paths were updated;
- **Blocked**: identify the missing interpreter, missing rules, unsafe ignore
  state, or preservation collision.

Also report the shared-rule count, local-rule count, effective deduplicated
count, and whether an existing hook was preserved. Report counts only, never
the terms.

Remind the user that Git's standard `--no-verify` option bypasses client-side
hooks; server-side policy is required when bypass prevention is mandatory.
