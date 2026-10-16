---
description: 'Check API architecture fit for Adapters'
---

Follow instructions from [check-api](check-api.md) for the adapters layer.

Consider only in your context ( in addition of [check-api](check-api.md) ) the files:

- `a.adapters.api` and

Start your analysis with the section `### Adapters Layer Analysis Overview`.  
Finish with a section `### Architectural Smells for Adapters`

Address the inbound and outbound adapters.

You document should match the following pattern:

```md
## Adapter Layer Analysis Overview

Explain what the adapter layer is for, in the context of this application, without detailing too much inbound and outbound (that will be done in the next two sub-sections).

### Inbound Adapters Layer Analysis

Explain what the inbound adapter layer is for, in the context of this application

Assess how well, based on the provided `a.adapters.api` API dump, the layer (the inbound part) is well-designed and adheres strictly to DDD and Hexagonal Architecture principles or not. How is the separation of concerns? Is there distinct and appropriate responsibilities for each component type?

### Outbound Adapters Layer Analysis

Explain what the outbound adapter layer is for, in the context of this application

Assess how well, based on the provided `a.adapters.api` API dump, the layer (the outbound part) is well-designed and adheres strictly to DDD and Hexagonal Architecture principles or not. How is the separation of concerns? Is there distinct and appropriate responsibilities for each component type?

### Architectural Smells for Adapters: `<number of smell/violation detected>`

Replace `<number of smell/violation detected>` with the number of smell/violation detected, and then proceed with:

- a short introduction on the layer cleanliness. And short explanation as to why it might have some violation or smell.
- a list of said violations or smells, or a single section to explain why there are none.
```

You write a markdown document, so respect instructions for markdown lists in [markdown.md](../../rules/markdown.md) : only one space in a list item: `- item 1` not `-   item 2` or `-  item 3`, `1. item 1` not `1.   item 2` or `1.  **item 3**`, etc.

Resolve input artifacts in the consuming project's review artifact home as
[artifact_files.md](../../rules/artifact_files.md) specifies. Resolve
`source.list`, when needed, from that project's root.
