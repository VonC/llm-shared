"""Release workflow services, imported only after isolated readiness checks.

Git execution/environment, physical paths and strict domain configuration are
explicit submodules. The initializer stays dependency-free for readiness;
configuration and schema imports happen only after runtime validation.
"""


# eof
