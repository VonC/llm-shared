# Process a draft into a named, versioned effort

Take a draft document named in the prompt, run a light first-pass that names what
it is, give it a title, a slug, and a target version, then hand the rename and the
branch creation to the `new_draft` tool. The last step is a hand-off: a
single-topic draft goes to the `write-requirement` instruction; a draft holding
more than one topic goes to the `split-and-define` instruction.

Do not write the feature-request or issue document here, and do not reshape the
draft body. This instruction classifies, names, and versions the draft, lets the
tool rename and branch it, then points at the next step.

## Inputs for process-draft

- The draft document, named in the prompt (for example `docs\draft.duration_outliers.md`). If the prompt names no draft, or the file is missing, ask the user which file to process and stop.
- `version.txt` at the repository root, read in step 5 to propose the target version.
- The `new_draft` tool, called in step 6 to rename the draft and create the branch.

Read the draft in full before proposing anything. If its content is empty or too
thin to classify, say so and ask the user for more context before going on.

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
same need. Ask the user to pick one (or to write their own). Put the chosen title
at the top of the draft as its main heading, and leave the rest of the body alone,
so the later instruction reuses the title without losing what the user wrote.

## Step 4 for process-draft, propose three slugs

Propose three slugs to reference the effort. A slug is one word, or two or more
words joined by `_` (for example `duration_outliers` or `cdc_gap`). Keep to
lowercase letters, digits, `_`, or `-`, starting with a letter or a digit, so the
slug reads as both a branch name and a filename part.

Check each proposed slug for a branch collision before offering it, using the same
rule the `new_draft` tool applies: the local heads first, then every declared
remote. Drop a slug that already names a branch so the effort never lands on top of
existing work.

Ask the user to pick one slug (or to write their own valid, free one). The chosen
slug names the renamed file and the branch in step 6. When the draft holds several
topics, the chosen slug is the umbrella name for the draft file and the shared
branch; `split-and-define` derives a per-topic key title for each feature-request
and issue later, so one slug here is enough.

## Step 5 for process-draft, pick the target version from version.txt

Read `version.txt`. Take the first whitespace-separated token of its first line as
the current version string, for example `0.4.0` from a first line of
`0.4.0 -- One command starts the next effort`. Drop a trailing `-SNAPSHOT` (any
case) when it is present, so `1.2.0-SNAPSHOT` becomes `1.2.0`. Parse the result as
`X.Y.Z`. This parse rule lives in `new_draft_models.read_version_txt`, shared with
the tool, so the instruction and the tool read the file the same way.

Offer four candidates and ask the user to pick one. The three bumps reset the
parts below the one they step, the same rule the `new_draft` tool follows:

- `X.Y.Z`: keep the current version, to ride along with the in-progress release.
- `X+1.0.0`: step the major part and reset the minor and patch parts to 0.
- `X.Y+1.0`: step the minor part and reset the patch part to 0.
- `X.Y.Z+1`: step the patch part.

Show each option with its computed value, not the formula alone. For a current
`0.4.0`, the four options read `0.4.0`, `1.0.0`, `0.5.0`, and `0.4.1`. When the
draft holds several topics, the chosen version labels the draft and its branch;
each requirement that comes out of `split-and-define` settles its own version later.

## Step 6 for process-draft, rename and branch with the new_draft tool

Hand the mechanical part to the `new_draft` tool rather than running git by hand, so
the slug, worktree-path, and branch rules stay in one tested place. Ask the user for
the branch layout first, then call the tool:

- A separate worktree: a sibling folder next to the repository root, named `<base>_<slug>`, where `<base>` is the root folder name with any trailing `_<suffix>` dropped (so a root `llm-shared` or `llm-shared_main` both give `..\llm-shared_<slug>`).
- The current working tree: the branch is created in place.

Call the `new_draft` `--from-draft` mode with the values already gathered, passed as
flags so the tool prompts for nothing: the draft path, `--slug`, `--version`, and
`--worktree` or `--in-place`. The tool checks the slug for a collision, creates the
branch with `git switch -c <slug>` in the current tree or a sibling worktree with
`git worktree add -b <slug>`, then places the draft as `draft.vX.Y.Z.<slug>.md`
inside the chosen tree. In the current tree the rename is a `git mv` when the draft is
already tracked, or a plain file rename when it is still untracked; for a worktree the
tool reads the draft text, writes it under the worktree's `docs`, stages it, and drops
the source. Either way, a draft that is not yet committed still moves across. Because
the tool creates the tree first and writes the draft inside it, there is no
cross-tree file move to do by hand.

## Step 7 for process-draft, hand off to the next instruction

Present a multi-choice of the next step and run the chosen one, with no go-ahead beyond the pick. `pw skill` supplies the produced `draft.vX.Y.Z.<slug>.md` name; offer these and run the selection straight away:

- `/write-requirement on docs/draft.vX.Y.Z.<slug>.md` — one topic (one feature-request or issue, including the single-requirement exception from step 2); pass the type from step 2, the version as `vX.Y.Z` from step 5, and the slug from step 4.
- `/split-and-define on docs/draft.vX.Y.Z.<slug>.md` — more than one topic, regrouped into a list of feature-requests and issues before any requirement is written.
- Type something else — a free-text entry, supplied by the LLM and not by `pw`, for any other instruction the author types.

Pre-select the entry the step-2 topic count points at (`write-requirement` for one topic, `split-and-define` for several), and leave the other two for the author to pick.

## Design decisions for process-draft

These choices come from the two review rounds (Q01 to Q08); each row names the
question that settled it, the step where it is integrated, and the options that were
turned down.

| Area | Decision | Question | Integrated in | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Version source | Keep `version.txt`; the parse rule moves to a shared `new_draft_models.read_version_txt` | Q01 | Step 5 | `pyproject.toml` only; read both and reconcile |
| Mechanical steps | The `new_draft` `--from-draft` mode renames and branches; the instruction keeps the reader-only steps | Q02 | Step 6 | Restate the rules in prose; reuse helpers but stitch by hand |
| Branch safety | Check the slug for a collision and create with `git switch -c` | Q03 | Steps 4, 6 | `git switch -C` overwrite; `-C` after a warning |
| Worktree order | Create the branch or worktree first, then rename inside the chosen tree | Q04 | Step 6 | Rename then move into the worktree; commit then branch |
| Multi-topic naming | One umbrella slug and version name the draft and branch; per-topic keys come from `split-and-define` | Q05 | Steps 4, 5 | Skip naming until the split; branch the flow by topic count |
| Body edits | Light touch: set the heading and the `- Type:` line, leave the body | Q06 | Steps 2, 3 | Reshape to the skeleton; record the type only in the hand-off |
| Tool interface | `--from-draft` takes the slug, version, and layout as flags and prompts for nothing | Q07 | Step 6 | Re-prompt interactively; hybrid flag-or-prompt |
| Draft relocation | Read the text and write it into the chosen tree, stage it, drop the source; in place `git mv` a tracked draft or plain-rename an untracked one | Q08 | Step 6 | Require a commit first; rename then move into the worktree |
