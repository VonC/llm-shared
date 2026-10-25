"""Release workflow services, imported only after isolated readiness checks.

Git execution/environment, physical paths, strict domain configuration, managed
writes, artifact capabilities and operation ownership are explicit submodules.
The initializer stays dependency-free for readiness;
configuration and schema imports happen only after runtime validation.
"""


# eof
