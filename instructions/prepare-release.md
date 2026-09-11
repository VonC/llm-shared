# Prepare a release

Automate the release-preparation process up to, but not including, the
tag-cutting `brel`. Run it from `main`, a long-lived integration branch such
as `develop`, or a feature branch created from main, integration, or another
feature. Main prepares in place and integration promotes everything integrated
there. Feature mode first finishes one topic: it isolates only the commits
after that feature's proven fork point, lands a collection topic on the branch
named by its umbrella slug, otherwise lands it on the generic integration
branch when one exists (or `main` for a standalone topic), rewords the merge,
and checks the topic's umbrella draft through `pw skill`. When another ordered requirement
remains, it stops there with a `process-draft` handoff and writes no release
artifacts. Only an exhausted umbrella, or a standalone feature with no umbrella,
continues through the full release path. A full run readies every release
artifact, records them in one `chore(release): prepare for vX.Y.Z release`
commit, then stops so you can review everything and run `brel` yourself.

This skill calls other skills and tools:

- `prepare_release_plan.bat` automatically, first for topology-only evidence
  and again for the exact Git 2.50+ `merge-tree` conflict preview after main
  is current.
- `group-commits-msg` when the working tree is dirty, and when a `ghog day`
  green gate needed fixes that must be committed.
- `update-merge-commit-msg` after it merges an integration, feature, or
  landing branch into its target.
- `pw skill --after-merge <umbrella-draft>` after a completed feature merge.
  It returns the first unfinished ordered collection item, or
  `prepare-release` when the collection is exhausted.
- `process-draft` as the proposed next action when that collection check finds
  an item whose requirement has not been created yet.
- `review-and-update-project-docs` against `<last_tag>..HEAD` when `wiki/`
  or `docs/wiki/` exists, before release notes are generated.
- `prepare_release_notes` for the `version.txt` summary and the
  `CHANGELOG.md`.
- the `ghog day` groundhog loop (the `groundhog` skill) to prove the suite
  is green after a feature-only `--onto` replay or after main was merged into
  an integration branch.

It uses a flag file (`a.prepare-release.active`, see "The run flag file"
below) so those sub-skills hand control back to it instead of finishing
with their own standalone closing message (see "Handoff" in each sub-skill
body).

## Invocation contract

The user only has to invoke `$llm-shared:prepare-release` and explain the
release context. From that point, this skill owns every ordinary inspection
and workflow command it needs, including git status checks, branch-role
detection, `prepare_release_plan.bat`, fetches, validation gates, and
sub-skill calls. Never ask the user to run `prepare_release_plan.bat` or make
it a prerequisite for invoking this skill.

Discover the shared launcher's full path from this installed instruction or
plugin location and invoke it directly. Do not depend on the user's current
shell having `LLM_SHARED_DIR`, a doskey alias, or another environment setup.
When a restricted sandbox requires approval for the safe isolated conflict
preview, request approval for the launcher command yourself; the user may
approve that action, but must not be told to copy and run the command.

Stop and report blockers discovered by these automatic checks. In particular,
the dirty-tree gate below lists the changed files and offers the existing
`group-commits-msg` path; it never silently continues. Pauses remain only for
the explicit decisions, approvals, conflict resolutions, and release-note
review described below. `brel`, tagging, and pushing remain outside this
skill by design.

## Workflow model: gitworkflow topic graduation

Use `gitworkflow` as one word for the specific topic-graduation workflow
described by Git's own `gitworkflows(7)` documentation and the
`rocketraman/gitworkflow` primer. Do not call this generic "Git flow" or imply
that it is Vincent Driessen's GitFlow.

Map the roles as follows: `main` corresponds to gitworkflow's `master`, a
feature branch corresponds to a topic, and `develop` serves the integration
purpose of `next`. The mapping is intentionally not exact: canonical
gitworkflow treats early integration branches as rewindable/rebuildable and
does not normally merge `next` wholesale into `master`, while repositories
using this skill keep `develop` as the published long-lived hosting default
and reserve `main` for release preparation and tagging.

In this variant, invoking the skill from a completed feature performs normal
continuous integration first. When the topic belongs to an umbrella, the
umbrella slug names its integration branch and the exact feature range returns
there. For a standalone topic, replay the range onto the generic integration
branch such as `develop` when necessary, using a temporary landing branch so
the original feature ref is not rewritten, then merge with `--no-ff`. Only a
standalone topic with no integration branch uses `main` as its first target.
The structured merge message marks
the requirement as integrated, but not necessarily release-ready. The umbrella
checkpoint decides whether to stop for the next requirement or continue.

Only after the umbrella is exhausted may release selection pick the integrated
history for `main`. With `develop`, the normal final path is the one wholesale
integration-to-main `--no-ff` merge. Without it, the last feature merge is
already on main and the run continues in place. The common gitworkflow idea is
independent topic selection at successive stability levels; temporary landing
branches preserve any already-published original feature.

Apply these release-selection rules:

1. Invoking from a feature means finish that topic first. Land a collection
   topic on its umbrella integration branch; this relationship must never fall
   back to `main`. Land a standalone topic on the resolved generic integration
   branch, or on main only when no such branch exists. Reword the merge, then
   run the umbrella checkpoint. A remaining item ends
   the run before any integration-to-main merge, wiki audit, `version.txt`,
   `CHANGELOG.md`, pyproject, lockfile, or release commit change.
2. Canonical gitworkflow forks a topic from the oldest integration branch it
   may eventually enter and warns against rebasing a topic after it has been
   merged elsewhere. When the original topic is safely based on the current
   target, merge it unchanged. Otherwise never rewrite the published original:
   isolate its exact commits and rebase only a temporary landing branch with
   `rebase --onto <target> <feature_base>` before the `--no-ff` merge.
3. Invoking from the integration branch explicitly means every topic already
   integrated there is release-ready. The one integration-to-main `--no-ff`
   merge is a bulk optimization and a deliberate departure from canonical
   gitworkflow, not the default selective path.
4. If every integrated topic except one is ready, reverting that topic's
   merge commit before a bulk integration merge is a GitFlow-style recovery
   shortcut, not normal gitworkflow graduation. It is safe only when the
   excluded topic has one unambiguous merge commit, no selected topic depends
   on it, and the team accepts the revert history plus the later need to
   revert the revert or rebuild integration. The current release planner does
   not preview this revert path, so explain the option and stop before
   mutation rather than silently performing it. Give the complete
   revert-on-a-review-branch runbook from "Unsupported planner handoffs"
   below, including the exact candidate merge OID, verification commands,
   re-entry point, and later reintroduction choice. Otherwise use the
   arbitrary-subset handoff and select topics individually.

Primary sources:

- <https://git-scm.com/docs/gitworkflows>
- <https://github.com/rocketraman/gitworkflow>
- <https://stackoverflow.com/a/44470240/6309>
- <https://stackoverflow.com/a/216228/6309>
- <https://stackoverflow.com/a/53405887/6309>

