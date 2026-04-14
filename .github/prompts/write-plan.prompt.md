---
agent: ask
description: 'Write a development plan.'
---

Your goal is write a markdown plan to address all addressable points, but also avoid or address any smells and risks identified in your last answer, based on the API dumps `a.xxx.api` or `arch.vX.Y.md` in your context.

That plan must include clear numbered steps (`### Step 1. ...`, `### Step 2. ...`) under a `## Numbered steps` section.  
It can ends with a "`## Order of implementation`" section in which you list steps than can be implemented togethers. 

Each step must include:

- `**Files involved**:`: First the list of filenames (relative to project root, starting with `src/...`) involved (code or test) to create, update or delete.
- `**Tests first**:`: Then always start with the tests, with a clear explanation of what is being tested, and why its helps the goal of that step. If new tests are created in a new folder, add an `__init__.py` to said folders.
- `**Classes and behavior**:`: then the classes to create/update/delete, with a clear explanation of what is being implemented, and why its helps the goal of that step. If new classes are created or deleted, always update or create the corresponding `__init__.py` in their folders.
- `**Completion criteria**:`: finally, completion criteria (either tests passing, or grep expressions returning or not returning results) to assess the step completion.

Then write a section summarizing the goal achieve by implementing all the steps of that document.

```markdown
## Plan goal

Explain the general goal.

- List the goal of each step.
```

Do not write code, only the plan. I will then provide the appropriate context, step after step, for you to implement said steps and address all smell, risks and tweaks.

Propose 3 different witty titles for the plan in you have just written, and or each of those titles, propose a short filename `plan.xxx.md`, as well as a short witty sub-title.

Those titles should reflect the mains issues from your previous answer, issues which triggered the writing of the plan to address them.

Title and sub-titles must be witty, and based on concrete concepts (like "A Matter of Time" / "Time, Mapper, ID, pathlib and uuid: The Great Un-Smelling"), not abstract goal ("Purify Domain and Decouple Layers" / "Address Architectural Smells via Strict Layering").

You write a markdown document, so respect instructions for markdown lists in #file:./../markdown.instructions.md .
