"""
Mapper / Drift-Detection Agent
------------------------------
Compares the *resolved* spec claims (MAS reconciled with decisions/reviews)
against scanned RTL facts and classifies each one. Every finding carries a full
evidence chain: the HAS requirement it traces to, the spec clause, any decision
that backs or amended it, a confidence level, and grounded RAG evidence text.

Statuses:
    verified      - RTL matches the effective claim
    drift         - RTL implements it, but differently than required
    missing       - required, but not implemented in RTL
    undocumented  - RTL implements something no claim covers
    ambiguous     - could not be determined -> human review

Confidence:
    high    - backed by an explicit decision/review, or a clean verify
    medium  - based on MAS alone
    review  - conflicting sources or undetermined
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .authority_resolver import ResolvedClaim, ResolverResult
from .decision_ingest import Decision
from .rtl_scanner import RTLFacts
from ..knowledge.rag_store import RagStore

VERIFIED = "verified"
DRIFT = "drift"
MISSING = "missing"
UNDOCUMENTED = "undocumented"
AMBIGUOUS = "ambiguous"

HIGH = "high"
MEDIUM = "medium"
REVIEW = "review"


def _norm_hex(v: str) -> str:
    """Normalize a hex offset for comparison (e.g. 0x8 == 0x08)."""
    v = str(v).strip().lower()
    if v.startswith("0x"):
        return "0x" + v[2:].lstrip("0").zfill(2)
    return v


@dataclass
class Finding:
    claim_id: str
    status: str
    detail: str
    spec_source: str
    rtl_evidence: str
    traces_to: str = ""
    confidence: str = MEDIUM
    backing: List[str] = field(default_factory=list)   # decision ids
    conflict: bool = False
    rag_evidence: str = ""                              # grounded citation text
    category: str = "functional"                        # milestone category

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def map_claims(result: ResolverResult, facts: RTLFacts,
               decisions: Optional[List[Decision]] = None,
               store: Optional[RagStore] = None) -> List[Finding]:
    findings: List[Finding] = []
    covered_regs = set()
    context = _context_by_target(decisions or [])

    for rc in result.resolved:
        c = rc.claim
        if c.type == "signal_width":
            f = _check_width(rc, facts)
        elif c.type == "reset_polarity":
            f = _check_reset(rc, facts)
        elif c.type == "register":
            covered_regs.add(c.target.upper())
            f = _check_register(rc, facts)
        elif c.type == "fsm_states":
            f = _check_fsm(rc, facts)
        else:
            f = Finding(c.id, AMBIGUOUS, f"Unknown claim type '{c.type}'.",
                        c.source, "n/a", traces_to=c.traces, confidence=REVIEW)
        f.category = getattr(c, "category", "functional") or "functional"
        _annotate(f, rc, store)
        findings.append(f)

    findings.extend(_find_undocumented(facts, covered_regs, context, store))
    return findings


# --------------------------------------------------------------------------- #
# Per-type checks (compare against the EFFECTIVE/resolved value)
# --------------------------------------------------------------------------- #

def _check_width(rc: ResolvedClaim, facts: RTLFacts) -> Finding:
    c = rc.claim
    actual = facts.port_widths.get(c.target)
    if actual is None:
        return Finding(c.id, MISSING, f"Signal '{c.target}' not found in RTL.",
                       c.source, "port not present", traces_to=c.traces)
    expected = int(rc.effective_expected)
    if actual == expected:
        return Finding(c.id, VERIFIED,
                       f"'{c.target}' width {actual} bits matches spec.",
                       c.source, f"{c.target}[{actual-1}:0]", traces_to=c.traces)
    return Finding(c.id, DRIFT,
                   f"'{c.target}' is {actual} bits but required {expected}.",
                   c.source, f"{c.target}[{actual-1}:0]", traces_to=c.traces)


def _check_reset(rc: ResolvedClaim, facts: RTLFacts) -> Finding:
    c = rc.claim
    actual = facts.reset_polarity
    if actual is None:
        return Finding(c.id, AMBIGUOUS,
                       "Could not determine reset polarity from RTL.",
                       c.source, "n/a", traces_to=c.traces, confidence=REVIEW)
    if actual == rc.effective_expected:
        return Finding(c.id, VERIFIED,
                       f"Reset '{c.target}' is active-{actual} as specified.",
                       c.source, f"active-{actual}", traces_to=c.traces)
    return Finding(c.id, DRIFT,
                   f"Reset is active-{actual} but required active-"
                   f"{rc.effective_expected}.",
                   c.source, f"active-{actual}", traces_to=c.traces)


def _check_register(rc: ResolvedClaim, facts: RTLFacts) -> Finding:
    c = rc.claim
    key = c.target.upper()
    actual = facts.address_map.get(key)
    exp = rc.effective_expected
    if actual is None:
        return Finding(c.id, MISSING,
                       f"Register '{c.target}' (required offset {exp}) is not "
                       f"implemented in RTL.",
                       c.source, "no matching ADDR_ localparam",
                       traces_to=c.traces)
    if _norm_hex(actual) == _norm_hex(exp):
        return Finding(c.id, VERIFIED,
                       f"Register '{c.target}' at {actual} matches spec.",
                       c.source, f"ADDR_{key} = {actual}", traces_to=c.traces)
    return Finding(c.id, DRIFT,
                   f"Register '{c.target}' at {actual} but required {exp}.",
                   c.source, f"ADDR_{key} = {actual}", traces_to=c.traces)


def _check_fsm(rc: ResolvedClaim, facts: RTLFacts) -> Finding:
    c = rc.claim
    expected = {s.strip().upper() for s in rc.effective_expected.split(",")
                if s.strip()}
    # Look up the FSM by the claim's target name (e.g. control_fsm); fall back
    # to the primary FSM if the design has only one.
    by_name = getattr(facts, "fsm_by_name", {}) or {}
    states = by_name.get(c.target) or by_name.get(c.target + "_e") or facts.fsm_states
    actual = set(states)
    missing = expected - actual
    extra = actual - expected
    if not missing and not extra:
        return Finding(c.id, VERIFIED, f"FSM states {sorted(actual)} match spec.",
                       c.source, ",".join(sorted(actual)), traces_to=c.traces)
    parts = []
    if missing:
        parts.append(f"missing {sorted(missing)}")
    if extra:
        parts.append(f"undocumented {sorted(extra)}")
    status = MISSING if missing else UNDOCUMENTED
    return Finding(c.id, status, f"FSM '{c.target}': " + "; ".join(parts) + ".",
                   c.source, ",".join(sorted(actual)) or "no states",
                   traces_to=c.traces)


# --------------------------------------------------------------------------- #
# Undocumented RTL + annotation
# --------------------------------------------------------------------------- #

def _find_undocumented(facts: RTLFacts, covered: set,
                       context: Dict[str, List[Decision]],
                       store: Optional[RagStore]) -> List[Finding]:
    out: List[Finding] = []
    for name, off in facts.address_map.items():
        if name in covered:
            continue
        # An undocumented CSR register defaults to the CSR category so it is
        # caught at the 0.1 boundary gate. It is only treated as a 0.8 'debug'
        # artifact when a decision note explicitly tags it as such.
        f = Finding("RTL-EXTRA", UNDOCUMENTED,
                    f"RTL register ADDR_{name} at {off} has no matching spec "
                    f"claim.",
                    "n/a", f"ADDR_{name} = {off}", confidence=REVIEW,
                    category="csr")
        notes = context.get(name)
        if notes:
            d = notes[0]
            f.category = "debug"
            f.detail += (f" Context: {d.id} ({d.authority}, {d.date}) notes it "
                         f"as a known temporary hook.")
            f.backing.append(d.id)
            f.confidence = MEDIUM
            f.rag_evidence = f"[DECISION {d.id}] {d.rationale[:160]}"
        elif store is not None:
            hits = store.retrieve(f"{name} register {off}", k=1)
            if hits:
                f.rag_evidence = f"{hits[0].citation()} {hits[0].text[:140]}"
        out.append(f)
    return out


def _annotate(f: Finding, rc: ResolvedClaim, store: Optional[RagStore]) -> None:
    # Confidence + backing from the resolver.
    if rc.backing:
        f.backing.extend(rc.backing)
    if rc.amended_by:
        f.conflict = True
        f.confidence = REVIEW
        f.backing.append(rc.amended_by)
    elif f.status == VERIFIED:
        f.confidence = HIGH
    elif f.status in (DRIFT, MISSING) and rc.backing:
        f.confidence = HIGH   # drift confirmed by an explicit decision
    elif f.status in (DRIFT, MISSING):
        f.confidence = MEDIUM

    # Grounded RAG evidence: pull the actual spec clause text.
    if store is not None and not f.rag_evidence:
        chunk = store.get("MAS", f.spec_source) or store.get("HAS", f.spec_source)
        if chunk is None and rc.claim.source:
            chunk = store.get("MAS", rc.claim.source)
        if chunk:
            f.rag_evidence = f"{chunk.citation()} {chunk.text[:140]}"


def _context_by_target(decisions: List[Decision]) -> Dict[str, List[Decision]]:
    out: Dict[str, List[Decision]] = {}
    for d in decisions:
        if d.property == "note" or d.value == "temporary":
            out.setdefault(d.target.upper(), []).append(d)
    return out
