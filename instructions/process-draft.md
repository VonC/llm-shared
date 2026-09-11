# Process a draft into a named, versioned effort

Take a draft document named in the prompt and use one of two modes:

- **Initial draft mode** runs a light first-pass that names the draft, gives it
  a title, slug, target version, and documentation layout, then hands the rename
  and branch creation to the `new_draft` tool.
- **Umbrella continuation mode** is selected by
  `process-draft on <umbrella-draft> based on <item-slug>`. It takes the next
  ordered item from an already settled collection, creates a focused child
  draft without changing the umbrella, and creates the item branch.

The last step is a hand-off: a single-topic initial draft goes to the
`write-requirement` instruction; an initial draft holding more than one topic
goes to the `split-and-define` instruction. An umbrella-derived child first
stops for human review and reaches that hand-off only after explicit approval.

Umbrella continuation must produce a real Markdown child draft on disk in the
new item branch or worktree before that review gate. That file is the review
artifact and the authoritative source for revisions. Showing its proposed or
current content in a chat response is only a preview and never substitutes for
creating and preserving the file for the human to review.

The child must also be a new working-tree result of the current continuation.
Merely finding an unchanged tracked file inherited from branch history does not
count as producing the draft. Before opening the review gate, run
`git status --short -- <child-path>` in the selected branch or worktree and
require an entry for that exact path as untracked, added, renamed, or materially
modified. A clean result means no review artifact was produced by this run, even
when a file already exists at that path.

Do not write the feature-request or issue document here. In initial mode, do not
reshape the draft body. In umbrella continuation mode, the focused child draft
is deliberately derived from one settled item while the umbrella remains
unchanged.

## Inputs for process-draft

- The draft document, named in the prompt (for example `docs\draft.duration_outliers.md`). If the prompt names no draft, or the file is missing, ask for the draft path and stop unless a valid path is supplied.
- In umbrella continuation mode, the `based on <item-slug>` selector printed by
  `pw skill --after-merge`. The selector must name exactly one entry below
  `## List of feature-requests and issues to create` in a draft marked
  `- Draft role: umbrella`.
- `version.txt` at the repository root, read in step 5 to propose the target version.
- [`../rules/docs_layout.md`](../rules/docs_layout.md), which defines the four
  supported effort-directory layouts and how later skills recover the choice.
- The `new_draft` tool, called in step 7 to rename the draft and create the branch.

Read the draft in full before proposing anything. If its content is empty or too
thin to classify, say so and ask for added context, then stop unless enough
context is supplied.

## Umbrella continuation mode

Run this section before the ordinary numbered steps when the prompt contains
`based on <item-slug>`.

1. Read the umbrella draft in full. Require `- Draft role: umbrella`, then
   parse the exact compact table below the authoritative
   `## List of feature-requests and issues to create` heading. Find the one row
   whose backticked `Slug` cell equals the selector. Stop when the marker,
   heading, canonical columns, consecutive order, row, or type is missing,
   malformed, or duplicated.
2. Recheck the ordering decision that `pw skill --after-merge` made. Every
   earlier row must be `completed`, name its requirement and validation plan,
   and point to a validation plan whose first non-title line is exactly
   `Yes, it is implemented.`. The selected row must be `pending`, its two
   document cells must be `-`, and no requirement document may already exist
   for its slug. When either check fails, rerun
   `pw skill --after-merge <umbrella-draft>` through its launcher and report
   its result instead of creating a competing branch or document.
3. Reuse the selected row's type, key title, slug, and the umbrella filename's
   `vX.Y.Z`. Infer the documentation layout kind from the umbrella draft's
   parent directory and apply that kind to the child version. Do not present
   the title, slug, version, documentation-layout, or type menus from Steps 2
   to 6: `split-and-define` already settled the identity and the umbrella path
   already records the layout.
4. Create a temporary unversioned child source at
   `<umbrella-dir>/draft.<item-slug>.md`. Its heading is the settled key title;
   its metadata records the settled type and the exact repository-relative
   umbrella path in `- Umbrella: <umbrella-draft>`. Write the value as plain
   path text after the colon: never surround it with Markdown backticks,
   quotation marks, angle brackets, or link syntax. `pw` consumes the exact
   literal value, so formatting characters become part of the filename and
   cause an `umbrella does not exist` error. Include the selected split entry
   and the matching requirement-detail subsection plus the umbrella sections,
   rules, examples, and constraints that entry says it regroups. Preserve
   their meaning and concrete detail; do not pull in work assigned to another
   item. Write this source as an actual Markdown file; do not keep the derived
   draft only in the conversation. Never edit, rename, or delete the umbrella
   draft.
