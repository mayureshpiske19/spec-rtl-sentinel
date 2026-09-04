"""
Decision Ingest Agent
---------------------
Ingests the "as-agreed" layer — architecture reviews, design reviews, and
meeting/discussion notes — that amend or reinforce the formal specs. This is
the layer no traditional lint/spec tool captures: the real decisions that live
in reviews and chats.

Each decision file has a YAML-ish front-matter block:

    ---
    id: DEC-01
    date: 2026-08-12
    authority: arch_review        # arch_review | design_review | meeting
    type: decision                # decision | discussion
    amends: MAS §3.2 | none
    target: STATUS                # signal / register / fsm the decision touches
    property: offset              # width_bits | offset | active | states | note
    value: 0x08
    ---
    <free-form rationale text>

Structured fields drive the authority resolver; the rationale text is ingested
into the RAG store for grounded citation.
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..knowledge.rag_store import RagStore, LAYER_DECISION

# Authority ranking used by the resolver (higher overrides lower).
AUTHORITY_RANK = {
    "arch_review": 3,
    "design_review": 2,
    "meeting": 1,
    "spec": 0,
}


@dataclass
class Decision:
    id: str
    date: str
    authority: str
    type: str
    amends: str
    target: str
    property: str
    value: str
    rationale: str = ""

    @property
    def rank(self) -> int:
        return AUTHORITY_RANK.get(self.authority, 0)

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["rank"] = self.rank
        return d


def ingest_decisions(decisions_dir: str,
                     store: Optional[RagStore] = None) -> List[Decision]:
    out: List[Decision] = []
    for path in sorted(glob.glob(os.path.join(decisions_dir, "*.md"))):
        dec = _parse_one(path)
        if dec:
            out.append(dec)
            if store is not None:
                store.add(doc_id=dec.id, layer=LAYER_DECISION, section=dec.id,
                          text=dec.rationale,
                          meta={"authority": dec.authority, "date": dec.date,
                                "target": dec.target, "property": dec.property,
                                "value": dec.value})
    return out


def _parse_one(path: str) -> Optional[Decision]:
    text = open(path, "r", encoding="utf-8").read()
    m = re.match(r"\s*---\s*(.*?)\s*---\s*(.*)", text, re.DOTALL)
    if not m:
        return None
    header, body = m.group(1), m.group(2).strip()
    fields: Dict[str, str] = {}
    for line in header.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return Decision(
        id=fields.get("id", os.path.basename(path)),
        date=fields.get("date", ""),
        authority=fields.get("authority", "meeting"),
        type=fields.get("type", "discussion"),
        amends=fields.get("amends", "none"),
        target=fields.get("target", ""),
        property=fields.get("property", ""),
        value=fields.get("value", ""),
        rationale=" ".join(body.split()),
    )
