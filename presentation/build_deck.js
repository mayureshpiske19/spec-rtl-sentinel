// Builds the Spec-RTL Sentinel pitch deck.
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
p.author = "Mayuresh Piske";
p.title = "Spec-RTL Sentinel — Design Intent Auditor";

const W = 13.3, Hh = 7.5;

// Palette
const NAVY = "12324F", NAVY2 = "1C4E7A", TEAL = "0C8599", TEALD = "0C6B78";
const ICE = "F4F8FC", INK = "1E2733", MUTE = "5A6473", RED = "B01722";
const PURPLE = "5C2D91", ORANGE = "B8560F", GREEN = "0E6B0E", LINE = "D7E1EC";
const HF = "Trebuchet MS", BF = "Calibri";
const shadow = () => ({ type: "outer", color: "1E2733", blur: 8, offset: 3, angle: 90, opacity: 0.12 });

function kicker(s, text, color = TEAL) {
  s.addShape(p.shapes.OVAL, { x: 0.6, y: 0.62, w: 0.16, h: 0.16, fill: { color } });
  s.addText(text.toUpperCase(), { x: 0.85, y: 0.5, w: 9, h: 0.4, fontFace: HF, fontSize: 13, bold: true, color, charSpacing: 3, align: "left", valign: "middle", margin: 0 });
}
function title(s, text, color = NAVY) {
  s.addText(text, { x: 0.58, y: 0.9, w: 12.1, h: 0.95, fontFace: HF, fontSize: 30, bold: true, color, align: "left", valign: "middle", margin: 0 });
}
function card(s, x, y, w, h, opts = {}) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: opts.fill || "FFFFFF" }, line: { color: opts.line || LINE, width: 1 }, shadow: opts.shadow ? shadow() : undefined });
}

// ---------------------------------------------------------------- SLIDE 1 — Title
let s = p.addSlide();
s.background = { color: NAVY };
s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: Hh, fill: { color: TEAL } });
s.addText("SPEC-RTL SENTINEL", { x: 0.9, y: 2.05, w: 11.6, h: 1.1, fontFace: HF, fontSize: 52, bold: true, color: "FFFFFF", align: "left", margin: 0 });
s.addText("Design Intent Auditor", { x: 0.95, y: 3.15, w: 11, h: 0.7, fontFace: HF, fontSize: 27, italic: true, color: "7FD4E0", align: "left", margin: 0 });
s.addText("Agentic RAG that catches spec-to-silicon drift before it becomes a bug.", { x: 0.95, y: 3.95, w: 11, h: 0.5, fontFace: BF, fontSize: 16, color: "CADCFC", align: "left", margin: 0 });
// layer motif
const layers = [["HAS", "0F5EA8"], ["MAS", PURPLE], ["Decisions", ORANGE], ["RTL", GREEN]];
let lx = 0.95;
layers.forEach(([t], i) => {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: lx, y: 4.95, w: 1.7, h: 0.55, rectRadius: 0.06, fill: { color: "1C4E7A" }, line: { color: "3E6E9E", width: 1 } });
  s.addText(t, { x: lx, y: 4.95, w: 1.7, h: 0.55, fontFace: HF, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  if (i < 3) s.addText("→", { x: lx + 1.7, y: 4.95, w: 0.42, h: 0.55, fontFace: HF, fontSize: 18, color: "7FD4E0", align: "center", valign: "middle", margin: 0 });
  lx += 2.12;
});
s.addText([
  { text: "Mayuresh Piske", options: { bold: true, color: "FFFFFF" } },
  { text: "   ·   Spec-faithful RTL verification, grounded in design intent", options: { color: "9DB4CC" } },
], { x: 0.95, y: 6.45, w: 11.6, h: 0.5, fontFace: BF, fontSize: 14, align: "left", margin: 0 });

