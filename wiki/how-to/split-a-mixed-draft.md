# How to split a mixed draft into requirements

<img src="../assets/logo-llm-shared-documents-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📝 Goal: turn one draft note that mixes several distinct topics into an
ordered list of feature-requests and issues, each ready for its own
`/write-requirement` run.

## Invocation model

The user supplies the draft and asks the AI to split and define it; the AI
classifies the content, writes the requirement artifacts, and presents the
boundaries for human validation. Follow the steps manually only when you need a
custom split outside the skill chain.

## 🤔 When splitting is worth it

Reach for `/split-and-define` when the draft mixes several items, when the
items differ in dependency order, or when you want the skill to propose a
slug per item. Skip it when the draft is one self-contained requirement:
call `/write-requirement` directly with the type, version and topic.

## 📋 Steps to split the draft

1. Make sure the draft has been processed: `/process-draft` classified it
   as a collection and renamed it
   `<effort-dir>/draft.vX.Y.Z.<slug>.md` on its own effort branch. The effort
   directory is one of the four layouts selected during `process-draft`.

2. Run the split:

   ```txt
   /split-and-define on <effort-dir>/draft.vX.Y.Z.<slug>.md
   ```

3. The skill appends a `## List of feature-requests and issues to create`
   section and adds `- Draft role: umbrella` after the collection type. The
   section starts with this canonical table:

   ```md
   | Order | Type | Key title | Slug | Status | Requirement | Validation plan |
   | --- | --- | --- | --- | --- | --- | --- |
   | 1 | Issue | Remove old routes | `route-cleanup` | pending | - | - |
   | 2 | Feature-request | Serve the root | `root-routing` | pending | - | - |
   ```

   Every new item is `pending`. The detail subsections below the table explain
   what was regrouped, why the title and boundary were chosen, and which prior
   items it depends on. Items are ordered from most independent to most
   dependent.

4. The skill runs:

   ```txt
   pw skill --after-merge <effort-dir>/draft.vX.Y.Z.<umbrella-slug>.md
   ```

   For a fresh umbrella it prints
   `/process-draft on <effort-dir>/draft.vX.Y.Z.<umbrella-slug>.md based on
   <first-slug>`. Run that continuation. It validates the ordered row, creates
   a focused child draft through a temporary unversioned source, inherits the
   umbrella's layout, and creates the item branch. It must write and verify the
   canonical `<effort-dir>/draft.vX.Y.Z.<first-slug>.md` file there before it
   pauses. Review that file itself; any complete copy shown in conversation is
   only a preview. Comments revise only the on-disk child and return to the
   same pause; an explicit `Go ahead` hands the approved draft to
   `/write-requirement`.

5. Let each item run through requirement, design, plan, implementation, and
   validation. When the last plan step turns the validation document into
   `Yes, it is implemented.`, `/implementation-check` updates the matching
   umbrella row in the same commit:

   ```md
   | 1 | Issue | Remove old routes | `route-cleanup` | completed | `docs/v10.0.0/issue.v10.0.0.route-cleanup.md` | `docs/v10.0.0/plan.v10.0.0.route-cleanup.validation.md` |
   ```

6. Run `/prepare-release` from the completed feature branch. It lands that
   exact feature on `develop` when present, otherwise `main`, rewords the merge,
   then runs the same `pw skill --after-merge` check. If another row is pending,
   the command proposes its `process-draft` continuation and stops before
   `main`, `version.txt`, or `CHANGELOG.md`. When every row is completed, it
   continues with full release preparation.

Do not manually mark rows completed. A pending row with complete validation
evidence or a completed row with missing evidence is a workflow error that must
be corrected at the final implementation check.

The focused writer still uses `pw skill --after-write requirement` for its
review, and the later implementation cycle uses `pw handoff`. The umbrella
checkpoint supplements those handoffs; it does not replace them.

## ✅ Check after the split

The draft is explicitly marked as an umbrella, its table is ordered and
machine-readable, and each row accurately records whether its evidence-backed
development effort is pending or completed. `pw` can now select the next row
without reconstructing progress from prose or filenames.

Related: [From draft note to settled requirement](../tutorials/02-from-draft-to-settled-requirement.md),
[skills catalog](../reference/skills-catalog.md).
