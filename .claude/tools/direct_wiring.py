#!/usr/bin/env python3
"""Generate hardware/images/direct-wiring.svg: a pad-by-pad wiring card for the
header-less bench build.  Run from the repo root:
    python3 .claude/tools/direct_wiring.py
"""
import os

W, H = 1040, 840
RED, BLK = "#d62728", "#2b2b2b"
C = dict(bck="#1f77b4", wsel="#17becf", din="#8e44ad", sck="#ff7f0e", sda="#2ca02c", a0="#b5a400",
         rst="#8c564b", cs="#e377c2", led="#e0b800", dt="#00897b", clk="#5fbf00", sdcs="#6c3fc4",
         miso="#c2185b", sw="#607d8b", back="#795548", ok="#3f51b5", none="#bbbbbb")
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
     f'font-family="Helvetica, Arial, sans-serif">', f'<rect width="{W}" height="{H}" fill="#fff"/>']


def t(x, y, s, size=11, anchor="start", fill="#222", weight="normal"):
    o.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
             f'font-weight="{weight}">{s}</text>')


def box(x, y, w, h, fill, stroke="#111", rx=8):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" rx="{rx}"/>')


def pad(x, y, kind):
    """kind: s = solder, p = plug a jumper socket on the existing pin, n = unused"""
    if kind == "p":
        o.append(f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10" fill="#fff" stroke="#111" stroke-width="1.6"/>')
    elif kind == "s":
        o.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#e8c34a" stroke="#111" stroke-width="1.4"/>')
    else:
        o.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#fff" stroke="#999" stroke-width="1.2"/>')


def tag(x, y, label, color, side="right"):
    """coloured wire stub + destination label, starting at a pad"""
    if color == C["none"]:
        t(x + (14 if side == "right" else -14), y + 4, label, 10.5, "start" if side == "right" else "end", "#999")
        return
    d = 1 if side == "right" else -1
    o.append(f'<line x1="{x + 7 * d}" y1="{y}" x2="{x + 46 * d}" y2="{y}" stroke="#1b1b1b" stroke-opacity=".5" stroke-width="6"/>')
    o.append(f'<line x1="{x + 7 * d}" y1="{y}" x2="{x + 46 * d}" y2="{y}" stroke="{color}" stroke-width="4"/>')
    t(x + 52 * d, y + 4, label, 11.5, "start" if side == "right" else "end")


t(W / 2, 32, "Paata — direct wiring, no headers (what goes on each pad)", 19, "middle", "#111", "bold")
t(W / 2, 52, "Each coloured stub is one wire; the label says where its other end goes. "
  "Blocks show pad order as printed on each board, not where the boards sit.", 11.5, "middle", "#555")

# ---------- ESP32 ----------
ex, ey, ew, eh = 420, 80, 200, 372
box(ex, ey, ew, eh, "#1f4e8c", "#0c2a52")
box(ex + 70, ey - 12, 60, 30, "#c8c8c8", "#666", 3)
t(ex + 100, ey + 8, "USB-C", 9.5, "middle", "#333")
t(ex + 100, ey + 190, "ESP32-S3-Zero", 14, "middle", "#fff", "bold")
t(ex + 100, ey + 208, "top view", 10.5, "middle", "#cfe0f5")
left = [("5V", "not used", C["none"], "n"), ("GND", "breadboard − rail", BLK, "s"),
        ("3V3", "breadboard + rail", RED, "s"), ("1", "Encoder CLK", C["clk"], "s"),
        ("2", "Encoder DT", C["dt"], "s"), ("3", "Display SD_CS pad", C["sdcs"], "s"),
        ("4", "Display LED", C["led"], "s"), ("5", "DAC BCK", C["bck"], "s"), ("6", "DAC WSEL", C["wsel"], "s")]
right = [("TX", "not used", C["none"], "n"), ("RX", "not used", C["none"], "n"),
         ("13", "Display SD_MISO pad", C["miso"], "s"), ("12", "Display SCK", C["sck"], "s"),
         ("11", "Display SDA", C["sda"], "s"), ("10", "Display CS", C["cs"], "s"),
         ("9", "Display A0", C["a0"], "s"), ("8", "Display RESET", C["rst"], "s"), ("7", "DAC DIN", C["din"], "s")]
for i, (n, lab, col, k) in enumerate(left):
    y = ey + 48 + i * 34
    pad(ex, y, k); t(ex + 12, y + 4, n, 11, "start", "#fff", "bold"); tag(ex, y, lab, col, "left")
for i, (n, lab, col, k) in enumerate(right):
    y = ey + 48 + i * 34
    pad(ex + ew, y, k); t(ex + ew - 12, y + 4, n, 11, "end", "#fff", "bold"); tag(ex + ew, y, lab, col, "right")
for i, (n, lab, col) in enumerate((("14", "Encoder SW", C["sw"]), ("15", "BACK button (breadboard)", C["back"]),
                                   ("16", "OK button (breadboard)", C["ok"]))):
    x = ex + 60 + i * 40
    pad(x, ey + eh - 22, "s"); t(x, ey + eh - 34, n, 10, "middle", "#fff", "bold")
    yy = ey + eh + 22 + i * 20
    o.append(f'<polyline points="{x},{ey + eh - 15} {x},{yy} {ex + ew + 6},{yy}" fill="none" stroke="{col}" stroke-width="4"/>')
    t(ex + ew + 12, yy + 4, lab, 11.5)
t(ex + 100, ey + eh - 52, "inner pads", 9.5, "middle", "#cfe0f5")

# ---------- lower blocks ----------
by = 560


def block(x, w, h, title, sub, fill, rows, textfill="#fff"):
    box(x, by, w, h, fill)
    t(x + 12, by + 22, title, 13, "start", textfill, "bold")
    t(x + 12, by + 38, sub, 9.5, "start", textfill)
    for i, (n, lab, col, k) in enumerate(rows):
        y = by + 62 + i * 24
        pad(x + 18, y, k)
        t(x + 30, y + 4, n, 10.5, "start", textfill, "bold")
        if col == C["none"]:
            t(x + 96, y + 4, lab, 10, "start", "#cfcfcf" if textfill == "#fff" else "#888")
        else:
            o.append(f'<line x1="{x + 92}" y1="{y}" x2="{x + 122}" y2="{y}" stroke="#fff" stroke-opacity=".7" stroke-width="6"/>')
            o.append(f'<line x1="{x + 92}" y1="{y}" x2="{x + 122}" y2="{y}" stroke="{col}" stroke-width="4"/>')
            t(x + 128, y + 4, lab, 10.5, "start", textfill)


block(20, 285, 262, "Display (1.8\" TFT)", "header pins already fitted; SD pads bare", "#b3261e",
      [("LED", "GPIO 4", C["led"], "p"), ("SCK", "GPIO 12", C["sck"], "p"), ("SDA", "GPIO 11", C["sda"], "p"),
       ("A0", "GPIO 9", C["a0"], "p"), ("RESET", "GPIO 8", C["rst"], "p"), ("CS", "GPIO 10", C["cs"], "p"),
       ("GND", "breadboard − rail", BLK, "p"), ("VCC", "breadboard + rail", RED, "p")])
# SD pads column inside the display block
sx = 20 + 285 - 4
box(318, by, 232, 262, "#8e1f18")
t(330, by + 22, "Display SD pads", 13, "start", "#fff", "bold")
t(330, by + 38, "on the far edge of the same board", 9.5, "start", "#fff")
for i, (n, lab, col) in enumerate((("SD_CS", "GPIO 3", C["sdcs"]), ("SD_MISO", "GPIO 13", C["miso"]),
                                   ("SD_SCK", "display SCK pin *", C["sck"]), ("SD_MOSI", "display SDA pin *", C["sda"]))):
    y = by + 62 + i * 24
    pad(336, y, "s"); t(348, y + 4, n, 10.5, "start", "#fff", "bold")
    o.append(f'<line x1="{410}" y1="{y}" x2="{440}" y2="{y}" stroke="#fff" stroke-opacity=".7" stroke-width="6"/>')
    o.append(f'<line x1="{410}" y1="{y}" x2="{440}" y2="{y}" stroke="{col}" stroke-width="4"/>')
    t(446, y + 4, lab, 10.5, "start", "#fff")
t(330, by + 176, "* short link on the display itself:", 9.5, "start", "#fff")
t(330, by + 190, "solder to the back of the header", 9.5, "start", "#fff")
t(330, by + 204, "pin, so the ESP32 needs only one", 9.5, "start", "#fff")
t(330, by + 218, "wire each for SCK and SDA.", 9.5, "start", "#fff")

block(566, 220, 262, "DAC (PCM5102A)", "no header: solder to the pads", "#22252b",
      [("VIN", "breadboard + rail", RED, "s"), ("GND", "breadboard − rail", BLK, "s"),
       ("WSEL", "GPIO 6", C["wsel"], "s"), ("DIN", "GPIO 7", C["din"], "s"), ("BCK", "GPIO 5", C["bck"], "s"),
       ("Lout", "not used", C["none"], "n"), ("G", "not used", C["none"], "n"), ("Rout", "not used", C["none"], "n")])
block(844, 176, 190, "Encoder", "pins already fitted", "#3a3f47",
      [("GND", "− rail", BLK, "p"), ("+", "+ rail", RED, "p"), ("SW", "pad 14", C["sw"], "p"),
       ("DT", "GPIO 2", C["dt"], "p"), ("CLK", "GPIO 1", C["clk"], "p")])

# ---------- breadboard strip ----------
bx, bw, bby = 20, 380, 470
box(bx, bby, bw, 76, "#f3efe4", "#b9b29c")
t(bx + 10, bby + 16, "Small breadboard: power rails + the two buttons", 11, "start", "#333", "bold")
o.append(f'<line x1="{bx + 12}" y1="{bby + 30}" x2="{bx + 190}" y2="{bby + 30}" stroke="{RED}" stroke-width="2"/>')
t(bx + 196, bby + 34, "+ rail = 3V3 (4 wires)", 10, "start", "#333")
o.append(f'<line x1="{bx + 12}" y1="{bby + 46}" x2="{bx + 190}" y2="{bby + 46}" stroke="#1f4fb4" stroke-width="2"/>')
t(bx + 196, bby + 50, "− rail = GND (4 wires + 2 buttons)", 10, "start", "#333")
t(bx + 12, bby + 67, "BACK: one side to pad 15, other side to − rail.  OK: pad 16 and − rail.", 10, "start", "#333")

# ---------- legend ----------
lx, ly = 800, 478
pad(lx + 8, ly, "s"); t(lx + 22, ly + 4, "solder the wire to this pad", 11)
pad(lx + 8, ly + 20, "p"); t(lx + 22, ly + 24, "push a jumper socket onto the existing pin", 11)
pad(lx + 8, ly + 40, "n"); t(lx + 22, ly + 44, "leave empty", 11)

o.append("</svg>")
dst = os.path.join(os.path.dirname(__file__), "..", "..", "hardware", "images", "direct-wiring.svg")
open(dst, "w").write("\n".join(o))
print("wrote", os.path.normpath(dst))
