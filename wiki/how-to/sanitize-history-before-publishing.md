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

1. Install the sensitive hooks, then divide the watch list between the
   configured shared rules file and the git-ignored project file at the repo
   root, `a.sensitive.replacements.local.txt`. Put only rules that apply to
   every participating repository in the shared file; keep project-specific
   rules local. Both use one rule per line:

   ```text
   regex:(?i)jdoe==>user
   regex:(?i)acmecorp==>acme
   ```

   Confirm it can never be committed:

   ```sh
   git check-ignore -v a.sensitive.replacements.local.txt
   git check-ignore -v a.sensitive.replacements.effective.local.txt
   ```

2. Run phase 1, the audit (or ask the agent to "sanitize-git-history
   phase 1"). The skill automatically calls `sensitive_history_scan.bat`
   without an explicit `--rules`, so it merges the configured shared file
   first and the project-local file second. It writes an ignored contextual
   report. Do not run the scanner as a prerequisite for the skill.

   **Do not add `--rules a.sensitive.replacements.local.txt` to this normal
   audit.** That option means “scan only this file” and excludes the configured
   shared rules. The default merge occurs only when positional terms,
   `--terms-file`, and `--rules` are all absent.

   To inspect the same evidence yourself before invoking the skill, initialize
   `senv.bat` in an interactive `cmd` and use the `shscan` alias:

   ```bat
   shscan --output a.sensitive.history-scan.local.md --full-lines --validation-term my-project
   ```

   From any shell, call the self-locating launcher by its full path. The report
   lists each matching commit/tag line, historical path, and blob line with its
   OID and representative path. It also shows exact casing and flags binary or
   shortened lines.

3. Review the draft rules and the findings. Before rewriting, copy the shared
   rules followed by the local rules into one git-ignored
   `a.sensitive.replacements.effective.local.txt`. Do not sort it: order is
   significant. Identities are not covered by replacement rules; list the
   emails to neutralize in `a.mailmap.local.txt`, in standard `.mailmap`
   format.

4. Run phase 2, the rewrite, on a fresh clone (or ask the agent for
   "sanitize-git-history phase 2"):

   ```sh
   git clone <origin-url> ../repo-public
   cd ../repo-public
   git filter-repo --mailmap <OLD_REPO>/a.mailmap.local.txt \
                   --replace-message <OLD_REPO>/a.sensitive.replacements.effective.local.txt \
                   --replace-text <OLD_REPO>/a.sensitive.replacements.effective.local.txt
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
[replacement-rules reference](../reference/sensitive-replacement-rules.md),
[why contextual object scanning matters](../explanation/why-sensitive-history-needs-context.md),
[skills catalog](../reference/skills-catalog.md).
