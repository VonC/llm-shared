---
agent: ask
description: 'Check API architecture fit for Domain Others'
---

Follow instructions from #file:check-api.prompt.md for the rest of the domain layer (except splitting domain, already analyzed).

Consider only in your context ( in addition of #file:check-api.prompt.md ) the files:

- #file:../../a.domain.root.api
- #file:../../a.domain.monitoring.api
- #file:../../a.domain.shared.api
- #file:../../a.domain.archiving.api
- #file:../../a.domain.workflow.api


Start your analysis with the section `### Other Domains Layer Analysis`.  
Finish with a section `### Architectural Smells for Other Domains`.

Address the domains root, monitoring, shared, archiving and workflow in your analysis and smell sections.

You document should match the following pattern (do not start with `## Domain Layer Analysis Overview`, as that is reserved for the splitting domain analysis):

```md
### Other Domains Layer Analysis

Assess how well, based on the provided `a.domain.xxx.api` API dump, the "`xxx` domain" layer is well-designed and adheres strictly to DDD and Hexagonal Architecture principles or not. How is the separation of concerns? Is there distinct and appropriate responsibilities for each component type?

Do so for each layer: `#### root`, `#### monitoring`, `#### shared`, `#### archiving` and `#### workflow`.

### Architectural Smells for Other Domains: `<number of smell/violation detected>`

Replace `<number of smell/violation detected>` with the number of smell/violation detected, and then proceed with:

- a short introduction on the layer cleanliness. And short explanation as to why it might have some violation or smell.
- a list of said violations or smells, or a single section to explain why there are none.
```

You write a markdown document, so respect instructions for markdown lists in #file:./../markdown.instructions.md : only one space in a list item: `- item 1` not `-   item 2` or `-  item 3`, `1. item 1` not `1.   item 2` or `1.  **item 3**`, etc.