Every user choice or approval pause in this instruction follows
[`../rules/interactive_menu.md`](../rules/interactive_menu.md). Read that rule
before each pause, then present only the concrete choices named by the current
step.

## What this skill never does

- It never creates the git tag. `brel` does that, after your review.
- It never pushes to a remote. It does fetch `origin/main` (read-only) to
  find the latest main, but pushing main, and the tag `brel` makes, stays a
  manual step you do afterwards.
- It never touches a sibling worktree folder such as `..._main`. It works
  only in the tree it runs from.
- It never starts release-artifact work while an umbrella collection still
  has an unfinished item. The feature merge and its structured message are the
  complete result of that invocation.

## Boundary with brel

`brel` (`build.bat rel`, which calls `tools\dev_workflow\update-version.bat
rel`) is the step that turns `version.txt` `X.Y.Z-SNAPSHOT` into the
release `X.Y.Z`, regenerates `CHANGELOG.md`, makes its own release commit,
and creates the `vX.Y.Z` tag. This skill stops one step short of that, at
the prepare commit, so the irreversible tag stays in your hands.

## The run flag file

The handoff to the sub-skills uses a flag file, `a.prepare-release.active`,
at the project root. The `a.*` rule in `.gitignore` keeps it out of git, so
it never gets committed. Its lifecycle across one run:

- At the start of the run, delete the flag file if it is still there, so a
  stale flag left by a crashed earlier run cannot lie about the state. This
  delete-at-start is what makes the flag self-healing.
- Create the flag file before each sub-skill call, so the sub-skill sees it
  and hands control back instead of ending on its own.
- Remove the flag file on every exit path: success, the nothing-to-release
  stop, the already-released stop, the abort, and any error stop.

A file works across the separate shells each command runs in, where an
environment variable set in one command would not survive into the next.
Existence is the whole signal; the file content does not matter.

## The green-gate routine

Some steps drive the project to a green test suite with `ghog day` before
the release goes on. When a step calls for the green gate:

1. Run the groundhog loop with `ghog day`, following the `groundhog` skill
   ([`groundhog.md`](groundhog.md)): from the project root, `cmd /d /c
   "<LLM_SHARED_DIR>\bin\ghog.bat day > a.ghog.log 2>&1"`, issued from
   PowerShell or cmd.exe, never from Git Bash (an MSYS shell mangles the
   `/d` / `/c` switches and `cmd` exits 0 without running the walk, leaving a
   stale log; see groundhog.md). Branch on the exit code, and fix and re-run
   until it reaches exit 0 (every check, the affected tests, and the full
   suite at the coverage gate). The groundhog loop owns running `check.bat`
   and the tests; never run them directly here.
2. When the first `ghog day` is green with nothing changed, there is
   nothing to commit: continue with the next skill step.
3. When fixes were needed to reach green, the working tree now carries
   them. Create the flag file, run the `group-commits-msg` skill to group
   and message those fixes, and wait for the user's review choice. On a
   go-ahead selection, commit, then continue with the next skill step.

## Resolve the project directory

Every git and file step runs against the project root. First ask git for the
top-level worktree containing the current directory. When that directory has
`version.txt`, use it even if an inherited `PRJ_DIR` points at a different
repository. Otherwise use `PRJ_DIR` when set. Stop when neither location is a
git project with `version.txt`; never silently operate on another repository.
Report the resolved `<PRJ_DIR>` before the first mutation. Resolve
`<LLM_SHARED_DIR>` independently, the same project-portable way the other
skills use, so the shared scripts are found from any consuming repository.

## Workflow

### Step 1 — Clear a stale flag and find the last tag

First, delete any stale flag file left by a crashed earlier run, so the
handoff signal starts clean:

```bash
rm -f "<PRJ_DIR>/a.prepare-release.active"
```

Then read the last released tag from `<PRJ_DIR>`:

```bash
git -C "<PRJ_DIR>" describe --tags --abbrev=0
```

When the command finds no tag (a repository that was never released), treat
the whole history as the development effort and skip the
already-released test in Step 2; the version still comes from the effort
document in Step 3.

### Step 2 — Detect the development effort and the already-released state

A development effort exists only when at least one commit since the last
tag adds or changes a feature, issue, design, or plan document. List those
commits:

```bash
git -C "<PRJ_DIR>" log --format= --name-only "<last_tag>..HEAD" -- \
  "docs/feature*" "docs/issue*" "docs/design*" "docs/plan*" \
  ":(glob)docs/**/feature*" ":(glob)docs/**/issue*" \
  ":(glob)docs/**/design*" ":(glob)docs/**/plan*"
```

When that list is empty, make no change to the tree and stop with one of
three messages:

- If HEAD sits exactly on a tag (idempotency, the release was just done):

  ```bash
  git -C "<PRJ_DIR>" describe --tags --exact-match HEAD
  ```

  When that succeeds, print "release already done for `<tag>`" and stop.
- Otherwise, when HEAD is not main, check whether a later release tag already
  contains this branch tip:

  ```bash
  git -C "<PRJ_DIR>" tag --contains HEAD --sort=version:refname
  ```

  When the command lists tags, report the earliest containing tag as
  "branch tip already released in `<tag>`" and stop. This distinguishes an
  old feature branch that was merged and released from a branch that merely
  has no qualifying effort document.
- Otherwise, print "nothing to release yet, no development effort in
  progress" and stop.

Only when the effort list is non-empty do you go on. This is the guard that
makes a second run a no-op.

### Step 3 — Derive the target version, slug, and release mode

Read the current branch first. Candidate versions are filtered to the release
mode's exact scope after classification, matching effort documents in any of
the four directories from `rules/docs_layout.md`:

```bash
git -C "<PRJ_DIR>" rev-parse --abbrev-ref HEAD
```

#### Resolve an umbrella destination before release mode

For a branch other than `main`, resolve the branch-matched requirement or issue
before the first planner call, using the supported effort directories and the
same slug comparison as `pw skill`: compare the branch leaf after folding
hyphens and underscores. Read its child draft's one explicit `- Umbrella:`
path, or use the one canonical umbrella table whose item slug matches when no
child marker exists.

When a topic has an umbrella, record it as `<umbrella_draft>` immediately. The
umbrella slug names its integration branch. Match that slug against local
branch leaves after folding hyphens and underscores and require exactly one
match. A missing or ambiguous branch stops the run; an umbrella topic must
never fall back to `main`, `develop`, configuration, or `origin/HEAD`.

Pass the exact draft through `--umbrella "<umbrella_draft>"`. The planner
validates the marker, canonical filename, normalized branch match, and feature
target. Do not translate the draft into a hand-written `--integration` value.

#### Choose the release mode

The release branch is `main`. When no umbrella destination was resolved,
resolve the optional generic long-lived integration branch in this order:

1. the local value of `prepare-release.integrationBranch`, when configured,
2. local `develop`, when that branch exists,
3. the branch named by `origin/HEAD` when it is not `main`.

