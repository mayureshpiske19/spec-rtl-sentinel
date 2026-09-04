---
id: DEC-03
date: 2026-08-20
authority: meeting
type: discussion
amends: none
target: DBG_SCRATCH
property: note
value: temporary
---
Bring-up sync meeting. A DBG_SCRATCH register may be added temporarily at 0x070
to park observation-bus state during silicon bring-up. It is explicitly NOT part
of the HAS or MAS and must be removed before tapeout. Recorded here so reviewers
know any DBG_SCRATCH register found in RTL is a known temporary hook, not
undocumented intent.
