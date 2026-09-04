# Spec-RTL Sentinel — Design Intent Ledger Report

- **Generated:** 2026-09-04 15:15
- **Milestone scope:** `1.0`  (HAS is the golden reference; MAS + RTL are checked against it)
- **HAS:** `sample_has.md` · **MAS:** `sample_mas.md` · **RTL:** `sample_ciu_axi_sub.sv`
- **Knowledge grounded:** DECISION=3, HAS=8, MAS=9 chunks

## 0. Milestone Gate Status

| Milestone | Scope | Checked | Fails | Gaps | Gate |
| --- | --- | --- | --- | --- | --- |
| **0.1** | Boundary — ports + CSR registers | 5 | 2 | 0 | 🚨 FAIL |
| **0.5** | + Functional behavior (FSM, datapath) | 6 | 3 | 0 | 🚨 FAIL |
| **0.8** | + Errors, DFT, perf counters, debug | 10 | 4 | 1 | 🚨 FAIL |
| **1.0** | Overall / integration — everything | 10 | 4 | 1 | 🚨 FAIL |

> Gates are cumulative: each milestone re-checks everything from the milestones below it. A milestone passes only when every in-scope claim is verified with no traceability gap.

## 1. Summary

- Claims checked (milestone 1.0 scope): **10**
- ✅ Verified: **5** · 🟥 Drift: **1** · ❌ Missing: **3** · 🟡 Undocumented: **1** · ⚠️ Review: **0**
- Spec conflicts (source vs source): **1**
- Traceability gaps (HAS not refined in MAS): **1**

**Verdict: 🚨 DRIFT / GAPS DETECTED**

## 2. Traceability — HAS → MAS → RTL

| HAS req | Kind | Requirement | MAS claims | RTL rollup | Trace |
| --- | --- | --- | --- | --- | --- |
| HAS-01 | concept | CSR block exposed to SoC fabric via an AXI4 subordinate interface | CLAIM-02 | ✅ | ✅ traced |
| HAS-02 | performance | Fabric data path is 64-bit wide for target throughput | CLAIM-01 | 🟥 | ✅ traced |
| HAS-03 | security | Secret boot key (BEK) provisioned by security engine into a dedicated register | CLAIM-05 | ✅ | ✅ traced |
| HAS-04 | concept | Block control managed by an FSM with explicit error handling | CLAIM-03, CLAIM-04, CLAIM-06 | ❌ | ✅ traced |
| HAS-05 | performance | CSR reads complete with single-cycle latency | — | n/a | ❌ GAP |
| HAS-06 | reliability | Fault conditions reported via an error-status register | CLAIM-07 | ✅ | ✅ traced |
| HAS-07 | testability | Scan-based DFT supported via a scan-enable control | CLAIM-08 | ❌ | ✅ traced |
| HAS-08 | performance | Performance counter exposes transaction activity | CLAIM-09 | ✅ | ✅ traced |

> ❌ **Traceability gap**: a HAS requirement has no MAS claim refining it — top-level intent that was never detailed, and therefore cannot be verified against RTL.

## 3. Spec Conflicts (resolved by authority + recency)

| Target | Property | MAS says | Decision says | Resolved (authority) |
| --- | --- | --- | --- | --- |
| STATUS | offset | 0x04 | 0x08 | **0x08** — DEC-02 (design_review, 2026-08-25) |

> ⚠️ A later review/decision overrides the stale MAS value. The MAS should be updated; flagged for human review.

## 4. Clause-by-Clause Findings

| Claim | Milestone | Category | Status | Conf | Traces | Spec | Detail | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLAIM-01 | 0.1 | boundary | 🟥 drift | 🟢 high | HAS-02 | §2.1 | 's_axi_wdata' is 32 bits but required 64. · backing: DEC-01 | [MAS §2.1] The CSR write-data bus `s_axi_wdata` shall be **64 bits** wide to match the SSS fabric data width. |
| CLAIM-02 | 0.1 | boundary | ✅ verified | 🟢 high | HAS-01 | §2.2 | Reset 'aresetn' is active-low as specified. | [MAS §2.2] The block shall use an **active-low** asynchronous reset named `aresetn`. |
| CLAIM-03 | 0.1 | csr | ✅ verified | 🟢 high | HAS-04 | §3.1 | Register 'CTRL' at 0x00 matches spec. | [MAS §3.1] `CTRL` register at byte offset **0x00** (read/write), reset value 0x0. |
| CLAIM-04 | 0.1 | csr | ❌ missing | 🔴 review | HAS-04 | §3.2 | Register 'STATUS' (required offset 0x08) is not implemented in RTL. · backing: DEC-02 | [MAS §3.2] `STATUS` register at byte offset **0x04** (read-only). |
| CLAIM-05 | 0.1 | csr | ✅ verified | 🟢 high | HAS-03 | §3.3 | Register 'BEK_KEY' at 0x10 matches spec. | [MAS §3.3] `BEK_KEY` register at byte offset **0x10** (write-only), written by the security engine during initialization. |
| CLAIM-06 | 0.5 | functional | ❌ missing | 🟠 medium | HAS-04 | §4.1 | FSM 'ciu_fsm': missing ['ERROR']. | [MAS §4.1] The control FSM `ciu_fsm` shall implement the states **IDLE, ACTIVE, ERROR**. |
| CLAIM-07 | 0.8 | error | ✅ verified | 🟢 high | HAS-06 | §5.1 | Register 'ERR_STATUS' at 0x0c matches spec. | [MAS §5.1] `ERR_STATUS` register at byte offset **0x0C** (read-only) reports fault conditions. |
| CLAIM-08 | 0.8 | dft | ❌ missing | 🟠 medium | HAS-07 | §5.2 | Signal 'scan_en' not found in RTL. | [MAS §5.2] A scan-enable input `scan_en` (1 bit) controls scan-based DFT. |
| CLAIM-09 | 0.8 | perf | ✅ verified | 🟢 high | HAS-08 | §5.3 | Register 'PERF_CNT' at 0x14 matches spec. | [MAS §5.3] `PERF_CNT` register at byte offset **0x14** (read-only) counts transactions. |
| RTL-EXTRA | 0.8 | debug | 🟡 undocumented | 🟠 medium | — | n/a | RTL register ADDR_DEBUG at 0x20 has no matching spec claim. Context: DEC-03 (meeting, 2026-07-30) notes it as a known temporary hook. · backing: DEC-03 | [DECISION DEC-03] Bring-up sync meeting. A DEBUG_SCRATCH register may be added temporarily at 0x20 to aid silicon bring-up. It is explicitly NOT part of the HAS or MAS and must b |

## 5. Decisions Considered

| id | date | authority | type | amends | note |
| --- | --- | --- | --- | --- | --- |
| DEC-03 | 2026-07-30 | meeting | discussion | none | DEBUG.note=temporary |
| DEC-01 | 2026-08-12 | arch_review | decision | none | s_axi_wdata.width_bits=64 |
| DEC-02 | 2026-08-25 | design_review | decision | MAS §3.2 | STATUS.offset=0x08 |

## 6. Simulation Checks

| Check | Status | Detail |
| --- | --- | --- |
| elaboration | skipped | iverilog not found on PATH; static checks only. Install Icarus Verilog to enable simulation-based confirmation. |