5. Continue at Step 7 and present only the branch-layout choice. Pass the
   temporary child source to `new_draft --from-draft` with the already settled
   slug, version, and inherited `--docs-layout` value. The tool moves that child
   source to `draft.vX.Y.Z.<item-slug>.md` in the derived effort directory in
   the new branch or worktree; the umbrella stays in the integration tree and
   is inherited by the new branch.
   - Recovery exception: when the human explicitly states that the current
     branch is already the selected item branch and `new_draft` would reject its
     existing name, do not create a competing branch. Rebuild the canonical
     child in place from the current umbrella row and detail subsection, using
     any pre-existing child only as revision context. The result must contain a
     truthful, material focused-draft change; never add a cosmetic marker just
     to dirty the path. If no material reconciliation is possible, stop and
     report the unexpected unchanged artifact instead of claiming creation.
   After the normal or recovery route, read the final child path and verify that
   it is a real file containing the focused draft. Then run
   `git status --short -- <child-path>` in that branch or worktree and require
   the exact path to appear as untracked, added, renamed, or modified. Step 7 is
   incomplete while the file is absent or that path-scoped status is clean; a
   pre-existing tracked file or chat-rendered copy does not satisfy this check.
6. After Step 7 creates the item branch or worktree and the focused child draft,
   lead with the exact path-scoped Git status entry and clickable child-file
   path, followed by its complete current content. Tell the human to review the
   file itself as the changed artifact; the conversation copy is only a
   convenience. Keep the child file on disk throughout this gate. State that
   the umbrella remains
   unchanged, then stop for human review. Do not run `pw skill`, enter Step 8,
   or invoke `write-requirement` yet.
   - When the human supplies comments, update only the focused child draft,
     present its complete revised content, and stop at this same review gate
     again. Repeat until the human explicitly approves it.
   - Treat only an explicit `Go ahead` as approval. Discussion, questions, and
     draft corrections do not authorize the hand-off.
7. After that approval, continue at Step 8 as one topic and hand off to
   `write-requirement`, passing the settled type, version, and slug. The
   umbrella draft remains associated context for the requirement.

The ordinary initial-mode steps below do not run in umbrella continuation mode
except for Steps 7 and 8 as narrowed above. The human review gate applies only
to the umbrella-derived child; an initial draft keeps the direct Step 8 hand-off.

## User choices for process-draft

Every user choice in this instruction follows
[`../rules/interactive_menu.md`](../rules/interactive_menu.md). Read that rule
before presenting the first choice. Present one choice at a time and wait for
the selection before showing the next choice. Do not batch the title, slug,
version, documentation-layout, and branch-layout choices into one chat prompt.

The five setup menus are:

1. title choice;
2. slug choice;
3. target-version choice;
4. documentation-layout choice;
5. branch-layout choice.

Each step below specifies the concrete choices for that decision. The shared
rule decides whether to add standard final entries or use a plain-text fallback.

## Step 1 for process-draft, read the draft

Resolve the draft path from the prompt and read the whole file. Note its current
heading, the topics it raises, and whether it already states a type or a title.

## Step 2 for process-draft, classify and record the type

Run the light first-pass with one question in mind: is this draft one
feature-request, one issue, or a collection of both (several topics)?

- A feature-request asks for a new or changed behavior that does not exist yet.
- An issue describes a current behavior that is wrong and a target behavior that fixes it.
- A collection of both holds more than one such topic in the same draft.

Keep the body as the user wrote it. The only edits this instruction makes to the
draft are the type line below and the heading in step 3; the deeper shaping is the
job of `write-requirement` or `split-and-define`. Record the type at the top of the
draft so it is written plainly, if the user has not already written it. Add or
confirm a short metadata line near the top, for example:

```md
- Type: feature-request
```

or, when the draft covers more than one topic:

```md
- Type: collection (feature-requests and issues)
```

Also record how many topics the draft holds (one, or several), because the hand-off
in step 7 branches on that count. If the draft already declares its type clearly,
keep the user's wording and only confirm it.

