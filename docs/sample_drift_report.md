# Spec-RTL Sentinel — Design Intent Ledger Report

- **Generated:** 2026-09-04 16:29
- **Milestone scope:** `1.0`  (HAS is the golden reference; MAS + RTL are checked against it)
- **Two checks:** HAS → MAS coverage (spec vs spec) · MAS → RTL conformance (spec vs implementation)
- **HAS:** `zephyr_coss_has.md` · **MAS:** `zephyr_coss_mas.md` · **RTL:** `rtl`
- **Knowledge grounded:** DECISION=3, HAS=10, MAS=11 chunks

## 0. Milestone Gate Status

| Milestone | Scope | Checked | Fails | Gaps | Gate |
| --- | --- | --- | --- | --- | --- |
| **0.1** | Boundary — ports + CSR registers | 12 | 1 | 0 | 🚨 FAIL |
| **0.5** | + Functional behavior (FSM, datapath) | 13 | 2 | 0 | 🚨 FAIL |
| **0.8** | + Errors, DFT, perf counters, debug | 29 | 3 | 0 | 🚨 FAIL |
| **1.0** | Overall / integration — everything | 29 | 3 | 1 | 🚨 FAIL |

> Gates are cumulative: each milestone re-checks everything from the milestones below it. A milestone passes only when every in-scope claim is verified with no traceability gap.

## 1. Summary

- Claims checked (milestone 1.0 scope): **29**
- ✅ Verified: **25** · 🟥 Drift: **1** · ❌ Missing: **2** · 🟡 Undocumented: **1** · ⚠️ Review: **0**
- Spec conflicts (source vs source): **1**
- Traceability gaps (HAS not refined in MAS): **1**

**Verdict: 🚨 DRIFT / GAPS DETECTED**

## 2. HAS → MAS Coverage  *(spec vs spec)*

_Does every top-level HAS requirement have a MAS claim refining it? A **gap** = present in the HAS but never detailed in the MAS._

| HAS req | Kind | Requirement | MAS claims | RTL rollup | Trace |
| --- | --- | --- | --- | --- | --- |
| HAS-01 | interface | AXI4 multi-master datapath with a 64-bit memory data width | CLAIM-01, CLAIM-02 | 🟥 | ✅ traced |
| HAS-02 | interface | Firmware CSR / job-descriptor interface over AXI4-Lite | CLAIM-03, CLAIM-04, CLAIM-05, CLAIM-06, CLAIM-07, CLAIM-08, CLAIM-09, CLAIM-10, CLAIM-11, CLAIM-12 | ✅ | ✅ traced |
| HAS-03 | function | LZ77 compression engine driven by a job-sequencer FSM | CLAIM-13 | ❌ | ✅ traced |
| HAS-04 | function | QoS arbiter with round-robin and selectable priority modes | CLAIM-23 | ✅ | ✅ traced |
| HAS-05 | function | L2 cache for the history window and job descriptors | CLAIM-21 | ✅ | ✅ traced |
| HAS-06 | reliability | Classified error detection, capture, and reporting | CLAIM-14, CLAIM-15, CLAIM-16 | ✅ | ✅ traced |
| HAS-07 | performance | Performance counters (bytes, jobs, cycles, cache hits/misses) | CLAIM-17, CLAIM-18, CLAIM-19, CLAIM-20, CLAIM-22 | ❌ | ✅ traced |
| HAS-08 | debug | Debug/observability: FSM/job state, trace, breakpoints, DFT | CLAIM-24, CLAIM-25, CLAIM-26, CLAIM-27, CLAIM-28 | ✅ | ✅ traced |
| HAS-09 | portability | Optional multi-clock CDC bridging between CSR and datapath | — | n/a | ❌ GAP |

> ❌ **Traceability gap**: a HAS requirement has no MAS claim refining it — top-level intent that was never detailed, and therefore cannot be verified against RTL.

## 3. Spec Conflicts (resolved by authority + recency)

