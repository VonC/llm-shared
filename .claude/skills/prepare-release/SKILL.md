---
name: prepare-release
description: 'Automate the release-preparation process from any branch: detect the development effort since the last tag, base the effort branch on the latest origin/main (rebase with a ghog day gate when it is behind), merge it into main, set the X.Y.Z-SNAPSHOT version, run prepare_release_notes for the version.txt summary and changelog, update pyproject and uv, then make one chore(release) prepare commit. It stops before brel (which the user runs to build and tag) and never pushes. Use when the user asks to prepare or cut a release.'
user-invocable: true
argument-hint: 'No argument needed. Run from any branch of a project that has a version.txt and the dev_workflow build (brel), with a design or plan document for the next version.'
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
