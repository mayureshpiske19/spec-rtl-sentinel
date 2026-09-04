"""
Render a draw.io (.drawio / mxGraphModel) file to a PNG.

A dependency-light renderer (matplotlib) that draws the vertices, labels and
orthogonal edges from a draw.io export. Keeps docs/architecture.png in sync with
docs/architecture.drawio without needing the draw.io desktop app or a browser.

Usage:
    python presentation/render_drawio.py docs/architecture.drawio docs/architecture.png
"""

from __future__ import annotations

import html
import re
import sys
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch


def _style(s: str) -> dict:
    out = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
        elif part.strip():
            out[part.strip()] = True
    return out


def _text(value: str):
    """Return (title, subtitle) from a draw.io HTML value."""
    if value is None:
        return "", ""
    v = value.replace("<br>", "\n").replace("<br/>", "\n")
    v = re.sub(r"&nbsp;", " ", v)
    v = re.sub(r"<[^>]+>", "", v)
    v = html.unescape(v)
    lines = [ln.strip() for ln in v.split("\n") if ln.strip()]
    if not lines:
        return "", ""
    return lines[0], " ".join(lines[1:])


def render(src: str, out: str) -> None:
    tree = ET.parse(src)
    root = tree.getroot()
    model = root.find(".//mxGraphModel")
    cells = model.findall(".//mxCell")

    verts, edges = {}, []
    for c in cells:
        geo = c.find("mxGeometry")
        style = _style(c.get("style", ""))
        if c.get("vertex") == "1" and geo is not None:
            verts[c.get("id")] = {
                "x": float(geo.get("x", 0)), "y": float(geo.get("y", 0)),
                "w": float(geo.get("width", 0)), "h": float(geo.get("height", 0)),
                "style": style, "value": c.get("value", ""),
            }
        elif c.get("edge") == "1":
            pts = []
            arr = geo.find("Array[@as='points']") if geo is not None else None
            if arr is not None:
                for p in arr.findall("mxPoint"):
                    pts.append((float(p.get("x")), float(p.get("y"))))
            edges.append({
                "source": c.get("source"), "target": c.get("target"),
                "style": style, "value": c.get("value", ""), "points": pts,
                "geo": geo,
            })

    xs = [v["x"] for v in verts.values()] + [v["x"] + v["w"] for v in verts.values()]
    ys = [v["y"] for v in verts.values()] + [v["y"] + v["h"] for v in verts.values()]
    minx, maxx = min(xs) - 40, max(xs) + 40
    miny, maxy = min(ys) - 40, max(ys) + 40
    W, H = maxx - minx, maxy - miny

    fig, ax = plt.subplots(figsize=(W / 100.0, H / 100.0), dpi=200)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(maxy, miny)  # invert Y (draw.io y grows downward)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def center(vid):
        v = verts[vid]
        return (v["x"] + v["w"] / 2, v["y"] + v["h"] / 2)

    # edges first (under boxes)
    for e in edges:
        st = e["style"]
        color = st.get("strokeColor", "#5A6473")
        lw = float(st.get("strokeWidth", 1)) * 0.9
        dashed = st.get("dashed") == "1"
        path = []
        src = e["source"]; tgt = e["target"]
        if src and src in verts:
            path.append(center(src))
        else:
            geo = e["geo"]
            sp = geo.find("mxPoint[@as='sourcePoint']") if geo is not None else None
            if sp is not None:
                path.append((float(sp.get("x")), float(sp.get("y"))))
        path.extend(e["points"])
        if tgt and tgt in verts:
            path.append(center(tgt))
        else:
            geo = e["geo"]
            tp = geo.find("mxPoint[@as='targetPoint']") if geo is not None else None
            if tp is not None:
                path.append((float(tp.get("x")), float(tp.get("y"))))
        if len(path) < 2:
            continue
        # draw segments, arrow on last
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            last = (i == len(path) - 2)
            arr = FancyArrowPatch(
                a, b, arrowstyle="-|>" if last else "-",
                mutation_scale=13, linewidth=lw, color=color,
                linestyle=(0, (5, 3)) if dashed else "solid",
                shrinkA=0, shrinkB=(6 if last else 0), zorder=1)
            ax.add_patch(arr)
        if e["value"]:
            mid = path[len(path) // 2]
            ax.text(mid[0], mid[1] - 8, _text(e["value"])[0], fontsize=8,
                    color=st.get("fontColor", "#333"), ha="center", va="center",
                    style="italic", zorder=5)

    # vertices
    for v in verts.values():
        st = v["style"]
        x, y, w, h = v["x"], v["y"], v["w"], v["h"]
        is_text = st.get("text") is True or "text" in st
        title, sub = _text(v["value"])
        if is_text:
            fs = float(st.get("fontSize", 12)) * 0.5 + 6
            fc = st.get("fontColor", "#242424")
            al = st.get("align", "left")
            hx = x if al == "left" else (x + w / 2 if al == "center" else x + w)
            ha = {"left": "left", "center": "center", "right": "right"}.get(al, "left")
            txt = title + (("  " + sub) if sub else "")
            ax.text(hx, y + h / 2, txt, fontsize=fs, color=fc, ha=ha,
                    va="center", fontweight="bold" if st.get("fontStyle") == "1"
                    or float(st.get("fontSize", 12)) >= 24 else "normal",
                    zorder=6)
            continue
        fill = st.get("fillColor", "#ffffff")
        stroke = st.get("strokeColor", "#333333")
        sw = float(st.get("strokeWidth", 1))
        box = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0,rounding_size=8",
            linewidth=sw, edgecolor=stroke, facecolor=fill, zorder=3)
        ax.add_patch(box)
        cx = x + w / 2
        fc = st.get("fontColor", "#242424")
        if sub:
            ax.text(cx, y + h * 0.40, title, ha="center", va="center",
                    fontsize=10.5, fontweight="bold", color=fc, zorder=4)
            ax.text(cx, y + h * 0.66, sub, ha="center", va="center",
                    fontsize=8.5, color="#444", zorder=4)
        else:
            ax.text(cx, y + h / 2, title, ha="center", va="center",
                    fontsize=10.5, fontweight="bold", color=fc, zorder=4)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight",
                pad_inches=0.12)
    print("wrote", out)


if __name__ == "__main__":
    s = sys.argv[1] if len(sys.argv) > 1 else "docs/architecture.drawio"
    o = sys.argv[2] if len(sys.argv) > 2 else "docs/architecture.png"
    render(s, o)
