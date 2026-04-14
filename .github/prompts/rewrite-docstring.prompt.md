---
agent: ask
description: 'Rewrite docstrings by summarizing and synthesizing content related to "Step", "Fix" or "Plan".'
---

Your goal is to look for any docstring in the code with mentions of "Step", "Fix" or "Plan" for the class or classes) in your context and:

- based on that content, summarize and synthesize what that (module/class/function) docstring is about, in a more concise way; removing any mention of "Step", "Fix" or "Plan".
- preserve any Args, Returns, Raises sections as is.
- preserve any existing comments, and existing docstring content that is not about "Step", "Fix" or "Plan".
- preserve the rest of the code as is.
