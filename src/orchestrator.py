"""
Orchestrator — Design Intent Ledger pipeline
---------------------------------------------

    HAS  ─▶ HAS Parser        ─▶ requirements ─┐
    MAS  ─▶ Claim Extractor   ─▶ claims ───────┤
    DEC  ─▶ Decision Ingest   ─▶ decisions ────┤   (all ingested into RAG store)
                                                │
        Authority Resolver  ◀───────────────────┘  ─▶ resolved claims + conflicts
        Traceability        (HAS ↔ MAS)             ─▶ trace rows (+ gaps)
    RTL  ─▶ RTL Scanner      ─▶ facts
        Mapper / Diff  (resolved claims vs facts)   ─▶ findings (evidence chain)
        Sim Checker                                 ─▶ sim results
        Report Generator                            ─▶ reports/drift_report.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .knowledge.rag_store import RagStore
from .agents.has_parser import parse_has, HASRequirement
from .agents.claim_extractor import extract_claims, Claim
from .agents.decision_ingest import ingest_decisions, Decision
from .agents.authority_resolver import resolve, ResolverResult
from .agents.traceability import build_trace, apply_rtl_rollup, TraceRow
from .agents.rtl_scanner import scan_rtl, RTLFacts
from .agents.mapper import map_claims, Finding
from .agents.sim_checker import run_sim_checks, SimResult
from .report import build_report, save_report


@dataclass
class PipelineResult:
    has_reqs: List[HASRequirement]
    claims: List[Claim]
    decisions: List[Decision]
    resolver: ResolverResult
    trace_rows: List[TraceRow]
    facts: RTLFacts
    findings: List[Finding]
    sim_results: List[SimResult]
    report_md: str
    report_path: str
    rag_stats: dict


def run_pipeline(has_path: str, spec_path: str, rtl_path: str,
                 decisions_dir: str, use_llm: bool = False,
                 out_dir: str = "reports") -> PipelineResult:
    store = RagStore()

    # Ingest all layers into the RAG store.
    has_reqs = parse_has(has_path, store=store)
    claims = extract_claims(spec_path, use_llm=use_llm, store=store)
    decisions = ingest_decisions(decisions_dir, store=store)

    # Reconcile spec vs decisions.
    resolver = resolve(claims, decisions)

    # Top-down traceability HAS -> MAS.
    trace_rows = build_trace(has_reqs, claims)

    # Scan RTL and diff against the resolved (effective) claims.
    facts = scan_rtl(rtl_path)
    findings = map_claims(resolver, facts, decisions=decisions, store=store)

    # Roll RTL status up onto each HAS requirement.
    status_by_claim = {f.claim_id: f.status for f in findings}
    apply_rtl_rollup(trace_rows, status_by_claim)

    sim_results = run_sim_checks(rtl_path)

    report_md = build_report(findings, sim_results, trace_rows, resolver,
                             decisions, store.stats(), has_path, spec_path,
                             rtl_path)
    report_path = save_report(report_md, out_dir=out_dir)

    return PipelineResult(has_reqs, claims, decisions, resolver, trace_rows,
                          facts, findings, sim_results, report_md, report_path,
                          store.stats())
