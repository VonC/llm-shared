# How to prepare a release from any branch

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📊 Goal: take a finished effort branch to a single
`chore(release): prepare for vX.Y.Z release` commit on `main`, ready for
the author to tag with `brel`.

## 📋 One command drives the whole prep

```txt
/prepare-release
```

From any branch, the skill: detects the effort since the last tag, makes
the tree clean, bases the branch on the latest `origin/main` (with a green
`ghog day` gate after a rebase), merges `--no-ff` into `main`, rewords the
merge commit, sets `version.txt` to `X.Y.Z-SNAPSHOT`, runs the
release-notes steps, updates `pyproject.toml` and `uv.lock`, and lands one
prepare commit. It never tags and never pushes.

It calls the smaller skills rather than repeating them
(`group-commits-msg`, `update-merge-commit-msg`, `prepare_release_notes`,
the groundhog loop), signalling each through the flag file
`a.prepare-release.active` so the callee hands control back.

## ⏸️ Where the run pauses for you

| Pause | What you decide or do |
| --- | --- |
| Dirty working tree | let the skill commit pending work, or stop and sort it out |
| Branch behind main | choose: rebase, merge `--no-ff` anyway, or abort |
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
[Where the human stays in the loop](../explanation/where-the-human-stays-in-the-loop.md).