| Target | Property | MAS says | Decision says | Resolved (authority) |
| --- | --- | --- | --- | --- |
| INT_STATUS | offset | 0x054 | 0x058 | **0x058** — DEC-02 (design_review, 2026-09-02) |

> ⚠️ A later review/decision overrides the stale MAS value. The MAS should be updated; flagged for human review.

## 4. MAS → RTL Conformance  *(spec vs implementation)*

_Does the RTL implement each MAS claim? Drift = implemented differently; missing = not implemented; undocumented = in RTL but no claim._

| Claim | Milestone | Category | Status | Conf | Traces | Spec | Detail | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLAIM-01 | 0.1 | boundary | 🟥 drift | 🟢 high | HAS-01 | §2.1 | 'm_axi_wdata' is 32 bits but required 64. · backing: DEC-01 | [MAS §2.1] The accelerator memory write-data bus `m_axi_wdata` shall be **64 bits** wide to match the SoC data path. |
| CLAIM-02 | 0.1 | boundary | ✅ verified | 🟢 high | HAS-01 | §2.2 | Reset 'aresetn' is active-low as specified. | [MAS §2.2] The CSR block shall use an **active-low**, asynchronous-assert / synchronous-release reset named `aresetn`. |
| CLAIM-03 | 0.1 | boundary | ✅ verified | 🟢 high | HAS-02 | §2.3 | 's_axi_awaddr' width 12 bits matches spec. | [MAS §2.3] The CSR address bus `s_axi_awaddr` shall be **12 bits** wide (covers the 0x000–0x06C register space). |
| CLAIM-04 | 0.1 | csr | ✅ verified | 🟢 high | HAS-02 | §3.1 | Register 'CTRL' at 0x000 matches spec. | [MAS §3.1] Control/config/status: `CTRL` **0x000**, `CFG` **0x004**, `STATUS` **0x008**. |
| CLAIM-05 | 0.1 | csr | ✅ verified | 🟢 high | HAS-02 | §3.1 | Register 'CFG' at 0x004 matches spec. | [MAS §3.1] Control/config/status: `CTRL` **0x000**, `CFG` **0x004**, `STATUS` **0x008**. |
| CLAIM-06 | 0.1 | csr | ✅ verified | 🟢 high | HAS-02 | §3.1 | Register 'STATUS' at 0x008 matches spec. | [MAS §3.1] Control/config/status: `CTRL` **0x000**, `CFG` **0x004**, `STATUS` **0x008**. |
| CLAIM-07 | 0.1 | csr | ✅ verified | 🟢 high | HAS-02 | §3.2 | Register 'RING_BASE' at 0x010 matches spec. | [MAS §3.2] Job ring: `RING_BASE` **0x010**, `RING_HEAD` **0x014**, `RING_TAIL` **0x018**, `RING_SIZE` **0x01C**. |
| CLAIM-08 | 0.1 | csr | ✅ verified | 🟢 high | HAS-02 | §3.2 | Register 'RING_HEAD' at 0x014 matches spec. | [MAS §3.2] Job ring: `RING_BASE` **0x010**, `RING_HEAD` **0x014**, `RING_TAIL` **0x018**, `RING_SIZE` **0x01C**. |
| CLAIM-09 | 0.1 | csr | ✅ verified | 🟢 high | HAS-02 | §3.2 | Register 'RING_TAIL' at 0x018 matches spec. | [MAS §3.2] Job ring: `RING_BASE` **0x010**, `RING_HEAD` **0x014**, `RING_TAIL` **0x018**, `RING_SIZE` **0x01C**. |
| CLAIM-10 | 0.1 | csr | ✅ verified | 🟢 high | HAS-02 | §3.2 | Register 'RING_SIZE' at 0x01c matches spec. | [MAS §3.2] Job ring: `RING_BASE` **0x010**, `RING_HEAD` **0x014**, `RING_TAIL` **0x018**, `RING_SIZE` **0x01C**. |
| CLAIM-11 | 0.1 | csr | ✅ verified | 🟢 high | HAS-02 | §3.5 | Register 'INT_EN' at 0x050 matches spec. | [MAS §3.5] Interrupt: `INT_EN` **0x050**, `INT_STATUS` **0x054** (W1C). |
| CLAIM-12 | 0.1 | csr | ✅ verified | 🔴 review | HAS-02 | §3.5 | Register 'INT_STATUS' at 0x058 matches spec. · backing: DEC-02 | [MAS §3.5] Interrupt: `INT_EN` **0x050**, `INT_STATUS` **0x054** (W1C). |
| CLAIM-13 | 0.5 | functional | ❌ missing | 🟠 medium | HAS-03 | §4.1 | FSM 'control_fsm': missing ['WRITE_OUT']. | [MAS §4.1] The job-sequencer FSM `control_fsm` shall implement the states **IDLE, FETCH_JOB, LOAD_DATA, COMPRESS, WRITE_OUT, DONE**. |
| CLAIM-14 | 0.8 | error | ✅ verified | 🟢 high | HAS-06 | §3.4 | Register 'ERROR' at 0x040 matches spec. | [MAS §3.4] Error: `ERROR` **0x040** (W1C), `ERR_ADDR` **0x044**, `ERR_INFO` **0x048**. |
| CLAIM-15 | 0.8 | error | ✅ verified | 🟢 high | HAS-06 | §3.4 | Register 'ERR_ADDR' at 0x044 matches spec. | [MAS §3.4] Error: `ERROR` **0x040** (W1C), `ERR_ADDR` **0x044**, `ERR_INFO` **0x048**. |
| CLAIM-16 | 0.8 | error | ✅ verified | 🟢 high | HAS-06 | §3.4 | Register 'ERR_INFO' at 0x048 matches spec. | [MAS §3.4] Error: `ERROR` **0x040** (W1C), `ERR_ADDR` **0x044**, `ERR_INFO` **0x048**. |
| CLAIM-17 | 0.8 | perf | ✅ verified | 🟢 high | HAS-07 | §3.3 | Register 'PERF_BYTES_IN' at 0x020 matches spec. | [MAS §3.3] Performance counters: `PERF_BYTES_IN` **0x020**, `PERF_BYTES_OUT` **0x024**, `PERF_JOBS` **0x028**, `PERF_CYCLES` **0x02C**, `PERF_HITS` **0 |
| CLAIM-18 | 0.8 | perf | ✅ verified | 🟢 high | HAS-07 | §3.3 | Register 'PERF_BYTES_OUT' at 0x024 matches spec. | [MAS §3.3] Performance counters: `PERF_BYTES_IN` **0x020**, `PERF_BYTES_OUT` **0x024**, `PERF_JOBS` **0x028**, `PERF_CYCLES` **0x02C**, `PERF_HITS` **0 |
| CLAIM-19 | 0.8 | perf | ✅ verified | 🟢 high | HAS-07 | §3.3 | Register 'PERF_JOBS' at 0x028 matches spec. | [MAS §3.3] Performance counters: `PERF_BYTES_IN` **0x020**, `PERF_BYTES_OUT` **0x024**, `PERF_JOBS` **0x028**, `PERF_CYCLES` **0x02C**, `PERF_HITS` **0 |
| CLAIM-20 | 0.8 | perf | ✅ verified | 🟢 high | HAS-07 | §3.3 | Register 'PERF_CYCLES' at 0x02c matches spec. | [MAS §3.3] Performance counters: `PERF_BYTES_IN` **0x020**, `PERF_BYTES_OUT` **0x024**, `PERF_JOBS` **0x028**, `PERF_CYCLES` **0x02C**, `PERF_HITS` **0 |
| CLAIM-21 | 0.8 | perf | ✅ verified | 🟢 high | HAS-05 | §3.3 | Register 'PERF_HITS' at 0x030 matches spec. | [MAS §3.3] Performance counters: `PERF_BYTES_IN` **0x020**, `PERF_BYTES_OUT` **0x024**, `PERF_JOBS` **0x028**, `PERF_CYCLES` **0x02C**, `PERF_HITS` **0 |
| CLAIM-22 | 0.8 | perf | ❌ missing | 🟠 medium | HAS-07 | §3.3 | Register 'PERF_MISS' (required offset 0x034) is not implemented in RTL. | [MAS §3.3] Performance counters: `PERF_BYTES_IN` **0x020**, `PERF_BYTES_OUT` **0x024**, `PERF_JOBS` **0x028**, `PERF_CYCLES` **0x02C**, `PERF_HITS` **0 |
| CLAIM-23 | 0.8 | perf | ✅ verified | 🟢 high | HAS-04 | §3.3 | Register 'ARB_GRANTS' at 0x038 matches spec. | [MAS §3.3] Performance counters: `PERF_BYTES_IN` **0x020**, `PERF_BYTES_OUT` **0x024**, `PERF_JOBS` **0x028**, `PERF_CYCLES` **0x02C**, `PERF_HITS` **0 |
| CLAIM-24 | 0.8 | debug | ✅ verified | 🟢 high | HAS-08 | §3.6 | Register 'DBG_CTRL' at 0x060 matches spec. | [MAS §3.6] Debug: `DBG_CTRL` **0x060**, `DBG_STATE` **0x064**, `DBG_OBS_SEL` **0x068**, `DBG_TRACE` **0x06C**. |
| CLAIM-25 | 0.8 | debug | ✅ verified | 🟢 high | HAS-08 | §3.6 | Register 'DBG_STATE' at 0x064 matches spec. | [MAS §3.6] Debug: `DBG_CTRL` **0x060**, `DBG_STATE` **0x064**, `DBG_OBS_SEL` **0x068**, `DBG_TRACE` **0x06C**. |
| CLAIM-26 | 0.8 | debug | ✅ verified | 🟢 high | HAS-08 | §3.6 | Register 'DBG_OBS_SEL' at 0x068 matches spec. | [MAS §3.6] Debug: `DBG_CTRL` **0x060**, `DBG_STATE` **0x064**, `DBG_OBS_SEL` **0x068**, `DBG_TRACE` **0x06C**. |
| CLAIM-27 | 0.8 | debug | ✅ verified | 🟢 high | HAS-08 | §3.6 | Register 'DBG_TRACE' at 0x06c matches spec. | [MAS §3.6] Debug: `DBG_CTRL` **0x060**, `DBG_STATE` **0x064**, `DBG_OBS_SEL` **0x068**, `DBG_TRACE` **0x06C**. |
| CLAIM-28 | 0.8 | dft | ✅ verified | 🟢 high | HAS-08 | §5.1 | 'scan_en' width 1 bits matches spec. | [MAS §5.1] A scan-enable input `scan_en` (1 bit) shall control scan-based DFT. |
| RTL-EXTRA | 0.8 | debug | 🟡 undocumented | 🟠 medium | — | n/a | RTL register ADDR_DBG_SCRATCH at 0x070 has no matching spec claim. Context: DEC-03 (meeting, 2026-08-20) notes it as a known temporary hook. · backing: DEC-03 | [DECISION DEC-03] Bring-up sync meeting. A DBG_SCRATCH register may be added temporarily at 0x070 to park observation-bus state during silicon bring-up. It is explicitly NOT part |

## 5. Decisions Considered

| id | date | authority | type | amends | note |
| --- | --- | --- | --- | --- | --- |
| DEC-03 | 2026-08-20 | meeting | discussion | none | DBG_SCRATCH.note=temporary |
| DEC-01 | 2026-08-28 | arch_review | decision | none | m_axi_wdata.width_bits=64 |
| DEC-02 | 2026-09-02 | design_review | decision | MAS §3.5 | INT_STATUS.offset=0x058 |

## 6. Simulation Checks

| Check | Status | Detail |
| --- | --- | --- |
| elaboration | skipped | iverilog not found on PATH; static checks only. Install Icarus Verilog to enable simulation-based confirmation. |
