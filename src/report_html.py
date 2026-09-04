"""
HTML Drift-Report UI
--------------------
Renders the Design Intent Ledger as a self-contained, styled HTML dashboard
(no external resources — safe to open locally or share). This is a first-class
product output alongside the markdown report.

Sections: header + verdict, milestone gate cards, summary chips, traceability
(HAS -> MAS -> RTL), spec conflicts, clause-by-clause findings (filterable by
milestone), and decisions considered.
"""

from __future__ import annotations

import html
import json
import os
from datetime import datetime
from typing import List

from .agents.mapper import (
    Finding, VERIFIED, DRIFT, MISSING, UNDOCUMENTED, AMBIGUOUS,
)
from .agents.authority_resolver import ResolverResult
from .agents.traceability import TraceRow, GAP
from .agents.decision_ingest import Decision
from . import milestones as ms

_STATUS_CLASS = {
    VERIFIED: "ok",
    DRIFT: "bad",
    MISSING: "bad",
    UNDOCUMENTED: "warn",
    AMBIGUOUS: "warn",
}
_STATUS_LABEL = {
    VERIFIED: "Verified",
    DRIFT: "Drift",
    MISSING: "Missing",
    UNDOCUMENTED: "Undocumented",
    AMBIGUOUS: "Review",
}
_CONF_CLASS = {"high": "ok", "medium": "warn", "review": "bad"}


def _e(x) -> str:
    return html.escape(str(x), quote=True)


def build_html(all_findings: List[Finding], trace_rows: List[TraceRow],
               resolver: ResolverResult, decisions: List[Decision],
               rag_stats: dict, gates: list, milestone: str,
               has_path: str, spec_path: str, rtl_path: str) -> str:
    counts = {k: 0 for k in _STATUS_LABEL}
    for f in all_findings:
        counts[f.status] = counts.get(f.status, 0) + 1
    gaps = sum(1 for r in trace_rows if r.status == GAP)
    ok = (counts[DRIFT] + counts[MISSING] == 0
          and not resolver.conflicts and gaps == 0)
    verdict = "SPEC-FAITHFUL" if ok else "DRIFT / GAPS DETECTED"
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    # --- milestone gate cards ---
    gate_cards = []
    for g in gates:
        cls = "ok" if g["passed"] else "bad"
        verd = "PASS" if g["passed"] else "FAIL"
        sub = f"{g['checked']} checked"
        if not g["passed"]:
            sub = f"{len(g['fails'])} fail · {len(g['gaps'])} gap · {g['checked']} checked"
        gate_cards.append(f"""
        <div class="gate {cls}">
          <div class="gate-top"><span class="ms">{_e(g['milestone'])}</span>
            <span class="badge {cls}">{verd}</span></div>
          <div class="gate-label">{_e(g['label'])}</div>
          <div class="gate-sub">{_e(sub)}</div>
        </div>""")

    # --- summary chips ---
    chips = [
        ("ok", counts[VERIFIED], "Verified"),
        ("bad", counts[DRIFT], "Drift"),
        ("bad", counts[MISSING], "Missing"),
        ("warn", counts[UNDOCUMENTED], "Undocumented"),
        ("warn", counts[AMBIGUOUS], "Review"),
        ("warn", len(resolver.conflicts), "Spec conflicts"),
        ("warn", gaps, "Traceability gaps"),
    ]
    chip_html = "".join(
        f'<div class="chip {c}"><span class="n">{n}</span>'
        f'<span class="t">{_e(t)}</span></div>' for c, n, t in chips)

    # --- traceability rows ---
    trace_html = []
    for r in trace_rows:
        if r.status == GAP:
            st, stc = "GAP", "bad"
        else:
            st = r.rtl_rollup.upper()
            stc = _STATUS_CLASS.get(r.rtl_rollup, "warn")
        claims = ", ".join(r.claim_ids) if r.claim_ids else "—"
        trace_html.append(f"""
        <tr><td class="mono">{_e(r.has_id)}</td><td>{_e(r.kind)}</td>
        <td>{_e(r.requirement)}</td><td class="mono">{_e(claims)}</td>
        <td><span class="badge {stc}">{_e(st)}</span></td></tr>""")

    # --- conflicts ---
    if resolver.conflicts:
        conf_rows = "".join(f"""
        <tr><td class="mono">{_e(c.target)}</td><td>{_e(c.property)}</td>
        <td class="mono">{_e(c.mas_value)}</td>
        <td class="mono">{_e(c.decision_value)}</td>
        <td><b>{_e(c.resolved_value)}</b><br><span class="muted">{_e(c.resolved_source)}</span></td></tr>"""
                            for c in resolver.conflicts)
        conflicts_section = f"""
      <h2>Spec Conflicts <span class="muted">— resolved by authority + recency</span></h2>
      <table><thead><tr><th>Target</th><th>Property</th><th>MAS says</th>
      <th>Decision says</th><th>Resolved</th></tr></thead>
      <tbody>{conf_rows}</tbody></table>"""
    else:
        conflicts_section = ""

    # --- findings (filterable) ---
    find_rows = []
    for f in all_findings:
        cls = _STATUS_CLASS.get(f.status, "warn")
        lbl = _STATUS_LABEL.get(f.status, f.status)
        cat = getattr(f, "category", "functional")
        mstone = ms.milestone_of(cat)
        conf_cls = _CONF_CLASS.get(f.confidence, "warn")
        ev = _e(f.rag_evidence or f.rtl_evidence)
        back = (" · backing: " + ", ".join(f.backing)) if f.backing else ""
        find_rows.append(f"""
        <tr data-cat="{_e(cat)}" data-ms="{_e(mstone)}">
          <td class="mono">{_e(f.claim_id)}</td>
          <td><span class="pill">{_e(mstone)}</span></td>
          <td><span class="cat">{_e(cat)}</span></td>
          <td><span class="badge {cls}">{_e(lbl)}</span></td>
          <td><span class="badge {conf_cls} sm">{_e(f.confidence)}</span></td>
          <td class="mono">{_e(f.traces_to or '—')}</td>
          <td>{_e(f.detail)}<span class="muted">{_e(back)}</span></td>
          <td class="ev mono">{ev}</td>
        </tr>""")

    # --- decisions ---
    dec_rows = "".join(f"""
        <tr><td class="mono">{_e(d.id)}</td><td>{_e(d.date)}</td>
        <td>{_e(d.authority)}</td><td>{_e(d.type)}</td><td>{_e(d.amends)}</td>
        <td class="mono">{_e((d.target + '.' + d.property + '=' + d.value) if d.value else '')}</td></tr>"""
        for d in sorted(decisions, key=lambda x: x.date))

    rag_line = ", ".join(f"{k}={v}" for k, v in sorted(rag_stats.items()))
    scope_json = json.dumps({m: sorted(ms.scope_for(m)) for m in ms.MILESTONES})

    verdict_cls = "ok" if ok else "bad"

    return _TEMPLATE.format(
        generated=_e(generated),
        milestone=_e(milestone),
        has=_e(os.path.basename(has_path)),
        mas=_e(os.path.basename(spec_path)),
        rtl=_e(os.path.basename(rtl_path)),
        rag=_e(rag_line),
        verdict=_e(verdict),
        verdict_cls=verdict_cls,
        gate_cards="".join(gate_cards),
        chips=chip_html,
        trace_rows="".join(trace_html),
        conflicts=conflicts_section,
        find_rows="".join(find_rows),
        dec_rows=dec_rows,
        scope_json=scope_json,
    )


