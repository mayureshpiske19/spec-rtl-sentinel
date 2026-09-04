"""Render a clean terminal-style PNG of the run_demo.py output for the demo scene."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
W, H = 1920, 1080
BG = (13, 17, 23)          # GitHub dark
BAR = (32, 37, 44)
GREEN = (63, 185, 80)
WHITE = (230, 237, 243)
GREY = (139, 148, 158)
RED = (248, 81, 73)
YELLOW = (210, 153, 34)
BLUE = (88, 166, 255)

# Curated lines to display (command + the punchy results).
LINES = [
    (GREEN, "PS> ", WHITE, "python run_demo.py"),
    (None, "", None, ""),
    (GREY, "", GREY, "Knowledge ingested : HAS=10, MAS=11, DECISION=3   (RAG store)"),
    (GREY, "", GREY, "RTL module         : zephyr_coss_top   (6 files scanned)"),
    (GREY, "", GREY, "MAS claims         : 28     HAS requirements : 9"),
    (None, "", None, ""),
    (WHITE, "", WHITE, "Milestone gate status (cumulative):"),
    (RED, "  [FAIL] 0.1  ", GREY, "Boundary - ports + CSR       <- CLAIM-01:drift"),
    (RED, "  [FAIL] 0.5  ", GREY, "+ Functional (FSM, datapath) <- CLAIM-13:missing"),
    (RED, "  [FAIL] 0.8  ", GREY, "+ Error / DFT / perf / debug <- CLAIM-22:missing"),
    (RED, "  [FAIL] 1.0  ", GREY, "Overall / integration        <- HAS-09:gap"),
    (None, "", None, ""),
    (WHITE, "", WHITE, "Findings:"),
    (RED,    "  [DRIFT]        ", WHITE, "CLAIM-01  m_axi_wdata is 32 bits but required 64   [DEC-01]"),
    (RED,    "  [MISSING]      ", WHITE, "CLAIM-13  control_fsm missing WRITE_OUT state"),
    (RED,    "  [MISSING]      ", WHITE, "CLAIM-22  PERF_MISS register not implemented"),
    (YELLOW, "  [CONFLICT]     ", WHITE, "INT_STATUS  MAS 0x054 vs review 0x058  -> RTL followed review"),
    (BLUE,   "  [UNDOCUMENTED] ", WHITE, "DBG_SCRATCH at 0x070  (temporary hook, per meeting note)"),
    (None, "", None, ""),
    (GREY, "", GREY, "Full report: reports/drift_report.md   HTML: reports/drift_report.html"),
]

def load_font(size, bold=False):
    for name in (["consolab.ttf","consola.ttf"] if not bold else ["consolab.ttf"]):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
        except Exception:
            pass
    return ImageFont.load_default()

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# window title bar
d.rectangle([0, 0, W, 70], fill=BAR)
for i, col in enumerate([(255,95,86),(255,189,46),(39,201,63)]):
    d.ellipse([40+i*46, 26, 40+i*46+22, 48], fill=col)
tf = load_font(26)
d.text((W/2-260, 22), "python  —  Spec-RTL Sentinel", font=tf, fill=GREY)

mono = load_font(34)
x0, y = 60, 110
lh = 46
for pre_col, pre, col, text in LINES:
    if not text and not pre:
        y += lh; continue
    x = x0
    if pre:
        d.text((x, y), pre, font=mono, fill=pre_col)
        x += d.textlength(pre, font=mono)
    d.text((x, y), text, font=mono, fill=col if col else WHITE)
    y += lh

img.save(os.path.join(HERE, "vo", "terminal.png"))
print("wrote terminal.png")
