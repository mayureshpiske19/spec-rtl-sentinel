---
id: DEC-01
date: 2026-08-28
authority: arch_review
type: decision
amends: none
target: m_axi_wdata
property: width_bits
value: 64
---
Architecture review (COSS datapath). Confirmed the accelerator memory data path
stays 64-bit to sustain the ~0.5 GB/s throughput target; no narrowing to 32-bit.
This reaffirms HAS §2.1 and MAS §2.1 — the 64-bit width is a hard requirement.
