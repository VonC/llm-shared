# How to sanitize a repository history before publishing

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📊 Goal: verify that no confidential word (person, company, internal host,
internal domain, internal email) survives anywhere in a repository history,
then rewrite that history with `git filter-repo` so the repository can go
public. A clean HEAD is not enough: old blobs, old commit messages, old
paths and old identities all travel with every clone.

This works on any git repository, not only llm-shared. All examples use
dummy words (`jdoe`, `acmecorp`): substitute the real list, and never
commit that list.

## Invocation model

Ask for the sanitize-history skill and let the AI run the scanner, prepare the
rewrite, re-audit the result, and restore remotes. The human approves the
destructive rewrite phase and remains responsible for any later force-push.
Run the scanner directly only for an ad hoc read-only audit or while developing
its matching rules.

## 📋 Steps to audit and rewrite

1. Write the watch list as replacement rules in a git-ignored file at the
   repo root, `a.sensitive.replacements.local.txt`, one rule per line:

   ```text
   regex:(?i)jdoe==>user
   regex:(?i)acmecorp==>acme
   ```

   Confirm it can never be committed:

   ```sh
   git check-ignore -v a.sensitive.replacements.local.txt
   ```

2. Run phase 1, the audit (or ask the agent to "sanitize-git-history
   phase 1"). The skill automatically calls `sensitive_history_scan.bat`
   against the rules file and writes an ignored contextual report. Do not run
   the scanner as a prerequisite for the skill.

   To inspect the same evidence yourself before invoking the skill, initialize
   `senv.bat` in an interactive `cmd` and use the `shscan` alias:

   ```bat
   shscan --rules a.sensitive.replacements.local.txt --output a.sensitive.history-scan.local.md --full-lines --validation-term my-project
   ```

   From any shell, call the self-locating launcher by its full path. The report
   lists each matching commit/tag line, historical path, and blob line with its
   OID and representative path. It also shows exact casing and flags binary or
   shortened lines.

3. Review the draft rules and the findings. Identities are not covered by
   the rules file: list the emails to neutralize in a second git-ignored
   file, `a.mailmap.local.txt`, in standard `.mailmap` format.

4. Run phase 2, the rewrite, on a fresh clone (or ask the agent for
   "sanitize-git-history phase 2"):

   ```sh
   git clone <origin-url> ../repo-public
   cd ../repo-public
   git filter-repo --mailmap ../a.mailmap.local.txt \
                   --replace-message ../a.sensitive.replacements.local.txt \
                   --replace-text ../a.sensitive.replacements.local.txt
   ```

5. Verify: no unexpected `***REMOVED***` in blobs or messages, a full
   re-audit comes back empty, the commit count is unchanged, and the
   commit-map fingerprint comparison names exactly the commits the audit
   predicted. Then restore, from the pre-cleanup repository's
   `.git/config`, both the remotes (filter-repo removes `origin`) and
   the branch upstreams (`branch.<name>.remote` / `branch.<name>.merge`,
   dropped together with the remote) into the new clone's `.git/config`
   — by writing the config directly, without fetching: a fetch before
   the force-push would re-download the old, unsanitized history.

6. Push yourself, once satisfied — the skill never pushes. Every existing
   clone must be re-cloned afterwards, and the hosting side may keep the
   old objects reachable for a while (forks, open PRs, events API).

## ⚠️ The comment-line trap

`git filter-repo` replacement files have no comment syntax: every line is
a rule, and a line without `==>` means "replace this text with
`***REMOVED***`". A bare `#` comment line silently becomes a rule that
replaces every `#` character in the whole history. Keep the rules file to
pure rules — no comments, no blank lines — and always run the
`***REMOVED***` grep of step 5 before trusting a rewrite.

## ✅ Check the result

On the rewritten clone, the phase 1 audit reports zero hits for every
watched word, `git log --all` shows the neutral messages and the neutral
emails, and neither the rules file nor the mailmap appears in
`git ls-files`.

The scanner's exact command surface and report contract are in the
[sensitive-history scanner reference](../reference/sensitive-history-scan.md).

Related: [Learn the scanner](../tutorials/06-audit-sensitive-history.md),
[scanner command reference](../reference/sensitive-history-scan.md),
[why contextual object scanning matters](../explanation/why-sensitive-history-needs-context.md),
[skills catalog](../reference/skills-catalog.md).
