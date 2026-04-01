---
agent: ask
description: 'Write a development plan.'
---

Your goal is to write a markdown plan to address all addressable points, and avoid or address any smells and risks identified in your last answer, based on the files and context you have.

That plan must include clear numbered steps (`### Step 1. ...`, `### Step 2. ...`) under a `## Numbered steps` section.
It can end with a "`## Order of implementation`" section in which you list steps that can be implemented together.

Each step must include:

- `**Files involved**:` First the list of filenames (relative to project root) involved (code or test) to create, update or delete.
- `**Tests first**:` Always start with the tests — explain what is being tested and why it helps the goal of that step.
- `**Classes and behavior**:` The classes or modules to create, update, or delete, with a clear explanation of what is being implemented and why. When adding or removing types, always update the corresponding module index files (e.g., `__init__.ts`, `index.ts`, `__init__.py`) in their folders.
- `**Architecture compliance**:` Verify that the step respects DDD / hexagonal architecture layer boundaries: domain must not import from infrastructure or application; application must not import from infrastructure. Flag any step that risks introducing a layer violation, and explain how to avoid it.
- `**Completion criteria**:` Completion criteria (either tests passing, or grep/search expressions returning or not returning results) to assess the step completion.

Then write a section summarizing the goal achieved by implementing all the steps of that document.

```markdown
## Plan goal

Explain the general goal.

- List the goal of each step.
```

Do not write code, only the plan. I will then provide the appropriate context, step after step, for you to implement said steps and address all smells, risks and tweaks.

Propose 3 different witty titles for the plan you have just written, and for each of those titles, propose a short filename `plan.xxx.md`, as well as a short witty sub-title.

Those titles should reflect the main issues from your previous answer, issues which triggered the writing of the plan to address them.

Titles and sub-titles must be witty and based on concrete concepts (like "A Matter of Time" / "Time, ID, pathlib and uuid: The Great Un-Smelling"), not abstract goals ("Purify Domain and Decouple Layers" / "Address Architectural Smells via Strict Layering").

You write a markdown document, so respect instructions for markdown lists in #file:./../markdown.instructions.md .
