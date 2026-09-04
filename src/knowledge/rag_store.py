"""
Multi-source RAG store
----------------------
A dependency-free, offline retrieval store that ingests every layer of the
design-intent hierarchy — HAS, MAS, and decisions/reviews/meetings — as
citeable chunks, and supports keyword/TF-cosine retrieval.

This is what makes Sentinel a *grounded* system: every finding can pull the
exact source text (with a layer + citation) that supports it, across all
documents — not just one spec.

Upgrade path (documented hook): replace the in-memory TF-cosine index in
`retrieve()` with real embeddings + a vector DB (Azure OpenAI embeddings +
ChromaDB / FAISS). The `Chunk` shape and public API stay identical, so nothing
downstream changes.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Layer authority ranking (higher = more authoritative as a *source of intent*).
LAYER_HAS = "HAS"
LAYER_MAS = "MAS"
LAYER_DECISION = "DECISION"

_STOPWORDS = {
    "the", "a", "an", "is", "are", "to", "of", "and", "or", "in", "on", "for",
    "by", "with", "shall", "be", "into", "that", "this", "it", "as", "at",
    "from", "not", "no", "has", "have", "will", "which", "each", "row",
}


def _tokenize(text: str) -> List[str]:
    toks = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return [t for t in toks if t not in _STOPWORDS and len(t) > 1]


@dataclass
class Chunk:
    doc_id: str
    layer: str            # HAS | MAS | DECISION
    section: str          # e.g. "§2.1" or "DEC-01"
    text: str
    meta: Dict[str, str] = field(default_factory=dict)
    _tf: Counter = field(default_factory=Counter, repr=False)

    def citation(self) -> str:
        return f"[{self.layer} {self.section}]"


class RagStore:
    def __init__(self) -> None:
        self.chunks: List[Chunk] = []

    def add(self, doc_id: str, layer: str, section: str, text: str,
            meta: Optional[Dict[str, str]] = None) -> Chunk:
        c = Chunk(doc_id=doc_id, layer=layer, section=section,
                  text=text.strip(), meta=meta or {})
        c._tf = Counter(_tokenize(text))
        self.chunks.append(c)
        return c

    def retrieve(self, query: str, k: int = 3,
                 layer: Optional[str] = None) -> List[Chunk]:
        q = Counter(_tokenize(query))
        if not q:
            return []
        scored = []
        for c in self.chunks:
            if layer and c.layer != layer:
                continue
            score = self._cosine(q, c._tf)
            if score > 0:
                scored.append((score, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k]]

    def get(self, layer: str, section: str) -> Optional[Chunk]:
        for c in self.chunks:
            if c.layer == layer and c.section == section:
                return c
        return None

    @staticmethod
    def _cosine(a: Counter, b: Counter) -> float:
        common = set(a) & set(b)
        if not common:
            return 0.0
        dot = sum(a[t] * b[t] for t in common)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def stats(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for c in self.chunks:
            out[c.layer] = out.get(c.layer, 0) + 1
        return out
