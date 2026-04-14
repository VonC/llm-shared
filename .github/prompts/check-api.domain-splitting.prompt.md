---
agent: ask
description: 'Check API architecture fit for Domain Splitting'
---

Follow instructions from #file:check-api.prompt.md for the splitting domain layer.

Consider only in your context ( in addition of #file:check-api.prompt.md ) the files:

- #file:../../a.domain.splitting.api

You document should match the following pattern:

```md
## Domain Layer Analysis Overview

Explain what the domain layer is for, in the context of this application.

### Splitting Domain Layer Analysis

Assess how well, based on the provided `a.domain.splitting.api` API dump, the layer is well-designed and adheres strictly to DDD and Hexagonal Architecture principles or not. How is the separation of concerns? Is there distinct and appropriate responsibilities for each component type?

Then present each sections seen in the API dump.  
For instance:

- **Entities**
- **Value Objects**
- **Ports**
- **Services**
- **Events**

### Architectural Smells for Splitting Domain: `<number of smell/violation detected>`

Replace `<number of smell/violation detected>` with the number of smell/violation detected, and then proceed with:

- a short introduction on the layer cleanliness. And short explanation as to why it might have some violation or smell.
- a list of said violations or smells, or a single section to explain why there are none.
```

You write a markdown document, so respect instructions for markdown lists in #file:./../markdown.instructions.md : only one space in a list item: `- item 1` not `-   item 2` or `-  item 3`, `1. item 1` not `1.   item 2` or `1.  **item 3**`, etc.

