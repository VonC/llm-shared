# sanitize-git-history instruction

Audit the full git history of a repository for confidential words, then
rewrite that history with `git filter-repo` so the repository can be
published. This is the full workflow behind the `sanitize-git-history`
skill. It applies to any git repository, not only llm-shared.

The process has two phases, run separately and both idempotent:

- **Phase 1 (audit)**: scan every commit message, every tag, every file
  path and every file version ever committed for a watch list of
  sensitive terms, list the author and committer identities, and produce
  (or refresh) the local replacement-rules file and mailmap.
- **Phase 2 (rewrite)**: on a fresh clone, rewrite the whole history with
  `git filter-repo` driven by those two files, re-run the phase 1 audit
  on the result, verify exactly which commits changed, restore the
  remotes, and stop before any push.

All examples below use dummy words (`jdoe`, `acmecorp`, `secretproject`):
substitute the real list, and never commit that list.

## Goal for the history sanitization

Verify that no confidential word (person, company, internal host,
internal domain, internal email) survives anywhere in the repository
history, then rewrite that history so the repository can be made public
without exposing any of it. The working tree of HEAD being clean is not
enough: old blobs, old commit messages, old paths and old identities all
travel with the clone.

## Inputs and the two local watch files

Run from the root of the repository to sanitize (the current project by
default, or the path given as argument). Two git-ignored files at that
root drive both phases:

- `a.sensitive.replacements.local.txt` — one replacement rule per line,
  in `git filter-repo` `--replace-text` syntax. Its left-hand terms are
  the watch list for phase 1 and the rewrite rules for phase 2. When the
  file is missing, phase 1 drafts it from the terms the user names.
- `a.mailmap.local.txt` — the identities to neutralize, in standard
  `.mailmap` format. Only needed when step 2 of the audit finds
  identities to scrub.

Both names match the usual `a.*` and `*.local.*` gitignore patterns.
Confirm they can never be committed before going further:

```sh
git check-ignore -v a.sensitive.replacements.local.txt
```

If `git check-ignore` reports nothing, stop and add the pattern to
`.gitignore` first: these files contain the very words being scrubbed.

Which phase to run comes from the user's request; default to phase 1
when unstated. Before running any command below, read
[`../rules/run_commands.md`](../rules/run_commands.md).

## Phase 1: audit the full history

Run everything from the repository root in a bash session. Build the
watch list as one case-insensitive alternation from the left-hand terms
of the replacement file, for example
`jdoe|acmecorp|secretproject|\.lan\b`. For each name, also watch
plausible misspellings (doubled or dropped letters, swapped vowels): for
`smith`, a tolerant pattern like `sm[iy]th?` also catches `smyth` and
`smit` in a commit typed by hand.

1. Scan commit and tag messages, on all refs:

   ```sh
   git log --all --format='%H %s %b' | grep -i -E 'jdoe|acmecorp|secretproject'
   git tag -l -n100 | grep -i -E 'jdoe|acmecorp|secretproject'
   ```

   To name the offending commits per term:

   ```sh
   git log --all -i -E --grep='acmecorp' --format='%h %ci %s'
   ```

2. List the author and committer identities. A replacement file does not
   touch these: they are rewritten by a mailmap in phase 2.

   ```sh
   git log --all --format='%an|%ae|%cn|%ce' | sort -u
   ```

   For every identity to neutralize, add a line to
   `a.mailmap.local.txt`. The standard `.mailmap` format applies: the
   email-only form maps the address and keeps the contributor name.

   ```text
   <jdoe@example.com> <jdoe@acmecorp.com>
   ```

   Verify the mapping before phase 2: the neutral identities must come
   out, and the untouched ones must stay unchanged.

   ```sh
   git -c mailmap.file="$(pwd)/a.mailmap.local.txt" log --all --use-mailmap \
     --format='%aN|%aE' | sort -u
   ```

3. Scan every file path ever tracked, not only the current tree:

   ```sh
   git rev-list --all --objects | cut -d' ' -f2- | sort -u \
     | grep -i -E 'jdoe|acmecorp|secretproject'
   ```

   While there, check that files ignored today (credentials, private
   configuration) were never committed in the past: grep the same path
   list for their names.

