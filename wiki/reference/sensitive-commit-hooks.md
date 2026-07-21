# Sensitive commit hooks

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Normally invoke `install-sensitive-git-hooks` and let the agent resolve paths,
run the installer, and verify the result. The direct command below is the
maintainer interface; Git invokes the installed hook entries during commits.

The sensitive commit protection is a pair of composable client-side Git hooks
installed by `tools/sensitive_history/install_hooks.py`.

## Managed layout

For each target repository, Git's resolved hook directory contains:

```text
hooks/
├── pre-commit
├── pre-commit.d/
│   ├── 50-existing       optional preserved user hook
│   └── 90-sensitive      managed staged-blob check
├── commit-msg
└── commit-msg.d/
    ├── 50-existing       optional preserved user hook
    └── 90-sensitive      managed message check
```

The dispatcher marker is:

```text
# llm-shared managed hook dispatcher v1
```

The managed entry marker is:

```text
# llm-shared managed sensitive hook v1
```

Dispatchers invoke entries in filename order and stop at the first non-zero
status. Running the sensitive entry as `90-sensitive` lets earlier hooks
modify the index or message before the final check.

## Installation command

```text
<LLM_SHARED_PYTHON> <LLM_SHARED_DIR>/tools/sensitive_history/install_hooks.py [TARGET_REPO] [--shared-root LLM_SHARED_DIR] [--shared-rules RULES_FILE]
```

| Argument | Meaning |
| --- | --- |
| `TARGET_REPO` | Repository to protect; defaults to the current directory |
| `--shared-root` | llm-shared checkout containing the tracked adapters |
| `--shared-rules` | Common replacement-rules file stored in target-local Git config |

The generated `90-sensitive` entries embed the absolute interpreter used to
run the installer. Invoke the installer with llm-shared's virtualenv Python so
the consuming repository needs no Python environment.

## Idempotency and preservation

The installer compares the desired bytes with every managed file:

- correct files are not rewritten;
- stale dispatcher, adapter, interpreter, or shared-rules paths are repaired;
- an unmanaged main hook is moved once to `50-existing`;
- a preservation collision stops installation;
- a no-change run prints
  `HOOK: sensitive hooks already installed`.

When `--shared-rules` is provided, the installer requires that file to exist
and writes its absolute path to
`sensitive.sharedRulesFile` in the target's local Git config.

## pre-commit scope

The staged check compares the index with `HEAD`, or with Git's empty tree on
an unborn branch. It batch-reads only the new object IDs of added or modified
blobs.

It excludes:

- unstaged working-tree content;
- old commits, tags, paths, and historical blobs;
- deletions;
- pure renames whose blob ID is unchanged;
- submodule commit IDs.

A rename with content changes is scanned under its new path. Reused blob IDs
are read once and associated with every pending path.

## commit-msg scope

Git passes the final message-file path to `commit-msg`. The adapter scans that
file after templates, editor changes, `-m` arguments, amend operations, and
earlier message hooks have produced the pending message.

The hook reports only `commit message line N`; it does not echo matched text.

## Matching and output

Both hooks merge the configured shared rules followed by the project-local
rules described in [Sensitive replacement-rules format](sensitive-replacement-rules.md).

A rejection prints redacted locations:

```text
ERROR: sensitive content found in the pending commit:
  - path/to/file.txt:12
Commit blocked; sensitive content was not printed.
```

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | The pending content checked by this hook is clean |
| `1` | Sensitive content was found; commit blocked |
| `2` | Rules, repository state, Git, or message input could not be checked reliably |

Configuration failures fail closed. Git's `--no-verify` bypasses client-side
hooks; enforce an equivalent server-side check when bypass must be prohibited.

## Source layout

```text
tools/sensitive_history/
├── install_hooks.py
├── sensitive_commit_check.py
├── sensitive_pre_commit.py
├── sensitive_commit_msg.py
└── history_scan.py
tests/unit/tools/sensitive_history/
├── test_install_hooks.py
└── test_sensitive_commit_check.py
```

Related: [Installation guide](../how-to/install-sensitive-commit-hooks.md),
[first-repository tutorial](../tutorials/08-protect-your-first-repository.md),
and [rationale](../explanation/why-sensitive-commit-protection-uses-two-hooks.md).
