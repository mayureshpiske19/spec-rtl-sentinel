---
id: DEC-02
date: 2026-09-02
authority: design_review
type: decision
amends: MAS §3.5
target: INT_STATUS
property: offset
value: 0x058
---
Design review (CSR map). INT_STATUS is relocated from 0x054 to 0x058 to leave a
reserved word at 0x054 for a future secondary interrupt-status register. The MAS
still lists 0x054 and has NOT yet been updated (action pending on the spec
owner). Until the MAS is revised, 0x058 is the authoritative offset and the RTL
follows it.
