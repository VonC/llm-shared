# Why sensitive commit protection uses two hooks

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Invoke `install-sensitive-git-hooks` when you want the agent to install or
verify the protection in the current repository. Humans normally encounter
the two hooks through `git commit`; this page explains why the installer uses
two lifecycle entry points.

📊 A confidential term can enter a commit through two independent channels:
the tree recorded by the index and the message attached to that tree. Git makes
those channels available at different moments, so one hook cannot reliably
protect both.

## The index exists before the message

`pre-commit` runs while Git is preparing the tree. It can inspect the index,
including staged contents that differ from the working tree, but the final
message file does not yet exist reliably. The sensitive pre-commit check
therefore compares the index only with `HEAD`—or the empty tree for a first
commit—and reads only new or updated blob object IDs.

That narrow scope matters. A full history scan at every commit would repeat
work unrelated to the pending change and become slow enough to encourage
bypassing the hook. Existing history, unstaged edits, deletions, unchanged
renames, and submodule commit IDs are not pending blob updates.

## The final message needs commit-msg

`commit-msg` runs after Git has assembled the actual message file. It catches
terms introduced by `-m`, an editor, a template, an amend, or another hook.
The same matching rules apply, but only to that pending file.

This division is a Git lifecycle boundary, not duplicated design. The generic
dispatchers keep both entry points composable while the dedicated adapters
remain small.

## Prevention and history auditing solve different problems

The hooks prevent a new reachable commit from being created locally. The
sensitive-history scanner examines every reachable historical message, tag,
path, and unique blob. It finds damage that predates hook installation or
arrived through a bypass, another clone, or a server-side merge.

Client-side hooks can always be bypassed with `--no-verify`. They are a fast
local guard, not an authorization boundary. Repositories that must prohibit
bypass need an equivalent server-side policy.

## Shared and local rules express ownership

Common organization or machine terms belong in one shared ignored rules file.
A repository keeps only terms specific to that project in its own
`a.sensitive.replacements.local.txt`. Local Git config records the shared
path; scanners merge shared rules first and local rules second.

That merge is the scanner's default-input behavior: `shscan` performs it only
when no positional terms, `--terms-file`, or `--rules` input is supplied. The
shared file is not discovered merely because it is global or beside the
repositories; each repository's `sensitive.sharedRulesFile` Git configuration
names it. Supplying `--rules PATH` deliberately scans only that explicit file.

This separation avoids copying confidential terms into every project while
allowing one repository to add a narrower rule. The exact syntax and merge
contract are in the
[sensitive replacement-rules reference](../reference/sensitive-replacement-rules.md).

Related: [Protect your first repository](../tutorials/08-protect-your-first-repository.md),
[install or verify the hooks](../how-to/install-sensitive-commit-hooks.md),
and [hook reference](../reference/sensitive-commit-hooks.md).
