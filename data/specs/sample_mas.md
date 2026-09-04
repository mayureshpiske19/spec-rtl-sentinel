# Micro-Architecture Specification (MAS) — Sample CIU AXI Subordinate CSR Block

> This is a **synthetic** spec written for the Spec-RTL Sentinel demo.
> It contains no Microsoft-confidential content.

## 1. Overview

The CIU AXI Subordinate block exposes control/status registers (CSRs) to the
SoC fabric over an AXI4 subordinate interface and drives an internal control
FSM. This document defines the register map, interface widths, reset behavior,
and FSM states that the RTL must implement faithfully.

## 2. Interface

- **§2.1** The CSR write-data bus `s_axi_wdata` shall be **64 bits** wide to
  match the SSS fabric data width.
- **§2.2** The block shall use an **active-low** asynchronous reset named
  `aresetn`.

## 3. Register Map

- **§3.1** `CTRL` register at byte offset **0x00** (read/write), reset value 0x0.
- **§3.2** `STATUS` register at byte offset **0x04** (read-only).
- **§3.3** `BEK_KEY` register at byte offset **0x10** (write-only), written by
  the security engine during initialization.

## 4. Control FSM

- **§4.1** The control FSM `ciu_fsm` shall implement the states
  **IDLE, ACTIVE, ERROR**.

---

## Testable Claims

The following machine-readable table is consumed by the Claim Extractor agent.
Each row is an independently verifiable claim against the RTL. The `traces`
column links the claim up to the HAS requirement it refines (top-down
traceability: HAS → MAS → RTL).

| id | type | target | property | expected | traces | source |
| --- | --- | --- | --- | --- | --- | --- |
| CLAIM-01 | signal_width | s_axi_wdata | width_bits | 64 | HAS-02 | §2.1 |
| CLAIM-02 | reset_polarity | aresetn | active | low | HAS-01 | §2.2 |
| CLAIM-03 | register | CTRL | offset | 0x00 | HAS-04 | §3.1 |
| CLAIM-04 | register | STATUS | offset | 0x04 | HAS-04 | §3.2 |
| CLAIM-05 | register | BEK_KEY | offset | 0x10 | HAS-03 | §3.3 |
| CLAIM-06 | fsm_states | ciu_fsm | states | IDLE,ACTIVE,ERROR | HAS-04 | §4.1 |