// ---------------------------------------------------------------- SLIDE 2 — Problem
s = p.addSlide(); s.background = { color: ICE };
kicker(s, "The Problem");
title(s, "Specs and silicon drift apart");
s.addText([
  { text: "RTL is built from a MAS, which refines a HAS.", options: { bullet: true, breakLine: true } },
  { text: "But real decisions — “widen the bus to 64-bit”, “move STATUS to 0x08” — live in reviews, chats, and meeting notes.", options: { bullet: true, breakLine: true } },
  { text: "They rarely make it back into the formal specs.", options: { bullet: true, breakLine: true } },
  { text: "Manual clause-by-clause cross-checking is slow, inconsistent, and dropped under schedule pressure.", options: { bullet: true } },
], { x: 0.7, y: 2.05, w: 6.7, h: 3.4, fontFace: BF, fontSize: 17, color: INK, lineSpacingMultiple: 1.25, paraSpaceAfter: 10 });
// right stat cards
const stats = [["Hours", "per block, manual spec review", RED], ["1", "missed mismatch = silicon bug or security hole", NAVY], ["4 sources", "HAS · MAS · decisions · RTL to reconcile", TEALD]];
let sy = 1.95;
stats.forEach(([big, sub, col]) => {
  card(s, 7.8, sy, 4.9, 1.55, { shadow: true });
  s.addShape(p.shapes.RECTANGLE, { x: 7.8, y: sy, w: 0.11, h: 1.55, fill: { color: col } });
  s.addText(big, { x: 8.1, y: sy + 0.18, w: 4.4, h: 0.75, fontFace: HF, fontSize: 34, bold: true, color: col, align: "left", margin: 0 });
  s.addText(sub, { x: 8.12, y: sy + 0.92, w: 4.5, h: 0.5, fontFace: BF, fontSize: 13, color: MUTE, align: "left", margin: 0 });
  sy += 1.72;
});

// ---------------------------------------------------------------- SLIDE 3 — Insight
s = p.addSlide(); s.background = { color: ICE };
kicker(s, "The Insight");
title(s, "The tribal layer nobody indexes");
s.addText("Formal specs capture the plan. The decisions that actually change the design live in the conversation around it — and no lint or spec-check tool reads that layer.", { x: 0.7, y: 1.95, w: 11.9, h: 0.8, fontFace: BF, fontSize: 17, color: INK, align: "left", margin: 0 });
const il = [["HAS", "0F5EA8", "Top-level intent — performance, concept, security", "the WHY"],
["MAS", PURPLE, "Micro-architecture detail — registers, widths, FSM", "the WHAT"],
["Decisions / Reviews / Meetings", ORANGE, "Amendments that override or reinforce the specs", "the AS-AGREED", true],
["RTL", GREEN, "The implementation", "the AS-BUILT"]];
let iy = 3.0;
il.forEach(([t, c, d, tag, hot]) => {
  card(s, 0.7, iy, 11.9, 0.92, { fill: hot ? "FDF0E2" : "FFFFFF", line: hot ? ORANGE : LINE, shadow: hot });
  s.addShape(p.shapes.RECTANGLE, { x: 0.7, y: iy, w: 0.13, h: 0.92, fill: { color: c } });
  s.addText(t, { x: 1.0, y: iy, w: 4.2, h: 0.92, fontFace: HF, fontSize: 17, bold: true, color: c, align: "left", valign: "middle", margin: 0 });
  s.addText(d, { x: 5.3, y: iy, w: 5.6, h: 0.92, fontFace: BF, fontSize: 14, color: INK, align: "left", valign: "middle", margin: 0 });
  s.addText(tag, { x: 10.7, y: iy, w: 1.8, h: 0.92, fontFace: HF, fontSize: 12, bold: true, italic: true, color: MUTE, align: "right", valign: "middle", margin: 0 });
  iy += 1.03;
});

