#!/usr/bin/env python3
"""Draws hardware/images/perfboard-layout.svg: parts on the 29 x 35 hole perf board.

Two panels: component side, and solder side (mirrored left to right).
Coordinates are in hole pitches (2.54 mm); hole (c, r) = column c, row r.
"""
from pathlib import Path

P = 26          # px per hole pitch
COLS, ROWS = 29, 35
W, H = 1960, 1130
COL = {"red": "#d92b2b", "black": "#222", "yellow": "#f2c81e", "blue": "#2f6fdd",
       "white": "#ffffff", "turq": "#22c7b8", None: "#d9a441"}

# pins: (col, row, label, wire colour, label side: l/r/u/d)
ESP_L = ["5V", "GND", "3V3", "1", "2", "3", "4", "5", "6"]
ESP_LC = ["red", "black", "red", "turq", "yellow", "turq", "white", "blue", "yellow"]
ESP_R = ["TX", "RX", "13", "12", "11", "10", "9", "8", "7"]
ESP_RC = [None, None, "white", "yellow", "blue", "yellow", "turq", "white", "turq"]
DAC = ["Rout", "G", "Lout", "BCK", "DIN", "WSEL", "GND", "VIN"]
DAC_C = [None, None, None, "blue", "turq", "yellow", "black", "red"]
TFT = ["LED", "SCK", "SDA", "A0", "RST", "CS", "GND", "VCC"]
TFT_C = ["white", "yellow", "blue", "turq", "white", "yellow", "black", "red"]
SD = ["SCK", "MISO", "MOSI", "CS"]
SD_C = ["yellow", "white", "blue", "turq"]
ENC = ["GND", "+", "SW", "DT", "CLK"]
ENC_C = ["black", "red", "white", "yellow", "turq"]

pins = []
pins += [(10, 1 + i, n, c, "r") for i, (n, c) in enumerate(zip(ESP_L, ESP_LC))]
pins += [(16, 1 + i, n, c, "l") for i, (n, c) in enumerate(zip(ESP_R, ESP_RC))]
pins += [(8, 4 + i, n, c, "l") for i, (n, c) in enumerate(zip(DAC, DAC_C))]
pins += [(20 + i, 2, n, c, "d") for i, (n, c) in enumerate(zip(TFT, TFT_C))]
pins += [(22 + i, 23, n, c, "u") for i, (n, c) in enumerate(zip(SD, SD_C))]
pins += [(24 + i, 35, n, c, "u") for i, (n, c) in enumerate(zip(ENC, ENC_C))]
pins += [(11, 29, "BACK", "blue", "u"), (13, 32, "GND", "black", "d"),
         (16, 29, "OK", "yellow", "u"), (18, 32, "GND", "black", "d"),
         (9, 26, "", "red", "u"), (10, 26, "", "red", "u"), (11, 26, "", None, "u"),
         (14, 11, "14", "white", "d"), (15, 11, "15", "blue", "d"), (16, 11, "16", "yellow", "d")]


