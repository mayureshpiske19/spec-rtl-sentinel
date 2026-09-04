# Spec-RTL Sentinel — Demo Video Narration
### Script for an AI presenter/avatar · Target length ≈ 2:00 (hard cap 2:00)

> Paste each block into your AI-voice tool. Timings are guides. Words in
> *(parentheses/italics)* are on-screen action cues — do **not** read them aloud.
> Total spoken words ≈ 300 (comfortable at ~150 wpm for 2 minutes).

---

## [0:00–0:15] — The Hook
*(On screen: title slide — "Spec-RTL Sentinel: Design Intent Auditor")*

"Every chip begins as intent — a high-level spec, refined into a
micro-architecture spec, then implemented as RTL. But intent drifts. A bus
width changes in a review. A register moves in a meeting. And those decisions
almost never make it back into the spec. When the RTL no longer matches the
intent, that's how bugs — and security holes — reach silicon."

---

## [0:15–0:35] — The Problem, Sharpened
*(On screen: the four-layer diagram — HAS → MAS → Decisions → RTL)*

"Today, catching that drift means an engineer manually cross-checking the RTL
against the HAS, the MAS, and a scattered trail of review notes — clause by
clause. It's slow, it's inconsistent, and it's the first thing dropped under
schedule pressure. Meet Spec-RTL Sentinel — a multi-agent system that does it
automatically."

---

## [0:35–0:55] — How It Works
*(On screen: architecture diagram; highlight each agent as named)*

"Sentinel ingests every layer of design authority into a RAG knowledge store —
the high-level spec, the micro-architecture spec, and the real decisions from
reviews and meetings. Its agents extract testable claims, scan the RTL
structure, and an authority resolver reconciles conflicts by seniority and
recency — a newer design review outranks a stale spec."

---

## [0:55–1:35] — Live Demo (the money shot)
*(On screen: terminal — run `python run_demo.py`, then the report)*

"Here it is on a real example — a hardware compression accelerator, the Zephyr
COSS. One command… and in seconds Sentinel produces a clause-by-clause drift
report across twenty-eight spec claims. Watch what it catches. The accelerator's
memory bus is thirty-two bits — but the spec *and* an architecture review both
demand sixty-four. That's a high-confidence drift. The control FSM is missing
its write-out state. A performance counter the spec requires isn't implemented.
And the interrupt-status register? The spec says one offset, but a later design
review moved it — Sentinel flags the conflict, resolves it by authority, and
confirms the RTL actually followed the review. There's even a debug register in
the RTL that no spec mentions — and Sentinel finds the meeting note that
explains it."

---

## [1:35–1:48] — Milestone Gates
*(On screen: the milestone gate table — 0.1 / 0.5 / 0.8 / 1.0, all FAIL)*

"And it grades maturity by milestone. The HAS is golden; the MAS and RTL are
checked against it stage by stage. At zero-point-one we only check the interface
— ports and registers. At zero-point-five, functional behavior. At
zero-point-eight, errors, DFT, and performance. Here the design fails its very
first gate on the bus-width drift — it isn't even zero-point-one ready — and a
top-level clock-crossing requirement was never even written into the MAS."

---

## [1:48–1:57] — Why It's Different
*(On screen: highlight "every finding cites its source")*

"What makes this unique? Sentinel is the only tool that indexes the *tribal
layer* — the decisions buried in reviews and chats — and reconciles them before
ever touching the RTL. And every finding cites its exact source. No
hallucinations — just grounded, traceable evidence."

---

## [1:57–2:00] — Close
*(On screen: logo + GitHub URL)*

"Spec-RTL Sentinel. Catching spec-to-silicon drift before it becomes a bug."

---

### Delivery notes for the AI voice
- Tone: confident, crisp, a touch of urgency on the problem, pride on the demo.
- Pace: ~150 wpm. If you run long, trim the demo section first (drop the debug-register line).
- Emphasize the numbers: "thirty-two bits", "sixty-four", "offset four … to eight".
- Pause ~0.5s before "Watch what it catches" and before the closing line.