Use plain git reads; a missing value or ref is not an error:

```bash
git -C "<PRJ_DIR>" config --get prepare-release.integrationBranch
git -C "<PRJ_DIR>" show-ref --verify --quiet refs/heads/develop
git -C "<PRJ_DIR>" symbolic-ref --quiet --short refs/remotes/origin/HEAD
```

Classify the run and tell the user which mode was detected:

- **On-main release** — HEAD is `main`. Select every commit in
  `<last_tag>..main`, then prepare the version, notes, changelog, and prepare
  commit in place. No rebase and no branch merge are needed. This is a fully
  supported release path, not a fallback.
- **Integration release** — HEAD is the resolved integration branch. The
  user selected every commit in `main..HEAD` for this release. Never rebase a
  published, long-lived integration branch. Step 6 proposes one `--no-ff`
  merge of the integration branch into main. State that this is the explicit
  all-topics-ready bulk exception to gitworkflow's normal topic-by-topic
  graduation.
- **Feature completion** — HEAD is any other branch. Select only the commits
  made for that feature after it forked from its actual parent, whether the
  parent was main, integration, or another feature branch. The first target is
  its umbrella integration branch when present, otherwise the resolved generic
  integration branch when present, otherwise main. Discover and
  confirm the exact `<feature_base>..<feature_branch>` range as described
  below. When that range is not already safely based on the current target,
  replay it on a temporary landing branch with
  `rebase --onto <target> <feature_base>`, then merge the landing branch into
  the target with `--no-ff`. Never use plain `rebase <target>` for a
  develop-derived or nested feature: it can replay commits inherited from the
  parent branch.

The configured integration branch is a workflow role, not necessarily the
hosting provider's default branch. A repository may keep `origin/HEAD` on
`main` while using `develop` for integration.

#### Obtain release-planner topology evidence automatically

Invoke the shared read-only planner before reproducing branch detection by
hand. This is an internal skill action, not a command the user runs:

```powershell
& "<LLM_SHARED_DIR>\bin\prepare_release_plan.bat" --root "<PRJ_DIR>" --json --no-conflict-preview
& "<LLM_SHARED_DIR>\bin\prepare_release_plan.bat" --root "<PRJ_DIR>" --json --no-conflict-preview --umbrella "<umbrella_draft>"
```

Run the second form for a feature associated with an umbrella; otherwise use
the first and pass `--integration <integration_branch>` when a generic role was
supplied by context or configuration and must be explicit. Feature targeting
defaults to `auto`: an umbrella or generic integration branch wins, and only a
standalone feature with no integration resolves to main.

Resolve `<LLM_SHARED_DIR>` yourself as required by the invocation contract.
The planner requires Git 2.50 or newer. It reports the Git version, start
branch, on-main/integration/feature mode, the feature target, exact scope and
commits, boundary evidence or candidates, and the proposed operation. It never
fetches, moves a ref, changes the index or working tree, rebases, or merges.
Use its result as the deterministic starting point for this step, while
retaining the human confirmation gates below. If it returns
`needs-feature-boundary`, show its candidates and rerun it with
`--feature-base <commit>` or `--feature-parent <branch>` after the user
chooses; never pick for them. Preserve `--umbrella` or the generic
`--integration` input on that rerun when it applied.

Keep the launcher as the stable skill entry point. Its Python package lives
under `<LLM_SHARED_DIR>/tools/prepare_release/`, with matching tests under
`tests/unit/tools/prepare_release/`; never invoke a package file directly from
a consuming project. The launcher owns locating the shared Python environment
and the package entry script.

The planner resolves an umbrella integration branch first when `--umbrella` is
present. Without an umbrella, it resolves the generic integration role from
its `--integration` override, `PREPARE_RELEASE_INTEGRATION_BRANCH`,
`prepare-release.integrationBranch` (with legacy
`release.integrationBranch` support), local `develop`, then `origin/HEAD`
when it names a local branch other than main. When the skill's prompt or other
context supplies the integration branch, pass it explicitly with
`--integration` so the planner and skill use the same role.

Treat planner output as topology evidence, not as permission to perform an
empty operation. Independently count `main..<integration_branch>` before an
integration merge. When it contains zero commits, never offer
`git merge --no-ff`: equal refs and an integration tip already contained by
main cannot produce the promised merge commit. Report the two tip OIDs. If
main has unreleased effort documents, tell the user to check out main and
invoke this skill again to make the broader on-main selection explicit;
otherwise report that there is no integration content to release. The Step 2
tag and effort checks remain authoritative for an empty on-main range.

The planner supports one release source per invocation: on-main preparation,
a non-empty integration promotion, or one contiguous feature range with a
proven boundary. It does not support subtracting a topic by reverting its
merge, aggregating several arbitrary topics in one plan, or replaying a
non-contiguous explicit commit list. For those results, do not merely say
"unsupported" or ask the user to run the planner. Use the handoff below.

#### Unsupported planner handoffs

Every unsupported result must end with an actionable block containing:

1. `Intent` — the requested release selection.
2. `Why the skill stopped` — the unsupported operation and why guessing could
   widen or change the release.
3. `Evidence` — actual branch names, tip and boundary OIDs, ordered commits,
   candidate merge OIDs, and conflicting or overlapping paths discovered by
   read-only checks.
4. `Recommended path` — one of the recipes below, with placeholders replaced
   by the discovered values. Never present an unresolved placeholder as a
   command the user can paste.
5. `Verify` — the log, diff, status, and project green-gate checks that prove
   the user's manual preparation has the intended content.
6. `Re-enter prepare-release` — the exact branch to check out and the context
   to include when invoking `$llm-shared:prepare-release` again.

For **all but one topic on integration**, first list first-parent merge commits
in `main..<integration_branch>` and identify the unique `--no-ff` merge that
introduced the excluded topic. Show its two parents, subject, and changed
paths. Also list later first-parent merges and path overlaps; state explicitly
that Git cannot prove the absence of semantic dependencies. If the merge is
not unique, has no integration first parent, or dependency review is not
affirmative, recommend the arbitrary-subset path and stop.

When the recovery preconditions hold, provide these concrete user-run steps:

1. Create `prepare-release/exclude-<topic>` from the current integration tip.
2. Run `git revert -m 1 <excluded_merge_oid>` on that review branch. Explain
   that the planner cannot predict revert conflicts; use
   `git revert --abort` if the result is not acceptable.
3. Inspect the revert diff and first-parent log, run the project's green gate,
   and obtain the required dependency review.
4. Merge the reviewed exclusion branch back into integration with `--no-ff`.
5. Reinvoke this skill from integration with context saying that all remaining
   topics are selected. The normal integration merge preview then applies.
6. Record the revert commit OID. Explain that restoring the topic later means
   either reverting that revert and testing again, or rebuilding the topic on
   current integration.

