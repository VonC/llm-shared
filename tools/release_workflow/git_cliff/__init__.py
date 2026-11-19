"""Pinned git-cliff provisioning for the release engine (v0.14.0 item 3).

Step 1 of v0.14.0 git-cliff-provisioning ships two modules:

- `manifest`: the admitted pins and the published identity of each Windows
  asset; the only module of this package that the configuration schema
  imports at load time.
- `budget`: the download budget policy, resolved once when a caller enters
  provisioning or the evidence harness starts.

Step 3 adds the cache:

- `cache`: the cache layout with its production and evidence namespaces, the
  entry record, the owner file and the lock-free reuse check;
- `cache_lock`: the provisioning lock of one version and platform, with its
  bounded wait and owner-aware recovery.

Step 4 adds the download:

- `network`: the opener from the standard proxies and the system
  certificates, archive streaming under an exact size cap, the release
  metadata fetch and the retry classification;
- `download_worker`: one archive attempt or metadata lookup in a worker
  process started through the bootstrap's internal `git-cliff-worker` kind;
- `archive`: the staged digest check and the single-member extraction.

Later steps add the provisioning service, the invocation object and the
compatibility evidence harness. This initializer imports nothing, so loading
the manifest loads no other module of the package.
"""


# eof
