"""
Orchestrator
------------
Runs the MAS-RTL Sentinel pipeline end to end:

    spec ──▶ Claim Extractor ──▶ claims
    rtl  ──▶ RTL Scanner      ──▶ facts
    claims + facts ──▶ Mapper ──▶ findings
    rtl  ──▶ Sim Checker      ──▶ sim results
    findings + sim ──▶ Report Generator ──▶ drift_report.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .agents.claim_extractor import extract_claims, Claim
from .agents.rtl_scanner import scan_rtl, RTLFacts
from .agents.mapper import map_claims, Finding
from .agents.sim_checker import run_sim_checks, SimResult
from .report import build_report, save_report


@dataclass
class PipelineResult:
    claims: List[Claim]
    facts: RTLFacts
    findings: List[Finding]
    sim_results: List[SimResult]
    report_md: str
    report_path: str


def run_pipeline(spec_path: str, rtl_path: str, use_llm: bool = False,
                 out_dir: str = "reports") -> PipelineResult:
    claims = extract_claims(spec_path, use_llm=use_llm)
    facts = scan_rtl(rtl_path)
    findings = map_claims(claims, facts)
    sim_results = run_sim_checks(rtl_path)
    report_md = build_report(findings, sim_results, spec_path, rtl_path)
    report_path = save_report(report_md, out_dir=out_dir)
    return PipelineResult(claims, facts, findings, sim_results,
                          report_md, report_path)
