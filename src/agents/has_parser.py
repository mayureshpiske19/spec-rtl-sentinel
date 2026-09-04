"""
HAS Parser Agent
----------------
Parses the High-level Architecture Specification into top-level requirements
(the *why*: performance, concept, security). Each requirement is expected to be
refined by one or more MAS claims further down the hierarchy.

Also ingests the HAS prose into the RAG store for grounded citation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from ..knowledge.rag_store import RagStore, LAYER_HAS


@dataclass
class HASRequirement:
    id: str
    kind: str          # concept | performance | security
    requirement: str
    category: str      # boundary | csr | functional | error | dft | perf | debug
    source: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def parse_has(has_path: str, store: Optional[RagStore] = None) -> List[HASRequirement]:
    text = open(has_path, "r", encoding="utf-8").read()

    if store is not None:
        _ingest_sections(text, store, has_path)

    reqs: List[HASRequirement] = []
    rows = re.findall(r"^\|\s*(HAS-\d+)\s*\|(.+)\|\s*$", text, re.MULTILINE)
    for rid, rest in rows:
        cols = [c.strip() for c in rest.split("|")]
        # cols = [kind, requirement, category, source]
        if len(cols) >= 4:
            reqs.append(HASRequirement(rid, cols[0], cols[1], cols[2], cols[3]))
        elif len(cols) >= 3:
            reqs.append(HASRequirement(rid, cols[0], cols[1], "functional", cols[2]))
    return reqs


def _ingest_sections(text: str, store: RagStore, path: str) -> None:
    # Ingest each "§x.y ... " bullet as a citeable chunk.
    for m in re.finditer(r"\*\*(§[\d.]+)\*\*\s*(.+?)(?=\n\n|\n- |\Z)",
                         text, re.DOTALL):
        section, body = m.group(1), " ".join(m.group(2).split())
        store.add(doc_id="HAS", layer=LAYER_HAS, section=section, text=body)