def save_html(text: str, out_dir: str = "reports") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "drift_report.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spec-RTL Sentinel — Drift Report</title>
<script>
  (() => {{
    const p = new URLSearchParams(window.location.search).get("scoutTheme");
    const t = p || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", t);
  }})();
</script>
<style>
:root {{
  color-scheme: light;
  --cp-bg:#f7f4ef; --cp-bg-elevated:#fcfbf8; --cp-surface:#ffffff;
  --cp-surface-soft:#f5f5f5; --cp-border:#dedede; --cp-border-strong:#919191;
  --cp-text:#242424; --cp-text-muted:#5c5c5c; --cp-text-soft:#6f6f6f;
  --cp-accent:#b11f4b; --cp-success:#16a34a; --cp-danger:#dc2626;
  --cp-warning:#f59e0b; --cp-link:#0078d4;
  --cp-shadow:0 0 2px rgba(0,0,0,0.12),0 1px 2px rgba(0,0,0,0.14);
}}
html[data-theme="dark"] {{
  color-scheme: dark;
  --cp-bg:#3d3b3a; --cp-bg-elevated:#343231; --cp-surface:#292929;
  --cp-surface-soft:#2e2e2e; --cp-border:#474747; --cp-border-strong:#5f5f5f;
  --cp-text:#dedede; --cp-text-muted:#919191; --cp-text-soft:#b0b0b0;
  --cp-accent:#fd8ea1; --cp-success:#4ade80; --cp-danger:#f87171;
  --cp-warning:#fbbf24; --cp-link:#4da6ff;
  --cp-shadow:0 0 2px rgba(0,0,0,0.32),0 1px 2px rgba(0,0,0,0.4);
}}
* {{ box-sizing: border-box; }}
body {{
  margin:0; background:var(--cp-bg); color:var(--cp-text);
  font-family:"Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif;
  line-height:1.5; padding:0 0 4rem;
}}
.mono {{ font-family:Consolas,"Courier New",Courier,monospace; font-size:.86em; }}
.wrap {{ max-width:1180px; margin:0 auto; padding:0 1.5rem; }}
header {{
  background:var(--cp-bg-elevated); border-bottom:1px solid var(--cp-border);
  padding:1.6rem 0 1.4rem;
}}
.brand {{ display:flex; align-items:center; gap:.7rem; }}
.dot {{ width:.85rem; height:.85rem; border-radius:50%; background:var(--cp-accent); }}
h1 {{ font-size:1.5rem; margin:0; font-weight:700; letter-spacing:-.01em; }}
.sub {{ color:var(--cp-text-muted); font-size:.9rem; margin-top:.15rem; }}
.meta {{ display:flex; flex-wrap:wrap; gap:1.2rem; margin-top:1rem; font-size:.82rem;
  color:var(--cp-text-soft); }}
