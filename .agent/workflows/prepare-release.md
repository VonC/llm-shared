---
description: Automate the release-preparation process from any branch: detect the development effort since the last tag, base the effort branch on the latest origin/main (rebase with a ghog day gate when it is behind), merge it into main, set the X.Y.Z-SNAPSHOT v...
---

1. Locate the shared instruction body `instructions/prepare-release.md`: in this
   workspace root when the workspace is llm-shared itself, else under the
   sibling clone `../llm-shared`, else under a `llm-shared` submodule folder.
2. Read that file in full.
3. Follow it exactly, treating any text given after the slash command as its
   arguments.
