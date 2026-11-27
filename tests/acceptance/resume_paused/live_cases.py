"""Human-run TUIOS scenarios. Each step specifies the command and its observable outcome."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Row:
    """Result line, required evidence and new dispatch phases for one checkout."""

    status: str
    words: tuple[str, ...] = ()
    phases: tuple[str, ...] = ()


@dataclass(frozen=True)
class Step:
    """One human launch, optionally a pair of simultaneous launches."""

    args: tuple[str, ...]
    alpha: Row
    bravo: Row | None = None
    code: int = 0
    concurrent: bool = False


PREVIEW = Step(("--dry-run",), Row("PLAN", ("$llm-shared:resume-session",)), Row("PLAN", ("/resume-session",)))
DELIVER = Row("DONE", ("accepted",), ("resume",))
CLEAR = Row("DONE", ("cleared, accepted",), ("clear", "resume"))
USED = Row("SKIP", ("already-used",))
REPEAT = Step((), USED, USED)
SWITCH = ("--switch-roles", "alpha")
EXCLUDE_REVIEWER = ("--except", "Claude primary")
CLAIM = Row("DONE", ("claimed g",), ("resume", "reviewer"))
MISSING = Row("DONE", ("claimed g", "excluded"), ("resume",))
CONTINUE = Row("DONE", ("claimed g",), ("reviewer",))
WAITING = Row("PENDING", ("reviewer-wait-active",), ("resume",))
PAIR_CASES = frozenset({"pair", "capture-pair", "later", "switch", "hibernate", "reboot"})
SINGLE_PREVIEW = Step(("--dry-run",), Row("PLAN", ("$llm-shared:resume-session",)))
CALLER = Row("REFUSED", ("agent-caller",))
DUAL_CASES = frozenset({"bulk", "clear", "exclude", "concurrent", "names", "routes", "damaged", "capture", "history"})

_BOTH_REPLIES = "Check that Codex peer replied RP-ACK-alpha and Claude secondary replied RP-ACK-bravo."
_PAIR_OBSERVED = "Check that Codex primary resumed first and exactly one Claude primary reviewer started."
OBSERVATIONS = {
    "bulk": _BOTH_REPLIES,
    "capture": _BOTH_REPLIES,
    "concurrent": _BOTH_REPLIES + " Check for one resume per target across both launchers.",
    "clear": "Check that both conversations cleared before resuming. " + _BOTH_REPLIES,
    "exclude": "Check that Claude secondary waited for the second launch. " + _BOTH_REPLIES,
    "damaged": "Check that Claude secondary replied RP-ACK-bravo and the malformed alpha pause stayed untouched.",
    "draft": "Check that RP-UNSENT-472 is still editable in Codex peer.",
    "busy": "Check that the Codex peer task continued uninterrupted.",
    "blocked": "Check that Codex peer still shows the original unanswered question.",
    "pair": _PAIR_OBSERVED,
    "capture-pair": _PAIR_OBSERVED,
    "later": "Check that only the missing Claude reviewer started on the second launch.",
    "switch": "Check that Claude primary resumed as requestor and exactly one Codex primary reviewer started.",
    "hibernate": "Check that exactly one reviewer started after the surviving waiter ended.",
    "reboot": "Check that exactly one reviewer started after reboot and the requestor was not resumed twice.",
    "recovery": "Check that Codex peer replied RP-ACK-alpha after the recovery Enter.",
    "copied": "Check both marked refusals. Record the receiving pane and mismatch diagnostic shown on screen.",
}


CASES: dict[str, tuple[Step, ...]] = {
    "bulk": (PREVIEW, Step((), DELIVER, DELIVER), REPEAT),
    "clear": (
        Step(("--dry-run", "--clear"), Row("PLAN", ("clear, then $llm-shared:resume-session",)), Row("PLAN", ("clear, then /resume-session",))),
        Step(("--clear",), CLEAR, CLEAR), REPEAT,
    ),
    "names": (
        Step(("--except", "absent"), Row("REFUSED", ("except-unmatched",)), code=1),
        Step(("--switch-roles", "absent"), Row("REFUSED", ("switch-unmatched",)), code=1),
        Step((*SWITCH, "--except", "bravo"), Row("ERROR", ("switch-not-applicable",)), Row("SKIP", ("excluded",)), code=1),
    ),
    "exclude": (Step(("--except", "bravo"), DELIVER, Row("SKIP", ("excluded",))), Step((), USED, DELIVER)),
    "routes": (Step((), Row("SKIP", ("routing-missing",)), Row("SKIP", ("target-absent",))),),
    "history": (Step((), Row("SKIP", ("unsupported-pauser",)), Row("SKIP", ("journal-resumed", "evidence journal: chatgpt"))),),
    "damaged": (Step((), Row("ERROR", ("checkout-unreadable",)), DELIVER, code=1),),
    "concurrent": (Step((), DELIVER, DELIVER, concurrent=True), REPEAT),
    "draft": (Step((), Row("SKIP", ("pane-draft",))),),
    "busy": (Step((), Row("SKIP", ("pane-busy",))),),
    "blocked": (Step((), Row("SKIP", ("pane-blocked",))),),
    "pair": (Step((), CLAIM),),
    "capture-pair": (Step((), CLAIM),),
    "later": (Step(EXCLUDE_REVIEWER, MISSING), Step((), CONTINUE)),
    "switch": (
        Step((*SWITCH, "--except", "Codex primary"), MISSING),
        Step((), Row("SKIP", ("switch-required",))), Step(SWITCH, CONTINUE),
    ),
    "hibernate": (Step((), WAITING), Step((), Row("PENDING", ("reviewer-wait-active",))), Step((), CONTINUE)),
    "reboot": (Step(EXCLUDE_REVIEWER, MISSING), Step((), CONTINUE)),
    "stall": (Step((), Row("FAIL", ("unconfirmed",), ("resume",)), code=1), Step((), Row("SKIP", ("already-resuming",)))),
    "recovery": (Step((), Row("DONE", ("accepted", "recovery enter"), ("resume",))),),
    "capture": (PREVIEW, Step((), DELIVER, DELIVER)),
    "copied": (SINGLE_PREVIEW, SINGLE_PREVIEW, SINGLE_PREVIEW),
    "caller": (Step((), CALLER, code=1), Step(("--dry-run",), CALLER, code=1)),
}


# eof
