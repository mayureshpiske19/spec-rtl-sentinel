"""
Milestone model
---------------
RTL matures in milestones. At each milestone only a defined scope of the design
is expected to be complete, so Sentinel only *checks* the parameters relevant to
that milestone — cumulatively (a later milestone still requires the earlier ones
to hold).

    Milestone   Introduces (category)                     Meaning
    ---------   ---------------------------------------   -------------------------
    0.1         boundary, csr                             interface: ports + CSRs
    0.5         functional                                functional behavior / FSM
    0.8         error, dft, perf, debug                   error/DFT/perf/debug
    1.0         integration                               overall / everything

HAS is the golden reference and is never flagged; only MAS and RTL are checked
against it. Each claim carries a `category`; the category determines the
milestone at which it first comes into scope.
"""

from __future__ import annotations

from typing import Dict, List, Set

MILESTONES: List[str] = ["0.1", "0.5", "0.8", "1.0"]

# Categories first required at each milestone.
MILESTONE_CATEGORIES: Dict[str, Set[str]] = {
    "0.1": {"boundary", "csr"},
    "0.5": {"functional"},
    "0.8": {"error", "dft", "perf", "debug"},
    "1.0": {"integration"},
}

# Human-friendly scope labels for the report.
MILESTONE_LABEL: Dict[str, str] = {
    "0.1": "Boundary — ports + CSR registers",
    "0.5": "+ Functional behavior (FSM, datapath)",
    "0.8": "+ Errors, DFT, perf counters, debug",
    "1.0": "Overall / integration — everything",
}


def normalize(milestone: str) -> str:
    m = str(milestone).strip()
    return m if m in MILESTONES else "1.0"


def scope_for(milestone: str) -> Set[str]:
    """Cumulative set of categories in scope at (and below) a milestone."""
    milestone = normalize(milestone)
    scope: Set[str] = set()
    for m in MILESTONES:
        scope |= MILESTONE_CATEGORIES[m]
        if m == milestone:
            break
    return scope


def milestone_of(category: str) -> str:
    """The milestone at which a category first comes into scope."""
    for m in MILESTONES:
        if category in MILESTONE_CATEGORIES[m]:
            return m
    return "1.0"


def in_scope(category: str, milestone: str) -> bool:
    return category in scope_for(milestone)


# Finding statuses that fail a milestone gate.
_FAILING = {"drift", "missing"}


def compute_gates(findings, trace_rows):
    """
    Compute per-milestone gate status.

    A milestone PASSES when every in-scope finding is verified (no drift/missing)
    and there is no traceability gap in scope. `findings` and `trace_rows` are
    the mapper Finding and traceability TraceRow objects (duck-typed here to
    avoid import cycles).

    Returns a list of dicts, one per milestone, ordered 0.1 -> 1.0.
    """
    gates = []
    for m in MILESTONES:
        scope = scope_for(m)
        in_scope_f = [f for f in findings if getattr(f, "category", "functional") in scope]
        # A gate fails on genuine RTL drift/missing or a traceability gap.
        # Spec conflicts (RTL correct vs a stale spec) and undocumented items are
        # surfaced as advisories, not gate blockers.
        fails = [f for f in in_scope_f if f.status in _FAILING]
        conflicts = [f for f in in_scope_f if getattr(f, "conflict", False)]
        warns = [f for f in in_scope_f
                 if f.status in ("undocumented", "ambiguous")
                 and f.status not in _FAILING]
        gaps = [t for t in trace_rows
                if t.status == "gap" and getattr(t, "category", "functional") in scope]
        passed = not fails and not gaps
        gates.append({
            "milestone": m,
            "label": MILESTONE_LABEL[m],
            "checked": len(in_scope_f),
            "fails": fails,
            "conflicts": conflicts,
            "warns": warns,
            "gaps": gaps,
            "passed": passed,
        })
    return gates
