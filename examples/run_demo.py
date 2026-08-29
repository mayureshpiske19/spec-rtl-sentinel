"""
Demo entry point.

Usage:
    python examples/run_demo.py
    python examples/run_demo.py --spec data/specs/sample_mas.md \
                                --rtl data/rtl/sample_ciu_axi_sub.sv
"""

import argparse
import os
import sys

# Make the project root importable when run directly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestrator import run_pipeline  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="MAS-RTL Sentinel demo")
    ap.add_argument("--spec", default="data/specs/sample_mas.md")
    ap.add_argument("--rtl", default="data/rtl/sample_ciu_axi_sub.sv")
    ap.add_argument("--llm", action="store_true",
                    help="Use LLM claim extraction (requires Azure OpenAI setup)")
    args = ap.parse_args()

    result = run_pipeline(args.spec, args.rtl, use_llm=args.llm)

    print("=" * 68)
    print("MAS-RTL Sentinel — pipeline complete")
    print("=" * 68)
    print(f"Claims extracted : {len(result.claims)}")
    print(f"RTL module       : {result.facts.module}")
    print(f"Findings         : {len(result.findings)}")
    print()
    for f in result.findings:
        print(f"  [{f.status.upper():12}] {f.claim_id:10} {f.detail}")
    print()
    print(f"Report written to: {result.report_path}")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