4. Scan every file version ever committed. Do not loop
   `git cat-file blob` per object (one process per blob is far too slow
   on Windows): collect the blob ids once, then stream them through a
   single `git cat-file --batch` into a small scanner. Save this as
   `scan.pl` in a scratch folder outside the repository:

   ```perl
   use strict; use warnings;
   binmode(STDIN);
   my $pat = qr/$ARGV[0]/i;
   my ($blobs, $hits) = (0, 0);
   while (my $hdr = <STDIN>) {
       chomp $hdr;
       my ($oid, $type, $size) = split / /, $hdr;
       last unless defined $size;
       my ($buf, $got) = ('', 0);
       while ($got < $size) {
           my $n = read(STDIN, $buf, $size - $got, $got);
           last unless $n;
           $got += $n;
       }
       my $lf; read(STDIN, $lf, 1);
       $blobs++;
       if ($buf =~ $pat) { print "$oid\n"; $hits++; }
   }
   print STDERR "scanned=$blobs hits=$hits\n";
   ```

   The inner `read` loop matters: a pipe may return fewer bytes than
   asked, and a single `read` silently truncates blobs. Then:

   ```sh
   git rev-list --all --objects | cut -d' ' -f1 | sort -u \
     | git cat-file --batch-check='%(objectname) %(objecttype)' \
     | awk '$2=="blob"{print $1}' > blobs.txt
   git cat-file --batch < blobs.txt | perl scan.pl 'jdoe|acmecorp|secretproject'
   ```

   This scans raw bytes, so binaries are covered too. To map a hit back
   to its paths, look the blob id up in the `git rev-list --all
   --objects` output, then show the matching lines with
   `git cat-file blob <oid> | grep -i -E '<terms>'` and tell whether the
   same file is still affected in HEAD (`git cat-file blob HEAD:<path>`).

5. Validate the scanner before trusting a zero. Run it once with a word
   that certainly exists (the repository name, for instance) and confirm
   a large hit count. A scanner bug reads exactly like a clean history.

6. Sweep for what the watch list does not name. Grep the same blob
   stream for the shapes of leaks rather than known words: `https?://`
   URLs and their hosts, email addresses, IP addresses, UNC paths
   (`\\\\host\\share`), `C:\\Users\\<name>` paths, and lines around
   `password`, `secret`, `token`, `credential`, `proxy`, `ldap`. Review
   the unique matches by hand: expect only public URLs, placeholders
   like `example.corp`, and localhost.

## Phase 1 output: the replacement-rules file

Report the findings to the user: per term, the hit counts in messages,
paths and blobs, the affected files, and whether HEAD is still affected
or only past versions are. Then write (or refresh)
`a.sensitive.replacements.local.txt`, one rule per line, most specific
first:

```text
regex:(?i)C:\\Users\\JDOE==>%USERPROFILE%
regex:(?i)jdoe==>user
regex:(?i)acmecorp==>acme
regex:(?i)secretproject==>projectx
regex:(?i)\.lan\b==>.corp
```

Two hard rules about this file:

- **No comments, no blank lines.** `git filter-repo` replacement files
  have no comment syntax: every line is a rule, and a line without
  `==>` means "replace this text with `***REMOVED***`". A bare `#`
  comment line becomes a rule replacing every `#` character in the whole
  history. Pure rules only.
- **Keep a defensive rule for every watched word even when the audit
  found zero hits**: the rewrite then guarantees what the scan only
  observed.

A rule line is literal and case-sensitive by default; prefix with
`regex:` and use `(?i)` for case-insensitive patterns. Broad rules like
`regex:(?i)jdoe` substitute inside longer words too — verify each
proposed replacement against the real matches found by the audit before
phase 2 runs.

## Phase 2: rewrite the history with git filter-repo

`git filter-repo` is a Python tool, not part of git. Use the
project-provided wrapper when one exists (senv ships
`git-filter-repo.bat`), or install it once with `pip install
git-filter-repo` / `uv tool install git-filter-repo`.

