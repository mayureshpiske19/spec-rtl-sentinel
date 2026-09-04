# Spec-RTL Sentinel — Design Intent Ledger

**Agentic RAG that checks RTL against the *entire chain of design intent* — HAS → MAS → decisions → RTL — and reports where the as-built silicon drifts from the as-agreed intent.**

---

## The problem

RTL is implemented from a **MAS** (Micro-Architecture Spec), which refines a
**HAS** (High-level Architecture Spec). But the *real* decisions — "we widened
the bus to 64-bit", "STATUS moved to 0x08" — live in **architecture reviews,
design reviews, and meeting notes**, and rarely make it back into the formal
specs. Over time, HAS, MAS, decisions, and RTL all drift apart. Manual
clause-by-clause review across all these sources is slow, inconsistent, and the
first thing dropped under schedule pressure — and a missed mismatch can become a
functional bug or a security hole in silicon.

## What it does

Sentinel ingests **every layer of design authority** into a RAG store and
grounds RTL against all of them at once:

```
   HAS   (performance / concept — the "why")
     |  refined by
   MAS   (micro-architecture detail — the "what")
     |  amended by
   Decisions / reviews / meetings (the "as-agreed")
     |  implemented as
   RTL   (the "as-built")
```

![Spec-RTL Sentinel architecture](docs/architecture.png)

It produces a **layered drift report**:

1. **Traceability** HAS -> MAS -> RTL, flagging **gaps** (top-level intent that
   was never detailed in the MAS, so it can't be verified).
2. **Spec conflicts** — where a review/decision contradicts the MAS, resolved by
   **authority + recency** (arch review > design review > meeting > spec).
3. **Clause-by-clause findings** with a full **evidence chain**: the HAS
   requirement, the spec clause, the decision that backs or amended it, a
   **confidence** level, and the grounded source text.

**Anti-hallucination by design:** every finding cites the exact source (HAS/MAS
clause or decision id) it is grounded in. Nothing is asserted without a
reference retrieved from the knowledge store.

## Why it's different

Traditional lint/spec-check tools compare RTL to **one** document. Sentinel is
the only one that indexes the **tribal layer** — the decisions in reviews and
chats — and reconciles *source-vs-source* conflicts before even looking at the
RTL. That's drift no single-document checker can catch.

## The agents

| Agent | Role |
| --- | --- |
| **HAS Parser** | Extracts top-level requirements (performance / concept / security) |
| **Claim Extractor** | Turns the MAS into testable claims, each traced to a HAS requirement |
| **Decision Ingest** | Ingests reviews/meetings with authority + date metadata |
| **Authority Resolver** | Reconciles spec vs decisions by authority + recency; flags conflicts |
| **Traceability** | Checks HAS -> MAS coverage; rolls RTL status up to each HAS requirement |
| **RTL Scanner** | Parses SystemVerilog into structured facts (port widths, CSR map, FSM) |
| **Mapper / Diff** | Diffs resolved claims vs RTL; classifies + attaches the evidence chain |
| **Sim Checker** | Confirms dynamic claims via simulation (Icarus Verilog) |
| **Report Generator** | Emits the layered Design Intent Ledger report |

All grounded in a dependency-free **RAG store** (`src/knowledge/rag_store.py`).

## Quick start

```bash
python examples/run_demo.py
```

Runs **fully offline** (no API keys) over the bundled synthetic HAS + MAS +
decisions + RTL. The sample RTL contains deliberately injected drift, and the
decisions include one **reinforcing** review (64-bit bus), one **conflicting**
review (STATUS offset), and one **contextual** note (temporary debug register) —
so you see the tool catch drift, resolve a spec conflict, flag a traceability
gap, and explain an undocumented register.

Two reports are written on every run:

- `reports/drift_report.md` — the markdown ledger
- `reports/drift_report.html` — a **self-contained, styled dashboard** (no
  external resources; opens locally or shares as a single file)

## The dashboard UI

![Spec-RTL Sentinel drift-report dashboard](docs/ui_screenshot.png)

The HTML report renders milestone gate cards, summary chips, the HAS→MAS→RTL
traceability table, resolved spec conflicts, and a **milestone-filterable**
clause-by-clause findings table — each finding citing its exact source. It
adapts to light/dark theme automatically. A rendered sample lives at
[`docs/sample_drift_report.html`](docs/sample_drift_report.html).

### What the demo catches

- **Drift (high confidence)** — RTL bus is 32-bit; MAS *and* the Aug-12 arch review require 64-bit.
- **Missing + conflict (review)** — STATUS register absent; MAS says 0x04 but the Aug-25 design review relocated it to 0x08.
- **Missing** — FSM lacks the `ERROR` state required by HAS-04 / MAS 4.1.
- **Undocumented (explained)** — a DEBUG register not in any spec, but a July-30 meeting flagged it as a temporary bring-up hook.
- **Traceability gap** — HAS-05 (single-cycle read latency) was never refined into a MAS claim.

## Milestone-based checking

HAS is the **golden reference** — it is never flagged. MAS and RTL are checked
against it **milestone by milestone**, where each milestone only checks the
parameters relevant at that stage (cumulatively):

| Milestone | Scope (what gets checked) |
| --- | --- |
| **0.1** | Boundary — interface ports + CSR registers |
| **0.5** | + Functional behavior (FSM, datapath) |
| **0.8** | + Errors, DFT, perf counters, debug |
| **1.0** | Overall / integration — everything |

Every run prints a **milestone gate table** — is the RTL 0.1-clean? 0.5-clean? —
and you can scope a run to one milestone:

```bash
python examples/run_demo.py --milestone 0.1   # only boundary + CSR
python examples/run_demo.py --milestone 0.5   # + functional
python examples/run_demo.py                    # 1.0 (everything, default)
```

Gates are cumulative: a milestone passes only when every in-scope claim is
verified with no traceability gap. In the demo, **all four gates fail** — 0.1
already fails on the bus-width drift and the missing STATUS register, so the RTL
isn't even 0.1-ready yet.

## RAG / LLM upgrade path

The demo uses deterministic extraction and an offline TF-cosine RAG index so
it's reproducible with zero setup. Documented hooks upgrade it to a full system:

1. **RAG store** (`src/knowledge/rag_store.py`) — swap the TF-cosine index for
   Azure OpenAI embeddings + ChromaDB / FAISS. Public API is unchanged.
2. **Claim Extractor** (`src/agents/claim_extractor.py`) — `_extract_with_llm()`
   extracts claims (and their HAS trace) from free-form prose via Azure OpenAI.
3. **RTL Scanner** (`src/agents/rtl_scanner.py`) — swap the regex parser for a
   real HDL parser (`pyslang` / `pyverilog`) for full-design scale.
4. **Decision Ingest** — point it at live sources (Teams, ADO review comments,
   meeting transcripts) instead of files.

## Project layout

```
data/has/          synthetic HAS (top-level requirements)
data/specs/        synthetic MAS (testable claims, traced to HAS)
data/decisions/    synthetic reviews/meetings (authority + date)
data/rtl/          synthetic SystemVerilog with injected drift
src/knowledge/     multi-source RAG store
src/agents/        the agents (parse, ingest, resolve, trace, scan, map, sim)
src/milestones.py    milestone scope + cumulative gate logic
src/orchestrator.py  end-to-end pipeline
src/report.py        layered markdown report generator
src/report_html.py   self-contained HTML dashboard generator
examples/run_demo.py
```

## Data note

All bundled HAS/MAS/decision/RTL content is **synthetic** and contains no
confidential material. Do not commit proprietary specs, review notes, or RTL to
this repository.

## License

MIT — see [LICENSE](LICENSE).
