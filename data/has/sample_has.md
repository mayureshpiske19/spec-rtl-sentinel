# High-level Architecture Specification (HAS) — Sample CIU Block

> **Synthetic** document for the Sentinel demo. No confidential content.
>
> The HAS captures **top-level intent**: performance targets, concepts, and
> architectural decisions — the *why*. It does not describe register-level
> detail (that is the MAS's job).

## 1. Concept

- **§1.2** The CIU control/status register (CSR) block is exposed to the SoC
  fabric through an **AXI4 subordinate** interface.

## 2. Performance

- **§2.1** The fabric data path is **64-bit** wide to meet target throughput.
- **§2.3** CSR reads shall complete with **single-cycle** latency.

## 3. Security

- **§3.4** A secret boot key (**BEK**) is provisioned by the security engine
  into a dedicated register during initialization.

## 4. Control Concept

- **§4.0** Block control is managed by a finite state machine that includes
  **explicit error handling**.

---

## Requirements (machine-readable)

The Sentinel HAS parser consumes this table. Each row is a top-level
requirement that the MAS is expected to refine.

| id | kind | requirement | source |
| --- | --- | --- | --- |
| HAS-01 | concept | CSR block exposed to SoC fabric via an AXI4 subordinate interface | §1.2 |
| HAS-02 | performance | Fabric data path is 64-bit wide for target throughput | §2.1 |
| HAS-03 | security | Secret boot key (BEK) provisioned by security engine into a dedicated register | §3.4 |
| HAS-04 | concept | Block control managed by an FSM with explicit error handling | §4.0 |
| HAS-05 | performance | CSR reads complete with single-cycle latency | §2.3 |
