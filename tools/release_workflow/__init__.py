"""Release workflow services, imported only after isolated readiness checks.

Git execution/environment, physical paths, strict domain configuration, managed
writes, artifact capabilities, operation ownership, shared strict record
decoding (`lock_records`), invocation, input transport, dispatch and result
rendering are explicit submodules. The `git_cliff` package (v0.14.0 item 3)
holds pinned git-cliff provisioning; Step 1 of v0.14.0 git-cliff-provisioning
ships its tested-pin manifest, which the schemas import, and its download
budget policy. Step 2 adds the Windows child layer: `windows_native`
(declarations), `windows_child` (children contained in a kill-on-close job
from their creation) and `windows_guard` (the use guard). The initializer
stays dependency-free for readiness;
configuration and schema imports happen only after runtime validation.
"""


# eof
