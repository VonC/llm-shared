# Arrange docs folders

Reorganize current effort documents under `docs/` into one of the layouts
defined by [`../rules/docs_layout.md`](../rules/docs_layout.md). Keep every
draft, requirement, design, plan, and validation plan for one version and topic
together.

## 1. Choose the target layout

Read [`../rules/interactive_menu.md`](../rules/interactive_menu.md), then present
one choice using computed examples from the first effort version found:

- `docs/` (`flat`);
- `docs/vX.Y/` (`minor`);
- `docs/vX.Y.Z/` (`version`, recommended);
- `docs/vX.Y/vX.Y.Z/` (`minor-version`);
- `docs/vX.Y.Z/<slug>/` (`version-slug`).

Wait for the user's choice before moving anything.

## 2. Move the files

1. Find Markdown effort files recursively under `docs/` whose basename matches
   `<type>.vX.Y.Z.<topic>.md`, including canonical drafts and validation plans.
2. Group them by their filename version and topic.
3. For each effort, compute the target directory from its version and the
   selected layout. Stop if two source files would map to the same target path.
4. Create the target directory and move every tracked file with `git mv`. Move
   untracked files without adding them to Git implicitly.
5. Check that the canonical draft and all related documents are together, and
   that `pw skill` resolves the effort from the new draft path.
6. Stage the approved moves with `git add -A docs/`.

## 3. Prepare the commit

Invoke the `group-commits-msg` workflow for the staged moves. Its normal review
gate owns `a.commit` formatting, validation, and batch commit. Do not call
`gcba.bat` until the user approves the displayed grouping.
