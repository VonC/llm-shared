---
name: review-and-update-project-docs
description: 'Review code and update project markdown documentation files (README.md, ARCHITECTURE.md, docs/architecture/**). If no specific markdown target is mentioned in the prompt, all documentation files are updated. If no specific code is mentioned, a global code review is performed first to inform the documentation updates.'
user-invocable: true
metadata:
  - "This skill reviews source code and updates project markdown documentation."
  - "Target documents: README.md, ARCHITECTURE.md, and any file under docs/architecture/."
  - "If the prompt names specific docs to update, only those docs are updated; otherwise all target docs are updated."
  - "If the prompt names specific code files or modules to review, only those are reviewed; otherwise a global code review is performed first."
argument-hint: 'Optionally specify which docs to update (e.g. "README.md only") and/or which code to review (e.g. "tools/git_batch_commit.py").'
---

[Instruction](../../../instructions/review-and-update-project-docs.md)