Work on a fresh clone: filter-repo refuses a repository with remotes or
local changes unless forced, and a bad rewrite on a clone costs nothing.
Record first, from the pre-cleanup repository's `.git/config`, everything
to restore at the end — the remotes (urls and pushurls) and the branch
upstreams:

```sh
git -C <old-repo> config --get-regexp '^remote\.'
git -C <old-repo> config --get-regexp '^branch\.[^.]*\.(remote|merge|pushremote)'
```

```sh
git clone <origin-url> ../repo-public
cd ../repo-public
git filter-repo --mailmap ../a.mailmap.local.txt \
                --replace-message ../a.sensitive.replacements.local.txt \
                --replace-text ../a.sensitive.replacements.local.txt
```

`--replace-message` rewrites commit and tag messages, `--replace-text`
rewrites every historical blob, `--mailmap` rewrites the author and
committer identities. Omit `--mailmap` when no identity needs scrubbing.

Then verify, in order:

1. **Damage check**: grep the rewritten history for `***REMOVED***`. Any
   hit outside a file that legitimately contains that string (such as
   filter-repo's own source) means a malformed rule replaced content it
   should not have — fix the rules file, delete the clone, re-clone and
   re-run.

   ```sh
   git grep -l '\*\*\*REMOVED\*\*\*' HEAD
   git log --all --format='%s%n%b' | grep -c 'REMOVED'
   ```

2. **Full re-audit**: re-run the whole phase 1 audit on the rewritten
   clone. It must come back empty for every watched word, and the
   identities must all be neutral.

3. **Which commits actually changed**: filter-repo writes
   `.git/filter-repo/commit-map` (old id, new id). A new id alone does
   not mean the commit changed — every descendant of a rewritten commit
   gets a new id through its parent link. Fingerprint each commit (hash
   of author name/email, committer name/email, subject, body) on both
   sides and compare the map pairs: the materially rewritten set must
   match what the audit predicted, and the commit count must be
   unchanged.

4. If commits landed between the audit and the rewrite, re-scan at least
   that delta first.

5. **Restore the remotes and the branch upstreams** in the rewritten
   clone. filter-repo removes the `origin` remote, and removing a remote
   also drops the `branch.<name>.remote` / `branch.<name>.merge`
   upstream entries that pointed at it. Recreate both in the new clone's
   `.git/config` from the values recorded in the pre-cleanup
   repository's `.git/config`:

   ```sh
   git remote add origin <url>
   git config --add remote.origin.pushurl <push-url>
   git config branch.master.remote origin
   git config branch.master.merge refs/heads/master
   ```

   One `--add remote.<name>.pushurl` line per recorded pushurl, one
   `remote`/`merge` pair per recorded branch, and the same treatment for
   any extra remote (`origin2`, ...). Write the upstream config directly
   rather than through `git branch --set-upstream-to`, which needs the
   remote-tracking ref and therefore a fetch — and do not fetch before
   the force-push: a fetch would re-download the old, unsanitized
   history into the clone. After the push, a plain `git fetch` re-syncs
   the tracking refs.

Then stop: publishing is the user's call, never the skill's. Report the
exact push commands without running them:

```sh
git push --force <origin-url> <branch> <tags...>
git push --force --mirror <origin-url>
```

Warn about the aftermath: every existing clone must be re-cloned;
`--mirror` through a remote shortname also pushes to any extra pushurl,
so target the explicit URL; the hosting side may cache the old ids (open
PRs, forks, the events API) and only the host's support can purge
unreachable objects; the pre-rewrite repository and any other remote
still hold the old history — the user decides whether those follow,
stay, or get archived.

## Check for a done sanitization

Phase 1 is done when the findings are reported per term and
`a.sensitive.replacements.local.txt` holds one verified rule per watched
word, comment-free, and is confirmed ignored. Phase 2 is done when the
re-audit on the rewritten clone reports zero hits for every watched
word, `git log --all` shows the neutral messages and neutral emails, the
commit count is unchanged, the remotes and branch upstreams are restored
from the pre-cleanup `.git/config`, and nothing was pushed.