For **several arbitrary ready topics**, explain that no combined planner run
can model an evolving main. List the selected feature branches and run the
topology-only planner read-only for each `--branch` in the intended order,
rerunning before every actual promotion because main changes after each
merge. Recommend promoting each confirmed feature range to main one at a
time, with its own `range-diff`, green gate, `--no-ff` merge, and structured
merge message; then invoke this skill once from main to prepare the release
artifacts for the resulting `last_tag..main`. Offer separate releases as the
safer alternative when topic dependencies or ordering are unclear.

For a **feature range that contains merges**, list the complete range and mark
each merge commit. The current planner cannot accept the "explicit commit
list" it asks for, so do not imply that supplying such a list to the planner
will continue the run. Ask the user to confirm the desired non-merge commits,
then recommend reconstructing a clean topic branch from current main with
ordered `git cherry-pick` commands, reviewing `main...<clean_branch>`, and
running the green gate. On conflict, the user may resolve and continue or run
`git cherry-pick --abort`. Re-enter this skill from that clean branch; its
contiguous main-based range is then a supported feature release. A corrected
parent or boundary is the alternative when the original boundary was wrong.

#### Find a feature branch's exact boundary

Run this subsection only in feature mode, before any mutation. Record
`<feature_branch>` and its tip. Find the commit where this branch left its
actual parent; do not assume the parent is main.

1. Inspect the feature branch reflog from oldest to newest. Collect entries
   that positioned the branch on a parent: `branch: Created from ...`,
   `reset: moving to ...`, and a completed rebase `onto ...`. A later reset or
   rebase can supersede the creation point, so do not blindly use the oldest
   entry. Prefer the most recent positioning entry that precedes the
   contiguous feature commits and whose recorded commit is their ancestor.
   Ignore a mere local checkout created from the same-named remote branch;
   that imports history but does not identify the original fork.
2. Inspect candidate parent refs: main, the integration branch, and every
   other local feature branch. For a candidate that does not contain the
   feature tip, try `git merge-base --fork-point`, then fall back to
   `git merge-base`. For a candidate that already contains the feature,
   locate the first merge on its first-parent history that introduced the
   feature; the boundary candidate is the merge base between the feature and
   that merge commit's first parent. A fast-forward or squash merge may leave
   no recoverable boundary.
3. Keep only candidates that are ancestors of the feature tip and leave a
   non-empty range. Prefer a clear, unsuperseded reflog positioning boundary;
   otherwise prefer the closest topology boundary to the feature tip. When
   different boundaries remain plausible, stop and present them. Let the user
   select or provide the parent branch or boundary commit; do not guess.
4. Check the selected range for merge commits. When it contains merges from
   other branches, a simple contiguous rebase would also replay the merged
   work. Stop and use the feature-range recipe in "Unsupported planner
   handoffs"; do not claim that the planner accepts an explicit commit list.
5. Show the exact commits and diff summary, in order:

   ```bash
   git -C "<PRJ_DIR>" log --reverse --oneline "<feature_base>..<feature_branch>"
   git -C "<PRJ_DIR>" diff --stat "<feature_base>...<feature_branch>"
   ```

   Present `Go ahead` and `Abort`, naming the detected parent ref and boundary
   commit. Continue only after the user confirms that every listed commit, and
   no other commit, belongs to the feature.

Save `<feature_base>`, `<feature_branch>`, and the confirmed commit list for
Step 5. A branch already merged into develop is supported when its reflog or
merge topology still proves the boundary. When Git evidence cannot isolate
the range, stop for the user's boundary instead of silently widening scope.

Now define the document scope used by the rest of the run:

- on-main and integration modes: `<last_tag>..HEAD`, because all commits since
  the last release that are present in the selected branch participate,
- feature mode: `<feature_base>..<feature_branch>`, because inherited parent
  documents are not part of this feature.

List the matching feature, feature-request, issue, design, and plan documents
from that range. In feature mode, when the list is empty, stop with "nothing
to release from this feature branch" even when Step 2 found inherited effort
documents. Use only this scoped list for the target version, slug evidence,
validation-plan gate, later-version notes, release notes, and final summary.

In feature mode, verify the earlier umbrella association against the exact
requirement slug from the scoped feature-request or issue and the authoritative
compact table below `## List of feature-requests and issues to create`. More
than one match is ambiguous and stops for the user's choice; no match confirms
that the feature is standalone. Discovering an umbrella only at this point is
a topology error: restart the planner with `--umbrella "<umbrella_draft>"`
instead of continuing with a main destination. Carry the verified association
to the Step 7A checkpoint.

#### Choose the target version and slug

Compare the semantic versions in the scoped effort-document names with the
last released tag. Choose the lowest version strictly greater than the last
released version. This is the next release target. Documents carrying later
versions are forward-looking notes for later efforts; list those versions in
the detection summary, but do not stop and do not exclude their commits from
the selected branch scope. Also scan `draft.vX.Y.Z.*.md` in each supported
effort directory in the selected branch scope and list later-version drafts as
carried notes. Drafts never
trigger Step 2 and never become target-version candidates. Selecting a version
labels the release; selecting the invocation branch selects its content.

When several documents share the target version, prefer the newest design or
plan document for the topic, then the newest feature-request or issue. For an
integration release, use the integration branch name as the slug because the
scope can contain several efforts. For a feature release off main, use the
feature branch name. On main, use the selected target document topic.

Cross-check the derived `X.Y.Z` against the first word of `version.txt`:

- No feature, issue, design, or plan document found means there is nothing
  to release; stop with that message.
- No document version is newer than the last released tag: when `version.txt`
  contains a newer `X.Y.Z-SNAPSHOT`, present the document versions and that
  snapshot as a target-version choice; otherwise stop and explain that no new
  release version can be derived.
- `version.txt` still holds the previous release number (no `-SNAPSHOT`),
  or a matching `X.Y.Z-SNAPSHOT`: that is expected, Step 9 sets it.
- `version.txt` holds a different `-SNAPSHOT` version: stop and present a
  version choice with the effort-document version and the `version.txt`
  version.

Then check every target-version validation plan selected by the branch scope,
`<effort-dir>/plan.vX.Y.Z.<topic>.validation.md`, when the target effort has a
plan. Resolve `<effort-dir>` through the canonical draft and
`rules/docs_layout.md`.
Later-version plans are forward-looking notes and do not gate this release.
Read each target plan's opening status line (the first non-title line): when it
still starts with `No, it is not implemented`, the implementation checks of
that target effort are not complete, or the last `implementation-check` never
flipped the document-level line to `Yes, it is implemented.` as its
instruction requires. Signal it to the user, naming the file and the line
found, remove the flag file, and stop without changing the tree. The user
either finishes the implementation checks or corrects the status line, then
re-runs. Do not carry a target-version effort whose validation plan reads as
unfinished into a release.

### Step 4 — Make the working tree clean

Check the status of the current worktree only (never a sibling worktree):

```bash
git -C "<PRJ_DIR>" status --porcelain
```

When the tree is dirty, create the flag file, then list the dirty files and
present these choices so the user can decide how to handle the pending work:

- `Go ahead` — run the `group-commits-msg` skill so the pending work is
  committed in tidy groups.

```bash
touch "<PRJ_DIR>/a.prepare-release.active"
```

Continue only once the tree is clean. Do not auto-commit without offering,
and do not sweep in edits the user did not mean to release. Before going
further, present a go-ahead choice asking the user to confirm that every step of
the current plan is validated and committed.

### Step 5 — Base on the latest destination

This step first makes local main current with `origin/main`, so a full release
never uses a stale base. In feature mode it also makes the first destination
current: the resolved integration branch when present, otherwise main. It then
bases the selected source branch on that exact destination. The basing half is
skipped in on-main mode because there is no source branch to merge.

#### Make local main current with origin/main

Run this half always, whether or not HEAD is main, so the release base is
the latest main. Fetch the latest main first (read-only, no push):

```bash
git -C "<PRJ_DIR>" fetch origin main
```

When the repository has no remote or no `origin/main` (nothing was ever
pushed), skip the compare below and use the local `main` ref as the latest
main.

Compare local main with `origin/main` using two ancestor tests:

```bash
git -C "<PRJ_DIR>" merge-base --is-ancestor main origin/main
git -C "<PRJ_DIR>" merge-base --is-ancestor origin/main main
```

Read the two exit codes together:

- Only the first succeeds: local main is strictly behind `origin/main` (a
  fast-forward).
  - When HEAD is not main, reset the local main ref to `origin/main`. main is
    checked out in the sibling worktree, which this skill ignores, so move
    the ref directly instead of switching to it:

    ```bash
    git -C "<PRJ_DIR>" update-ref -m "prepare-release: reset main to origin/main" refs/heads/main origin/main
    ```

    This leaves the sibling worktree out of sync with the new main tip, which
    is expected, the user deals with it later.
  - When HEAD is main, local main is the checked-out worktree, so do not move
    the ref under your own feet. Stop and warn the user that local main is
    behind `origin/main`, and let them bring it current (a fast-forward, then
    a re-run) before the release goes on. Do not fast-forward silently.
- Only the second succeeds: local main already contains `origin/main` (it is
  ahead). Leave it as is.
- Both succeed: the two are equal. Nothing to do.
- Neither succeeds: local main and `origin/main` have diverged (each carries
  commits the other does not). Stop and explain that the user must rebase local
  main on top of `origin/main`, which replays the local commits on the latest
  remote main and loses none, then re-run. Do not reset, which would drop the
  local commits.

From here, local `main` is the latest main.

#### Make the feature destination current

Run this subsection only in feature mode when the destination is the resolved
integration branch. Fetch `origin/<integration_branch>`, when it exists, then
compare the local and remote integration refs with the same two ancestor tests
used for main above.

- When local integration is strictly behind and is not checked out (HEAD is
  still the feature), move its ref forward with `git update-ref`, using a
  `prepare-release: reset <integration_branch> to
  origin/<integration_branch>` reflog message.
- When local integration is equal or ahead, leave it alone.
- When the refs diverged, stop for explicit reconciliation. Never reset away
  local integration commits and never rebase the published long-lived branch.
- With no remote integration ref, use the local ref as-is.

The feature destination is now `<target_branch>`: integration when this
subsection ran, otherwise main.

#### Preview the exact operation and its conflicts

Now automatically rerun the release planner without `--no-conflict-preview`,
because main is current and the preview must use the exact tips that would be
changed. Pass the confirmed integration branch or feature boundary when
applicable:

```powershell
& "<LLM_SHARED_DIR>\bin\prepare_release_plan.bat" --root "<PRJ_DIR>" --json
& "<LLM_SHARED_DIR>\bin\prepare_release_plan.bat" --root "<PRJ_DIR>" --json --integration "<integration_branch>"
& "<LLM_SHARED_DIR>\bin\prepare_release_plan.bat" --root "<PRJ_DIR>" --json --feature-base "<feature_base>"
& "<LLM_SHARED_DIR>\bin\prepare_release_plan.bat" --root "<PRJ_DIR>" --json --umbrella "<umbrella_draft>" --feature-base "<feature_base>"
```

Run only the one matching the detected mode and feature destination. The tool uses
`git merge-tree --write-tree -z --name-only --messages` in an isolated
temporary object directory. It does not touch repository refs, the index,
working tree, or permanent object store.

When a restricted sandbox blocks creation of that system temporary directory,
request approval for the same planner command. Do not fall back to the live
object database, index, or a temporary worktree just to avoid the approval.

- For a `--no-ff` merge, it previews the exact destination and source tips.
- When integration lacks main, it previews main merging into integration;
  after that sync is green, integration will contain main and the final
  promotion is structurally conflict-free.
- For `rebase --onto`, it simulates each confirmed feature commit as a
  three-way merge onto an evolving synthetic tip. It reports the first commit,
  paths, stable conflict types, and Git messages that would stop the rebase.
  It cannot predict later rebase conflicts because those depend on how the
  first conflict is resolved.

Include the planner's clean/conflicted result in the next go-ahead prompt. A
conflicted preview is a warning, not permission to mutate: show every reported
path and conflict type before asking. A clean preview is evidence for the
current tips, not a permanent guarantee; rerun it if either tip or the chosen
boundary changes. If `merge-tree` cannot run, stop instead of proceeding
without the preview.

#### Base the selected branch on its latest destination

Skip this half in on-main mode: there is no branch to base, the half above
already made local main current, and Step 6 is skipped on main too.

In integration mode, check whether local main is already an ancestor of the
branch tip:

```bash
git -C "<PRJ_DIR>" merge-base --is-ancestor main HEAD
```

When that succeeds (exit 0), integration already contains the latest main: go
straight to Step 6, with no rebase and no extra test. When it does not, never
offer to rebase the long-lived integration branch. Offer only:

1. Merge main into the integration branch, then test:
   - merge main into the checked-out integration branch with `--no-ff`,
   - run the green-gate routine,
   - continue to Step 6 only when the integration branch is green.
2. Abort the release preparation:
   - remove the flag file and stop.

This keeps published integration history stable and brings any production
hotfixes from main back through the integration test gate before promotion.

In feature mode, use the boundary and commit list confirmed in Step 3 and the
`<target_branch>` resolved above.

- First check whether the feature tip is already an ancestor of the target:

  ```bash
  git -C "<PRJ_DIR>" merge-base --is-ancestor "<feature_branch>" "<target_branch>"
  ```

  When it is, do not create a landing branch or attempt an empty replay. Report
  that the feature is already integrated into `<target_branch>`. If the target
  tip is the feature's merge commit and already has the required `Why:` /
  `What:` message, switch to the target and continue at the Step 7A umbrella
  checkpoint. Otherwise stop with the merge OID; the skill cannot safely
  invent or reword a non-tip historical merge.