// ---------------------------------------------------------------- SLIDE 4 — Solution
s = p.addSlide(); s.background = { color: ICE };
kicker(s, "What It Does");
title(s, "One audit across every layer of intent");
s.addText("Sentinel ingests all four layers into a RAG store, reconciles conflicts by authority, and checks RTL against the resolved intent — producing a clause-by-clause drift report.", { x: 0.7, y: 1.9, w: 11.9, h: 0.75, fontFace: BF, fontSize: 17, color: INK, margin: 0 });
const steps = [["1", "Ingest", "HAS + MAS + decisions + RTL into a grounded RAG store"],
["2", "Reconcile", "Authority resolver settles spec-vs-decision conflicts by seniority + recency"],
["3", "Trace", "HAS → MAS → RTL; flag requirements never refined (gaps)"],
["4", "Report", "Verified / drift / missing / conflict / gap — each citing its source"]];
let x4 = 0.7;
steps.forEach(([n, h, d]) => {
  card(s, x4, 3.0, 2.86, 3.0, { shadow: true });
  s.addShape(p.shapes.OVAL, { x: x4 + 0.35, y: 3.35, w: 0.7, h: 0.7, fill: { color: TEAL } });
  s.addText(n, { x: x4 + 0.35, y: 3.35, w: 0.7, h: 0.7, fontFace: HF, fontSize: 24, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  s.addText(h, { x: x4 + 0.3, y: 4.2, w: 2.3, h: 0.5, fontFace: HF, fontSize: 19, bold: true, color: NAVY, align: "left", margin: 0 });
  s.addText(d, { x: x4 + 0.3, y: 4.75, w: 2.36, h: 1.1, fontFace: BF, fontSize: 13.5, color: MUTE, align: "left", margin: 0 });
  x4 += 3.05;
});

// ---------------------------------------------------------------- SLIDE 5 — Architecture
s = p.addSlide(); s.background = { color: "FFFFFF" };
kicker(s, "Architecture");
title(s, "Multi-agent RAG pipeline");
s.addImage({ path: "docs/architecture.png", x: 0.5, y: 1.75, w: 12.3, h: 5.55, sizing: { type: "contain", w: 12.3, h: 5.55 } });

// ---------------------------------------------------------------- SLIDE 6 — Agents
s = p.addSlide(); s.background = { color: ICE };
kicker(s, "The Agents");
title(s, "A pipeline of specialised agents");
const agents = [["HAS Parser", "Extracts top-level requirements"],
["Claim Extractor", "MAS → testable claims, traced to HAS"],
["Decision Ingest", "Reviews/meetings w/ authority + date"],
["RTL Scanner", "Ports, CSR map, FSM states"],
["Authority Resolver", "Reconciles spec vs decisions"],
["Traceability", "HAS→MAS→RTL coverage + gaps"],
["Mapper / Diff", "Resolved claims × RTL facts"],
["Sim Checker", "Confirms dynamic claims"],
["Report Generator", "Layered drift report"]];
let ax = 0.7, ay = 2.0, aw = 3.9, ah = 1.5, gap = 0.13;
agents.forEach((a, i) => {
  const col = i % 3, row = Math.floor(i / 3);
  const x = ax + col * (aw + gap), y = ay + row * (ah + gap);
  card(s, x, y, aw, ah, { shadow: true });
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.11, h: ah, fill: { color: TEAL } });
  s.addText(a[0], { x: x + 0.28, y: y + 0.2, w: aw - 0.5, h: 0.5, fontFace: HF, fontSize: 16, bold: true, color: NAVY, align: "left", margin: 0 });
  s.addText(a[1], { x: x + 0.28, y: y + 0.72, w: aw - 0.5, h: 0.65, fontFace: BF, fontSize: 13, color: MUTE, align: "left", margin: 0 });
});
s.addText("All grounded in a dependency-free multi-source RAG store — runs fully offline.", { x: 0.7, y: 7.0, w: 11.9, h: 0.4, fontFace: BF, fontSize: 13, italic: true, color: TEALD, margin: 0 });

