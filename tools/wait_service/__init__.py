"""Durable waits, shared source monitoring and exact-recipient registration.

The owner pumps one scheduler and waits on its event and next timer. Bounded
workers perform source/host I/O; only the owner persists acknowledgements.
Synthetic ports exercise these boundaries without workflow integrations.
"""


# eof
