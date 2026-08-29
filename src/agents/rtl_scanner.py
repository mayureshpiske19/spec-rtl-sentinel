"""
RTL Scanner Agent
-----------------
Parses a SystemVerilog source file into structured facts the Mapper can reason
about: port widths, CSR address-map localparams, and FSM enum states.

This is a lightweight structural parser (regex based) so the demo runs with no
external toolchain. For production, swap in a real parser (pyslang / pyverilog)
in scan_rtl() — the returned RTLFacts shape stays the same.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RTLFacts:
    module: str = ""
    port_widths: Dict[str, int] = field(default_factory=dict)   # name -> bits
    reset_polarity: Optional[str] = None                        # "low" | "high"
    address_map: Dict[str, str] = field(default_factory=dict)   # NAME -> "0xNN"
    fsm_states: List[str] = field(default_factory=list)


def scan_rtl(rtl_path: str) -> RTLFacts:
    text = open(rtl_path, "r", encoding="utf-8").read()
    text = _strip_comments(text)
    facts = RTLFacts()

    m = re.search(r"\bmodule\s+(\w+)", text)
    if m:
        facts.module = m.group(1)

    facts.port_widths = _parse_ports(text)
    facts.reset_polarity = _parse_reset_polarity(text)
    facts.address_map = _parse_address_map(text)
    facts.fsm_states = _parse_fsm_states(text)
    return facts


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def _parse_ports(text: str) -> Dict[str, int]:
    widths: Dict[str, int] = {}
    pat = re.compile(
        r"\b(?:input|output|inout)\b\s+(?:wire|logic|reg)?\s*"
        r"(?:\[\s*(\d+)\s*:\s*(\d+)\s*\])?\s*(\w+)"
    )
    for msb, lsb, name in pat.findall(text):
        if msb == "" and lsb == "":
            widths[name] = 1
        else:
            widths[name] = abs(int(msb) - int(lsb)) + 1
    return widths


def _parse_reset_polarity(text: str) -> Optional[str]:
    if re.search(r"negedge\s+\w*resetn\b", text) or re.search(r"if\s*\(\s*!\s*\w*resetn", text):
        return "low"
    if re.search(r"posedge\s+\w*reset\b", text) or re.search(r"if\s*\(\s*\w*reset\b", text):
        return "high"
    return None


def _parse_address_map(text: str) -> Dict[str, str]:
    amap: Dict[str, str] = {}
    pat = re.compile(r"localparam\s+ADDR_(\w+)\s*=\s*\d+'h([0-9a-fA-F]+)")
    for name, off in pat.findall(text):
        amap[name.upper()] = "0x" + off.lower().zfill(2)
    return amap


def _parse_fsm_states(text: str) -> List[str]:
    states: List[str] = []
    m = re.search(r"typedef\s+enum\b[^{]*\{(.*?)\}", text, re.DOTALL)
    if m:
        body = m.group(1)
        for tok in re.findall(r"\b([A-Za-z_]\w*)\b", body):
            states.append(tok.upper())
    return states
