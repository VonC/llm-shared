---
agent: ask
description: 'Write a summary of the changes made for this release.'
---

Your goal is to write a release note draft, explaining succinctly the general goals and the main changes of this release.

You will derive those goals from the list (present in your prompt or your context) of conventional commit subjects (composed of a type and a scope between '`*(scope)*`', followed by a colon, followed by a description).

Check other files in your context for more elements illustrating the objectives and deliveries included in this release.

Do not be overly descriptive, the goal is to have a concise but clear summary of the release, not a full changelog.

Separate each section with an empty line.
Make sure each line is at most 80 characters wide.

If you have in your context any `docs/plan.xxx.md` file, you can consider the plan as illustrating the context in which those commits were done: that can inform your redaction.

Once you have written the summary, propose 3 possible short titles and sub-titles for said release.

The titles and sub-titles must be witty, based on concrete elements, not on abstract "architectural refactoring" terminology.

For instance: title "Putting Time in its Place" / subtitle "It was time for a major clean-up."

You write a markdown document, so respect instructions for markdown lists in #file:./../markdown.instructions.md , but with lines of at most 80 characters.

Your markdown document must follow the structure:

```md
This release <explain its general purpose>

<Explain why this purpose was needed in a second paragraph>

<Explain how the result is better (or needs improvement) in a third paragraph>

### Key changes

- **Theme1, for instance "Domain Purification"**: short description

- **Theme2, for instance "Adapters Boundaries"**: short description

- **Theme3, for instance "Mapper Independence"**: short description

- ...

### Titles and Subtitles

1. Title: "A first witty title example".
   Subtitle: "A first witty subtitle example".

2. Title: "A second witty title example".
   Subtitle: "A second witty subtitle example".

3. Title: "A third witty title example".
   Subtitle: "A third witty subtitle example".
```
