"""
Generates the Spec-RTL Sentinel architecture diagram as a high-res PNG.
Professional Microsoft-Fluent styling. No hand-drawn look.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

W, H = 16.0, 9.0
fig, ax = plt.subplots(figsize=(W, H), dpi=200)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
fig.patch.set_facecolor("white")

# Fluent palette (stroke, fill)
BLUE   = ("#0F5EA8", "#D6E8FA")   # HAS
PURPLE = ("#5C2D91", "#EADFF5")   # MAS
ORANGE = ("#B8560F", "#FDEBD3")   # Decisions
GREEN  = ("#0E6B0E", "#DCF3DC")   # RTL
TEAL   = ("#0C6B78", "#D3EEF2")   # RAG / knowledge
SLATE  = ("#2B3A55", "#E7ECF5")   # agents
DARK   = ("#1E1E1E", "#F3F2F1")

def box(x, y, w, h, colors, title, sub=None, tfs=15, sfs=11, radius=0.10,
        title_color=None):
    stroke, fill = colors
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.02,rounding_size={radius}",
                       linewidth=2.0, edgecolor=stroke, facecolor=fill,
                       zorder=3)
    ax.add_patch(p)
    cx = x + w / 2
    if sub:
        ax.text(cx, y + h * 0.62, title, ha="center", va="center",
                fontsize=tfs, fontweight="bold",
                color=title_color or stroke, zorder=4)
        ax.text(cx, y + h * 0.28, sub, ha="center", va="center",
                fontsize=sfs, color="#333333", zorder=4)
    else:
        ax.text(cx, y + h / 2, title, ha="center", va="center",
                fontsize=tfs, fontweight="bold",
                color=title_color or stroke, zorder=4)
    return (x, y, w, h)

def arrow(p1, p2, color="#5A6473", lw=2.0, style="-|>", dashed=False):
    ls = (0, (4, 3)) if dashed else "solid"
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=16,
                        linewidth=lw, color=color, zorder=2,
                        linestyle=ls, shrinkA=2, shrinkB=2)
    ax.add_patch(a)

def bottom(b):  x, y, w, h = b; return (x + w / 2, y)
def top(b):     x, y, w, h = b; return (x + w / 2, y + h)
def left(b):    x, y, w, h = b; return (x, y + h / 2)
def right(b):   x, y, w, h = b; return (x + w, y + h / 2)

# ---- Title ----
ax.text(0.6, 8.62, "Spec-RTL Sentinel", fontsize=27, fontweight="bold",
        color="#12324F", ha="left", va="center")
ax.text(0.62, 8.16, "Design Intent Ledger — agentic RAG for spec-faithful RTL verification",
        fontsize=13.5, color="#5A6473", ha="left", va="center")

# ---- Layer captions (left rail) ----
def caption(y, text):
    ax.text(0.12, y, text, fontsize=10.5, color="#8A93A2", rotation=90,
            ha="center", va="center", fontweight="bold")

# ---- Row 1: Sources ----
y1, h1 = 6.95, 0.95
has = box(0.9, y1, 2.55, h1, BLUE,   "HAS", "top-level intent", tfs=16)
mas = box(3.65, y1, 2.55, h1, PURPLE, "MAS", "micro-arch detail", tfs=16)
dec = box(6.40, y1, 3.05, h1, ORANGE, "Decisions / Reviews", "meetings · the as-agreed", tfs=15)
rtl = box(9.85, y1, 2.55, h1, GREEN,  "RTL", "the as-built", tfs=16)

# ---- Row 2: Parse / ingest agents ----
y2, h2 = 5.55, 0.9
hasp = box(0.9, y2, 2.55, h2, SLATE, "HAS Parser", "requirements", tfs=13, sfs=10)
clex = box(3.65, y2, 2.55, h2, SLATE, "Claim Extractor", "testable claims", tfs=12.5, sfs=10)
deci = box(6.40, y2, 3.05, h2, SLATE, "Decision Ingest", "authority + date", tfs=13, sfs=10)
rsc  = box(9.85, y2, 2.55, h2, SLATE, "RTL Scanner", "ports · regs · FSM", tfs=12.5, sfs=10)

for s, t in [(has, hasp), (mas, clex), (dec, deci), (rtl, rsc)]:
    arrow(bottom(s), top(t))

# ---- RAG store (spans the three doc parsers) ----
y3, h3 = 4.35, 0.72
rag = box(0.9, y3, 8.55, h3, TEAL,
          "Multi-Source RAG Knowledge Store",
          "grounded citations across HAS + MAS + Decisions", tfs=14, sfs=10.5)
for t in (hasp, clex, deci):
    arrow(bottom(t), (t[0] + t[2] / 2, y3 + h3))

# ---- Row 4: Reasoning agents ----
y4, h4 = 3.05, 0.85
resv = box(1.15, y4, 3.5, h4, SLATE, "Authority Resolver",
           "spec vs decisions → conflicts", tfs=12.5, sfs=9.5)
trac = box(5.05, y4, 4.0, h4, SLATE, "Traceability",
           "HAS → MAS → RTL · gaps", tfs=12.5, sfs=9.5)
arrow((3.0, y3), top(resv))
arrow((6.6, y3), top(trac))

# ---- Mapper (center-bottom) ----
y5, h5 = 1.55, 0.95
mapper = box(3.15, y5, 4.2, h5, ("#B01722", "#FBDDDF"),
             "Mapper / Drift Detection",
             "resolved claims  ×  RTL facts", tfs=14, sfs=10.5)
arrow(bottom(resv), (4.6, y5 + h5), color="#5A6473")
arrow(bottom(trac), (6.0, y5 + h5), color="#5A6473")
# RTL scanner down the right into mapper
arrow(bottom(rsc), (7.15, y5 + h5 * 0.7), color="#0E6B0E")

# ---- Sim checker + Report (below mapper) ----
y6, h6 = 0.35, 0.8
sim = box(3.15, y6, 2.0, h6, SLATE, "Sim Checker", "confirm", tfs=12, sfs=9)
rep = box(5.35, y6, 2.0, h6, SLATE, "Report Gen", "ledger", tfs=12, sfs=9)
arrow((4.15, y5), top(sim))
arrow(right(sim), left(rep), color="#5A6473")

# ---- Output panel (right rail) ----
px, py, pw, ph = 12.75, 0.35, 2.95, 8.05
panel = FancyBboxPatch((px, py), pw, ph,
                       boxstyle="round,pad=0.02,rounding_size=0.12",
                       linewidth=2.2, edgecolor="#12324F",
                       facecolor="#F7FAFD", zorder=1)
ax.add_patch(panel)
ax.text(px + pw / 2, py + ph - 0.4, "Drift Report", fontsize=15,
        fontweight="bold", color="#12324F", ha="center", va="center")
ax.text(px + pw / 2, py + ph - 0.8, "Design Intent Ledger", fontsize=10.5,
        color="#5A6473", ha="center", va="center", style="italic")

outcomes = [
    ("#0E6B0E", "✔", "Verified", "matches intent"),
    ("#B01722", "▮", "Drift", "confidence-scored"),
    ("#B01722", "✖", "Missing", "not implemented"),
    ("#B8560F", "⚠", "Spec Conflict", "auto-resolved"),
    ("#5C2D91", "▲", "Traceability Gap", "HAS not refined"),
    ("#0C6B78", "◆", "Undocumented", "explained by note"),
]
oy = py + ph - 1.5
for color, sym, label, sub in outcomes:
    ax.text(px + 0.35, oy, sym, fontsize=15, color=color, ha="center",
            va="center", fontweight="bold")
    ax.text(px + 0.62, oy + 0.09, label, fontsize=12, color="#1E1E1E",
            ha="left", va="center", fontweight="bold")
    ax.text(px + 0.62, oy - 0.22, sub, fontsize=9, color="#5A6473",
            ha="left", va="center")
    oy -= 0.92

ax.text(px + pw / 2, py + 0.45, "every finding cites\nits exact source",
        fontsize=9.5, color="#0C6B78", ha="center", va="center",
        style="italic", fontweight="bold")

arrow(right(rep), (px, py + 1.2), color="#12324F", lw=2.4)

# ---- Anti-hallucination callout ----
arrow(right(rag), (px + 0.2, y3 + 0.1), color="#0C6B78", lw=1.6, dashed=True)
ax.text(11.15, 4.75, "grounded\nevidence", fontsize=9, color="#0C6B78",
        ha="center", va="center", style="italic")

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
out = "docs/architecture.png"
import os
os.makedirs("docs", exist_ok=True)
fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("wrote", out)
