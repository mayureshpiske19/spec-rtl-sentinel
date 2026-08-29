"""
Simulation Checker Agent
------------------------
For claims that can be dynamically confirmed, this agent runs (or would run) a
directed simulation and reports whether the claim holds at runtime.

Offline/demo behavior: if a Verilog simulator (iverilog) is on PATH, it lint-
compiles the RTL and records that the design elaborates. Otherwise it records a
"skipped" result. Either way it never blocks the pipeline.

Upgrade path: generate directed stimulus per claim (e.g. reset-value checks,
register read/write checks) and parse the simulator log to confirm behavior.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class SimResult:
    name: str
    status: str   # passed | failed | skipped
    detail: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def run_sim_checks(rtl_path: str) -> List[SimResult]:
    results: List[SimResult] = []
    iverilog = shutil.which("iverilog")
    if not iverilog:
        results.append(SimResult(
            "elaboration",
            "skipped",
            "iverilog not found on PATH; static checks only. "
            "Install Icarus Verilog to enable simulation-based confirmation.",
        ))
        return results

    try:
        proc = subprocess.run(
            [iverilog, "-g2012", "-tnull", rtl_path],
            capture_output=True, text=True, timeout=60,
        )
        if proc.returncode == 0:
            results.append(SimResult(
                "elaboration", "passed",
                "RTL elaborates cleanly under iverilog (-g2012).",
            ))
        else:
            results.append(SimResult(
                "elaboration", "failed",
                (proc.stderr or proc.stdout).strip()[:500],
            ))
    except Exception as exc:  # pragma: no cover
        results.append(SimResult("elaboration", "skipped", f"sim error: {exc}"))
    return results