def panel(ox, oy, mirror, title, sub):
    o = []
    X = lambda c: ox + ((COLS + 1 - c) if mirror else c) * P
    Y = lambda r: oy + r * P

    def box(c0, r0, c1, r1, fill, stroke="#000", rx=4, op=1.0, dash=False):
        x0, x1 = sorted((X(c0), X(c1)))
        d = ' stroke-dasharray="6 4"' if dash else ""
        o.append(f'<rect x="{x0:.1f}" y="{Y(r0):.1f}" width="{x1 - x0:.1f}" height="{Y(r1) - Y(r0):.1f}" '
                 f'rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="1.2"{d}/>')

    def t(c, r, s, size=11, anchor="middle", fill="#111", weight="normal"):
        o.append(f'<text x="{X(c):.1f}" y="{Y(r) + size * .35:.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'fill="{fill}" font-weight="{weight}">{s}</text>')

    o.append(f'<text x="{ox + 15 * P}" y="{oy - 62}" font-size="19" text-anchor="middle" font-weight="bold">{title}</text>')
    o.append(f'<text x="{ox + 15 * P}" y="{oy - 42}" font-size="12" text-anchor="middle" fill="#444">{sub}</text>')
    # board and holes
    box(0.35, 0.35, COLS + .65, ROWS + .65, "#d8b98a", "#8a6a3a", 6)
    for c in range(1, COLS + 1):
        for r in range(1, ROWS + 1):
            o.append(f'<circle cx="{X(c):.1f}" cy="{Y(r):.1f}" r="2.2" fill="#8a6a3a"/>')
    for c in list(range(1, COLS + 1, 2)):
        o.append(f'<text x="{X(c):.1f}" y="{oy - 4}" font-size="10" text-anchor="middle" fill="#555">{c}</text>')
    for r in range(1, ROWS + 1, 2):
        for xx in ((ox + (COLS + 1) * P + 6,) if mirror else (ox - 6,)):
            o.append(f'<text x="{xx}" y="{Y(r) + 3.5:.1f}" font-size="10" text-anchor="middle" fill="#555">{r}</text>')

    op = 0.30 if mirror else 0.92
    dash = mirror
    lab = "#111" if mirror else "#fff"
    # SD card (sticks out past the board edge)
    if not mirror:
        box(30.4, 9.3, 38.0, 18.8, "#e9edf2", "#7a8799", 4, 1.0, dash)
        t(34.3, 13.3, "SD card", 11, fill="#333")
        t(34.3, 14.4, "sticks out", 10, fill="#555")
    # display
    box(17.2, 1.33, 30.6, 24.2, "#c8372d", "#7d1d17", 4, op, dash)
    if not mirror:
        box(18.0, 4.2, 29.8, 20.6, "#15171a", "#000", 3)
    t(23.9, 11.5, "Display", 16, fill="#111" if mirror else "#fff", weight="bold")
    t(23.9, 12.7, "seen through the board" if mirror else "screen up, header at the top", 10.5,
      fill="#333" if mirror else "#ddd")
    # DAC
    box(0.52, 1.0, 8.48, 12.0, "#1d1d22", "#000", 4, op, dash)
    box(3.0, -0.4, 6.0, 3.4, "#9a9a9a", "#555", 3, 1.0 if not mirror else .4, dash)
    t(4.5, 1.5, "jack", 10, fill="#111")
    t(3.9, 7.0, "DAC", 15, fill=lab, weight="bold")
    # ESP32
    box(9.48, 0.37, 16.52, 9.8, "#1f4f9c", "#0d2c5e", 4, op, dash)
    box(11.2, -0.25, 14.8, 2.6, "#c9c9c9", "#666", 3, 1.0 if not mirror else .4, dash)
    t(13, 1.2, "USB-C", 10, fill="#111")
    t(13, 4.6, "ESP32", 14, fill=lab, weight="bold")
    t(13, 5.7, "data / flashing", 9.5, fill="#111" if mirror else "#cfe0f5")
    t(13.6, 8.6, "pads 14 15 16", 8.5, fill="#111" if mirror else "#cfe0f5")
    # battery
    box(1.6, 13.5, 15.4, 23.3, "#b9bec6", "#6d7480", 6, op if mirror else .95, dash)
    t(8.5, 17.9, "Battery", 15, fill="#111", weight="bold")
    t(8.5, 19.1, "35 × 25 mm, on foam tape", 10.5, fill="#333")
    # charger
    box(0.6, 25.1, 7.4, 35.6, "#1f6aa8", "#0d3a61", 4, op, dash)
    box(2.2, 33.0, 5.8, 35.9, "#c9c9c9", "#666", 3, 1.0 if not mirror else .4, dash)
    t(4, 34.6, "USB-C", 10, fill="#111")
    t(4, 29.3, "Charger", 13, fill=lab, weight="bold")
    t(4, 30.4, "TP4056", 10, fill="#111" if mirror else "#cfe0f5")
    for c, s in ((1.5, "B+"), (3.0, "OUT+"), (5.0, "OUT−"), (6.5, "B−")):
        t(c, 25.9, s, 8, fill="#111" if mirror else "#fff")
    # switch
    box(8.4, 25.4, 11.6, 26.6, "#444", "#000", 2, op, dash)
    t(10, 24.6, "power switch", 9.5, fill="#333")
    # buttons
    for c0, name in ((10.6, "BACK"), (15.6, "OK")):
        box(c0, 28.6, c0 + 2.8, 32.4, "#2d2d2d", "#000", 4, op, dash)
        o.append(f'<circle cx="{X(c0 + 1.4):.1f}" cy="{Y(30.5):.1f}" r="{.75 * P}" fill="#777" fill-opacity="{op}" stroke="#000"/>')
    # encoder
    box(20.5, 25.4, 29.4, 35.6, "#16181c", "#000", 4, op, dash)
    o.append(f'<circle cx="{X(25):.1f}" cy="{Y(30.2):.1f}" r="{2.6 * P}" fill="#9aa0a8" fill-opacity="{op}" stroke="#444"/>')
    o.append(f'<circle cx="{X(25):.1f}" cy="{Y(30.2):.1f}" r="{1.1 * P}" fill="#d5d8dc" fill-opacity="{op}" stroke="#444"/>')
    t(25, 26.3, "Encoder, knob up", 11, fill=lab, weight="bold")

    for c, r, n, col, side in pins:
        o.append(f'<circle cx="{X(c):.1f}" cy="{Y(r):.1f}" r="6" fill="{COL[col if mirror else None]}" stroke="#222" stroke-width="1.1"/>')
        if not n:
            continue
        dx = {"l": -.42, "r": .42}.get(side, 0)
        dy = {"u": -.62, "d": .66}.get(side, 0)
        anchor = "middle"
        if dx:
            right = (dx > 0) != mirror
            anchor = "start" if right else "end"
        tc = "#111" if mirror else ("#fff" if (c, r) not in ((14, 11), (15, 11), (16, 11)) else "#111")
        if side in "ud" and r in (29, 32):
            tc = "#111"
        t(c + dx, r + dy, n, 8.5 if len(n) > 3 else 9.5, anchor, tc, "bold")
    return "\n".join(o)


o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica, Arial, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']
o.append(panel(40, 110, False, "Component side", "Columns 1–29 left to right, rows 1–35 top to bottom. Jack and ESP32 USB-C at the top edge, charging port at the bottom, SD card out of the right side."))
o.append(panel(40 + 39 * P + 50, 110, True, "Solder side (board flipped left to right)", "Same holes seen from the back. Pin colour = colour of the wire soldered there; gold pins get no wire."))
key = [("red", "3.3 V and battery +"), ("black", "GND"), ("yellow", "wires 1, 3, 9, 12, 15, 18"),
       ("blue", "wires 2, 10, 11, 17"), ("white", "wires 5, 6, 8, 16"), ("turq", "wires 4, 7, 13, 14")]
for i, (c, s) in enumerate(key):
    x = 60 + i * 300
    o.append(f'<circle cx="{x}" cy="{H - 28}" r="7" fill="{COL[c]}" stroke="#222"/>')
    o.append(f'<text x="{x + 14}" y="{H - 24}" font-size="12.5" fill="#222">{s}</text>')
o.append("</svg>")
out = Path(__file__).resolve().parents[2] / "hardware/images/perfboard-layout.svg"
out.write_text("\n".join(o))
print(out)
