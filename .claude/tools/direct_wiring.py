#!/usr/bin/env python3
"""Generate hardware/images/direct-wiring.svg: boards drawn in the orientation they
take in the box (seen from the back, display face down), every pad tagged with the
colour and number of the wire soldered to it.
Run from the repo root:   python3 .claude/tools/direct_wiring.py
"""
import os

W, H = 1190, 960
S = 9  # px per mm
COL = {"red": "#d62728", "black": "#111111", "yellow": "#f2c200", "blue": "#1e63d6",
       "white": "#ffffff", "turq": "#1cc7b6"}
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
     f'font-family="Helvetica, Arial, sans-serif">', f'<rect width="{W}" height="{H}" fill="#eceff1"/>']


def t(x, y, s, size=11, anchor="start", fill="#222", weight="normal", rot=None):
    tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
    o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
             f'font-weight="{weight}"{tr}>{s}</text>')


def box(x, y, w, h, fill, stroke="#111", rx=6, extra=""):
    o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" rx="{rx}" {extra}/>')


def pad(x, y, used=True):
    o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{"#e8c34a" if used else "#cfd3d6"}" stroke="#111" stroke-width="1.2"/>')


def stub(x, y, dx, dy, wires, name=None, name_fill="#fff", ln=30):
    """wires: list of (label, colour), all the same colour. One stub, one tag per wire."""
    col = wires[0][1]
    x1, y1, x2, y2 = x + dx * 6, y + dy * 6, x + dx * ln, y + dy * ln
    o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#6b7278" stroke-width="6.4" stroke-linecap="round"/>')
    o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{COL[col]}" stroke-width="3.8" stroke-linecap="round"/>')
    for i, (lab, _) in enumerate(wires):
        lx = x2 + dx * (13 + i * 24) if dx else x2
        ly = y2 + 4 if dx else y2 + dy * (12 + i * 16) + 4
        o.append(f'<rect x="{lx - 11:.1f}" y="{ly - 11:.1f}" width="22" height="14" rx="3" fill="#fff" stroke="#444" stroke-width=".8"/>')
        t(lx, ly, lab, 10, "middle", "#111", "bold")
    if name:
        if dx:
            t(x - dx * 10, y + 4, name, 10.5, "end" if dx > 0 else "start", name_fill, "bold")
        else:
            t(x + 4, y - dy * 10, name, 10, "end" if dy > 0 else "start", name_fill, "bold", rot=-90)


t(W / 2, 30, "Paata — direct wiring, seen from the back (display face down)", 19, "middle", "#111", "bold")
t(W / 2, 50, "Boards are in the orientation they take in the box, spread apart so the pads are readable. "
  "Each tag is one wire: its colour and its number in the wire list.", 11.5, "middle", "#444")

# ------------------------------------------------------------------ encoder (top of the side column, back side up)
nx0, ny0 = 80, 105
nw, nh = 21.7 * S, 26 * S
box(nx0, ny0, nw, nh, "#16181c")
t(nx0 + nw / 2, ny0 - 22, "Encoder board, BACK side up", 12, "middle", "#111", "bold")
t(nx0 + nw / 2, ny0 - 8, "shaft points down, through the front of the case", 10, "middle", "#444")
for i in range(3):
    o.append(f'<circle cx="{nx0 + 45 + i * 26}" cy="{ny0 + 26}" r="7" fill="#c9ccd1" stroke="#555"/>')
for i, n in enumerate(("R1", "R2", "R3")):
    box(nx0 + 44, ny0 + 52 + i * 34, 42, 20, "#2b2f36", "#aaa", 2)
    t(nx0 + 36, ny0 + 66 + i * 34, n, 9, "end", "#ddd")
for cy in (ny0 + 40, ny0 + 190):
    o.append(f'<circle cx="{nx0 + nw - 44}" cy="{cy}" r="13" fill="#eceff1" stroke="#777"/>')
