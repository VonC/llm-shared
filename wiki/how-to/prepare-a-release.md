# How to prepare a release from the right branch

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Invoke `prepare-release` once with the release intent. The AI owns planner
calls, conflict evidence, supported Git operations, release notes, and version
updates; do not run its prerequisites manually. Use the lower-level commands
only for the diagnostic or unsupported-path circumstances named below.

📊 Goal: select the intended release scope from main, develop/integration,
or a feature branch created from any parent and finish with one
`chore(release): prepare for vX.Y.Z release` commit on `main`, ready for the
author to tag with `brel`.

## 🧭 Choose the invocation branch

| Goal | Start from | Result |
| --- | --- | --- |
| Release everything integrated and validated | `develop` or the configured integration branch | The skill proposes one `git merge --no-ff develop` into main and never rebases develop |
| Release all but one integrated feature | `develop`, with the excluded topic named in the context | Unsupported by the planner; the skill stops before mutation and outputs the exact merge evidence plus a review-branch revert, verification, re-entry, and later restoration runbook |
| Release several arbitrary integrated features | Name every feature branch and their intended order | Unsupported as one planner transaction; the skill outputs per-topic promotion evidence so you can promote them separately, then prepare the combined artifacts once from main |
| Release one feature created from main | Its feature branch | Merge directly when it already contains latest main; otherwise replay its confirmed range onto main, test, and merge `--no-ff` |
| Release one feature created from develop or another feature | Its feature branch | Recover and confirm the actual fork, replay only `fork..feature` onto main on a promotion branch, test, and merge `--no-ff` |
| Revisit a feature branch already contained by main | Its feature branch | Stop as already integrated; if a tag contains it, report it as already released; otherwise rerun from main only if all unreleased main changes should ship |
| Prepare changes already on the release branch | `main` | Select `last_tag..main`; no rebase and no merge; prepare the version and notes in place |

To name an integration branch other than develop:

```bash
git config prepare-release.integrationBranch integration
```

The repository hosting default is `develop`, which is also the long-lived
continuous-integration branch. `main` remains the release and tag branch.
Before release preparation, a feature normally enters integration by being
rebased onto current develop and merged there with `--no-ff`.

