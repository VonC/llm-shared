---
name: prepare-release
description: 'Automate the release-preparation process from any branch: detect the development effort since the last tag, base the effort branch on the latest origin/main (rebase with a ghog day gate when it is behind), merge it into main, set the X.Y.Z-SNAPSHOT version, run prepare-release-notes for the version.txt summary and changelog, update pyproject and uv, then make one chore(release) prepare commit. It stops before brel (which the user runs to build and tag) and never pushes. Use when the user asks to prepare or cut a release.'
---

[Instruction](../../instructions/prepare-release.md)

