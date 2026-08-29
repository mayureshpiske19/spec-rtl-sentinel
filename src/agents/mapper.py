"""
Mapper / Drift-Detection Agent
------------------------------
Compares extracted spec Claims against scanned RTLFacts and classifies each
claim. Every finding cites the spec source clause and the concrete RTL evidence
(anti-hallucination: nothing is asserted without a grounded reference).

Statuses:
    verified      - RTL matches the claim
    drift         - RTL implements it, but differently than the spec
    missing       - spec requires it, RTL does not implement it
    undocumented  - RTL implements something not covered by any claim
    ambiguous     - could not be determined automatically -> human review
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .claim_extractor import Claim
from .rtl_scanner import RTLFacts


VERIFIED = "verified"
DRIFT = "drift"
MISSING = "missing"
UNDOCUMENTED = "undocumented"
AMBIGUOUS = "ambiguous"


@dataclass
class Finding:
    claim_id: str
    status: str
    detail: str
    spec_source: str
    rtl_evidence: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def map_claims(claims: List[Claim], facts: RTLFacts) -> List[Finding]:
    findings: List[Finding] = []
    covered_regs = set()

    for c in claims:
        if c.type == "signal_width":
            findings.append(_check_width(c, facts))
        elif c.type == "reset_polarity":
            findings.append(_check_reset(c, facts))
        elif c.type == "register":
            covered_regs.add(c.target.upper())
            findings.append(_check_register(c, facts))
        elif c.type == "fsm_states":
            findings.append(_check_fsm(c, facts))
        else:
            findings.append(
                Finding(c.id, AMBIGUOUS, f"Unknown claim type '{c.type}'.",
                        c.source, "n/a")
            )

    findings.extend(_find_undocumented(facts, covered_regs))
    return findings


def _check_width(c: Claim, facts: RTLFacts) -> Finding:
    actual = facts.port_widths.get(c.target)
    if actual is None:
        return Finding(c.id, MISSING,
                       f"Signal '{c.target}' not found in RTL.",
                       c.source, "port not present")
    expected = int(c.expected)
    if actual == expected:
        return Finding(c.id, VERIFIED,
                       f"'{c.target}' width {actual} bits matches spec.",
                       c.source, f"{c.target}[{actual-1}:0]")
    return Finding(c.id, DRIFT,
                   f"'{c.target}' is {actual} bits but spec requires {expected}.",
                   c.source, f"{c.target}[{actual-1}:0]")


def _check_reset(c: Claim, facts: RTLFacts) -> Finding:
    actual = facts.reset_polarity
    if actual is None:
        return Finding(c.id, AMBIGUOUS,
                       "Could not determine reset polarity from RTL.",
                       c.source, "n/a")
    if actual == c.expected:
        return Finding(c.id, VERIFIED,
                       f"Reset '{c.target}' is active-{actual} as specified.",
                       c.source, f"active-{actual}")
    return Finding(c.id, DRIFT,
                   f"Reset is active-{actual} but spec requires active-{c.expected}.",
                   c.source, f"active-{actual}")


def _check_register(c: Claim, facts: RTLFacts) -> Finding:
    key = c.target.upper()
    actual = facts.address_map.get(key)
    if actual is None:
        return Finding(c.id, MISSING,
                       f"Register '{c.target}' (spec offset {c.expected}) "
                       f"is not implemented in RTL.",
                       c.source, "no matching ADDR_ localparam")
    if actual.lower() == c.expected.lower():
        return Finding(c.id, VERIFIED,
                       f"Register '{c.target}' at {actual} matches spec.",
                       c.source, f"ADDR_{key} = {actual}")
    return Finding(c.id, DRIFT,
                   f"Register '{c.target}' at {actual} but spec says {c.expected}.",
                   c.source, f"ADDR_{key} = {actual}")


def _check_fsm(c: Claim, facts: RTLFacts) -> Finding:
    expected = {s.strip().upper() for s in c.expected.split(",") if s.strip()}
    actual = set(facts.fsm_states)
    missing = expected - actual
    extra = actual - expected
    if not missing and not extra:
        return Finding(c.id, VERIFIED,
                       f"FSM states {sorted(actual)} match spec.",
                       c.source, ",".join(sorted(actual)))
    parts = []
    if missing:
        parts.append(f"missing {sorted(missing)}")
    if extra:
        parts.append(f"undocumented {sorted(extra)}")
    status = MISSING if missing else UNDOCUMENTED
    return Finding(c.id, status,
                   f"FSM '{c.target}': " + "; ".join(parts) + ".",
                   c.source, ",".join(sorted(actual)) or "no states")


def _find_undocumented(facts: RTLFacts, covered: set) -> List[Finding]:
    out: List[Finding] = []
    for name, off in facts.address_map.items():
        if name not in covered:
            out.append(
                Finding("RTL-EXTRA", UNDOCUMENTED,
                        f"RTL register ADDR_{name} at {off} has no matching "
                        f"spec claim.",
                        "n/a", f"ADDR_{name} = {off}")
            )
    return out
