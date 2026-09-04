# Micro-Architecture Specification (MAS) — Zephyr LZ Compression Offload Sub-System (COSS)

> Synthetic specification authored for the Spec-RTL Sentinel demo.
> It contains no proprietary or confidential content. Implementation companion
> to the Zephyr COSS HAS.

## 1. Overview

Three masters (Input DMA, Output DMA, LZ accelerator) drive an AXI interconnect
into a write-back L2 cache and memory controller. The control plane — an
AXI4-Lite CSR register file and a job-sequencer FSM — consumes job descriptors,
drives the datapath, and reports results, performance, errors, and debug state.

## 2. Interface

- **§2.1** The accelerator memory write-data bus `m_axi_wdata` shall be
  **64 bits** wide to match the SoC data path.
- **§2.2** The CSR block shall use an **active-low**, asynchronous-assert /
  synchronous-release reset named `aresetn`.
- **§2.3** The CSR address bus `s_axi_awaddr` shall be **12 bits** wide (covers
  the 0x000–0x06C register space).

## 3. Register Map

Offsets are byte offsets from the COSS CSR base. All registers are 32-bit.

- **§3.1** Control/config/status: `CTRL` **0x000**, `CFG` **0x004**,
  `STATUS` **0x008**.
- **§3.2** Job ring: `RING_BASE` **0x010**, `RING_HEAD` **0x014**,
  `RING_TAIL` **0x018**, `RING_SIZE` **0x01C**.
- **§3.3** Performance counters: `PERF_BYTES_IN` **0x020**,
  `PERF_BYTES_OUT` **0x024**, `PERF_JOBS` **0x028**, `PERF_CYCLES` **0x02C**,
  `PERF_HITS` **0x030**, `PERF_MISS` **0x034**, `ARB_GRANTS` **0x038**.
- **§3.4** Error: `ERROR` **0x040** (W1C), `ERR_ADDR` **0x044**,
  `ERR_INFO` **0x048**.
- **§3.5** Interrupt: `INT_EN` **0x050**, `INT_STATUS` **0x054** (W1C).
- **§3.6** Debug: `DBG_CTRL` **0x060**, `DBG_STATE` **0x064**,
  `DBG_OBS_SEL` **0x068**, `DBG_TRACE` **0x06C**.

## 4. Control FSM

- **§4.1** The job-sequencer FSM `control_fsm` shall implement the states
  **IDLE, FETCH_JOB, LOAD_DATA, COMPRESS, WRITE_OUT, DONE**.

## 5. Test & DFT

- **§5.1** A scan-enable input `scan_en` (1 bit) shall control scan-based DFT.

---

## Testable Claims

The Sentinel Claim Extractor consumes this table. Each row is an independently
verifiable claim against the RTL. The `category` column places the claim in a
maturity milestone (boundary/csr = 0.1, functional = 0.5,
error/dft/perf/debug = 0.8); the `traces` column links the claim up to the HAS
requirement it refines (top-down: HAS → MAS → RTL).

| id | type | target | property | expected | category | traces | source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CLAIM-01 | signal_width | m_axi_wdata | width_bits | 64 | boundary | HAS-01 | §2.1 |
| CLAIM-02 | reset_polarity | aresetn | active | low | boundary | HAS-01 | §2.2 |
| CLAIM-03 | signal_width | s_axi_awaddr | width_bits | 12 | boundary | HAS-02 | §2.3 |
| CLAIM-04 | register | CTRL | offset | 0x000 | csr | HAS-02 | §3.1 |
| CLAIM-05 | register | CFG | offset | 0x004 | csr | HAS-02 | §3.1 |
| CLAIM-06 | register | STATUS | offset | 0x008 | csr | HAS-02 | §3.1 |
| CLAIM-07 | register | RING_BASE | offset | 0x010 | csr | HAS-02 | §3.2 |
| CLAIM-08 | register | RING_HEAD | offset | 0x014 | csr | HAS-02 | §3.2 |
| CLAIM-09 | register | RING_TAIL | offset | 0x018 | csr | HAS-02 | §3.2 |
| CLAIM-10 | register | RING_SIZE | offset | 0x01C | csr | HAS-02 | §3.2 |
| CLAIM-11 | register | INT_EN | offset | 0x050 | csr | HAS-02 | §3.5 |
| CLAIM-12 | register | INT_STATUS | offset | 0x054 | csr | HAS-02 | §3.5 |
| CLAIM-13 | fsm_states | control_fsm | states | IDLE,FETCH_JOB,LOAD_DATA,COMPRESS,WRITE_OUT,DONE | functional | HAS-03 | §4.1 |
| CLAIM-14 | register | ERROR | offset | 0x040 | error | HAS-06 | §3.4 |
| CLAIM-15 | register | ERR_ADDR | offset | 0x044 | error | HAS-06 | §3.4 |
| CLAIM-16 | register | ERR_INFO | offset | 0x048 | error | HAS-06 | §3.4 |
| CLAIM-17 | register | PERF_BYTES_IN | offset | 0x020 | perf | HAS-07 | §3.3 |
| CLAIM-18 | register | PERF_BYTES_OUT | offset | 0x024 | perf | HAS-07 | §3.3 |
| CLAIM-19 | register | PERF_JOBS | offset | 0x028 | perf | HAS-07 | §3.3 |
| CLAIM-20 | register | PERF_CYCLES | offset | 0x02C | perf | HAS-07 | §3.3 |
| CLAIM-21 | register | PERF_HITS | offset | 0x030 | perf | HAS-05 | §3.3 |
| CLAIM-22 | register | PERF_MISS | offset | 0x034 | perf | HAS-07 | §3.3 |
| CLAIM-23 | register | ARB_GRANTS | offset | 0x038 | perf | HAS-04 | §3.3 |
| CLAIM-24 | register | DBG_CTRL | offset | 0x060 | debug | HAS-08 | §3.6 |
| CLAIM-25 | register | DBG_STATE | offset | 0x064 | debug | HAS-08 | §3.6 |
| CLAIM-26 | register | DBG_OBS_SEL | offset | 0x068 | debug | HAS-08 | §3.6 |
| CLAIM-27 | register | DBG_TRACE | offset | 0x06C | debug | HAS-08 | §3.6 |
| CLAIM-28 | signal_width | scan_en | width_bits | 1 | dft | HAS-08 | §5.1 |