t(nx0 + nw - 44, ny0 + 120, "mounting", 8.5, "middle", "#aaa")
t(nx0 + nw - 44, ny0 + 131, "holes", 8.5, "middle", "#aaa")
for i, (n, w) in enumerate((("CLK", ("14", "turq")), ("DT", ("15", "yellow")), ("SW", ("16", "white")),
                            ("+", ("R3", "red")), ("GND", ("K3", "black")))):
    x, y = nx0 + 24 + i * 23, ny0 + nh - 16
    pad(x, y)
    t(x, y - 10, n, 8.5, "middle", "#fff", "bold")
    stub(x, y, 0, 1, [w], ln=34)

# ------------------------------------------------------------------ ESP32 (bottom of the side column, USB down)
ex0, ey0 = 102, 560
box(ex0, ey0, 18 * S, 23.8 * S, "#1f4e8c", "#0c2a52")
box(ex0 + 45, ey0 + 23.8 * S - 16, 72, 34, "#c8c8c8", "#666", 3)
t(ex0 + 81, ey0 + 23.8 * S + 34, "USB-C (bottom edge)", 10, "middle", "#333")
t(ex0 + 81, ey0 + 128, "ESP32-S3-Zero", 12.5, "middle", "#fff", "bold")
t(ex0 + 81, ey0 + 144, "component side up", 9.5, "middle", "#cfe0f5")
t(ex0 + 81, ey0 + 157, "USB end down", 9.5, "middle", "#cfe0f5")
right = [("5V", []), ("GND", [("K1", "black"), ("K4", "black")]), ("3V3", [("R1", "red")]), ("1", [("14", "turq")]),
         ("2", [("15", "yellow")]), ("3", [("7", "turq")]), ("4", [("6", "white")]), ("5", [("11", "blue")]),
         ("6", [("12", "yellow")])]
left = [("TX", []), ("RX", []), ("13", [("8", "white")]), ("12", [("1", "yellow")]), ("11", [("2", "blue")]),
        ("10", [("3", "yellow")]), ("9", [("4", "turq")]), ("8", [("5", "white")]), ("7", [("13", "turq")])]
ys = [ey0 + (23.8 - 2.3 - i * 2.54) * S for i in range(9)]
for i in range(9):
    y = ys[i]
    for (n, w), x, d in ((right[i], ex0 + 18 * S, 1), (left[i], ex0, -1)):
        pad(x, y, bool(w))
        if w:
            stub(x, y, d, 0, w, n)
        else:
            t(x - d * 10, y + 4, n, 10.5, "end" if d > 0 else "start", "#9db4d3", "bold")
# inner pads: a short column just inside the left edge, level with pads 7, 8, 9
for (n, lab, col), y in zip((("14", "16", "white"), ("15", "17", "blue"), ("16", "18", "yellow")), (ys[8], ys[7], ys[6])):
    x = ex0 + 44
    pad(x, y)
    t(x + 9, y + 4, n, 9.5, "start", "#fff", "bold")
    o.append(f'<line x1="{x + 26}" y1="{y}" x2="{x + 44}" y2="{y}" stroke="#6b7278" stroke-width="6.4" stroke-linecap="round"/>')
    o.append(f'<line x1="{x + 26}" y1="{y}" x2="{x + 44}" y2="{y}" stroke="{COL[col]}" stroke-width="3.8" stroke-linecap="round"/>')
    o.append(f'<rect x="{x + 47}" y="{y - 7}" width="22" height="14" rx="3" fill="#fff" stroke="#444" stroke-width=".8"/>')
    t(x + 58, y + 4, lab, 10, "middle", "#111", "bold")
t(ex0 + 81, ey0 + 96, "inner pads 14 · 15 · 16", 9.5, "middle", "#cfe0f5")

