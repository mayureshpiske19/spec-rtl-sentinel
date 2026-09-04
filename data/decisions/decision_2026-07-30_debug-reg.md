---
id: DEC-03
date: 2026-07-30
authority: meeting
type: discussion
amends: none
target: DEBUG
property: note
value: temporary
---
Bring-up sync meeting. A DEBUG_SCRATCH register may be added temporarily at
0x20 to aid silicon bring-up. It is explicitly NOT part of the HAS or MAS and
must be removed before tapeout. Recorded here so reviewers know any DEBUG
register found in RTL is a known temporary hook, not undocumented intent.
