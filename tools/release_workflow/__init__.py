"""Release workflow services, imported only after isolated readiness checks.

Git execution/environment and physical path services are explicit submodules;
the package initializer stays dependency-free for the readiness bootstrap.
"""


# eof
