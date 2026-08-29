# MAS–RTL Sentinel

**Agentic RAG for spec-faithful RTL verification — catching RTL/spec drift before it becomes a silicon bug.**

Microsoft Global Hackathon 2026 · Challenge: *Hack for Customer-Focused AI Wins with Forward Deployed Engineering*

---

## The problem

RTL code and its golden **Micro-Architecture Specification (MAS)** drift apart
over time. Manual clause-by-clause review is slow, inconsistent, and easy to
skip under schedule pressure — and a missed mismatch can become a functional
bug or a security hole in silicon.

## What it does

MAS–RTL Sentinel is a multi-agent system that automatically checks whether RTL
stays faithful to its spec and produces a **clause-by-clause drift report**:
what's verified, what drifted, what's missing, what's undocumented, and what
needs human review.

```
          ┌──────────────────┐
 spec ───▶│ Claim Extractor  │──▶ testable claims
          └──────────────────┘
          ┌──────────────────┐
  rtl ───▶│   RTL Scanner    │──▶ structured facts (ports, regs, FSM)
          └──────────────────┘
                 │  claims + facts
                 ▼
          ┌──────────────────┐
          │   Mapper / Diff  │──▶ verified | drift | missing | undocumented
          └──────────────────┘
                 │
                 ▼
          ┌──────────────────┐      ┌──────────────────┐
          │   Sim Checker    │────▶ │ Report Generator │──▶ drift_report.md
          └──────────────────┘      └──────────────────┘
```

**Anti-hallucination by design:** every finding cites the exact spec clause and
the concrete RTL evidence. Nothing is asserted without a grounded reference.

## Agents

| Agent | Role |
| --- | --- |
| **Claim Extractor** | Turns the MAS into independently testable claims |
| **RTL Scanner** | Parses SystemVerilog into structured facts (port widths, CSR address map, FSM states) |
| **Mapper / Diff** | Matches claims ↔ RTL and classifies each one |
| **Sim Checker** | Confirms dynamic claims via simulation (Icarus Verilog) |
| **Report Generator** | Emits the clause-by-clause drift report |

## Quick start

```bash
pip install -r requirements.txt
python examples/run_demo.py
```

This runs **fully offline** (no API keys) against the bundled synthetic spec and
RTL. The sample RTL contains deliberately injected drifts, so you'll see the
tool catch a bus-width drift, a missing register, a missing FSM state, and an
undocumented register. The report is written to `reports/drift_report.md`.

## RAG / LLM upgrade path

The demo uses deterministic extraction so it's reproducible. Two documented
hooks upgrade it to a full RAG system:

1. **Claim Extractor** (`src/agents/claim_extractor.py`) — `_extract_with_llm()`
   calls Azure OpenAI to extract claims from free-form spec prose.
2. **RTL Scanner** (`src/agents/rtl_scanner.py`) — swap the regex parser for a
   real HDL parser (`pyslang` / `pyverilog`) for full-design scale.

Add a vector store (ChromaDB / FAISS) over the spec corpus to ground claim
extraction and give the Mapper clause-level retrieval.

## ⚠️ Data note

All bundled spec and RTL are **synthetic** and contain no confidential content.
Do not commit proprietary specs or RTL to this repository.

## License

MIT — see [LICENSE](LICENSE).
