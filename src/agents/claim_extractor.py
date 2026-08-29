"""
Claim Extractor Agent
---------------------
Reads a MAS specification and produces a list of testable claims.

Offline mode (default): parses the machine-readable "Testable Claims" markdown
table in the spec. This makes the demo deterministic and runnable with no API
keys.

LLM mode (hook): set use_llm=True to extract claims from free-form prose using
an Azure OpenAI model. Wire your deployment in _extract_with_llm().
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class Claim:
    id: str
    type: str          # signal_width | reset_polarity | register | fsm_states
    target: str        # signal / register / fsm name
    property: str      # width_bits | active | offset | states
    expected: str      # expected value (string form)
    source: str        # spec clause reference, e.g. "§2.1"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "target": self.target,
            "property": self.property,
            "expected": self.expected,
            "source": self.source,
        }


def extract_claims(spec_path: str, use_llm: bool = False) -> List[Claim]:
    text = open(spec_path, "r", encoding="utf-8").read()
    if use_llm:
        return _extract_with_llm(text)
    return _extract_from_table(text)


def _extract_from_table(text: str) -> List[Claim]:
    claims: List[Claim] = []
    rows = re.findall(r"^\|\s*(CLAIM-\d+)\s*\|(.+)\|\s*$", text, re.MULTILINE)
    for cid, rest in rows:
        cols = [c.strip() for c in rest.split("|")]
        # cols = [type, target, property, expected, source]
        if len(cols) >= 5:
            claims.append(
                Claim(
                    id=cid,
                    type=cols[0],
                    target=cols[1],
                    property=cols[2],
                    expected=cols[3],
                    source=cols[4],
                )
            )
    return claims


def _extract_with_llm(text: str) -> List[Claim]:  # pragma: no cover - hook
    """
    TODO (upgrade path): call Azure OpenAI to extract claims from prose.

    Example skeleton:
        from openai import AzureOpenAI
        client = AzureOpenAI(...)
        resp = client.chat.completions.create(
            model="<deployment>",
            messages=[{"role": "system", "content": CLAIM_PROMPT},
                      {"role": "user", "content": text}],
            response_format={"type": "json_object"},
        )
        parse resp -> List[Claim]
    """
    raise NotImplementedError(
        "LLM extraction is a documented upgrade hook. "
        "Run in offline table mode for the demo."
    )
