"""
Authority / Conflict Resolver Agent
-----------------------------------
Reconciles the formal spec (MAS claims) with the "as-agreed" layer (decisions
and reviews). For every (target, property) it decides the *effective* required
value by ranking sources on (authority, recency):

    arch_review > design_review > meeting > spec(MAS)   then newer date wins

Outputs:
  * resolved claims  - MAS claims with the effective expected value applied
  * conflicts        - where a decision contradicts the MAS (needs human review)
  * reinforcements   - where a decision confirms the MAS value (raises confidence)
  * context_notes    - non-amending notes attached to a target (e.g. a temporary
                       debug register explained by a meeting)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .claim_extractor import Claim
from .decision_ingest import Decision


@dataclass
class ResolvedClaim:
    claim: Claim
    effective_expected: str
    backing: List[str] = field(default_factory=list)   # decision ids confirming
    amended_by: Optional[str] = None                   # decision id that changed it


@dataclass
class Conflict:
    target: str
    property: str
    mas_value: str
    decision_value: str
    decision_id: str
    authority: str
    date: str
    resolved_value: str
    resolved_source: str
    category: str = "functional"   # milestone category of the amended claim


@dataclass
class ResolverResult:
    resolved: List[ResolvedClaim]
    conflicts: List[Conflict]
    reinforcements: List[str]
    context_notes: Dict[str, List[Decision]]


def resolve(claims: List[Claim], decisions: List[Decision]) -> ResolverResult:
    # Index amending decisions by (target, property).
    by_key: Dict[tuple, List[Decision]] = {}
    context: Dict[str, List[Decision]] = {}
    for d in decisions:
        if d.property == "note" or not d.value or d.value == "temporary":
            context.setdefault(d.target.upper(), []).append(d)
            continue
        by_key.setdefault((d.target.upper(), d.property), []).append(d)

    resolved: List[ResolvedClaim] = []
    conflicts: List[Conflict] = []
    reinforcements: List[str] = []

    for c in claims:
        key = (c.target.upper(), c.property)
        rc = ResolvedClaim(claim=c, effective_expected=c.expected)
        candidates = by_key.get(key, [])
        if not candidates:
            resolved.append(rc)
            continue

        # The authoritative decision wins by (authority rank, then recency).
        winner = max(candidates, key=lambda d: (d.rank, d.date))

        if _norm(winner.value) == _norm(c.expected):
            # Winner agrees with the MAS -> reinforcement (higher confidence).
            for d in candidates:
                if _norm(d.value) == _norm(c.expected):
                    rc.backing.append(d.id)
                    reinforcements.append(
                        f"{c.id}: {c.target}.{c.property}={c.expected} reinforced "
                        f"by {d.id} ({d.authority}, {d.date})"
                    )
        else:
            # Winner overrides the stale MAS value.
            rc.effective_expected = winner.value
            rc.amended_by = winner.id
            conflicts.append(Conflict(
                target=c.target, property=c.property,
                mas_value=c.expected, decision_value=winner.value,
                decision_id=winner.id, authority=winner.authority,
                date=winner.date, resolved_value=winner.value,
                resolved_source=f"{winner.id} ({winner.authority}, {winner.date})",
                category=getattr(c, "category", "functional") or "functional",
            ))
            # Any decision agreeing with the winning value backs it up.
            for d in candidates:
                if d.id != winner.id and _norm(d.value) == _norm(winner.value):
                    rc.backing.append(d.id)
        resolved.append(rc)

    return ResolverResult(resolved, conflicts, reinforcements, context)


def _norm(v: str) -> str:
    v = v.strip().lower()
    if v.startswith("0x"):
        return "0x" + v[2:].lstrip("0").zfill(2)
    return v
