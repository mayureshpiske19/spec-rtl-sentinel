---
id: DEC-01
date: 2026-08-12
authority: arch_review
type: decision
amends: none
target: s_axi_wdata
property: width_bits
value: 64
---
Architecture review (owner: arch lead). Confirmed the CSR/fetch datapath is
widened to 64-bit to match the SoC fabric. No width converter will be added;
the RTL datapath is to be updated directly. This reaffirms HAS §2.1 and MAS
§2.1 — the 64-bit width is a hard requirement, not negotiable.
