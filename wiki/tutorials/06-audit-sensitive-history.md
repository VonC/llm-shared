# Audit sensitive Git history for the first time

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Start the sanitization skill and let the AI call the scanner and interpret its
context. The direct `shscan` command shown here is for learning, ad hoc audits,
and replacement-rule development; it never rewrites history.

📊 In this tutorial you scan a small watch list through every reachable commit
message, tag, historical path, and unique blob. You will inspect context and
draft replacement rules, but you will not rewrite history.

## 1. Create an ignored terms file

At the repository root, confirm the local-report convention is ignored:

```bash
git check-ignore -v a.sensitive.terms.local.txt
```

Then create `a.sensitive.terms.local.txt` with one literal term per line:

```text
secretproject
internal.example
```

The terms-file format permits blank lines and `#` comments. Replacement-rule
files do not; those are executable `git filter-repo` inputs.

## 2. Run the contextual scan

In an interactive `cmd` initialized by `senv.bat`, run:

```bat
shscan --terms-file a.sensitive.terms.local.txt --output a.sensitive.history-scan.local.md --validation-term my-project
```

`--validation-term` is a positive control: choose a harmless repository term
known to occur in a historical blob. The scan fails rather than presenting a
misleading zero when that control is absent.

Open the report. Its summary separates commit lines, tag lines, historical
paths, blob lines, and unique blobs. The detailed sections include OIDs, line
numbers, representative paths, exact casing, and the complete or shortened
matching line.

## 3. Compare replacement shapes

Suppose the report contains both prose and this identifier:

```text
test_render_drops_the_secretproject_strings
```

A broad replacement containing a hyphen would break that identifier. Put a
specific identifier-safe rule first, followed by the broad prose/path rule:

```text
regex:(?i)_secretproject_==>_my_project_
regex:(?i)secretproject==>my-project
```

Save pure project-specific rules only in
`a.sensitive.replacements.local.txt`. For the normal repository audit, omit
`--rules`:

```bat
shscan --output a.sensitive.history-scan.local.md --full-lines --validation-term my-project
```

With no positional terms, `--terms-file`, or `--rules`, `shscan` loads the file
configured by `sensitive.sharedRulesFile` first and this repository's local
file second. Put a term in the shared file only when it applies to every
participating repository; keep project names, hosts, and other repo-specific
terms local. Use `shscan --rules PATH` only when deliberately testing that one
file in isolation; it disables the default shared-plus-local selection.

The scanner uses every left-hand rule as a case-insensitive watch pattern.
`--full-lines` preserves long lines in the ignored report; omit it for bounded
console-friendly excerpts.

## 4. Hand the evidence to the skill

Ask for:

```text
$llm-shared:sanitize-git-history phase 1
```

The skill calls the same launcher automatically, reviews identities and
leak-shaped patterns, and settles the defensive rules. It still does not
rewrite history until you explicitly request phase 2.

## What you learned

You scanned the object database rather than only HEAD, used a positive control,
and chose ordered rules from real syntax contexts. The command supplies
repeatable evidence; the skill owns the wider audit and rewrite decisions.

Next: [Sanitize history before publishing](../how-to/sanitize-history-before-publishing.md)
and [Sensitive-history scanner reference](../reference/sensitive-history-scan.md).
For the exact file grammar, see
[Sensitive replacement rules](../reference/sensitive-replacement-rules.md).
