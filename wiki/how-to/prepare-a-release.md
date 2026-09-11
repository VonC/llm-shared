# How to prepare a release from the right branch

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Invoke `prepare-release` once with the release intent. The AI owns planner
calls, conflict evidence, supported Git operations, release notes, and version
updates; do not run its prerequisites manually. Use the lower-level commands
only for the diagnostic or unsupported-path circumstances named below.

📊 Goal: finish a collection feature on its umbrella-slug integration branch,
or a standalone feature on generic integration when present, and either stop
cleanly for the next ordered umbrella requirement or continue to
one `chore(release): prepare for vX.Y.Z release` commit on `main` when the
umbrella is exhausted.

## 🧭 Choose the invocation branch

| Goal | Start from | Result |
| --- | --- | --- |
| Release everything integrated and validated | `develop` or the configured integration branch | The skill proposes one `git merge --no-ff develop` into main and never rebases develop |
| Release all but one integrated feature | `develop`, with the excluded topic named in the context | Unsupported by the planner; the skill stops before mutation and outputs the exact merge evidence plus a review-branch revert, verification, re-entry, and later restoration runbook |
| Release several arbitrary integrated features | Name every feature branch and their intended order | Unsupported as one planner transaction; the skill outputs per-topic promotion evidence so you can promote them separately, then prepare the combined artifacts once from main |
| Finish one feature in an umbrella | Its feature branch | Resolve the umbrella before planning, fold hyphens and underscores to find its integration branch, land the exact range there, and stop for the next row unless the umbrella is exhausted |
| Release a standalone feature | Its feature branch | Land on generic integration when present, otherwise main, then continue through full release preparation |
| Revisit a feature already contained by its first destination | Its feature branch | Verify only a current-tip structured merge; otherwise stop with the historical merge OID |
| Prepare changes already on the release branch | `main` | Select `last_tag..main`; no rebase and no merge; prepare the version and notes in place |

To name an integration branch other than develop:

```bash
git config prepare-release.integrationBranch integration
```

The repository hosting default is `develop`, which is also the long-lived
continuous-integration branch. `main` remains the release and tag branch.
Before release preparation, a collection feature enters the branch named by
its umbrella slug. The generic develop/configured branch applies only to a
standalone topic or an explicit integration release.

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
checks the working tree, resolves an umbrella before planning, automatically
invokes `prepare_release_plan.bat`,
synchronizes the first destination, confirms the selected scope, merges with
`--no-ff`, and rewords the merge commit. For an umbrella feature it then runs
`pw skill --after-merge` before any release artifact. A pending row ends the
run there. An exhausted umbrella, a standalone feature, or a run from main or
integration continues through the Diataxis audit, `version.txt`,
`CHANGELOG.md`, `pyproject.toml`, `uv.lock`, and one prepare commit. You do not
run the planner or set `LLM_SHARED_DIR` yourself. It never tags and never
pushes.

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

The usual feature-completion pick replays the exact confirmed range onto current
develop when needed and then records a non-fast-forward merge:

![A feature is rebased onto develop and merged there with no fast-forward.](../assets/prepare-release/feature-to-develop.svg)

Run directly from the feature branch, regardless of whether it started from
main, develop, or another feature. The skill searches the branch-creation
reflog and the candidate parent branches' fork and merge topology. It then
shows the detected parent, boundary commit, ordered commit list, and diff
summary. Confirm only when that range contains this feature and nothing else.

After the merge and structured reword, an associated umbrella is checked before
release artifacts. Each `completed` row must name an existing requirement and a
validation plan whose first non-title line is `Yes, it is implemented.`. If the
first unfinished row is still `pending`, the run prints its exact
`process-draft on <umbrella> based on <slug>` command and stops. It does not
merge develop into main or update `version.txt` and `CHANGELOG.md`.

When every umbrella row is complete, the same invocation continues. If the
first destination was develop, it promotes develop wholesale to main and
rewords that merge before creating release artifacts. If no develop branch
exists, the feature is already on main and artifact preparation continues in
place.

When the feature already contains the latest destination and its boundary
belongs to that destination, the skill can merge it directly with `--no-ff`.
Otherwise it creates a temporary landing branch and runs:

```bash
git rebase --onto <destination> <feature-base> <landing-branch>
```

It verifies the replay with `git range-diff`, runs `ghog day`, and merges the
landing branch with `--no-ff`. The original feature ref remains unchanged.
With develop, this is the continuous-integration pick. Without develop, main
is the destination.

If the feature tip is already an ancestor of the destination, there is nothing
to replay. The skill can continue only when the destination tip is the feature
merge whose structured message can still be verified; otherwise it stops with
the merge OID rather than rewriting historical integration.

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
| Feature is not safely on its first destination | confirm the exact range, replay it on a temporary landing branch with `rebase --onto`, or abort |
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
| Umbrella has a pending row | take the printed `process-draft` command as the next effort; release files remain untouched |
| Umbrella status and evidence disagree | rerun or repair the final implementation check; never infer completion |
| Diataxis wiki audit | review grouped wiki corrections before release notes |
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

`git log` on `main` contains any reviewed wiki-correction commit before the
release-notes work and ends with one
`chore(release): prepare for vX.Y.Z release` commit; `version.txt` carries the
chosen title; `CHANGELOG.md` has the new section.

Related: [Why release branch roles matter](../explanation/why-release-branch-roles-matter.md),
[Where the human stays in the loop](../explanation/where-the-human-stays-in-the-loop.md),
[Prepare your first release from develop](../tutorials/05-prepare-a-release-from-develop.md),
[Reword a merge commit from the branch docs](reword-a-merge-commit.md), and
[Prepare-release scenarios](../reference/prepare-release-scenarios.md).