When the draft holds several topics, watch for one exception: if the draft states,
in plain words, that those topics must stay one single feature-request or one
single issue, treat it as one topic for step 7 even though it reads as several.

## Step 3 for process-draft, propose three witty titles

Propose three short, witty titles for the draft, each one a different angle on the
same need. Present those three titles as the concrete choices. Put the chosen
or custom title at the top of the draft as its main heading, and leave the rest
of the body alone, so the later instruction reuses the title without losing what
the user wrote.

## Step 4 for process-draft, propose three slugs

Propose three slugs to reference the effort. A slug is one word, or two or more
words joined by `_` (for example `duration_outliers` or `cdc_gap`). Keep to
lowercase letters, digits, `_`, or `-`, starting with a letter or a digit, so the
slug reads as both a branch name and a filename part.

Check each proposed slug for a branch collision before offering it, using the same
rule the `new_draft` tool applies: the local heads first, then every declared
remote. Drop a slug that already names a branch so the effort never lands on top of
existing work.

Present the collision-free slugs as the concrete choices. A custom slug must
pass the same validation and branch-collision checks before it is accepted. The
chosen slug names the renamed file and the branch in step 6. When the draft
holds several topics, the chosen slug is the umbrella name for the draft file
and the shared branch; `split-and-define` derives a per-topic key title for each
feature-request and issue later, so one slug here is enough.

## Step 5 for process-draft, pick the target version from version.txt

Read `version.txt`. Take the first whitespace-separated token of its first line as
the current version string, for example `0.4.0` from a first line of
`0.4.0 -- One command starts the next effort`. Drop a trailing `-SNAPSHOT` (any
case) when it is present, so `1.2.0-SNAPSHOT` becomes `1.2.0`. Parse the result as
`X.Y.Z`. This parse rule lives in `new_draft_models.read_version_txt`, shared with
the tool, so the instruction and the tool read the file the same way.

Offer four candidates as the concrete choices. The three bumps reset the parts
below the one they step, the same rule the `new_draft` tool follows:

- `X.Y.Z`: keep the current version, to ride along with the in-progress release.
- `X+1.0.0`: step the major part and reset the minor and patch parts to 0.
- `X.Y+1.0`: step the minor part and reset the patch part to 0.
- `X.Y.Z+1`: step the patch part.

Show each option with its computed value, not the formula alone. For a current
`0.4.0`, the four options read `0.4.0`, `1.0.0`, `0.5.0`, and `0.4.1`. A custom
version must parse as `X.Y.Z` before it is accepted. When the draft holds several topics, the chosen version labels the
draft and its branch; each requirement that comes out of `split-and-define`
settles its own version later.

## Step 6 for process-draft, choose the documentation layout

Read [`../rules/docs_layout.md`](../rules/docs_layout.md). Using the target
`vX.Y.Z` selected in Step 5, present these four concrete directory choices:

- `docs/` (`--docs-layout flat`): keep every effort document directly under
  the documentation root; this preserves the historical layout.
- `docs/vX.Y/` (`--docs-layout minor`): group all patch releases for one minor
  release line.
- `docs/vX.Y.Z/` (`--docs-layout version`): group each exact release version in
  one directory. Mark this as the recommended choice because it adds one useful
  boundary without a second directory level.
- `docs/vX.Y/vX.Y.Z/` (`--docs-layout minor-version`): group exact versions
  below their minor release line for repositories with many maintained lines.

Show the computed paths, not the formulas alone. For target version `0.4.1`,
the choices are `docs/`, `docs/v0.4/`, `docs/v0.4.1/`, and
`docs/v0.4/v0.4.1/`. This choice is per effort. The canonical draft's parent
directory records it for `pw` and every later writing skill.

## Step 7 for process-draft, rename and branch with the new_draft tool

Hand the mechanical part to the `new_draft` tool rather than running git by hand,
so the slug, worktree-path, and branch rules stay in one tested place. Present
the branch-layout choices, then call the tool:

- A separate worktree: a sibling folder next to the repository root, named `<base>_<slug>`, where `<base>` is the root folder name with any trailing `_<suffix>` dropped (so a root `llm-shared` or `llm-shared_main` both give `..\llm-shared_<slug>`).
- The current working tree: the branch is created in place.