# ------------------------------------------------------------------ display (back view)
px0, py0 = 555, 222
dw, dh = 34 * S, 58.2 * S
box(px0 - 19 * S, py0 + 21 * S, 19 * S + 60, 24 * S, "#dfe7f5", "#3b5b92", 4, 'stroke-dasharray="7 5"')
t(px0 - 9.5 * S, py0 + 32 * S, "SD adapter", 12, "middle", "#27437a", "bold")
t(px0 - 9.5 * S, py0 + 32 * S + 15, "sticks out 19 mm", 10, "middle", "#27437a")
t(px0 - 9.5 * S, py0 + 32 * S + 29, "on this side", 10, "middle", "#27437a")
box(px0, py0, dw, dh, "#b3261e", "#7f1010")
box(px0, py0 + 18 * S, 19 * S, 30 * S, "#c9ccd1", "#666", 2)
t(px0 + 9.5 * S, py0 + 33 * S, "SD slot", 12, "middle", "#333", "bold")
t(px0 + 26.5 * S, py0 + 31 * S, "Display", 14, "middle", "#fff", "bold")
t(px0 + 26.5 * S, py0 + 31 * S + 16, "back side up", 10, "middle", "#ffd9d5")
t(px0 + 26.5 * S, py0 + 31 * S + 30, "(screen faces", 10, "middle", "#ffd9d5")
t(px0 + 26.5 * S, py0 + 31 * S + 44, "the desk)", 10, "middle", "#ffd9d5")
hdr = [("VCC", [("R2", "red"), ("R3", "red")]), ("GND", [("K2", "black"), ("K3", "black")]), ("CS", [("3", "yellow")]),
       ("RESET", [("5", "white")]), ("A0", [("4", "turq")]), ("SDA", [("2", "blue"), ("10", "blue")]),
       ("SCK", [("1", "yellow"), ("9", "yellow")]), ("LED", [("6", "white")])]
for i, (n, w) in enumerate(hdr):
    x, y = px0 + (7.2 + i * 2.54) * S, py0 + 3 * S
    pad(x, y)
    t(x + 4, y - 9, n, 9.5, "start", "#fff", "bold", rot=-90)
    stub(x, y, 0, 1, w, ln=28)
sd = [("SD_CS", ("7", "turq")), ("SD_MOSI", ("10", "blue")), ("SD_MISO", ("8", "white")), ("SD_SCK", ("9", "yellow"))]
for i, (n, w) in enumerate(sd):
    x, y = px0 + (13.2 + i * 2.54) * S, py0 + 55 * S
    pad(x, y)
    stub(x, y, 0, 1, [w], ln=26)
    t(x + 4, y - 10, n, 9.5, "start", "#fff", "bold", rot=-90)

# ------------------------------------------------------------------ DAC (lies on the back of the display, jack up)
dx0, dy0 = 915, 150
box(dx0 + 58, dy0 - 30, 66, 36, "#3a3a3a", "#000", 3)
t(dx0 + 91, dy0 - 50, "DAC: sits on the back of the display,", 10.5, "middle", "#111", "bold")
t(dx0 + 91, dy0 - 37, "jack at the top edge", 10.5, "middle", "#111", "bold")
box(dx0, dy0, 20.2 * S, 28 * S, "#22252b")
t(dx0 + 70, dy0 + 120, "DAC", 15, "middle", "#fff", "bold")
t(dx0 + 70, dy0 + 138, "PCM5102A", 10.5, "middle", "#cfcfcf")
t(dx0 + 70, dy0 + 152, "component side up", 9.5, "middle", "#cfcfcf")
dac = [("Rout", []), ("G", []), ("Lout", []), ("BCK", [("11", "blue")]), ("DIN", [("13", "turq")]),
       ("WSEL", [("12", "yellow")]), ("GND", [("K1", "black"), ("K2", "black")]), ("VIN", [("R1", "red"), ("R2", "red")])]
for i, (n, w) in enumerate(dac):
    y = dy0 + (5.6 + i * 2.54) * S
    x = dx0 + 18.9 * S
    pad(x, y, bool(w))
    if w:
        stub(x, y, 1, 0, w, n)
    else:
        t(x - 10, y + 4, n, 10.5, "end", "#8d9399", "bold")

