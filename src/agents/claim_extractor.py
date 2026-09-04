"""
Claim Extractor Agent
---------------------
Reads a MAS specification and produces a list of testable claims, each linked
up to the HAS requirement it refines (top-down traceability).

Offline mode (default): parses the machine-readable "Testable Claims" markdown
table in the spec. Deterministic and runnable with no API keys.

LLM mode (hook): set use_llm=True to extract claims from free-form prose using
an Azure OpenAI model. Wire your deployment in _extract_with_llm().
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from ..knowledge.rag_store import RagStore, LAYER_MAS


@dataclass
class Claim:
    id: str
    type: str          # signal_width | reset_polarity | register | fsm_states
    target: str        # signal / register / fsm name
    property: str      # width_bits | active | offset | states
    expected: str      # expected value (string form)
    traces: str        # HAS requirement id this claim refines (e.g. "HAS-02")
    source: str        # spec clause reference, e.g. "§2.1"

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def extract_claims(spec_path: str, use_llm: bool = False,
                   store: Optional[RagStore] = None) -> List[Claim]:
    text = open(spec_path, "r", encoding="utf-8").read()
    if store is not None:
        _ingest_sections(text, store)
    if use_llm:
        return _extract_with_llm(text)
    return _extract_from_table(text)


def _extract_from_table(text: str) -> List[Claim]:
    claims: List[Claim] = []
    rows = re.findall(r"^\|\s*(CLAIM-\d+)\s*\|(.+)\|\s*$", text, re.MULTILINE)
    for cid, rest in rows:
        cols = [c.strip() for c in rest.split("|")]
        # cols = [type, target, property, expected, traces, source]
        if len(cols) >= 6:
            claims.append(Claim(cid, cols[0], cols[1], cols[2], cols[3],
                                cols[4], cols[5]))
        elif len(cols) >= 5:
            # Backward-compatible: no traces column present.
            claims.append(Claim(cid, cols[0], cols[1], cols[2], cols[3],
                                "", cols[4]))
    return claims


def _ingest_sections(text: str, store: RagStore) -> None:
    for m in re.finditer(r"\*\*(§[\d.]+)\*\*\s*(.+?)(?=\n\n|\n- |\Z)",
                         text, re.DOTALL):
        section, body = m.group(1), " ".join(m.group(2).split())
        store.add(doc_id="MAS", layer=LAYER_MAS, section=section, text=body)


def _extract_with_llm(text: str) -> List[Claim]:  # pragma: no cover - hook
    """
    TODO (upgrade path): call Azure OpenAI to extract claims from prose and
    infer the HAS requirement each one traces to. Offline table mode is used
    for the reproducible demo.
    """
    raise NotImplementedError(
        "LLM extraction is a documented upgrade hook. "
        "Run in offline table mode for the demo."
    )