This selection model is
[gitworkflow](https://git-scm.com/docs/gitworkflows), one word, rather than
generic Git flow or GitFlow. Integration proves that topics work together;
release selection graduates the chosen topic branches independently. Starting
from develop is the explicit shortcut that says every integrated topic is
ready.

## 📋 One command drives the whole prep

Start the skill and include the release context:

```txt
$llm-shared:prepare-release - prepare v9.13.5 from develop; later-version documents are future notes
```

The skill detects the branch mode and effort documents since the last tag,
checks the working tree, automatically invokes `prepare_release_plan.bat`,
synchronizes with the latest `origin/main`, confirms the selected scope,
merges `--no-ff` into `main` when needed, rewords the merge commit, sets
`version.txt` to `X.Y.Z-SNAPSHOT`, runs the release-notes steps, updates
`pyproject.toml` and `uv.lock`, and lands one prepare commit. You do not run
the planner or set `LLM_SHARED_DIR` yourself. It never tags and never pushes.

If a feature boundary is ambiguous, the skill presents the candidates and
reruns its planner with the boundary or parent you choose. It never asks you
to invoke the launcher. The [planner command reference](../reference/prepare-release-planner.md)
documents the internal tool for diagnostics and development. The stable
launcher delegates to the package under `tools/prepare_release/`; consuming
projects do not call those Python files directly.

After bringing local main current, the skill reruns the planner against the
exact refs it would merge or replay. A merge preview names all predicted
conflicted paths and conflict types. A rebase preview names the first commit
that would stop; later conflicts cannot be known until that one is resolved.

The target is the lowest effort-document version newer than the last tag,
including `feature-request.v…` names. Later effort and draft versions are
reported as forward-looking notes, not treated as an ambiguity. Drafts never
choose the target. All notes remain in the release whenever the invocation
branch selected them.

## 🚂 Release all of develop

![All validated feature merges on develop are selected by one solid merge into main; develop is not rebased.](../assets/prepare-release/develop-to-main.svg)

1. Check out develop and make sure every intended target-version plan is
   validated and committed.
2. Run `/prepare-release`.
3. Verify the summary says `Integration release`, source `develop`, target
   `main`, and `--no-ff`.
4. Confirm the bulk promotion.

If develop lacks a main hotfix, accept the proposed merge of main into
develop and let the `ghog day` gate finish before promotion. Do not rebase
the shared integration branch.

Use this bulk path only when every topic currently represented by develop is
approved. It deliberately departs from canonical gitworkflow, where `next` is
rebuildable and is not merged wholesale into `master`.

## Exclude one integrated topic

If exactly one topic is not approved, name it in the release context. A
possible GitFlow-style recovery is to revert its no-fast-forward merge commit
and then bulk-merge develop. Before using that shortcut, prove that the merge
commit is unique, check that no selected topic depends on it, and plan how the
topic will later return by reverting the revert or rebuilding integration.

The current planner does not model or conflict-preview the revert operation,
so the skill stops before mutation. It must nevertheless identify the actual
candidate merge, show its parents and changed paths, list later integration
merges and path overlaps, and state that Git cannot prove semantic
independence.

When one unique two-parent merge and an affirmative dependency review make
the recovery acceptable, the skill outputs commands equivalent to these,
with the discovered branch names and OIDs filled in:

```bash
git switch develop
git switch -c prepare-release/exclude-<topic>
git revert -m 1 <excluded-merge-oid>
git show --stat HEAD
```

Run the project's green gate on that review branch. If the revert conflicts
or removes the wrong content, use `git revert --abort` before it completes, or
discard the review branch after returning to develop. Once the result is
reviewed and green:

```bash
git switch develop
git merge --no-ff prepare-release/exclude-<topic>
```

Reinvoke `$llm-shared:prepare-release` from develop and say that every topic
remaining there is selected. Record the revert commit: restoring the excluded
topic later requires reverting that revert and testing again, or rebuilding
the topic on current develop.

For more than one exclusion, a non-unique merge, or uncertain dependencies,
do not subtract changes from develop. Use the arbitrary-subset path below or
split the release.

## Promote several arbitrary topics

The planner accepts one source branch and cannot preview several promotions
against a main tip that changes after each merge. Give the skill the ready
feature branch names and their order. It performs read-only planner calls for
each branch and reports each confirmed boundary, ordered range, and proposed
promotion. It stops before changing history.

Promote the topics one at a time in that order. For each topic, recreate only
its confirmed range on current main when needed, review `git range-diff`, run
the green gate, merge `--no-ff`, and give the merge its structured message.
Rerun the preview before every promotion because the previous merge changed
main. When all selected topics are on main, invoke the skill once from main;
that on-main run prepares one set of release notes and one prepare commit for
the combined `last_tag..main` scope.

When ordering or dependencies are unclear, make separate releases instead of
letting a guessed order define production content.

## 🏠 Prepare directly from main

Check out main, make sure local main is current with `origin/main`, and run
`/prepare-release`. The skill selects `last_tag..main`, derives the next
version from the scoped effort documents, and asks you to confirm an on-main
release. It performs no rebase, switch, or merge; it starts directly with the
snapshot version and release-note preparation after the cleanliness and
validation gates.

## 🎯 Release one selected feature

The usual integration pick rebases the feature onto current develop and then
records a non-fast-forward merge:

![A feature is rebased onto develop and merged there with no fast-forward.](../assets/prepare-release/feature-to-develop.svg)

Run directly from the feature branch, regardless of whether it started from
main, develop, or another feature. The skill searches the branch-creation
reflog and the candidate parent branches' fork and merge topology. It then
shows the detected parent, boundary commit, ordered commit list, and diff
summary. Confirm only when that range contains this feature and nothing else.

When the feature already contains latest main and its boundary belongs to
main, the skill can merge the feature branch directly with `--no-ff`.
Otherwise it creates `prepare-release/<feature>-onto-main`, runs:

```bash
git rebase --onto main <feature-base> <promotion-branch>
```

It verifies the replay with `git range-diff`, runs `ghog day`, and merges the
promotion branch with `--no-ff`. The original feature branch remains
unchanged, including when it was already merged into develop.

![A stale feature is replayed onto a temporary main-based promotion copy and merged into main.](../assets/prepare-release/feature-direct-to-main.svg)

This is gitworkflow's topic-graduation decision. The feature's merge into
develop—normally after rebasing onto develop—tested it with other topics; its
separate `--no-ff` merge into main accepts it for release. This is the second
pick of the same logical feature. A main-based topic can be merged unchanged.
The temporary promotion rebase exists for develop-derived, nested, or stale
topics and never rewrites the original branch. A feature selected directly
for main can skip the develop pick entirely.

When the feature was already tested on develop, its exact confirmed range is
still the selection unit. Other develop commits are not pulled along:

![Only one develop-tested feature is replayed and merged into main; unrelated develop work stays out.](../assets/prepare-release/feature-from-develop-to-main.svg)

If the feature tip is already an ancestor of main, there is nothing left to
merge or replay. The skill stops. It reports the earliest containing release
tag when one exists; otherwise it explains that the feature is integrated but
unreleased. Start again from main only when you intend to release every change
in `last_tag..main`—the skill never broadens the feature invocation for you.

If the reflog expired, a squash or fast-forward erased the fork evidence, or
two bases remain equally plausible, the skill pauses for a parent or boundary.
It never widens the range to make the release proceed.

When the confirmed range itself contains merges, the path is not supported:
the planner has no explicit commit-list option. The skill marks every merge,
shows the ordered range, and asks you to confirm the desired non-merge commits.
Reconstruct a clean topic from current main:

```bash
git switch -c prepare-release/<feature>-clean main
git cherry-pick <first-commit-oid> <next-commit-oid>
git log --reverse --oneline main..HEAD
git diff --stat main...HEAD
```

Use only the exact ordered OIDs you confirmed. Resolve and continue a
cherry-pick conflict, or use `git cherry-pick --abort`. Run the green gate,
then reinvoke the skill from the clean branch. Its main-based contiguous range
is supported. If the range contained merges only because the wrong boundary
was chosen, select the corrected parent or boundary instead.

It calls the smaller skills rather than repeating them
(`group-commits-msg`, `update-merge-commit-msg`, `prepare_release_notes`,
the groundhog loop), signalling each through the flag file
`a.prepare-release.active` so the callee hands control back.

## ⏸️ Where the run pauses for you

| Pause | What you decide or do |
| --- | --- |
| Dirty working tree | let the skill commit pending work, or stop and sort it out |
| Integration lacks main | merge main into integration and test, or abort; never rebase integration |
| Feature is not safely on latest main | confirm the exact range, replay it with `rebase --onto main`, or abort |
| Feature parent is ambiguous | choose or provide the parent/boundary; no mutation occurs first |
| Feature range contains merges | confirm the desired commits, reconstruct a clean main-based topic, validate it, and rerun from that branch; the planner accepts no explicit commit list |
| Empty `main..integration` | do not merge; rerun from main only if every unreleased main commit should ship |
| All but one topic | review the unique merge and dependencies, then follow the temporary revert-branch handoff or choose a subset/split release |
| Several arbitrary topics | promote each confirmed topic in order, then prepare artifacts once from main |
| Conflict preview is red | inspect the predicted paths and conflict types before deciding whether to proceed |
| Rebase conflict | resolve, `git add`, then "go ahead" |
| Local main diverged | decide how to reconcile; the skill never resets local commits |
| `ghog day` not green | review the grouped fixes, then "go ahead" |
| Merge message | review or edit the `Why:` / `What:` message |
| Title choice | pick one of three witty title and subtitle pairs |
| Notes review | edit the `version.txt` summary, or ask for `.changelog.fixes` rules |
| End of the run | review everything, then run `brel` |

## 📰 The release-notes half on its own

`/prepare_release_notes` can run standalone. It drives
`scripts/prepare_release_notes.sh`, which reads the `X.Y.Z-SNAPSHOT`
version from `version.txt`, collects every conventional-commit title since
the last tag, and writes `a.md` grouped by type. The skill then writes the
summary into `version.txt` (main theme, key changes, three title pairs),
pauses for the title pick, and folds the result into `CHANGELOG.md` via
`update-changelog.bat`.

## 🏷️ Tagging is a separate act

The author runs `brel`, which calls `t_build.bat rel` from the
`senv_dev_workflow` tooling: it drops `-SNAPSHOT`, commits the release
version, creates the `vX.Y.Z` tag, and marks it `[valid]` only after a
green build. On failure it resets the pre-release state and deletes the
tag, so `main` is never left half-tagged.

## ✅ Check before running brel

`git log` on `main` ends with the merge commit (reworded) followed by one
`chore(release): prepare for vX.Y.Z release` commit; `version.txt` carries
the chosen title; `CHANGELOG.md` has the new section.

Related: [Reword a merge commit from the branch docs](reword-a-merge-commit.md),
[Prepare-release scenarios](../reference/prepare-release-scenarios.md),
[Why release branch roles matter](../explanation/why-release-branch-roles-matter.md),
and [Where the human stays in the loop](../explanation/where-the-human-stays-in-the-loop.md).
