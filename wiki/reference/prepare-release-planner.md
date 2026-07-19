# Prepare-release planner command

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

`prepare_release_plan.bat` is a read-only topology and conflict-preview
command for `/prepare-release`. It requires Git 2.50 or newer.

Normal release preparation does not require running this command. Invoke
`$llm-shared:prepare-release` and provide the release context; the skill finds
the launcher and calls it automatically for topology detection and conflict
preview. The command interface below is for planner development,
troubleshooting, or independent inspection.

## Invocation model

The prepare-release skill calls this planner automatically after its clean-tree
and repository checks. Invoke it directly only for read-only diagnosis, planner
development, or an advance conflict preview; doing so does not perform the
remaining release workflow.

## Source layout

The stable external entry point is `bin/prepare_release_plan.bat`. Its Python
sources form the `tools.prepare_release` package:

```txt
tools/prepare_release/
├─ __init__.py
├─ prepare_release_plan.py
├─ prepare_release_plan_git.py
├─ prepare_release_plan_models.py
└─ prepare_release_plan_workflow.py
```

Matching tests live under `tests/unit/tools/prepare_release/`. Consumers call
the batch launcher rather than a package file, so this internal organization
does not change the skill invocation or standalone diagnostic command.

## Standalone diagnostic command

From PowerShell:

```powershell
& "$env:LLM_SHARED_DIR\bin\prepare_release_plan.bat" --root .
```

From another repository without relying on an environment variable, call the
launcher by its full path.

## Options

| Option | Meaning |
| --- | --- |
| `--root PATH` | Repository to inspect; defaults to the current directory |
| `--main NAME` | Release branch name; defaults to `main` |
| `--integration NAME` | Explicit integration branch, overriding automatic role detection |
| `--branch REF` | Plan for this ref instead of checked-out HEAD; useful for inspection and tests |
| `--feature-base COMMIT` | Use a user-confirmed feature boundary |
| `--feature-parent BRANCH` | Derive the boundary only from this user-confirmed parent |
| `--no-conflict-preview` | Detect topology without running `merge-tree` |
| `--json` | Emit the complete structured plan as JSON |

Integration is otherwise resolved from
`PREPARE_RELEASE_INTEGRATION_BRANCH`,
`prepare-release.integrationBranch`, the legacy
`release.integrationBranch`, local `develop`, then a non-main `origin/HEAD`
that also exists locally.

## Actions

| Action | Meaning |
| --- | --- |
| `prepare-in-place` | HEAD is main; no rebase or branch merge |
| `merge-no-ff` | Merge the selected integration or already-main-based feature into main |
| `sync-integration-then-merge` | Merge main into integration, test it, then merge integration into main |
| `rebase-onto-main-then-merge` | Replay only `feature_base..feature` on a promotion branch, test, then merge it |
| `already-released` | A release tag already contains the feature tip |
| `already-integrated` | Main contains the feature tip, but no release tag does |
| `needs-feature-boundary` | Git evidence is ambiguous or the selected range contains merges |

The JSON output includes `scope`, the ordered `commits`, proposed
`operations`, feature boundary evidence and candidates, containing tags, and
the conflict preview.

## Supported and unsupported planning paths

| Path | Planner status |
| --- | --- |
| Non-empty on-main scope | Supported; no topology change is previewed |
| Non-empty integration-to-main merge | Supported |
| Main-to-stale-integration synchronization | Supported |
| One main-based feature merge | Supported |
| One contiguous stale, develop-based, or nested feature replay | Supported when its boundary is proven |
| Already released or already integrated feature | Supported stop |
| Ambiguous feature boundary | Supported pause with candidates |
| Empty `main..integration` | Ancestry classification can currently emit `merge-no-ff`; callers must reject the empty scope |
| Revert one integration merge before promotion | Unsupported; no revert action or preview |
| Several arbitrary feature branches in one evolving plan | Unsupported; one `--branch` is accepted per run |
| Merge-containing or non-contiguous feature selection | Unsupported; there is no explicit commit-list option |

The prepare-release skill enforces the empty-scope guard and turns each
unsupported selection into an evidence-backed manual runbook. Standalone
planner users must inspect `scope` and `commits`; never execute a proposed
integration merge when `main..integration` is empty.

## Conflict preview

For one merge, the command runs the equivalent of:

```bash
git merge-tree --write-tree -z --name-only --messages <destination> <source>
```

It reports cleanliness from the exit status, conflicted paths from the
documented file-info section, and the stable conflict type plus human message
from each NUL-delimited informational record.

For `rebase --onto`, the command does not pretend that one aggregate merge is
equivalent to a rebase. It previews every commit in order, using the original
parent as the merge base and an evolving synthetic destination tip. It stops
at the first conflict because its human resolution determines the input to
later commits.

Trees and synthetic commits are written to a disposable object directory
whose alternate is the repository object database. The command never fetches,
updates a ref, reads or writes the index or working tree, merges, or rebases.
The disposable directory is removed when the command exits.
In a restricted agent sandbox, creating that system temporary directory can
require approval; the safe fallback is to approve the same command, not to use
the repository's live object store or index.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | A plan was produced; predicted conflicts are data in that plan, not a command failure |
| `2` | The repository, Git version, refs, boundary, or merge-tree operation prevented planning |

A clean result applies only to the exact OIDs and boundary shown. Rerun after
a fetch, ref movement, boundary change, or conflict resolution.

Related: [Prepare-release scenarios](prepare-release-scenarios.md) and
[How to prepare a release](../how-to/prepare-a-release.md).