// ---------------------------------------------------------------- SLIDE 7 — Demo results
s = p.addSlide(); s.background = { color: ICE };
kicker(s, "Live Demo");
title(s, "What it catches — in seconds");
const finds = [
  [RED, "🟥 Drift · high confidence", "m_axi_wdata is 32-bit; MAS and the Aug-28 arch review both require 64-bit"],
  [RED, "❌ Missing · 0.5", "Control FSM lacks the WRITE_OUT state required by MAS §4.1"],
  [RED, "❌ Missing · 0.8", "PERF_MISS performance counter (MAS §3.3) not implemented"],
  [ORANGE, "⚠ Spec conflict · auto-resolved", "INT_STATUS: MAS 0x054 vs Sep-02 review 0x058 — RTL follows the review"],
  [TEALD, "🟡 Undocumented · explained", "DBG_SCRATCH in RTL — an Aug-20 meeting flagged it as a temporary hook"],
  [PURPLE, "▲ Traceability gap", "HAS-09 (multi-clock CDC) was never refined into a MAS claim"],
];
let fy = 1.9;
finds.forEach(([c, h, d]) => {
  card(s, 0.7, fy, 8.7, 0.8, { shadow: true });
  s.addShape(p.shapes.RECTANGLE, { x: 0.7, y: fy, w: 0.12, h: 0.8, fill: { color: c } });
  s.addText(h, { x: 1.0, y: fy + 0.1, w: 8.2, h: 0.36, fontFace: HF, fontSize: 13.5, bold: true, color: c, align: "left", margin: 0 });
  s.addText(d, { x: 1.0, y: fy + 0.44, w: 8.3, h: 0.34, fontFace: BF, fontSize: 11.5, color: INK, align: "left", margin: 0 });
  fy += 0.9;
});
// verdict panel
card(s, 9.7, 1.9, 3.0, 5.3, { fill: NAVY });
s.addText("ZEPHYR COSS", { x: 9.7, y: 2.2, w: 3.0, h: 0.4, fontFace: HF, fontSize: 13, bold: true, color: "7FD4E0", align: "center", charSpacing: 1, margin: 0 });
s.addText("🚨", { x: 9.7, y: 2.65, w: 3.0, h: 0.85, fontSize: 40, align: "center", margin: 0 });
s.addText("DRIFT\nDETECTED", { x: 9.7, y: 3.5, w: 3.0, h: 0.95, fontFace: HF, fontSize: 22, bold: true, color: "FFFFFF", align: "center", margin: 0 });
s.addText([
  { text: "25 verified · 1 drift", options: { breakLine: true } },
  { text: "2 missing · 1 conflict", options: { breakLine: true } },
  { text: "1 gap · 1 undocumented", options: {} },
], { x: 9.7, y: 4.6, w: 3.0, h: 1.2, fontFace: BF, fontSize: 13, color: "CADCFC", align: "center", margin: 0 });
s.addText("28 claims · one command · zero API keys", { x: 9.7, y: 6.55, w: 3.0, h: 0.5, fontFace: BF, fontSize: 11, italic: true, color: "7FD4E0", align: "center", margin: 0 });

