---
name: prepare-release
description: 'Automate the release-preparation process from any branch: detect the development effort since the last tag, base the effort branch on the latest origin/main (rebase with a ghog day gate when it is behind), merge it into main, set the X.Y.Z-SNAPSHOT version, run prepare_release_notes for the version.txt summary and changelog, update pyproject and uv, then make one chore(release) prepare commit. It stops before brel (which the user runs to build and tag) and never pushes. Use when the user asks to prepare or cut a release.'
user-invocable: true
metadata:
  - "This skill prepares every release artifact and stops before brel; it never creates the tag and never pushes."
  - "Step 1-2: find the last tag (git describe --tags --abbrev=0) and detect a development effort (a commit since the tag touching docs/{feature,issue,design,plan}.*). With none, stop with 'release already done' (HEAD on a tag) or 'nothing to release yet'."
  - "Step 3: derive the version from the newest effort document name and the slug from the branch when off main; cross-check version.txt; stop and ask on a version conflict."
  - "Step 4-5: make the current worktree clean (offer group-commits-msg when dirty); on every branch, main included, fetch origin/main and bring local main current (git update-ref to origin/main when behind off main, warn instead on main where the ref is checked out, ask the user to rebase main onto origin/main on divergence); then off main, when the branch is behind main, offer rebase (then a ghog day green gate), merge --no-ff anyway (ghog day gate after the merge), or abort."
  - "Step 6-7: switch to main with git switch --ignore-other-worktrees main and git merge --no-ff the effort branch in the current tree (leave sibling worktrees such as ..._main alone, even if they fall out of sync), then call update-merge-commit-msg so the merge message gets the group-commits-msg Why:/What: structure (never a free-form git commit --amend -m; verify both sections are present after the reword)."
  - "Step 8-12: set version.txt to X.Y.Z-SNAPSHOT, call prepare_release_notes for the summary and changelog, then pause for the user to review and adjust version.txt and .changelog.fixes (stage version.txt and CHANGELOG.md first and note HEAD; on go-ahead, regenerate the changelog when the staged files or HEAD changed (a commit landed during the pause) or .changelog.fixes was edited, re-staging and looping until a clean go-ahead), update pyproject.toml and uv when present, then make one chore(release): prepare for vX.Y.Z release commit (including .changelog.fixes when changed)."
  - "Step 13: report a summary and tell the user to review and run brel. It uses the flag file a.prepare-release.active (git-ignored, deleted at start, created before each sub-skill call, removed on exit) so the called skills return control to it."
---

[Instruction](../../../instructions/prepare-release.md)

Implementation is mutualized across the shared directories:

- [`../instructions/prepare-release.md`](../../../instructions/prepare-release.md)
  — the full workflow.

This skill calls the `group-commits-msg`, `update-merge-commit-msg`, and
`prepare_release_notes` skills, and runs the `ghog day` groundhog loop when
it rebases the branch or merges a stale base, using the flag file
`a.prepare-release.active` (git-ignored) so the called skills return control
to it instead of ending standalone. It readies every release artifact and
stops at the `chore(release): prepare for vX.Y.Z release` commit; the next
step is for the user to review and run `brel` to build and tag. The skill
never creates a tag and never pushes to a remote.
