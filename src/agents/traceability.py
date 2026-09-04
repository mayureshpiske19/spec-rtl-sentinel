"""
Traceability Agent
------------------
Verifies the top-down chain HAS -> MAS -> RTL:

  * Every HAS requirement should be refined by at least one MAS claim.
    A HAS requirement with no MAS claim is a TRACEABILITY GAP (intent that was
    never detailed — a common source of silent under-implementation).
  * Rolls up the RTL result for each HAS requirement (worst-case status of the
    claims that refine it), so you can see intent-level health, not just
    clause-level pass/fail.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .has_parser import HASRequirement
from .claim_extractor import Claim


GAP = "gap"          # HAS requirement not refined by any MAS claim
TRACED = "traced"    # refined by >=1 MAS claim


@dataclass
class TraceRow:
    has_id: str
    kind: str
    requirement: str
    status: str                       # traced | gap
    claim_ids: List[str] = field(default_factory=list)
    rtl_rollup: str = "n/a"           # worst RTL status among refining claims


def build_trace(has_reqs: List[HASRequirement], claims: List[Claim]) -> List[TraceRow]:
    by_has: Dict[str, List[Claim]] = {}
    for c in claims:
        if c.traces:
            by_has.setdefault(c.traces, []).append(c)

    rows: List[TraceRow] = []
    for r in has_reqs:
        cs = by_has.get(r.id, [])
        rows.append(TraceRow(
            has_id=r.id, kind=r.kind, requirement=r.requirement,
            status=TRACED if cs else GAP,
            claim_ids=[c.id for c in cs],
        ))
    return rows


# Severity order for rolling up RTL status onto a HAS requirement.
_SEVERITY = {
    "verified": 0,
    "undocumented": 1,
    "ambiguous": 2,
    "drift": 3,
    "missing": 4,
}


def apply_rtl_rollup(rows: List[TraceRow], status_by_claim: Dict[str, str]) -> None:
    for row in rows:
        worst = "n/a"
        worst_rank = -1
        for cid in row.claim_ids:
            st = status_by_claim.get(cid)
            if st is None:
                continue
            rank = _SEVERITY.get(st, 0)
            if rank > worst_rank:
                worst_rank, worst = rank, st
        row.rtl_rollup = worst