// ---------------------------------------------------------------- SLIDE 7b — Milestone gates
s = p.addSlide(); s.background = { color: ICE };
kicker(s, "Milestone Gates");
title(s, "Is the RTL 0.1-clean? 0.5-clean?");
s.addText([
  { text: "HAS is the golden reference — never flagged. ", options: { bold: true, color: NAVY } },
  { text: "MAS and RTL are checked against it milestone by milestone, so each stage only checks what should be done by then.", options: { color: INK } },
], { x: 0.7, y: 1.9, w: 11.9, h: 0.7, fontFace: BF, fontSize: 16, margin: 0 });
const gates = [
  ["0.1", "Boundary — interface ports + CSR registers", "FAIL", "m_axi_wdata 32-bit vs 64-bit drift"],
  ["0.5", "+ Functional behavior (FSM, datapath)", "FAIL", "control FSM missing WRITE_OUT state"],
  ["0.8", "+ Errors, DFT, perf counters, debug", "FAIL", "PERF_MISS counter not implemented"],
  ["1.0", "Overall / integration — everything", "FAIL", "HAS-09 multi-clock CDC gap"],
];
let gy = 2.75;
gates.forEach(([m, scope, verdict, why]) => {
  card(s, 0.7, gy, 9.0, 0.92, { shadow: true });
  s.addShape(p.shapes.RECTANGLE, { x: 0.7, y: gy, w: 0.13, h: 0.92, fill: { color: RED } });
  s.addShape(p.shapes.OVAL, { x: 0.95, y: gy + 0.2, w: 0.52, h: 0.52, fill: { color: NAVY } });
  s.addText(m, { x: 0.95, y: gy + 0.2, w: 0.52, h: 0.52, fontFace: HF, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  s.addText(scope, { x: 1.65, y: gy + 0.12, w: 6.0, h: 0.4, fontFace: HF, fontSize: 14.5, bold: true, color: NAVY, align: "left", margin: 0 });
  s.addText(why, { x: 1.65, y: gy + 0.5, w: 6.0, h: 0.36, fontFace: BF, fontSize: 12, color: MUTE, align: "left", margin: 0 });
  s.addText("🚨 " + verdict, { x: 7.75, y: gy, w: 1.8, h: 0.92, fontFace: HF, fontSize: 15, bold: true, color: RED, align: "center", valign: "middle", margin: 0 });
  gy += 1.03;
});
// side note panel
card(s, 9.9, 2.75, 2.8, 4.07, { fill: NAVY });
s.addText("Cumulative gates", { x: 9.9, y: 3.05, w: 2.8, h: 0.4, fontFace: HF, fontSize: 15, bold: true, color: "7FD4E0", align: "center", margin: 0 });
s.addText([
  { text: "Each milestone re-checks everything below it.", options: { breakLine: true } },
  { text: "", options: { breakLine: true } },
  { text: "A gate passes only when every in-scope claim is verified — no drift, no gap.", options: {} },
], { x: 10.1, y: 3.55, w: 2.4, h: 2.2, fontFace: BF, fontSize: 13, color: "CADCFC", align: "left", margin: 0 });
s.addText("RTL isn't even 0.1-ready yet.", { x: 9.9, y: 6.2, w: 2.8, h: 0.5, fontFace: HF, fontSize: 12.5, italic: true, bold: true, color: "FFFFFF", align: "center", margin: 0 });

// ---------------------------------------------------------------- SLIDE 8 — Why different
s = p.addSlide(); s.background = { color: ICE };
kicker(s, "Why It's Different");
title(s, "Grounded. Traceable. Trustworthy.");
const cols = [
  ["Indexes the tribal layer", "The only tool that reads the decisions in reviews and meetings — not just one static spec.", TEAL],
  ["Resolves source conflicts", "Reconciles spec-vs-decision by authority + recency before ever touching the RTL.", ORANGE],
  ["Cites every finding", "Each result links to the exact HAS/MAS clause or decision it is grounded in. No hallucinations.", PURPLE],
];
let cx = 0.7;
cols.forEach(([h, d, c]) => {
  card(s, cx, 2.2, 3.9, 4.2, { shadow: true });
  s.addShape(p.shapes.OVAL, { x: cx + 0.35, y: 2.6, w: 0.8, h: 0.8, fill: { color: c } });
  s.addText("✓", { x: cx + 0.35, y: 2.6, w: 0.8, h: 0.8, fontFace: HF, fontSize: 30, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  s.addText(h, { x: cx + 0.3, y: 3.6, w: 3.3, h: 0.9, fontFace: HF, fontSize: 19, bold: true, color: NAVY, align: "left", margin: 0 });
  s.addText(d, { x: cx + 0.3, y: 4.5, w: 3.35, h: 1.7, fontFace: BF, fontSize: 14, color: MUTE, align: "left", margin: 0 });
  cx += 4.05;
});

// ---------------------------------------------------------------- SLIDE 9 — Impact
s = p.addSlide(); s.background = { color: ICE };
kicker(s, "Impact");
title(s, "From hours of review to seconds");
const imp = [["seconds", "to audit RTL against 4 intent layers", TEAL], ["100%", "of findings source-cited", NAVY], ["0", "API keys — runs fully offline", TEALD]];
let ix = 0.7;
imp.forEach(([b, d, c]) => {
  card(s, ix, 2.1, 3.9, 1.9, { shadow: true });
  s.addText(b, { x: ix + 0.3, y: 2.35, w: 3.3, h: 0.95, fontFace: HF, fontSize: 40, bold: true, color: c, align: "left", margin: 0 });
  s.addText(d, { x: ix + 0.32, y: 3.35, w: 3.4, h: 0.55, fontFace: BF, fontSize: 13.5, color: MUTE, align: "left", margin: 0 });
  ix += 4.05;
});
s.addText("Who benefits", { x: 0.7, y: 4.35, w: 6, h: 0.5, fontFace: HF, fontSize: 18, bold: true, color: NAVY, margin: 0 });
s.addText([
  { text: "Design & verification engineers — stop hand-diffing specs against RTL", options: { bullet: true, breakLine: true } },
  { text: "Architects — see which top-level requirements are actually implemented", options: { bullet: true, breakLine: true } },
  { text: "Leads & PMs — a living drift metric per commit, not a one-time review", options: { bullet: true, breakLine: true } },
  { text: "Security IP teams — catch key/register drift before tapeout", options: { bullet: true } },
], { x: 0.7, y: 4.9, w: 11.9, h: 2.2, fontFace: BF, fontSize: 16, color: INK, paraSpaceAfter: 8, lineSpacingMultiple: 1.15 });

// ---------------------------------------------------------------- SLIDE 10 — Roadmap / Close
s = p.addSlide(); s.background = { color: NAVY };
s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: Hh, fill: { color: TEAL } });
s.addShape(p.shapes.OVAL, { x: 0.9, y: 0.75, w: 0.16, h: 0.16, fill: { color: "7FD4E0" } });
s.addText("ROADMAP", { x: 1.15, y: 0.63, w: 9, h: 0.4, fontFace: HF, fontSize: 13, bold: true, color: "7FD4E0", charSpacing: 3, margin: 0 });
s.addText("Built offline today — Azure OpenAI RAG tomorrow", { x: 0.9, y: 1.15, w: 11.6, h: 0.9, fontFace: HF, fontSize: 28, bold: true, color: "FFFFFF", margin: 0 });
s.addText([
  { text: "Swap the TF-cosine index for Azure OpenAI embeddings + ChromaDB / FAISS", options: { bullet: true, breakLine: true, color: "CADCFC" } },
  { text: "LLM claim extraction from free-form spec prose (documented hook)", options: { bullet: true, breakLine: true, color: "CADCFC" } },
  { text: "Real HDL parsing at scale (pyslang / pyverilog)", options: { bullet: true, breakLine: true, color: "CADCFC" } },
  { text: "Live decision sources — Teams, ADO review comments, meeting transcripts", options: { bullet: true, color: "CADCFC" } },
], { x: 1.0, y: 2.3, w: 11.4, h: 2.3, fontFace: BF, fontSize: 16, paraSpaceAfter: 9 });
card(s, 0.9, 5.35, 11.5, 1.35, { fill: "1C4E7A", line: "3E6E9E" });
s.addText([
  { text: "Try it:  ", options: { bold: true, color: "7FD4E0" } },
  { text: "python examples/run_demo.py", options: { color: "FFFFFF", fontFace: "Consolas" } },
], { x: 1.25, y: 5.55, w: 11, h: 0.5, fontFace: BF, fontSize: 17, margin: 0 });
s.addText("github.com/mayureshpiske19/mas-rtl-sentinel", { x: 1.25, y: 6.05, w: 11, h: 0.5, fontFace: BF, fontSize: 15, color: "CADCFC", margin: 0 });
s.addText("Spec-RTL Sentinel — catching spec-to-silicon drift before it becomes a bug.", { x: 0.9, y: 6.95, w: 11.6, h: 0.4, fontFace: HF, fontSize: 13, italic: true, color: "9DB4CC", margin: 0 });

p.writeFile({ fileName: "presentation/Spec-RTL-Sentinel-Pitch.pptx" }).then(f => console.log("wrote", f));