.meta b {{ color:var(--cp-text); font-weight:600; }}
.verdict {{
  display:inline-flex; align-items:center; gap:.5rem; margin-top:1rem;
  padding:.5rem .9rem; border-radius:.625rem; font-weight:700; font-size:1rem;
  border:1px solid transparent;
}}
.verdict.ok {{ background:color-mix(in srgb,var(--cp-success) 14%,transparent); color:var(--cp-success);
  border-color:color-mix(in srgb,var(--cp-success) 40%,transparent); }}
.verdict.bad {{ background:color-mix(in srgb,var(--cp-danger) 12%,transparent); color:var(--cp-danger);
  border-color:color-mix(in srgb,var(--cp-danger) 38%,transparent); }}
h2 {{ font-size:1.12rem; margin:2.2rem 0 .9rem; font-weight:700; }}
h2 .muted {{ font-weight:400; font-size:.85rem; }}
.muted {{ color:var(--cp-text-muted); }}
.gates {{ display:grid; grid-template-columns:repeat(4,1fr); gap:.9rem; margin-top:1.4rem; }}
.gate {{ background:var(--cp-surface); border:1px solid var(--cp-border);
  border-left:4px solid var(--cp-border-strong); border-radius:12px; padding:.9rem 1rem;
  box-shadow:var(--cp-shadow); }}
.gate.ok {{ border-left-color:var(--cp-success); }}
.gate.bad {{ border-left-color:var(--cp-danger); }}
.gate-top {{ display:flex; align-items:center; justify-content:space-between; }}
.ms {{ font-size:1.35rem; font-weight:800; letter-spacing:-.02em; }}
.gate-label {{ font-size:.82rem; margin-top:.35rem; min-height:2.4em; }}
.gate-sub {{ font-size:.74rem; color:var(--cp-text-muted); margin-top:.4rem; }}
.badge {{ display:inline-block; padding:.12rem .5rem; border-radius:999px; font-size:.72rem;
  font-weight:700; text-transform:uppercase; letter-spacing:.02em; }}
.badge.sm {{ text-transform:none; }}
.badge.ok {{ background:color-mix(in srgb,var(--cp-success) 16%,transparent); color:var(--cp-success); }}
.badge.bad {{ background:color-mix(in srgb,var(--cp-danger) 15%,transparent); color:var(--cp-danger); }}
.badge.warn {{ background:color-mix(in srgb,var(--cp-warning) 18%,transparent);
  color:color-mix(in srgb,var(--cp-warning) 75%,var(--cp-text)); }}
.chips {{ display:flex; flex-wrap:wrap; gap:.6rem; margin-top:1.2rem; }}
.chip {{ background:var(--cp-surface); border:1px solid var(--cp-border); border-radius:.625rem;
  padding:.5rem .8rem; display:flex; align-items:baseline; gap:.45rem; box-shadow:var(--cp-shadow); }}
.chip .n {{ font-size:1.15rem; font-weight:800; }}
.chip .t {{ font-size:.78rem; color:var(--cp-text-muted); }}
.chip.ok .n {{ color:var(--cp-success); }}
.chip.bad .n {{ color:var(--cp-danger); }}
.chip.warn .n {{ color:var(--cp-warning); }}
table {{ width:100%; border-collapse:collapse; background:var(--cp-surface);
  border:1px solid var(--cp-border); border-radius:12px; overflow:hidden; box-shadow:var(--cp-shadow);
  font-size:.85rem; }}
th,td {{ text-align:left; padding:.6rem .75rem; border-bottom:1px solid var(--cp-border);
  vertical-align:top; }}
th {{ background:var(--cp-surface-soft); font-weight:600; font-size:.76rem; text-transform:uppercase;
  letter-spacing:.03em; color:var(--cp-text-muted); }}
