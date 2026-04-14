---
agent: ask
description: 'Check API architecture fit'
---

Your goal is to detect any DDD-Hexagonal (adapters-ports) architecture violation or smell, any layer using other layers it should not, or other internal lib it should not, based on API JSON dump files `a.xxx.api` listed in your prompt.

Consider in your context only the files listed in your prompt.

First: are those `a.xxx.api` JSON files included in full in your context? Those JSON files MUST end up with `"_marker": "eof"}`. If not, stop right there and list the files which are incomplete or missing in your context based on the list communicated in your prompt.

If all the files are present in full (i.e. "complete", meaning ending with `"_marker": "eof"}`) in your context, then:

Do you detect any DDD-Hexagonal (adapters-ports) architecture violation or smell, any layer using other layers it should not, or other internal lib it should not?

In particular, is there any class which is importing another class it should not (either a layer importing another wrong layer, or importing a technical lib when it should be business-only). Is there any function whose intent should not be in a particular class or layer? Is there a layer using logging when it should emit events instead?

Use those questions and your own analysis to provide:

- a detailed analysis of the architecture for the requested layer, 
- then a section about violation and smells.

You write a markdown document, so respect instructions for markdown lists in #file:./../markdown.instructions.md .
