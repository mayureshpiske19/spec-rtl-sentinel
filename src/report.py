"""
Drift Report Generator
----------------------
Renders the full design-intent audit into a layered markdown report:

  1. Summary + verdict
  2. Traceability (HAS -> MAS -> RTL) with intent-level rollup
  3. Spec conflicts (source vs source, resolved by authority + recency)
  4. Clause-by-clause findings with the full evidence chain
  5. Decisions considered
  6. Simulation checks
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import List

from .agents.mapper import (
    Finding, VERIFIED, DRIFT, MISSING, UNDOCUMENTED, AMBIGUOUS,
)
from .agents.authority_resolver import ResolverResult
from .agents.traceability import TraceRow, GAP
from .agents.decision_ingest import Decision
from .agents.sim_checker import SimResult

_ICON = {
    VERIFIED: "✅",
    DRIFT: "🟥",
    MISSING: "❌",
    UNDOCUMENTED: "🟡",
    AMBIGUOUS: "⚠️",
}
_CONF = {"high": "🟢 high", "medium": "🟠 medium", "review": "🔴 review"}


def build_report(findings: List[Finding], sim_results: List[SimResult],
                 trace_rows: List[TraceRow], resolver: ResolverResult,
                 decisions: List[Decision], rag_stats: dict,
                 has_path: str, spec_path: str, rtl_path: str) -> str:
    counts = {k: 0 for k in _ICON}
    for f in findings:
        counts[f.status] = counts.get(f.status, 0) + 1
    total = len(findings)
    drift_like = counts[DRIFT] + counts[MISSING] + counts[UNDOCUMENTED]
    gaps = sum(1 for r in trace_rows if r.status == GAP)

    L: List[str] = []
    L.append("# MAS–RTL Sentinel — Design Intent Ledger Report")
    L.append("")
    L.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append(f"- **HAS:** `{os.path.basename(has_path)}` · "
             f"**MAS:** `{os.path.basename(spec_path)}` · "
             f"**RTL:** `{os.path.basename(rtl_path)}`")
    L.append(f"- **Knowledge grounded:** "
             + ", ".join(f"{k}={v}" for k, v in sorted(rag_stats.items()))
             + " chunks")
    L.append("")

    # 1. Summary
    L.append("## 1. Summary")
    L.append("")
    L.append(f"- Claims checked: **{total}**")
    L.append(f"- {_ICON[VERIFIED]} Verified: **{counts[VERIFIED]}** · "
             f"{_ICON[DRIFT]} Drift: **{counts[DRIFT]}** · "
             f"{_ICON[MISSING]} Missing: **{counts[MISSING]}** · "
             f"{_ICON[UNDOCUMENTED]} Undocumented: **{counts[UNDOCUMENTED]}** · "
             f"{_ICON[AMBIGUOUS]} Review: **{counts[AMBIGUOUS]}**")
    L.append(f"- Spec conflicts (source vs source): **{len(resolver.conflicts)}**")
    L.append(f"- Traceability gaps (HAS not refined in MAS): **{gaps}**")
    L.append("")
    ok = drift_like == 0 and not resolver.conflicts and gaps == 0
    L.append(f"**Verdict: {'✅ SPEC-FAITHFUL' if ok else '🚨 DRIFT / GAPS DETECTED'}**")
    L.append("")

    # 2. Traceability
    L.append("## 2. Traceability — HAS → MAS → RTL")
    L.append("")
    L.append("| HAS req | Kind | Requirement | MAS claims | RTL rollup | Trace |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for r in trace_rows:
        claims = ", ".join(r.claim_ids) if r.claim_ids else "—"
        roll = _ICON.get(r.rtl_rollup, r.rtl_rollup)
        trace = "❌ GAP" if r.status == GAP else "✅ traced"
        L.append(f"| {r.has_id} | {r.kind} | {r.requirement} | {claims} | "
                 f"{roll} | {trace} |")
    L.append("")
    if gaps:
        L.append("> ❌ **Traceability gap**: a HAS requirement has no MAS claim "
                 "refining it — top-level intent that was never detailed, and "
                 "therefore cannot be verified against RTL.")
        L.append("")

    # 3. Conflicts
    L.append("## 3. Spec Conflicts (resolved by authority + recency)")
    L.append("")
    if resolver.conflicts:
        L.append("| Target | Property | MAS says | Decision says | Resolved (authority) |")
        L.append("| --- | --- | --- | --- | --- |")
        for c in resolver.conflicts:
            L.append(f"| {c.target} | {c.property} | {c.mas_value} | "
                     f"{c.decision_value} | **{c.resolved_value}** "
                     f"— {c.resolved_source} |")
        L.append("")
        L.append("> ⚠️ A later review/decision overrides the stale MAS value. "
                 "The MAS should be updated; flagged for human review.")
    else:
        L.append("_No spec-vs-spec conflicts detected._")
    L.append("")

    # 4. Findings
    L.append("## 4. Clause-by-Clause Findings")
    L.append("")
    L.append("| Claim | Status | Conf | Traces | Spec | Detail | Evidence |")
    L.append("| --- | --- | --- | --- | --- | --- | --- |")
    for f in findings:
        icon = _ICON.get(f.status, "")
        conf = _CONF.get(f.confidence, f.confidence)
        back = (" · backing: " + ",".join(f.backing)) if f.backing else ""
        ev = (f.rag_evidence or f.rtl_evidence).replace("|", "\\|")
        L.append(f"| {f.claim_id} | {icon} {f.status} | {conf} | "
                 f"{f.traces_to or '—'} | {f.spec_source} | {f.detail}{back} | "
                 f"{ev} |")
    L.append("")

    # 5. Decisions
    L.append("## 5. Decisions Considered")
    L.append("")
    if decisions:
        L.append("| id | date | authority | type | amends | note |")
        L.append("| --- | --- | --- | --- | --- | --- |")
        for d in sorted(decisions, key=lambda x: x.date):
            note = f"{d.target}.{d.property}={d.value}" if d.value else ""
            L.append(f"| {d.id} | {d.date} | {d.authority} | {d.type} | "
                     f"{d.amends} | {note} |")
    else:
        L.append("_No decisions ingested._")
    L.append("")

    # 6. Sim
    L.append("## 6. Simulation Checks")
    L.append("")
    if sim_results:
        L.append("| Check | Status | Detail |")
        L.append("| --- | --- | --- |")
        for s in sim_results:
            L.append(f"| {s.name} | {s.status} | {s.detail} |")
    else:
        L.append("_No simulation checks run._")
    L.append("")
    return "\n".join(L)


def save_report(text: str, out_dir: str = "reports") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "drift_report.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path
