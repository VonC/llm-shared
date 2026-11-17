"""Pinned git-cliff provisioning for the release engine (v0.14.0 item 3).

Step 1 of v0.14.0 git-cliff-provisioning ships two modules:

- `manifest`: the admitted pins and the published identity of each Windows
  asset; the only module of this package that the configuration schema
  imports at load time.
- `budget`: the download budget policy, resolved once when a caller enters
  provisioning or the evidence harness starts.

Later steps add the cache and its lock, the download, the provisioning
service, the invocation object and the compatibility evidence harness. This
initializer imports nothing, so loading the manifest loads no other module of
the package.
"""


# eof
