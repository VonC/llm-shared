---
name: split-and-define
description: 'split a draft into several feature-requests and issues, and define their key title for each one'
user-invocable: true
metadata:
  - "This skill is used to extract titles for feature-requests and issues, from a draft markdown document where several topics are described."
argument-hint: 'Provide the draft in the context".'
---

Check your prompt for a draft.vX.Y.ZA.xxx.md document in the context, and if it exists, review it and split it into several feature-requests and issues, and define their key title for each one.

The goal is not to create the feature-request and issue documents, but only to regroup topics from the draft document into a list of feature-requests and issues, and to define a key title for each one.

As a result, add a section "List of feature-requests and issues to create" at the end of the draft document, with a list of the feature-requests and issues to create, and their key title. For example:

```md
## List of feature-requests and issues to create
- Feature-request: "Add support for X in Y"
- Issue: "Fix the bug in Z when doing W"
```

(there can be more than one feature-request and issue in the list, depending on the number of topics described in the draft document).

For each item, detail what have been regrouped from the draft document to create it, and what is the key title for it, with arguments for this choice of title.

In addition of a key title, provide two to three words to describe the topic of the feature-request or issue, to help the reader understand at a glance what it is about. Those words should be separated by '-', and should be added in brackets at the end of the title. For example:

```md## List of feature-requests and issues to create
- Feature-request: "Add support for X in Y [X-Y-support]: short description of the elements from the draft document that have been regrouped to create this feature-request, and arguments for the choice of the title."
- Issue: "Fix the bug in Z when doing W [Z-W-bug]: short description of the elements from the draft document that have been regrouped to create this issue, and arguments for the choice of the title."
```

They will be used for the future filenames of the feature-request and issue documents, as well as for the future branch names in which commits will be created to implement the feature or fix the issue.

Again, do not create documents, do not write feature-request or issue in full, only regroup topics from the draft document into a list of feature-requests and issues, and define a key title for each one, with arguments for this choice of title, and two to three words to describe the topic of the feature-request or issue.
