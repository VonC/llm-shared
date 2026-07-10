# Prepare a release

Automate the release-preparation process up to, but not including, the
tag-cutting `brel`. Run it from any branch of any project that has a
`version.txt` and the dev_workflow build (`brel`). The skill readies every
release artifact, records them in one `chore(release): prepare for vX.Y.Z
release` commit, then stops so you can review everything and run `brel`
yourself.

This skill calls other skills and tools:

- `group-commits-msg` when the working tree is dirty, and when a `ghog day`
  green gate needed fixes that must be committed.
- `update-merge-commit-msg` after it merges the effort branch into main.
- `prepare_release_notes` for the `version.txt` summary and the
  `CHANGELOG.md`.
- the `ghog day` groundhog loop (the `groundhog` skill) to prove the suite
  is green when the branch was rebased onto the latest main or merged with a
  stale base.

It uses a flag file (`a.prepare-release.active`, see "The run flag file"
below) so those sub-skills hand control back to it instead of finishing
with their own standalone closing message (see "Handoff" in each sub-skill
body).

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

Every git and file step runs against the project root. Resolve it once
from `PRJ_DIR` when set, otherwise the current directory, and use it as
`<PRJ_DIR>` throughout. Resolve `<LLM_SHARED_DIR>` the same project-portable
way the other skills use, so the shared scripts are found from any
consuming repository.

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
  "docs/feature*" "docs/issue*" "docs/design*" "docs/plan*"
