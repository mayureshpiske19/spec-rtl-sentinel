---
id: DEC-02
date: 2026-08-25
authority: design_review
type: decision
amends: MAS §3.2
target: STATUS
property: offset
value: 0x08
---
Design review. The STATUS register is relocated from 0x04 to 0x08 for 8-byte
alignment with the new 64-bit datapath. The MAS still lists 0x04 and has NOT
yet been updated (action pending on the spec owner). Until the MAS is revised,
this is the authoritative offset.