# ------------------------------------------------------------------ breadboard with the two buttons
bx0, by0 = 930, 440
box(bx0, by0, 160, 176, "#f3efe4", "#b9b29c")
t(bx0 + 80, by0 + 18, "Breadboard", 12, "middle", "#333", "bold")
t(bx0 + 80, by0 + 32, "(buttons only, for now)", 9.5, "middle", "#555")
for i, (n, lab, col) in enumerate((("BACK", "17", "blue"), ("OK", "18", "yellow"))):
    y = by0 + 66 + i * 50
    box(bx0 + 66, y - 15, 30, 30, "#2d2d2d", "#000", 3)
    t(bx0 + 81, y + 4, n, 8.5, "middle", "#fff", "bold")
    stub(bx0 + 66, y, -1, 0, [(lab, col)], ln=28)
    o.append(f'<line x1="{bx0 + 96}" y1="{y}" x2="{bx0 + 132}" y2="{y}" stroke="#111" stroke-width="3"/>')
o.append(f'<line x1="{bx0 + 132}" y1="{by0 + 52}" x2="{bx0 + 132}" y2="{by0 + 150}" stroke="#111" stroke-width="3"/>')
t(bx0 + 140, by0 + 100, "−", 14, "middle", "#111", "bold")
pad(bx0 + 132, by0 + 150)
stub(bx0 + 132, by0 + 150, -1, 0, [("K4", "black")], ln=28)

# ------------------------------------------------------------------ inset: how it closes up
ix, iy, k = 935, 690, 2.6
t(ix, iy - 30, "How it closes up (draft)", 12, "start", "#111", "bold")
t(ix, iy - 15, "back view, about 62 × 64 mm", 10, "start", "#444")
box(ix, iy, 62 * k, 64 * k, "none", "#555", 6, 'stroke-dasharray="5 4"')
box(ix + 26 * k, iy + 3 * k, 34 * k, 58.2 * k, "#b3261e", "#7f1010", 2)
box(ix + 7 * k, iy + 24 * k, 40 * k, 24 * k, "#dfe7f5", "#3b5b92", 2)
box(ix + 2 * k, iy + 2 * k, 21.7 * k, 26 * k, "#16181c", "#000", 2)
box(ix + 4 * k, iy + 38 * k, 17.9 * k, 23.8 * k, "#1f4e8c", "#0c2a52", 2)
box(ix + 27 * k, iy + 1 * k, 20.2 * k, 28 * k, "#22252b", "#fff", 2, 'fill-opacity=".85"')
t(ix + 13 * k, iy + 16 * k, "encoder", 8.5, "middle", "#fff")
t(ix + 13 * k, iy + 52 * k, "ESP32", 9, "middle", "#fff")
t(ix + 37 * k, iy + 16 * k, "DAC", 9, "middle", "#fff")
t(ix + 52 * k, iy + 54 * k, "display", 9, "middle", "#fff")
t(ix + 30 * k, iy + 38 * k, "SD adapter", 8.5, "middle", "#27437a")

# ------------------------------------------------------------------ colour key
kx, ky = 30, 862
box(kx - 10, ky - 22, 800, 104, "#fafafa", "#bbb")
t(kx, ky - 4, "Wire colours", 12, "start", "#111", "bold")
key = [("red", "3.3 V  (R1–R3)"), ("black", "GND  (K1–K4)"), ("yellow", "1, 3, 9, 12, 15, 18"),
       ("blue", "2, 10, 11, 17"), ("white", "5, 6, 8, 16"), ("turq", "4, 7, 13, 14")]
for i, (c, lab) in enumerate(key):
    x, y = kx + (i % 3) * 262, ky + 18 + (i // 3) * 22
    o.append(f'<line x1="{x}" y1="{y}" x2="{x + 34}" y2="{y}" stroke="#6b7278" stroke-width="7" stroke-linecap="round"/>')
    o.append(f'<line x1="{x}" y1="{y}" x2="{x + 34}" y2="{y}" stroke="{COL[c]}" stroke-width="4.2" stroke-linecap="round"/>')
    t(x + 44, y + 4, {"turq": "turquoise"}.get(c, c) + ":  " + lab, 11)
t(kx, ky + 66, "A pad with two tags takes two wires. Grey pads stay empty. "
  "The same number appears at both ends of a wire.", 10.5, "start", "#444")

o.append("</svg>")
dst = os.path.join(os.path.dirname(__file__), "..", "..", "hardware", "images", "direct-wiring.svg")
open(dst, "w").write("\n".join(o))
print("wrote", os.path.normpath(dst))