- Otherwise, when `<feature_base>` is an ancestor of `<target_branch>` **and**
  `<target_branch>` is an ancestor of `<feature_branch>`, the feature already
  contains the latest destination without carrying a parent-only base. Use
  `<feature_branch>` as `<source_branch>` and go directly to Step 6.
- Otherwise, replay only the confirmed range onto the destination. Preserve
  the original feature ref: create a uniquely named temporary landing branch
  at the feature tip, then rebase that branch with the explicit boundary:

  ```bash
  git -C "<PRJ_DIR>" branch "<landing_branch>" "<feature_branch>"
  git -C "<PRJ_DIR>" rebase --onto "<target_branch>" "<feature_base>" "<landing_branch>"
  ```

  Name it `prepare-release/<feature-branch>-onto-<target-branch>`, sanitized
  for a valid ref, with a numeric suffix when that name already exists. Never
  move or rewrite `<feature_branch>` itself.

  When the rebase reports conflicts, stop and report the conflicted files.
  The user resolves them and runs `git add`. Present `Go ahead`; when selected,
  resume without an editor:

  ```bat
  cmd /V /C "set "GIT_EDITOR=true" && git rebase --continue"
  ```

  Repeat until the rebase finishes. Then prove the replay still corresponds
  to the confirmed source range:

  ```bash
  git -C "<PRJ_DIR>" range-diff "<feature_base>..<feature_branch>" "<target_branch>..<landing_branch>"
  ```

  Stop when range-diff shows a dropped or added commit outside deliberate
  conflict-resolution changes. Otherwise run the green-gate routine on the
  landing branch, set it as `<source_branch>`, and continue to Step 6. Keep the
  landing branch through the user's review; report it at the collection stop
  or Step 14 so the user can delete it after the merge is accepted.

There is no feature-mode "merge stale anyway" path: it would widen the target
with commits inherited from another parent branch. The choices are the exact
`--onto` replay or abort.

### Step 6 — Confirm the scope, switch to the destination, and merge

In integration mode, present the detected action before changing branches:
"Integration release from `<integration_branch>`: release every commit in
`main..<integration_branch>` by merging `<integration_branch>` into `main`
with `--no-ff`. This is the all-topics-ready bulk exception; canonical
gitworkflow would graduate topics individually." List later-version document
notes reported in Step 3 and
make clear that they remain part of the selected branch content but do not
change the target version. Offer `Go ahead` and `Abort`; do not switch or
merge until the user selects `Go ahead`.

Add the planner preview to this confirmation: say either that the exact
operation is currently clean, or list the predicted conflicted paths and
conflict types. For an integration sync, name that first merge as the previewed
operation. For a feature replay, name the first commit expected to stop and
state that later conflicts remain unknown until it is resolved.

In feature mode, present the equivalent action for the confirmed feature-only
range, naming the original feature branch, boundary, destination branch,
source branch (the original or landing branch), and commit count; offer
`Go ahead` and `Abort`.
In on-main mode, report: "On-main release: prepare every commit in
`<last_tag>..main` in place; no rebase and no merge." Offer `Go ahead` and
`Abort`, then skip the rest of this step on `Go ahead`.

After confirmation, set `<destination_branch>` to main in integration mode and
to `<target_branch>` in feature mode. Switch the current worktree to that
destination and merge the selected source branch with a merge commit. Use
`--ignore-other-worktrees` so the switch goes through even when the destination
is also checked out in a sibling worktree:

```bash
git -C "<PRJ_DIR>" switch --ignore-other-worktrees "<destination_branch>"
git -C "<PRJ_DIR>" merge --no-ff "<source_branch>"
```

Ignore every sibling worktree folder, in both senses the spec asks for: the
`--ignore-other-worktrees` flag lets the switch proceed in place, and you
never read, switch, sync, or check the state of a folder such as
`..._main`. That sibling may end up out of sync with the new destination tip
after the merge; that is expected, the user deals with it later. Only the current
worktree matters, and its cleanliness was already checked in Step 4. Do not
stop because the destination is checked out elsewhere, and do not write outside the
current tree.

The green gate already ran after a feature `--onto` replay or integration sync
in Step 5, or was not needed because the selected branch already contained the
latest destination. Do not run it again after the Step 6 merge.

### Step 7 — Reword the merge commit

Run this step only when Step 6 produced a merge (skip it on the on-main
case). Do not skip it for any other reason, not to conserve context, and
never reword the merge with a free-form `git commit --amend -m "..."`: a
hand-typed message applies no template, so it comes out as a bare subject
and one paragraph, with no `Why:` / `What:` structure, which is exactly the
wrong shape for a release merge.

The merge commit message must be the product of the
`update-merge-commit-msg` skill, which applies the group-commits-msg
template: a `Why:` section (the reason for the merge, then the now-state it
allows) followed by a `What:` section with a dashed list of the changes.
Create the flag file if it is not already present, then invoke that skill:

```bash
touch "<PRJ_DIR>/a.prepare-release.active"
```

Because the flag file is present, that skill returns control here once the
merge message is final, rather than ending on its own.

Then verify the result before going on: the merge commit, which is HEAD at
this point, must carry the `Why:` and `What:` sections.

```bash
git -C "<PRJ_DIR>" show -s --format=%B HEAD
```

When the body has no `Why:` and no `What:` section, the reword did not go
through the skill (a free-form amend, or a skipped step). Do not continue to
Step 8: run `update-merge-commit-msg` again so the merge message gets the
required structure.

### Step 7A — Check the umbrella backlog before release artifacts

Run this checkpoint only for a feature-completion invocation, after its first
destination merge has been reworded. It deliberately runs before the wiki
audit, `version.txt`, `CHANGELOG.md`, pyproject, lockfile, or release commit.

In Step 3, record `<umbrella_draft>` when the feature requirement is related to
exactly one draft marked `- Draft role: umbrella` whose authoritative compact
table contains the feature slug. When there is no such collection draft, treat
the feature as standalone and continue to the full release path. A malformed
marked umbrella is an error, not a standalone feature.

For a collection, run the read-only post-merge lookup through the full launcher
path:

```powershell
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-merge "<umbrella_draft>" --root "<PRJ_DIR>"
```

Before using the printed host-prefixed command, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md) and trust
the prefix the tool selected.

- When it prints `process-draft on <umbrella_draft> based on <next-slug>`, the
  merged requirement is complete but the umbrella is not. Remove
  `a.prepare-release.active`, report the destination merge OID and structured
  subject, the original and landing branch names, and the untouched release
  files. Present that exact `process-draft` command as the next action and
  stop. Do not merge integration to main and do not enter Step 8.
- When it prints another workflow command for an already-created but unfinished
  item, report and present that command, remove the flag, and stop at the same
  boundary.
- When it prints `prepare-release`, every ordered collection item has a
  completed validation-plan status. Continue automatically:
  - if the feature destination was main, reclassify the remainder as on-main
    release preparation and continue to Step 8;
  - if the destination was integration, rerun the planner in integration mode,
    perform the integration sync from Step 5 when needed, then run Steps 6 and
    7 once more for the integration-to-main merge. Do not run this checkpoint
    again for that final merge; continue to Step 8.
