"""
RTL Scanner Agent
-----------------
Parses SystemVerilog into structured facts the Mapper can reason about: port
widths, CSR address-map localparams, and FSM enum states. Accepts either a
single file or a directory (a multi-file design is merged into one fact set).

This is a lightweight structural parser (regex based) so the demo runs with no
external toolchain. For production, swap in a real parser (pyslang / pyverilog)
in scan_rtl() — the returned RTLFacts shape stays the same.
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RTLFacts:
    module: str = ""
    files: List[str] = field(default_factory=list)
    port_widths: Dict[str, int] = field(default_factory=dict)   # name -> bits
    reset_polarity: Optional[str] = None                        # "low" | "high"
    address_map: Dict[str, str] = field(default_factory=dict)   # NAME -> "0xNN"
    fsm_states: List[str] = field(default_factory=list)         # primary FSM
    fsm_by_name: Dict[str, List[str]] = field(default_factory=dict)  # var/type -> states


def scan_rtl(rtl_path: str) -> RTLFacts:
    paths = _collect_files(rtl_path)
    facts = RTLFacts()

    top_module = None
    for path in paths:
        text = _strip_comments(open(path, "r", encoding="utf-8").read())
        facts.files.append(os.path.basename(path))

        for name, width in _parse_ports(text).items():
            facts.port_widths.setdefault(name, width)

        if facts.reset_polarity is None:
            facts.reset_polarity = _parse_reset_polarity(text)

        for name, off in _parse_address_map(text).items():
            facts.address_map[name] = off

        for fsm_name, states in _parse_fsm_states(text).items():
            facts.fsm_by_name[fsm_name] = states

        # Prefer a *_top module as the reported top-level name.
        for m in re.finditer(r"\bmodule\s+(\w+)", text):
            mod = m.group(1)
            if top_module is None:
                top_module = mod
            if mod.endswith("_top"):
                top_module = mod

    facts.module = top_module or ""
    # Primary FSM list: the control FSM if present, else the first one found.
    if facts.fsm_by_name:
        primary = next((k for k in facts.fsm_by_name if "control" in k.lower()),
                       next(iter(facts.fsm_by_name)))
        facts.fsm_states = facts.fsm_by_name[primary]
    return facts


def _collect_files(rtl_path: str) -> List[str]:
    if os.path.isdir(rtl_path):
        files: List[str] = []
        for ext in ("*.sv", "*.v", "*.svh"):
            files.extend(glob.glob(os.path.join(rtl_path, "**", ext), recursive=True))
        return sorted(files)
    return [rtl_path]


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


def _parse_fsm_states(text: str) -> Dict[str, List[str]]:
    """
    Return {fsm identifier -> [states]}. Keyed by both the enum typedef name
    (e.g. control_fsm_e) and any variable declared of that type (control_fsm),
    so a claim can target the FSM by its signal name.
    """
    out: Dict[str, List[str]] = {}
    for m in re.finditer(
            r"typedef\s+enum\b[^{]*\{(.*?)\}\s*(\w+)\s*;", text, re.DOTALL):
        body, type_name = m.group(1), m.group(2)
        states = [t.upper() for t in re.findall(r"\b([A-Za-z_]\w*)\b", body)]
        out[type_name] = states
        # Map variables declared of this enum type to the same states.
        for vm in re.finditer(rf"\b{re.escape(type_name)}\s+(\w+)\s*[;,]", text):
            out[vm.group(1)] = states
    return out
