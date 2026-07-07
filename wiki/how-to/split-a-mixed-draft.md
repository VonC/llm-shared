# How to split a mixed draft into requirements

<img src="../assets/logo-llm-shared-documents-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📝 Goal: turn one draft note that mixes several distinct topics into an
ordered list of feature-requests and issues, each ready for its own
`/write-requirement` run.

## 🤔 When splitting is worth it

Reach for `/split-and-define` when the draft mixes several items, when the
items differ in dependency order, or when you want the skill to propose a
slug per item. Skip it when the draft is one self-contained requirement:
call `/write-requirement` directly with the type, version and topic.

## 📋 Steps to split the draft

1. Make sure the draft has been processed: `/process-draft` classified it
   as a collection and renamed it `docs\draft.vX.Y.Z.<slug>.md` on its own
   effort branch.

2. Run the split:

   ```txt
   /split-and-define on docs/draft.vX.Y.Z.<slug>.md
   ```

3. The skill appends a `## List of feature-requests and issues to create`
   section to the draft. Each entry carries:

   - the type (`Feature-request:` or `Issue:`),
   - a key title with a 2-3 word `[topic-slug]` in brackets,
   - the rationale for the regrouping.

   Items are ordered from most independent to most dependent, so they can
   be defined and implemented in that order.

4. The skill ends on a multi-choice with one
   `/write-requirement on docs/feature-request.vX.Y.Z.<slugN>.md` (or
   `issue.`) entry per slug. Pick the first item; repeat for each slug.

## ✅ Check after the split

The draft now ends with the list section, and each
`/write-requirement` run creates one `docs\<type>.vX.Y.Z.<topic>.md` that
enters its own review loop.

Related: [From draft note to settled requirement](../tutorials/02-from-draft-to-settled-requirement.md),
[skills catalog](../reference/skills-catalog.md).