- When the lookup exits non-zero or prints no command, stop without release
  artifacts and report the exact lookup error. Never guess that the collection
  is exhausted.

This is the automatic stop decision: the merge itself does not imply a release,
and a growing set of implemented requirements does not override the umbrella's
declared order.

### Step 8 — Audit and update existing Diataxis wiki roots

Check for these documentation roots:

- `<PRJ_DIR>/wiki`
- `<PRJ_DIR>/docs/wiki`

Do not create either root. When neither exists, record that the wiki audit was
not applicable and continue to Step 9. When one or both exist, audit every
existing root.

The review scope is the complete release range `<last_tag>..HEAD` at this
point. This is deliberately not the feature-only or integration-only planning
range: after Step 6, `HEAD` is the exact main history being prepared, and the
wiki must account for every commit that will be released. Read the commit
subjects, changed-file list, relevant per-topic diffs, and final state. A later
commit that reverted or replaced an earlier change determines what the wiki
should describe.

Create the flag file if it is not already present, then invoke
`review-and-update-project-docs` with:

- every existing wiki root as the only documentation target;
- `<last_tag>..HEAD` as the review scope;
- an explicit request to map every release topic to suitable wiki coverage,
  update gaps, validate links and Diataxis purpose, and report uncovered
  topics.

```bash
touch "<PRJ_DIR>/a.prepare-release.active"
```

The wiki review must preserve one purpose per page and category order:
explanation, tutorials, how-to guides, then reference. It need not force every
release topic into all four categories.

When the review reports an uncovered topic or an unresolved question, stop
and resolve it before continuing. When it changes no file, continue to Step 9.
When it changes wiki files:

1. Review the skill's validation results.
2. Stage only the changed files under the selected wiki roots.
3. Create or keep the flag file, invoke `group-commits-msg`, and wait for the
   user's commit review choice.
4. On a go-ahead selection, commit the wiki changes and return here.

The wiki commit must land before Step 10 prepares release notes, so its
conventional subject is part of the release history and changelog input.

### Step 9 — Set the snapshot version in version.txt

Read the first line of `<PRJ_DIR>/version.txt`. When its first word is not
the target `X.Y.Z-SNAPSHOT`, rewrite that first word to `X.Y.Z-SNAPSHOT`,
keeping the space-delimited `--` separator and the rest of the line. This is the form
`prepare_release_notes` and `brel` both expect.

### Step 10 — Prepare the release notes and the changelog

Create the flag file if it is not already present, then invoke the
`prepare_release_notes` skill:

```bash
touch "<PRJ_DIR>/a.prepare-release.active"
```

With the flag file present, it generates `a.md`, writes the `version.txt`
release-notes summary, pauses for you to pick a witty title, finalizes
`version.txt`, updates `CHANGELOG.md`, and then returns control here instead
of telling you to run `brel`.

Do not run `update-changelog.bat` again yourself: `prepare_release_notes`
already updates `CHANGELOG.md`, and `brel` regenerates it at release time.
Running it a third time here would be duplicate work.

### Step 11 — Review pause for version.txt and the changelog

Step 10 has written `version.txt` and `CHANGELOG.md`. Stop here, before Step
12, so the user can refine the release notes. This pause is for the
release-notes content only: the `version.txt` summary and the
`.changelog.fixes` rules that shape how `CHANGELOG.md` reads. It is not for
coding a project fix; the code was already taken to green by the `ghog day`
gate earlier.

1. Stage the two files Step 10 changed, as a baseline that makes any later
   edit trivial to detect with a `git diff`, and note the current HEAD, since
   the changelog is built from the git history and a commit landing during
   the pause makes it stale:

   ```bash
   git -C "<PRJ_DIR>" add version.txt CHANGELOG.md
   git -C "<PRJ_DIR>" rev-parse HEAD
   ```

2. Tell the user the run is paused for review. During the pause the user
   may:
   - edit the `version.txt` release-note summary (title, theme, key
     changes), and
   - request the creation or update of `.changelog.fixes`, the Perl
     find/replace rules `update-changelog` applies to the rendered
     changelog; make those edits on the user's request.

   Present the go-ahead choices and do not resume on your own:

   - `Go ahead` — check whether release-note inputs changed.

3. On a go-ahead selection, check whether anything that feeds the changelog
   changed since the baseline, comparing both the staged files and the HEAD
   noted in step 1:

   ```bash
   git -C "<PRJ_DIR>" diff -- version.txt CHANGELOG.md
   git -C "<PRJ_DIR>" rev-parse HEAD
   ```

   Treat it as changed when that diff is non-empty, when HEAD has moved since
   step 1 (a commit landed during the pause, for instance a fix committed
   here: the changelog is built from the git history, so a new commit makes it
   stale), or when you created or updated `.changelog.fixes` during the pause
   (its rules only reach the changelog through a regeneration).
   - When something changed, regenerate `CHANGELOG.md` so the edits and the
     fix rules take effect, then go back to step 1 of this step: re-stage,
     and pause again so the user reviews the regenerated changelog.

     ```bat
     tools\dev_workflow\update-changelog.bat
     ```

     Run it from PowerShell or cmd.exe, not from Git Bash — it is a `.bat`
     toolchain script (see [`../rules/run_commands.md`](../rules/run_commands.md)).

   - When nothing changed (a go-ahead selection that follows no further edit),
     continue to Step 12.

This loop ends on a go-ahead selection with nothing left to regenerate.

### Step 12 — Update the other version sources

`version.txt` is rarely the only file stating the version, and the others must
move with it. A project can hold the same version in `pyproject.toml`, in
`uv.lock`, in a Maven POM and its module parents, and in a `cicd/config/.env`
read by the CI shared library. Leaving one behind publishes an artifact under a
version no other file names.

When the project ships `tools/set_version.py`, that single call is the whole
step. Pass the snapshot form: `version.txt` stays at `X.Y.Z-SNAPSHOT` until
`brel`, and the tool gives each other source the form its own consumer expects.

```bash
python "<PRJ_DIR>/tools/set_version.py" X.Y.Z-SNAPSHOT
```

Without such a tool, edit each source that exists:

- `pyproject.toml`: set its `version` to the release `X.Y.Z`, with no
  `-SNAPSHOT`. The draft is explicit on that point, and the suffix is not a
  canonical PEP 440 identifier, so a Python conformity check rejects it.
- Maven POM: set the project version, and the parent reference of every
  module, to `X.Y.Z-SNAPSHOT`. A Maven snapshot carries the suffix.
- `cicd/config/.env`: set `APP_SERVICE_VERSION` to `X.Y.Z-SNAPSHOT`.

Then, only when a `pyproject.toml` exists:

- Run `uv sync` from `<PRJ_DIR>`.
- Confirm the release `X.Y.Z` is reflected in the regenerated `uv.lock`.

