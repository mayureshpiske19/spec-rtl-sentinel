"""
Drift Report Generator
----------------------
Renders the Mapper findings + Sim results into a clause-by-clause markdown
report: what's verified, what drifted, what's missing, what's undocumented,
and what needs human review.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import List

from .agents.mapper import (
    Finding, VERIFIED, DRIFT, MISSING, UNDOCUMENTED, AMBIGUOUS,
)
from .agents.sim_checker import SimResult

_ICON = {
    VERIFIED: "✅",
    DRIFT: "🟥",
    MISSING: "❌",
    UNDOCUMENTED: "🟡",
    AMBIGUOUS: "⚠️",
}


def build_report(findings: List[Finding], sim_results: List[SimResult],
                 spec_path: str, rtl_path: str) -> str:
    counts = {k: 0 for k in _ICON}
    for f in findings:
        counts[f.status] = counts.get(f.status, 0) + 1

    total = len(findings)
    drift_like = counts[DRIFT] + counts[MISSING] + counts[UNDOCUMENTED]

    lines: List[str] = []
    lines.append("# MAS–RTL Sentinel — Drift Report")
    lines.append("")
    lines.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- **Spec:** `{os.path.basename(spec_path)}`")
    lines.append(f"- **RTL:** `{os.path.basename(rtl_path)}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Claims checked: **{total}**")
    lines.append(f"- {_ICON[VERIFIED]} Verified: **{counts[VERIFIED]}**")
    lines.append(f"- {_ICON[DRIFT]} Drift: **{counts[DRIFT]}**")
    lines.append(f"- {_ICON[MISSING]} Missing: **{counts[MISSING]}**")
    lines.append(f"- {_ICON[UNDOCUMENTED]} Undocumented: **{counts[UNDOCUMENTED]}**")
    lines.append(f"- {_ICON[AMBIGUOUS]} Needs review: **{counts[AMBIGUOUS]}**")
    lines.append("")
    verdict = "✅ SPEC-FAITHFUL" if drift_like == 0 else "🚨 DRIFT DETECTED"
    lines.append(f"**Verdict: {verdict}**")
    lines.append("")

    lines.append("## Clause-by-Clause Findings")
    lines.append("")
    lines.append("| Claim | Status | Spec | Detail | RTL evidence |")
    lines.append("| --- | --- | --- | --- | --- |")
    for f in findings:
        icon = _ICON.get(f.status, "")
        lines.append(
            f"| {f.claim_id} | {icon} {f.status} | {f.spec_source} | "
            f"{f.detail} | `{f.rtl_evidence}` |"
        )
    lines.append("")

    lines.append("## Simulation Checks")
    lines.append("")
    if sim_results:
        lines.append("| Check | Status | Detail |")
        lines.append("| --- | --- | --- |")
        for s in sim_results:
            lines.append(f"| {s.name} | {s.status} | {s.detail} |")
    else:
        lines.append("_No simulation checks run._")
    lines.append("")
    return "\n".join(lines)


def save_report(text: str, out_dir: str = "reports") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "drift_report.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path