tr:last-child td {{ border-bottom:none; }}
.ev {{ color:var(--cp-text-soft); max-width:320px; }}
.pill {{ display:inline-block; padding:.1rem .5rem; border-radius:999px; font-size:.74rem;
  font-weight:700; background:var(--cp-accent); color:#fff; }}
html[data-theme="dark"] .pill {{ color:#1a1a1a; }}
.cat {{ font-size:.78rem; color:var(--cp-text-muted); }}
.filters {{ display:flex; gap:.4rem; margin:.4rem 0 1rem; flex-wrap:wrap; }}
.filters button {{ font:inherit; font-size:.8rem; padding:.35rem .8rem; border-radius:.625rem;
  border:1px solid var(--cp-border); background:var(--cp-surface); color:var(--cp-text);
  cursor:pointer; }}
.filters button.active {{ background:var(--cp-accent); color:#fff; border-color:var(--cp-accent); }}
html[data-theme="dark"] .filters button.active {{ color:#1a1a1a; }}
footer {{ text-align:center; color:var(--cp-text-soft); font-size:.78rem; margin-top:2.5rem; }}
.note {{ font-size:.8rem; color:var(--cp-text-muted); margin-top:.6rem; }}
.axes {{ margin-top:.7rem; font-size:.82rem; color:var(--cp-text-soft); }}
.axes b {{ color:var(--cp-accent); }}
</style>
</head>
<body>
<header><div class="wrap">
  <div class="brand"><span class="dot"></span>
    <div><h1>Spec-RTL Sentinel</h1>
    <div class="sub">Design Intent Ledger — HAS is golden; MAS + RTL checked against it</div></div>
  </div>
  <div class="meta">
    <span>Generated <b>{generated}</b></span>
    <span>Milestone scope <b>{milestone}</b></span>
    <span>HAS <b>{has}</b> · MAS <b>{mas}</b> · RTL <b>{rtl}</b></span>
    <span>Knowledge <b>{rag}</b> chunks</span>
  </div>
  <div class="verdict {verdict_cls}">{verdict}</div>
  <div class="axes">Two checks: <b>HAS → MAS</b> coverage (spec vs spec) &nbsp;·&nbsp; <b>MAS → RTL</b> conformance (spec vs implementation)</div>
</div></header>

<div class="wrap">
  <h2>Milestone Gates <span class="muted">— cumulative</span></h2>
  <div class="gates">{gate_cards}</div>
  <div class="note">Gates are cumulative: each milestone re-checks everything below it.
    A gate passes only when every in-scope claim is verified with no traceability gap.</div>

  <h2>Summary</h2>
  <div class="chips">{chips}</div>

  <h2>HAS → MAS Coverage <span class="muted">— spec vs spec · a gap = in HAS, not detailed in MAS</span></h2>
  <table><thead><tr><th>HAS</th><th>Kind</th><th>Requirement</th>
    <th>MAS claims</th><th>RTL rollup</th></tr></thead>
    <tbody>{trace_rows}</tbody></table>

  {conflicts}

  <h2>MAS → RTL Conformance <span class="muted">— spec vs implementation · drift / missing / undocumented</span></h2>
  <div class="filters" id="filters">
    <button data-f="all" class="active">All</button>
    <button data-f="0.1">0.1</button><button data-f="0.5">0.5</button>
    <button data-f="0.8">0.8</button><button data-f="1.0">1.0</button>
  </div>
  <table id="findings"><thead><tr><th>Claim</th><th>MS</th><th>Category</th>
    <th>Status</th><th>Conf</th><th>Traces</th><th>Detail</th><th>Evidence</th></tr></thead>
    <tbody>{find_rows}</tbody></table>

  <h2>Decisions Considered</h2>
  <table><thead><tr><th>ID</th><th>Date</th><th>Authority</th><th>Type</th>
    <th>Amends</th><th>Change</th></tr></thead><tbody>{dec_rows}</tbody></table>

  <footer>Spec-RTL Sentinel · every finding cites its exact source · runs fully offline</footer>
</div>

<script>
  var SCOPE = {scope_json};
  var btns = document.querySelectorAll('#filters button');
  var rows = document.querySelectorAll('#findings tbody tr');
  btns.forEach(function(b) {{
    b.addEventListener('click', function() {{
      btns.forEach(function(x) {{ x.classList.remove('active'); }});
      b.classList.add('active');
      var f = b.getAttribute('data-f');
      rows.forEach(function(r) {{
        var cat = r.getAttribute('data-cat');
        var show = (f === 'all') || (SCOPE[f] && SCOPE[f].indexOf(cat) !== -1);
        r.style.display = show ? '' : 'none';
      }});
    }});
  }});
</script>
</body>
</html>"""
