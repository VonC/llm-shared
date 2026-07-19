# Prepare-release scenarios

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📊 Exact branch classification, scope, version, and merge behavior for
`/prepare-release`.

## Branch-role resolution

`main` is the release branch. The integration branch is resolved in order:

1. `git config prepare-release.integrationBranch`,
2. local `develop`,
3. `origin/HEAD` when it names a branch other than main.

The hosting default is `develop`; it is also the long-lived integration
branch. That default does not redefine the release branch: `main` remains the
branch prepared and tagged for releases.

## Workflow vocabulary

`gitworkflow` means the specific workflow in Git's
[`gitworkflows(7)` documentation](https://git-scm.com/docs/gitworkflows) and
the [`rocketraman/gitworkflow` primer](https://github.com/rocketraman/gitworkflow),
not generic Git flow and not GitFlow. `main`, feature, and develop correspond
roughly to `master`, topic, and `next`. Unlike canonical gitworkflow, this
variant uses a long-lived default develop branch, commonly rebases features
onto develop before `--no-ff` integration, may replay the exact feature onto
main for release, and permits a wholesale develop merge when every topic is
ready.

## Scenario matrix

| Invocation | Status | Selected content | Action or handoff |
| --- | --- | --- | --- |
| `main` with a non-empty `last_tag..main` | Supported | Every commit in that range | Prepare in place; no rebase and no merge |
| `main` with an empty range | Stopped safely | No new release content | Report the exact tag or that no effort is in progress |
| integration with a non-empty `main..integration` | Supported | Every commit in that range | Confirm, then merge integration into main with `--no-ff`; never rebase integration |
| integration already contained by main | Stopped safely by the skill | No integration-only content | Reject an ancestry-only `merge-no-ff` plan; release from main only when all unreleased main content is selected |
| integration, all but one topic selected | Unsupported by planner | Desired tree excludes one merge | Stop before mutation; output the unique merge evidence and a review-branch revert, verification, re-entry, and reintroduction runbook |
| integration, several arbitrary topics selected | Unsupported as one plan | Named topic branches only | Output one ordered feature-promotion plan per topic; merge them to main separately, then prepare artifacts once from main |
| feature created from main and already containing latest main | Supported | Confirmed `feature_base..feature` range | Merge the original feature with `--no-ff` |
| feature created from old main, integration, or another feature | Supported | Confirmed `feature_base..feature` range only | Rebase that range onto main on a promotion branch, verify and test, then merge `--no-ff` |
| feature tip already contained by main and a release tag | Stopped safely | No new content | Report the earliest containing tag; do not replay or merge |
| feature tip already contained by main but no release tag | Stopped safely | No safe feature-only operation remains | Report it as integrated but unreleased; suggest an explicit on-main invocation only if all `last_tag..main` changes should ship |
| feature with ambiguous or erased fork evidence | Supported pause | Nothing until a boundary is selected | Ask for the parent or boundary; never guess or widen the range |
| feature whose confirmed range contains merges | Unsupported by planner | A non-contiguous user-selected commit list | Mark the merges and output a clean-branch reconstruction runbook; the planner has no explicit commit-list option |

Feature-boundary evidence is resolved from branch-positioning reflog entries
(creation, reset, or completed rebase), candidate-parent `--fork-point`,
ordinary merge-base, and the first-parent merge that introduced an
already-merged feature. A later reset/rebase can supersede branch creation.
The closest valid boundary wins only when it is unambiguous. A selected range
containing merges cannot be resumed by passing an explicit commit list: the
current planner has no such option. Reconstruct a clean main-based topic from
the user-confirmed commits, validate it, then re-enter from that branch.

## Gitworkflow selection rules

| Release intent | Classification |
| --- | --- |
| One topic already tested on develop | Normal gitworkflow graduation: merge the same main-based topic into main, or promote only its exact commits when its base is unsuitable |
| Every topic on develop is ready | Bulk optimization: merge develop into main; intentional departure from canonical gitworkflow |
| Every topic except one is ready | GitFlow-style recovery: revert one merge, then bulk merge; not currently planner-supported |
| Several arbitrary topics are ready | Graduate those topic branches individually; never infer the subset from develop's aggregate history |

## Required unsupported-path output

The skill never ends an unsupported result with only “the planner cannot do
this.” Its handoff contains the release intent, the safety reason for stopping,
actual branch and commit evidence, pasteable commands with real OIDs, checks
for the result, and the exact re-entry branch and invocation context.

| Unsupported path | Required user handoff |
| --- | --- |
| All but one topic | Identify the excluded topic's unique two-parent merge; show its parents, changed paths, later merges and overlaps; explain that semantic independence needs human confirmation; give a temporary review-branch `git revert -m 1`, green-gate, `--no-ff` integration merge, rerun-from-integration, and later revert-the-revert/rebuild plan |
| Arbitrary topic subset | Name the ordered topic branches; show one planner-derived boundary and commit range per branch; require a fresh preview as main evolves; promote each range separately, then invoke prepare-release once from main for the combined release artifacts |
| Merge-containing feature range | Show every commit and mark merges; let the user confirm the non-merge list; give ordered cherry-picks onto a clean branch from current main, diff and test checks, and rerun-from-clean-branch instructions |

When the evidence cannot establish a unique merge, an unambiguous topic
range, or acceptable dependencies, the only safe instructions are to split
the release, rebuild a clean topic, or abort. The skill never manufactures the
missing evidence.

Before these release scenarios, the normal integration operation is
`feature rebase onto develop` followed by `develop merge --no-ff feature`.
That pick proves the feature with other work. A selective release is a second,
independent pick onto main. A feature may instead be picked directly for main
without first entering develop.

A topic merged into develop and later into main therefore has two merge
commits with different meanings. Canonical gitworkflow does not require a
rebase between them when the topic forked from the oldest target branch. The
skill's temporary `rebase --onto main` is an adaptation for develop-based,
nested, or stale topics and never rewrites the published original.

## Planner and conflict evidence

`prepare_release_plan.bat` reports the detected mode, action, exact commit
scope, boundary evidence, and proposed commands. The skill runs topology-only
planning before selection and a full `merge-tree` preview after local main is
current. The caller never runs the planner manually: invoking
`$llm-shared:prepare-release` transfers ownership of both planner calls,
their safe-sandbox approval requests, and any boundary-based rerun to the
skill.

| Planned action | Preview performed |
| --- | --- |
| Prepare on main | None; no branch histories are combined |
| Merge integration or feature into main | Merge the exact source tip into current main |
| Synchronize stale integration | Merge current main into the integration tip |
| Rebase a feature range | Replay each commit after the confirmed boundary onto a synthetic main tip; stop at first conflict |

The planner models one source branch at a time. It does not model a revert,
an evolving sequence of several source branches, or a non-contiguous replay.
The skill supplies the handoffs above around that boundary. It also verifies
that `main..integration` is non-empty because equal refs satisfy Git's
ancestor predicate even though `git merge --no-ff` cannot create the promised
release merge.

A conflict report includes paths, stable Git conflict types, and Git's human
messages. A clean report is valid only for the OIDs shown. The preview uses a
temporary object directory and changes no ref, index, or worktree.

## Version selection

| Input | Rule |
| --- | --- |
| Last released tag | Semantic-version lower bound |
| Effort-document versions, including `feature-request.v…` | Choose the lowest version strictly newer than the last tag |
| Later effort and draft versions | Report as forward-looking notes; drafts never choose the target or trigger a release |
| Invocation branch | Selects release content; choosing a version never filters commits |
| `version.txt` at previous release | Expected; Step 8 writes the target snapshot |
| Different newer snapshot in `version.txt` | Pause for a target-version choice |

Only target-version validation plans gate the release. Later-version plans can
remain pending notes.

## Base synchronization

| State | Integration mode | Effort mode |
| --- | --- | --- |
| main is ancestor of source | Merge is ready | Merge directly only when the confirmed base belongs to main; otherwise replay the feature-only range |
| source lacks latest main | Merge main into integration, then `ghog day` | `rebase --onto main` on a promotion branch, `range-diff`, then `ghog day` |
| feature tip is already an ancestor of main | Not applicable | Stop; a replay would be empty and cannot create a feature-only release boundary |
| local main behind origin/main | Move the off-main local ref to origin/main | Same |
| local main diverged from origin/main | Stop for reconciliation | Same |

## Outputs and boundaries

The skill produces a structured merge commit when off main, updates
`version.txt`, `CHANGELOG.md`, and optional pyproject/uv files, then creates
one `chore(release): prepare for vX.Y.Z release` commit. It never pushes,
runs `brel`, or creates a tag.

Feature promotion branches remain until the author finishes review and
`brel`; the original feature refs are never rewritten.

Related: [Prepare-release planner](prepare-release-planner.md),
[How to prepare a release](../how-to/prepare-a-release.md), and
[Why release branch roles matter](../explanation/why-release-branch-roles-matter.md).
