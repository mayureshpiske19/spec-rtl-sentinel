# High-level Architecture Specification (HAS) — Zephyr LZ Compression Offload Sub-System (COSS)

> Reference SoC sub-system. Synthetic specification authored for the Spec-RTL
> Sentinel demo — no proprietary or confidential content.
>
> The HAS captures **top-level intent**: the feature set, block partitioning,
> external interfaces, and functional / performance / error / debug
> requirements — the *what* and the *why*. Signal-level detail and the register
> map live in the MAS.

## 1. Overview

The Zephyr COSS is a firmware-driven AXI sub-system that accepts a compression
job (a descriptor plus a pointer to uncompressed data), compresses the data in
hardware with an LZ77-family algorithm (optionally DEFLATE-class Huffman), and
writes the compressed result back to memory. It models the class of IP found in
storage controllers, SmartNICs, and datacenter compression accelerators.

## 2. Interfaces

- **§2.1** The data/memory path is a full **AXI4** interconnect shared by three
  masters (Input DMA, Output DMA, LZ accelerator); the memory data width is
  **64-bit**.
- **§2.2** Firmware configures the sub-system over an **AXI4-Lite** CSR
  subordinate (single-beat, 32-bit registers).

## 3. Compression & Control

- **§3.1** An **LZ77** sliding-window engine (match finder + literal/copy token
  encoder, optional Huffman) performs the compression.
- **§3.2** A **job-sequencer FSM** consumes descriptors from a ring, drives the
  DMAs and accelerator, and writes back per-job results.
- **§3.3** The AXI arbiter supports **round-robin** and firmware-selectable
  **priority** modes.
- **§3.4** An **L2 cache** holds the LZ history window and job descriptors to
  cut DRAM latency.

## 4. Reliability, Performance & Debug

- **§4.1** Errors are **detected, classified, captured with context, reported**
  via the ERROR register + interrupt, and recovered by firmware.
- **§4.2** **Performance counters** expose bytes in/out, job count, active
  cycles, and cache hits/misses for the live dashboard.
- **§4.3** **Debug facilities** provide FSM/job visibility, a job trace buffer,
  breakpoints, and scan-based **DFT** provisions.

## 5. Portability (stretch)

- **§5.1** An optional **multi-clock CDC** bridging mode is noted for
  deployments where the CSR and datapath run on separate clocks. (Stretch goal;
  the reference design is single-clock.)

---

## Requirements (machine-readable)

The Sentinel HAS parser consumes this table. Each row is a top-level requirement
the MAS is expected to refine. The `category` column places each requirement in
a maturity milestone (boundary/csr = 0.1, functional = 0.5,
error/dft/perf/debug = 0.8, integration = 1.0).

| id | kind | requirement | category | source |
| --- | --- | --- | --- | --- |
| HAS-01 | interface | AXI4 multi-master datapath with a 64-bit memory data width | boundary | §2.1 |
| HAS-02 | interface | Firmware CSR / job-descriptor interface over AXI4-Lite | csr | §2.2 |
| HAS-03 | function | LZ77 compression engine driven by a job-sequencer FSM | functional | §3.2 |
| HAS-04 | function | QoS arbiter with round-robin and selectable priority modes | functional | §3.3 |
| HAS-05 | function | L2 cache for the history window and job descriptors | functional | §3.4 |
| HAS-06 | reliability | Classified error detection, capture, and reporting | error | §4.1 |
| HAS-07 | performance | Performance counters (bytes, jobs, cycles, cache hits/misses) | perf | §4.2 |
| HAS-08 | debug | Debug/observability: FSM/job state, trace, breakpoints, DFT | debug | §4.3 |
| HAS-09 | portability | Optional multi-clock CDC bridging between CSR and datapath | integration | §5.1 |
