---
description: 'Check API architecture fit for Application'
---

Follow instructions from [check-api](check-api.md) for the application layer.

Consider only in your context ( in addition of [check-api](check-api.md) ) the files:

- `a.application.api` and

Start your analysis with the section `### Application Layer Analysis Overview`.  
Finish with a section `### Architectural Smells for layer Application`

You document should match the following pattern:

```md
## Application Layer Analysis Overview

Explain what the application layer is for, in the context of this application.

Assess how well, based on the provided `a.application.api` API dump, the layer is well-designed and adheres strictly to DDD and Hexagonal Architecture principles or not. How is the separation of concerns? Is there distinct and appropriate responsibilities for each component type?

Address in three separate sections:

- **Application Services and Handlers**
- **Commands, Queries, and DTOs**
- **Ports and Translators**

### Architectural Smells for Application: `<number of smell/violation detected>`

Replace `<number of smell/violation detected>` with the number of smell/violation detected, and then proceed with:

- a short introduction on the layer cleanliness. And short explanation as to why it might have some violation or smell.
- a list of said violations or smells, or a single section to explain why there are none.
```

You write a markdown document, so respect instructions for markdown lists in [markdown.md](../../rules/markdown.md) .

Resolve input artifacts in the consuming project's review artifact home as
[artifact_files.md](../../rules/artifact_files.md) specifies. Resolve
`source.list`, when needed, from that project's root.
