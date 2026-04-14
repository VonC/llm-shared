---
agent: ask
description: 'Check API architecture fit for Others Layers'
---

Follow instructions from #file:check-api.prompt.md for the rest of the layer (except domain, application and adapters layers, already analyzed).

Consider only in your context ( in addition of #file:check-api.prompt.md ) the files:

- #file:../../a.config.api
- #file:../../a.typing.api
- #file:../../a.core.api
- #file:../../a.root.api
- #file:../../a.bootstrap.api


Start your analysis with the section `### Other Layers Analysis`.  
Finish with a section `### Architectural Smells for Other Layers`.

Address the layers root, bootstrap, config, core and typing  in your analysis and smell sections.

You document should match the following pattern:

```md
## Other Layers Analysis Overview

Explain what the other layers (config, typing, core, root and bootstrap) are for, in the context of this application, without detailing too much each one (that will be done in each other layer sub-section).

### Other Layers Analysis

Assess how well, based on the provided `a.xxx.api` API dump, the layer is well-designed and adheres strictly to DDD and Hexagonal Architecture principles or not. How is the separation of concerns? Is there distinct and appropriate responsibilities for each component type?

Do so for each layer: `#### root (main)`, `#### bootstrap`, `#### core`, `#### config`, and `#### typing`.

### Architectural Smells for Other Layers: `<number of smell/violation detected>`

Replace `<number of smell/violation detected>` with the number of smell/violation detected, and then proceed with:

- a short introduction on the layer cleanliness. And short explanation as to why it might have some violation or smell.
- a list of said violations or smells, or a single section to explain why there are none.
```

You write a markdown document, so respect instructions for markdown lists in #file:./../markdown.instructions.md , and make sure to add an empty line before and after any list, and use only one space between a list maker and its content.