```

When that list is empty, make no change to the tree and stop with one of
two messages:

- If HEAD sits exactly on a tag (idempotency, the release was just done):

  ```bash
  git -C "<PRJ_DIR>" describe --tags --exact-match HEAD
  ```

  When that succeeds, print "release already done for `<tag>`" and stop.
- Otherwise, print "nothing to release yet, no development effort in
  progress" and stop.

Only when the effort list is non-empty do you go on. This is the guard that
makes a second run a no-op.

### Step 3 — Derive the target version and the slug

Read the version from the effort documents detected in Step 2, matching
`docs/{feature,issue,design,plan}.vX.Y.Z.*.md`. Prefer a design or plan
document when one exists, it is the most authoritative for a release
version; otherwise use the feature-request or issue document (a
feature-only effort, like this very release, has no design or plan).
Take the newest when several share one version. The slug is that document
topic, or the current branch name when the work is not on main:

```bash
git -C "<PRJ_DIR>" rev-parse --abbrev-ref HEAD
```

Cross-check the derived `X.Y.Z` against the first word of `version.txt`:

- No feature, issue, design, or plan document found means there is nothing
  to release; stop with that message.
- Several documents carry different versions: stop and present a version choice,
  with one row per detected version. Do not guess.
- `version.txt` still holds the previous release number (no `-SNAPSHOT`),
  or a matching `X.Y.Z-SNAPSHOT`: that is expected, Step 8 sets it.
- `version.txt` holds a different `-SNAPSHOT` version: stop and present a
  version choice with the effort-document version and the `version.txt`
  version.

Then check the effort's validation plan,
`docs/plan.vX.Y.Z.<topic>.validation.md`, when the effort has a plan. Read
its opening status line (the first non-title line): when it still starts
with `No, it is not implemented`, the implementation checks of the effort
are not complete, or the last `implementation-check` never flipped the
document-level line to `Yes, it is implemented.` as its instruction
requires. Signal it to the user, naming the file and the line found, remove
the flag file, and stop without changing the tree. The user either finishes
the implementation checks or corrects the status line, then re-runs. Do not
carry an effort whose validation plan reads as unfinished into a release.

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

### Step 5 — Base on the latest main

This step has two halves. The first, making local main current with
`origin/main`, runs on every branch, main included, so a release never goes
out on a local main that trails the remote. The second, basing the effort
branch on that main, is skipped when HEAD is already main: there is no
branch to rebase.

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

From here, local `main` is the latest main, and the branch check below, any
rebase, and the Step 6 merge all reference it.

#### Base the effort branch on the latest main

Skip this half when HEAD is already main: there is no branch to rebase, the
half above already made local main current, and Step 6 is skipped on main
too.

Check whether local main is already an ancestor of the branch tip:

```bash
git -C "<PRJ_DIR>" merge-base --is-ancestor main HEAD
```

When that succeeds (exit 0), the branch is already based on the latest
main: go straight to Step 6, with no rebase and no extra test.

When it does not (the branch is behind main), stop and offer the user three
choices. Use the chosen path; do not guess.

1. Rebase the branch onto main, then test:
   - Rebase in place:

     ```bash
     git -C "<PRJ_DIR>" rebase main
     ```

   - When the rebase reports conflicts, stop and report the conflicted
     files. The user resolves them (edit, then `git add`). Present the
     `Go ahead` choice; when selected, resume the rebase without an editor
     popping up:

     ```bat
     cmd /V /C "set "GIT_EDITOR=true" && git rebase --continue"
     ```

     The rebase may stop again on the next conflicting commit; repeat
     resolve-then-continue until it finishes.
   - Once the rebase finishes cleanly, run the green-gate routine on the
     rebased branch, then go to Step 6.
2. Merge `--no-ff` anyway:
   - Accept the stale base and go to Step 6 as-is. Because the base is
     stale, Step 6 runs the green-gate routine after the merge; this is the
     only case where it does.
3. Abort the release preparation:
   - Remove the flag file and stop, changing nothing.

### Step 6 — Switch to main and merge the effort branch

When HEAD is already main, skip this whole step: Step 5 already made local
main current with `origin/main`, and there is no branch to merge.

Otherwise switch the current worktree to main and merge the effort branch
with a merge commit. Use `--ignore-other-worktrees` so the switch goes
through even when main is also checked out in a sibling worktree (such as
`..._main`):

```bash
git -C "<PRJ_DIR>" switch --ignore-other-worktrees main
git -C "<PRJ_DIR>" merge --no-ff "<effort_branch>"
```

Ignore every sibling worktree folder, in both senses the spec asks for: the
`--ignore-other-worktrees` flag lets the switch proceed in place, and you
never read, switch, sync, or check the state of a folder such as
`..._main`. That sibling may end up out of sync with the new main tip after
the merge; that is expected, the user deals with it later. Only the current
worktree matters, and its cleanliness was already checked in Step 4. Do not
stop because main is checked out elsewhere, and do not write outside the
current tree.

When you reached this step through the "merge --no-ff anyway" choice of
Step 5 (the branch was not based on the latest main), run the green-gate
routine now, after the merge, before going on. In every other case the gate
already ran during the rebase in Step 5, or was not needed because the
branch was already based on the latest main, so do not run it again here.

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

### Step 8 — Set the snapshot version in version.txt

Read the first line of `<PRJ_DIR>/version.txt`. When its first word is not
the target `X.Y.Z-SNAPSHOT`, rewrite that first word to `X.Y.Z-SNAPSHOT`,
keeping the ` -- ` separator and the rest of the line. This is the form
`prepare_release_notes` and `brel` both expect.

### Step 9 — Prepare the release notes and the changelog

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

### Step 10 — Review pause for version.txt and the changelog

Step 9 has written `version.txt` and `CHANGELOG.md`. Stop here, before Step
11, so the user can refine the release notes. This pause is for the
release-notes content only: the `version.txt` summary and the
`.changelog.fixes` rules that shape how `CHANGELOG.md` reads. It is not for
coding a project fix; the code was already taken to green by the `ghog day`
gate earlier.

1. Stage the two files Step 9 changed, as a baseline that makes any later
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
     continue to Step 11.

This loop ends on a go-ahead selection with nothing left to regenerate.

### Step 11 — Update pyproject.toml and uv

Only when a `pyproject.toml` exists at `<PRJ_DIR>`:

- Set its `version` to the release `X.Y.Z` (no `-SNAPSHOT` here, the draft
  is explicit on that point).
- Run `uv sync` from `<PRJ_DIR>`.
- Confirm the release `X.Y.Z` is reflected in the regenerated `uv.lock`.

`pyproject.toml` deliberately sits at the release `X.Y.Z` while
`version.txt` stays at `X.Y.Z-SNAPSHOT` until `brel`; that gap is intended.

### Step 12 — Make the single prepare commit

Stage `version.txt`, `CHANGELOG.md`, `.changelog.fixes` when Step 10 changed
it, and, when present, `pyproject.toml` and `uv.lock`, then commit them
together:

```bash
git -C "<PRJ_DIR>" add version.txt CHANGELOG.md
git -C "<PRJ_DIR>" commit -m "chore(release): prepare for vX.Y.Z release"
```

Add `.changelog.fixes` to the `add` when Step 10 changed it, and
`pyproject.toml` and `uv.lock` when Step 11 ran. Keep it to this one commit,
so the human review and the later `brel` see one clean prepare step.

### Step 13 — Report and stop

Remove the flag file:

```bash
rm -f "<PRJ_DIR>/a.prepare-release.active"
```

Then print a summary of what changed:

- the effort branch merged into main (or the on-main case), and whether it
  was rebased, merged with a stale base, or already based on the latest
  main,
- the target version `X.Y.Z` and the slug,
- the files written (`version.txt`, `CHANGELOG.md`, and the pyproject and
  uv files when present),
- the prepare commit hash and subject.

Then tell the user the next step: review everything, and run `brel` to
build, finalize, and tag the release. This skill never runs `brel` and
never tags.

## Idempotency and the safe re-run

Run the skill twice and the second run does nothing harmful:

- The Step 2 guard stops a run with no new feature, issue, design, or plan
  commit since the last tag, with either "release already done" (HEAD on a
  tag) or "nothing to release yet".
- The Step 5 base check is a no-op once the branch is based on the latest
  main (the common case after a rebase).
- The Step 8 version write is a no-op when `version.txt` already holds the
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
  as-is. The branch half, skipped on main, then references the local `main`
  ref for the rebase check.
- Reaching a green suite uses the `ghog day` loop (the `groundhog` skill).
  Rebase conflicts are resolved by the user; on a go-ahead selection the
  skill resumes the rebase non-interactively with `GIT_EDITOR=true`. A
  `ghog day` failure is fixed, then committed through `group-commits-msg`
  with the user's review before the release goes on.
- The effort test keys on the `docs/{feature,issue,design,plan}.*` files. A
  release that is only code, with no such document, reads as "nothing to
  release"; add the matching document, or release it by hand.
- The skill stops, by design, before `brel`. Building, finalizing the
  changelog, and tagging stay manual.