Finally, when the project ships `tools/check_versions.py`, run it and require
it to pass before Step 13. A failure there means two sources disagree, and the
prepare commit would record a version the project cannot name.

`pyproject.toml` deliberately sits at the release `X.Y.Z` while `version.txt`
stays at `X.Y.Z-SNAPSHOT` until `brel`; that gap is intended. The Maven sources
follow `version.txt` rather than `pyproject.toml`, for the same reason.

### Step 13 — Make the single prepare commit

Stage `version.txt`, `CHANGELOG.md`, `.changelog.fixes` when Step 11 changed
it, and every version source Step 12 touched, then commit them together:

```bash
git -C "<PRJ_DIR>" add version.txt CHANGELOG.md
git -C "<PRJ_DIR>" commit -m "chore(release): prepare for vX.Y.Z release"
```

Add `.changelog.fixes` to the `add` when Step 11 changed it, and whatever
Step 12 rewrote: `pyproject.toml`, `uv.lock`, the POM and its module POMs, and
`cicd/config/.env`. Keep it to this one commit, so the human review and the
later `brel` see one clean prepare step.

### Step 14 — Final clean-tree gate, report and stop

Check the tree one last time before reporting:

```bash
git -C "<PRJ_DIR>" status --porcelain
```

The Step 4 gate ran before any mutation, but the later pauses can
dirty the tree again (an editor or spell-checker tweak during the
Step 11 review, a tool-written file), and the Step 13 prepare commit
stages only the named release files, so anything else stays behind.
When the status is not empty, never present "run `brel`" as the next
step on a dirty tree: list the pending files, signal that `brel` must
start from a clean tree, keep (or re-create) the flag file, and
present the same choices as Step 4:

- `Go ahead` — run the `group-commits-msg` skill so the pending work
  is committed in tidy groups.

Continue to the report below only once `git status --porcelain` is
empty.

Remove the flag file:

```bash
rm -f "<PRJ_DIR>/a.prepare-release.active"
```

Then print a summary of what changed:

- the detected release mode: on-main, integration, or feature,
- the source branch or branches merged into their destinations (or the on-main
  case), and whether each was synchronized, replayed from a confirmed feature
  boundary onto a landing branch, or already based on its latest destination,
- in feature mode, the original branch, parent ref, boundary commit, confirmed
  commit count, first destination, umbrella-check result, and landing branch,
- the target version `X.Y.Z`, later-version note documents that stayed in the
  selected scope, and the slug,
- the files written (`version.txt`, `CHANGELOG.md`, and the pyproject and
  uv files when present),
- the prepare commit hash and subject.

Then tell the user the next step: review everything, and run `brel` to
build, finalize, and tag the release. This skill never runs `brel` and
never tags.

## Idempotency and the safe re-run

Run the skill twice and the second run does nothing harmful:

- The Step 2 guard stops a run with no new feature, issue, design, or plan
  commit since the last tag, with "release already done" (HEAD on a tag),
  "branch tip already released" (an old branch contained by a later tag), or
  "nothing to release yet".
- The Step 5 base check is a no-op once integration contains the latest main,
  recognizes an already-integrated feature, or is a no-op once a feature's
  confirmed range already sits safely on its latest destination.
- The Step 7A lookup repeats the same ordered collection decision from disk.
  Once one item is complete it advances to the next; once all are complete it
  returns `prepare-release` and the current run crosses the artifact boundary.
- The Step 9 version write is a no-op when `version.txt` already holds the
  target `X.Y.Z-SNAPSHOT`.
- `prepare_release_notes` stops on its own when the last tag already
  matches the snapshot version.

## Known limitations

- The handoff signal is the flag file `a.prepare-release.active` at the
  project root, not an environment variable (shell state does not survive
  between the separate shells each command runs in). The skill deletes a
  stale flag at the start of every run, so a crashed earlier run cannot
  leave a flag that lies about the state; a sub-skill run on its own, with
  no flag file present, behaves standalone, which is the wanted default.
- Step 5 first brings local main up to `origin/main` (fetched read-only) on
  every branch, main included. Off main, when local main is strictly behind,
  it moves the main ref with `git update-ref` even though main is checked out
  in the ignored sibling worktree (which then falls out of sync). On main,
  where the ref cannot move under the checked-out worktree, it stops and
  warns instead, leaving the fast-forward to the user. When local main and
  `origin/main` have diverged, the skill stops with the menu described in Step
  5 so the user can rebase local main onto `origin/main` rather than reset and
  drop local commits.
  With no remote, or unpushed main, it uses local main
  as-is. Feature mode also makes the resolved integration destination current
  when present; a diverged published integration ref stops for reconciliation.
- Reaching a green suite uses the `ghog day` loop (the `groundhog` skill).
  Integration branches are never rebased: main is merged into them before
  the gate when they do not contain the latest main. Feature replays use a
  separate landing branch so the original feature ref is never rewritten.
  Rebase conflicts are resolved by the user; on a go-ahead selection the
  skill resumes non-interactively with `GIT_EDITOR=true`. A `ghog day` failure
  is fixed, then committed through `group-commits-msg` with the user's review
  before the release goes on.
- Conflict previews require Git 2.50+ and are produced by the shared
  `prepare_release_plan.bat` launcher. `merge-tree` uses the same ort merge
  machinery without touching the index or working tree, but its result is
  tied to the exact refs and feature boundary supplied. Sequential rebase
  preview stops at the first conflict because a human resolution changes the
  synthetic tip for every later commit.
- Git does not always retain a feature's fork point: reflogs expire, and a
  fast-forward or squash merge can erase parent evidence. In that case the
  skill stops for a user-supplied parent or boundary commit. It never widens
  the range to make the release proceed.
- The planner models one source branch and one contiguous feature range. It
  cannot preview a revert-one recovery, a combined arbitrary topic subset, or
  a non-contiguous commit replay. The skill therefore stops before mutation
  and emits the evidence, commands, verification, and re-entry instructions
  required by "Unsupported planner handoffs". It also rejects an empty
  `main..integration` range even if ancestry-only planner output says
  `merge-no-ff`.
- Candidate document versions define the target label, not the release
  content. The lowest version newer than the last tag is the target;
  later-version notes remain in an integration release because the invocation
  branch selected them.
- Umbrella continuation depends on the explicit umbrella marker and canonical
  ordered status table written by `split-and-define`.
  `pw skill --after-merge` verifies every completed row against its named
  requirement and validation plan, and refuses missing, malformed, or stale
  collection state instead of assuming that release preparation may continue.
- The effort test keys on `feature`, `feature-request`, `issue`, `design`, and
  `plan` documents in the four supported effort directories. A release that is
  only code, with no such document, reads as "nothing to release"; add the
  matching document, or release it by hand. Versioned drafts are reported as
  notes but never trigger a release or choose its target.
- The skill stops, by design, before `brel`. Building, finalizing the
  changelog, and tagging stay manual.
