# Why sensitive-history replacement needs context

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

`sanitize-git-history` normally calls the contextual scanner and interprets
its report before proposing a rewrite. Run `shscan` directly for an ad hoc
read-only audit or while refining replacement rules; direct scanning does not
authorize history rewriting.

📊 A sensitive word is not merely present or absent. Its surroundings determine
whether one replacement rule is safe.

## HEAD is only one version

Git clones carry every object reachable from branches and tags. Removing a
name from the current working tree leaves it in old commit messages, annotated
tags, filenames, and prior blob versions. A working-tree grep therefore answers
a smaller question than a publication audit.

The scanner walks `git rev-list --all --objects`, filters unique blobs once,
and streams them through one `git cat-file --batch` process. This covers old
content and binary bytes without checking out each commit or starting one Git
process per blob.

## Syntax changes the safe replacement

The same project name can occur as prose, a directory, a log prefix, a
hyphenated compound, and part of a Python identifier. Replacing all occurrences
with `my-project` reads naturally in prose and paths but introduces a minus
operator inside an identifier.

Ordered rules solve that mismatch: replace the narrow identifier form with an
underscore-safe value first, then apply the broad human-readable replacement.
The contextual report exposes those forms before `git filter-repo` makes them
permanent across history.

Case evidence also matters. The scanner always searches case-insensitively and
reports the exact forms it observed. A defensive `regex:(?i)` rule can still be
appropriate when history currently contains only lowercase text: it protects
the subsequent rewrite from a missed casing variant.

## The tool and skill have different jobs

`sensitive_history_scan.bat` is a deterministic, read-only evidence engine. It
accepts literal terms, a terms file, or replacement rules and reports precise
locations. It never edits refs, replacements, mailmaps, or remotes.

`sanitize-git-history` orchestrates the security decision. Phase 1 invokes the
tool automatically, checks identities and unnamed leak shapes, and reviews the
rules with the user. Phase 2 works on a fresh clone, rewrites messages and
blobs, re-audits, compares changed commits, restores remote configuration, and
stops before pushing.

Keeping those responsibilities separate makes the scanner useful during rule
design while preserving a deliberate human gate around destructive history
rewrites.

Related: [Audit tutorial](../tutorials/06-audit-sensitive-history.md),
[sanitization guide](../how-to/sanitize-history-before-publishing.md), and
[scanner reference](../reference/sensitive-history-scan.md).