Call the `new_draft` `--from-draft` mode with the values already gathered, passed as
flags so the tool prompts for nothing: the draft path, `--slug`, `--version`,
`--docs-layout`, and `--worktree` or `--in-place`. The tool checks the slug for a
collision, creates the branch with `git switch -c <slug>` in the current tree or
a sibling worktree with `git worktree add -b <slug>`, then places the draft as
`draft.vX.Y.Z.<slug>.md` inside the selected effort directory. In the current
tree the rename is a `git mv` when the draft is
already tracked, or a plain file rename when it is still untracked; for a worktree the
tool reads the draft text, writes it under the selected effort directory in the
worktree, stages it, and drops the source. Either way, a draft that is not yet
committed still moves across. Because the tool creates the tree first and writes
the draft inside it, there is no cross-tree file move to do by hand.

## Step 8 for process-draft, hand off to the next instruction

Before using or showing a host-prefixed workflow command, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md) and use its
prefix rule.

Present the next-step choice and run the chosen one, with no go-ahead beyond
the pick. `pw skill` (run via its launcher, see [`run-pw.md`](run-pw.md))
supplies the produced draft's actual repository-relative path. Reuse that
printed path verbatim; do not reconstruct one of the four layouts. Offer these
and run the selection straight away:

- `<command-prefix>write-requirement on <effort-dir>/draft.vX.Y.Z.<slug>.md` — one topic (one feature-request or issue, including the single-requirement exception from step 2); pass the type from step 2, the version as `vX.Y.Z` from step 5, and the slug from step 4.
- `<command-prefix>split-and-define on <effort-dir>/draft.vX.Y.Z.<slug>.md` — more than one topic, regrouped into a list of feature-requests and issues before any requirement is written.
- `Type something else` — let the author provide a different next instruction or correction.

Pre-select the entry the step-2 topic count points at (`write-requirement` for one topic, `split-and-define` for several), and leave the other entries for the author to pick.

## Design decisions for process-draft

The original choices come from the two review rounds (Q01 to Q08); the
documentation-layout row records the later configurable-layout extension. Each
row names its source, integration step, and alternatives.

This table is a seeded design record for this instruction, not a consolidation
output. Its `Question` column sits third on purpose. Do not copy this column
order into a document's decisions section: `pw skill` routes on a row opening
with `| Qxx`, so a consolidated table must lead with the question id, as
[`consolidate-then-review-ask-questions.md`](consolidate-then-review-ask-questions.md)
specifies.

| Area | Decision | Question | Integrated in | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Version source | Keep `version.txt`; the parse rule moves to a shared `new_draft_models.read_version_txt` | Q01 | Step 5 | `pyproject.toml` only; read both and reconcile |
| Mechanical steps | The `new_draft` `--from-draft` mode renames and branches; the instruction keeps the reader-only steps | Q02 | Step 7 | Restate the rules in prose; reuse helpers but stitch by hand |
| Branch safety | Check the slug for a collision and create with `git switch -c` | Q03 | Steps 4, 7 | `git switch -C` overwrite; `-C` after a warning |
| Worktree order | Create the branch or worktree first, then rename inside the chosen tree | Q04 | Step 7 | Rename then move into the worktree; commit then branch |
| Multi-topic naming | One umbrella slug and version name the draft and branch; per-topic keys come from `split-and-define` | Q05 | Steps 4, 5 | Skip naming until the split; branch the flow by topic count |
| Body edits | Light touch: set the heading and the `- Type:` line, leave the body | Q06 | Steps 2, 3 | Reshape to the skeleton; record the type only in the hand-off |
| Tool interface | `--from-draft` takes the slug, version, docs layout, and branch placement as flags and prompts for nothing | Q07 | Step 7 | Re-prompt interactively; hybrid flag-or-prompt |
| Draft relocation | Read the text and write it into the chosen tree, stage it, drop the source; in place `git mv` a tracked draft or plain-rename an untracked one | Q08 | Step 7 | Require a commit first; rename then move into the worktree |
| Documentation layout | Offer `docs/`, `docs/vX.Y/`, `docs/vX.Y.Z/`, and `docs/vX.Y/vX.Y.Z/`; persist the choice in the draft parent | User request | Step 6 | One fixed version/topic directory; project-global configuration |
| Umbrella child approval | Present and revise an umbrella-derived child until explicit human approval; keep an initial draft's direct hand-off | User request | Umbrella continuation Steps 6 and 7 | Send every child directly to `write-requirement`; pause initial drafts too |
