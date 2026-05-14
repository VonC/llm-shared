# Write release notes summary

## Goal for the release notes summary

Write a release note draft that explains, in a few short paragraphs, the
general purpose of the release and its main changes. Derive those from
the list of conventional commit subjects in your prompt or context (each
subject is composed of a type and a scope between `*(scope)*`, followed
by a colon and a description).

Check other files in your context (design docs, issue/feature-request
docs, and any `docs/plan.xxx.md` files) for additional context on the
goals and deliveries of the release. A plan file, when present, frames
the context in which those commits were made and should inform the
redaction.

Stay concise: the goal is a clear summary, not a full changelog.

## Writing constraints for the release notes draft

- Each line is at most 80 characters wide.
- Sections are separated by an empty line.
- Follow the markdown list rules from
  [`markdown.md`](../rules/markdown.md): one space after the list
  marker, an empty line before the first item and after the last item,
  two-space indents for sub-items.
- Do not use words listed in [`blacklist.md`](../rules/blacklist.md).
  Replace them with simpler, direct language.

## Document structure for the release notes draft

The output is a markdown document with the following shape:

```md
This release <explain its general purpose>

<Explain why this purpose was needed in a second paragraph>

<Explain how the result is better (or needs improvement) in a third
paragraph>

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

## Witty titles guidance

After the summary, propose three short title and subtitle pairs.

- Titles and subtitles must be witty and grounded in concrete elements
  of the release (a renamed concept, a removed dependency, a measured
  speed-up, a fixed bug class), not abstract phrases like
  "architectural refactoring".
- Example: title "Putting Time in its Place", subtitle "It was time for
  a major clean-up.".

## Workflow for the release notes draft

1. Collect the conventional commit subjects already provided in the
   prompt or in the current context. If none are present, ask the user
   for the list before writing anything.
2. Read any `docs/plan.*.md` files referenced in the context to capture
   the framing of the release.
3. Group commits by theme (domain, adapters, mappers, performance,
   docs, etc.) and pick three to five themes for the "Key changes"
   list.
4. Write the three intro paragraphs (purpose, motivation, outcome),
   then the "Key changes" list, then the "Titles and Subtitles"
   section, all within the 80-character line limit.
5. Display the draft for user review.
