"""
Demo entry point — Design Intent Ledger.

Usage:
    python examples/run_demo.py
    python examples/run_demo.py --milestone 0.1
    python examples/run_demo.py --has data/has/sample_has.md \
        --spec data/specs/sample_mas.md \
        --rtl data/rtl/sample_ciu_axi_sub.sv \
        --decisions data/decisions --milestone 0.5
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestrator import run_pipeline  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Spec-RTL Sentinel — Design Intent Ledger")
    ap.add_argument("--has", default="data/has/sample_has.md")
    ap.add_argument("--spec", default="data/specs/sample_mas.md")
    ap.add_argument("--rtl", default="data/rtl/sample_ciu_axi_sub.sv")
    ap.add_argument("--decisions", default="data/decisions")
    ap.add_argument("--milestone", default="1.0",
                    choices=["0.1", "0.5", "0.8", "1.0"],
                    help="Check scope: 0.1 boundary+CSR, 0.5 +functional, "
                         "0.8 +error/dft/perf/debug, 1.0 overall")
    ap.add_argument("--llm", action="store_true")
    args = ap.parse_args()

    r = run_pipeline(args.has, args.spec, args.rtl, args.decisions,
                     use_llm=args.llm, milestone=args.milestone)

    print("=" * 72)
    print("Spec-RTL Sentinel — Design Intent Ledger")
    print("=" * 72)
    print(f"Knowledge ingested : {r.rag_stats}  (HAS/MAS/DECISION chunks)")
    print(f"HAS requirements   : {len(r.has_reqs)}   (golden reference)")
    print(f"MAS claims         : {len(r.claims)}")
    print(f"Decisions          : {len(r.decisions)}")
    print(f"RTL module         : {r.facts.module}")
    print(f"Milestone scope    : {r.milestone}")
    print()

    print("Milestone gate status (cumulative):")
    for g in r.gates:
        verdict = "PASS" if g["passed"] else "FAIL"
        reasons = ""
        if not g["passed"]:
            bits = []
            if g["fails"]:
                bits.append(", ".join(f"{x.claim_id}:{x.status}" for x in g["fails"]))
            if g["gaps"]:
                bits.append(", ".join(f"{t.has_id}:gap" for t in g["gaps"]))
            reasons = "  <- " + "; ".join(bits)
        print(f"  [{verdict}] {g['milestone']:4} {g['label']:38} "
              f"checked={g['checked']}{reasons}")
    print()

    if r.resolver.conflicts:
        print("Spec conflicts (source vs source):")
        for c in r.resolver.conflicts:
            print(f"  {c.target}.{c.property}: MAS={c.mas_value} vs "
                  f"{c.decision_id}={c.decision_value} -> resolved "
                  f"{c.resolved_value} ({c.authority})")
        print()

    print(f"Findings (milestone {r.milestone} scope):")
    for f in r.findings:
        back = f" [backing: {','.join(f.backing)}]" if f.backing else ""
        print(f"  [{f.status.upper():12}] {f.claim_id:10} {f.category:10} "
              f"({f.confidence:6}) {f.traces_to or '   '}  {f.detail}{back}")
    print()
    print(f"Full report: {r.report_path}")
    print(f"HTML report: {r.html_path}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
