#!/usr/bin/env python3
"""Draws the three build drawings in hardware/images/:

  wiring-diagram.svg         what connects to what (pins grouped by job)
  perfboard-layout.svg       component side of the 29 x 35 hole board
  perfboard-connections.svg  solder side (mirrored), every pin tagged with its wires

Board coordinates are in hole pitches (2.54 mm); hole (c, r) = column c, row r.
"""
from pathlib import Path

IMG = Path(__file__).resolve().parents[2] / "hardware/images"
COL = {"red": "#d92b2b", "black": "#222", "yellow": "#f2c81e", "blue": "#2f6fdd",
       "white": "#ffffff", "turq": "#22c7b8", None: "#d9a441"}
FONT = 'font-family="Helvetica, Arial, sans-serif"'

# ---------------------------------------------------------------- perf board
P = 30
COLS, ROWS = 22, 35


def col_pins(c, r0, side, rows):
    return [(c, r0 + i, n, col, side, ids) for i, (n, col, ids) in enumerate(rows)]


def row_pins(c0, r, side, cols):
    return [(c0 + i, r, n, col, side, ids) for i, (n, col, ids) in enumerate(cols)]


# (col, row, name, wire colour, label side, wire ids)
pins = []
pins += col_pins(2, 27, "r", [("7", "turq", "13"), ("8", "white", "5"), ("9", "turq", "4"), ("10", "yellow", "3"),
                              ("11", "blue", "2 10"), ("12", "yellow", "1 9"), ("13", "white", "8"),
                              ("RX", None, ""), ("TX", None, "")])
pins += col_pins(8, 27, "l", [("6", "yellow", "12"), ("5", "blue", "11"), ("4", "white", "6"), ("3", "turq", "7"),
                              ("2", "yellow", "15"), ("1", "turq", "14"), ("3V3", "red", "R1 R3"),
                              ("GND", "black", "K1 K5 K6"), ("5V", "red", "B2")])
pins += col_pins(8, 4, "l", [("Rout", None, ""), ("G", None, ""), ("Lout", None, ""), ("BCK", "blue", "11"),
                             ("DIN", "turq", "13"), ("WSEL", "yellow", "12"), ("GND", "black", "K2 K3"),
                             ("VIN", "red", "R1 R2")])
pins += row_pins(12, 2, "d", [("LED", "white", "6"), ("SCK", "yellow", "1"), ("SDA", "blue", "2"),
                              ("A0", "turq", "4"), ("RST", "white", "5"), ("CS", "yellow", "3"),
                              ("GND", "black", "K3"), ("VCC", "red", "R2")])
pins += row_pins(14, 23, "u", [("SCK", "yellow", "9"), ("MISO", "white", "8"), ("MOSI", "blue", "10"),
                               ("CS", "turq", "7")])
pins += row_pins(17, 35, "u", [("GND", "black", "K5"), ("+", "red", "R3"), ("SW", "white", "16"),
                               ("DT", "yellow", "15"), ("CLK", "turq", "14")])
pins += [(2, 17, "BACK", "blue", "u", "17"), (4, 20, "GND", "black", "d", "K4"),
         (6, 17, "OK", "yellow", "u", "18"), (8, 20, "GND", "black", "d", "K1 K2 K4"),
         (10, 29, "", "red", "d", "B2"), (11, 29, "", "red", "d", "B1"), (12, 29, "", None, "d", ""),
         (3, 25, "14", "white", "u", "16"), (4, 25, "15", "blue", "u", "17"), (5, 25, "16", "yellow", "u", "18")]
back_pins = [(12.7, 4.5, "OUT+", "red", "r", "B1"), (12.7, 6.2, "B+", None, "r", "battery red"),
             (12.7, 7.8, "B−", None, "r", "battery black"), (12.7, 9.5, "OUT−", "black", "r", "K6")]


def board(name, mirror, title, sub):
    ox, oy = 50, 110
    W = (COLS + 1) * P + (150 if mirror else 330)
    H = (ROWS + 1) * P + 190
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
         f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']
    X = lambda c: ox + ((COLS + 1 - c) if mirror else c) * P
    Y = lambda r: oy + r * P

    def box(c0, r0, c1, r1, fill, stroke="#000", rx=4, op=1.0, dash=False):
        x0, x1 = sorted((X(c0), X(c1)))
        d = ' stroke-dasharray="6 4"' if dash else ""
        o.append(f'<rect x="{x0:.1f}" y="{Y(r0):.1f}" width="{x1 - x0:.1f}" height="{Y(r1) - Y(r0):.1f}" '
                 f'rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="1.2"{d}/>')

    def t(c, r, s, size=11, anchor="middle", fill="#111", weight="normal", dy=0, halo=None):
        halo = mirror if halo is None else halo
        h = ' stroke="#f1e2c6" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round"' if halo else ""
        o.append(f'<text x="{X(c):.1f}" y="{Y(r) + size * .35 + dy:.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'fill="{fill}" font-weight="{weight}"{h}>{s}</text>')

    mid = W / 2
    o.append(f'<text x="{mid}" y="38" font-size="21" text-anchor="middle" font-weight="bold">{title}</text>')
    for i, line in enumerate(sub):
        o.append(f'<text x="{mid}" y="{62 + i * 18}" font-size="13" text-anchor="middle" fill="#444">{line}</text>')
    box(0.35, 0.35, COLS + .65, ROWS + .65, "#d8b98a", "#8a6a3a", 6)
    for c in range(1, COLS + 1):
        for r in range(1, ROWS + 1):
            o.append(f'<circle cx="{X(c):.1f}" cy="{Y(r):.1f}" r="2.4" fill="#8a6a3a"/>')
        o.append(f'<text x="{X(c):.1f}" y="{oy - 8}" font-size="10.5" text-anchor="middle" fill="#555">{c}</text>')
    for r in range(1, ROWS + 1):
        xx = ox + (COLS + 1) * P + 10 if mirror else ox - 10
        o.append(f'<text x="{xx}" y="{Y(r) + 3.5:.1f}" font-size="10.5" text-anchor="middle" fill="#555">{r}</text>')

    op = 0.22 if mirror else 0.93
    lab = "#111" if mirror else "#fff"
    soft = "#333" if mirror else "#dfe8f5"
    metal = .35 if mirror else 1.0
    if not mirror:
        box(22.5, 9.3, 30.0, 18.8, "#e9edf2", "#7a8799", 4)
        t(26.3, 13.5, "SD card", 13, fill="#333", weight="bold")
        t(26.3, 14.5, "sticks out of the case", 11, fill="#555")
    # display
    box(9.2, 1.33, 22.6, 24.2, "#c8372d", "#7d1d17", 4, op, mirror)
    if not mirror:
        box(10.0, 4.6, 21.8, 20.6, "#15171a", "#000", 3)
        t(15.9, 11.6, "Display", 18, fill=lab, weight="bold")
        t(15.9, 12.7, "screen up, header at the top", 11.5, fill=soft)
    # DAC
    box(0.52, 1.0, 8.48, 12.0, "#1d1d22", "#000", 4, op, mirror)
    box(3.0, -0.4, 6.0, 3.3, "#9a9a9a", "#555", 3, metal, mirror)
    t(4.5, 1.4, "jack", 11)
    t(3.0, 6.5 if mirror else 7.5, "DAC", 17, fill=lab, weight="bold")
    # ESP32, USB-C at the bottom edge
    box(1.48, 26.2, 8.52, 35.63, "#1f4f9c", "#0d2c5e", 4, op, mirror)
    box(3.4, 33.5, 6.6, 36.2, "#c9c9c9", "#666", 3, metal, mirror)
    if not mirror:
        t(5, 35.0, "USB-C", 10.5)
        t(5, 31.6, "flashing port", 10.5, fill=soft)
        t(3.6, 26.75, "pads 14 15 16", 8.5, "start", soft)
    t(5, 28.0 if mirror else 30.5, "ESP32", 15, fill=lab, weight="bold")
    # switch
    box(9.4, 28.35, 12.6, 29.65, "#444", "#000", 2, op, mirror)
    t(11, 27.6, "power switch", 10.5, fill="#333")
    # buttons
    for c0 in (1.6, 5.6):
        box(c0, 16.6, c0 + 2.8, 20.4, "#2d2d2d", "#000", 4, op, mirror)
        o.append(f'<circle cx="{X(c0 + 1.4):.1f}" cy="{Y(18.5):.1f}" r="{.75 * P}" fill="#777" fill-opacity="{op}" stroke="#000"/>')
    # encoder
    box(13.5, 25.4, 22.4, 35.6, "#16181c", "#000", 4, op, mirror)
    for rad, f in ((2.6, "#9aa0a8"), (1.1, "#d5d8dc")):
        o.append(f'<circle cx="{X(18):.1f}" cy="{Y(30.0):.1f}" r="{rad * P}" fill="{f}" fill-opacity="{op}" stroke="#444"/>')
    t(18, 26.2, "Encoder, knob up", 12.5, fill=lab, weight="bold")
    # parts on the back: charger and battery
    if mirror:
        box(11.8, 3.6, 22.3, 10.4, "#1f6aa8", "#0d3a61", 4, .95)
        box(19.6, 5.2, 23.0, 8.8, "#c9c9c9", "#666", 3)
        t(21.3, 7.0, "USB-C", 10.5, halo=False)
        t(17.2, 6.6, "Charger", 15, fill="#fff", weight="bold", halo=False)
        t(17.2, 7.6, "charging port", 10.5, fill="#dfe8f5", halo=False)
        box(8.6, 11.6, 22.4, 21.4, "#b9bec6", "#6d7480", 6, .97)
        t(15.5, 16.0, "Battery", 17, weight="bold", halo=False)
        t(15.5, 17.1, "foam tape, thin card underneath", 11.5, fill="#333", halo=False)

    dark_names = {(2, 17), (4, 20), (6, 17), (8, 20), (3, 25), (4, 25), (5, 25)}
    for c, r, n, col, side, ids in pins + (back_pins if mirror else []):
        rad = 8 if mirror else 6.5
        o.append(f'<circle cx="{X(c):.1f}" cy="{Y(r):.1f}" r="{rad}" fill="{COL[col if mirror else None]}" stroke="#222" stroke-width="1.2"/>')
        tc = "#111" if mirror or (c, r) in dark_names else "#fff"
        if side in "lr":
            dx = .42 if side == "r" else -.42
            anchor = "start" if (dx > 0) != mirror else "end"
            s = n
            if mirror and ids:
                s = f'{n} <tspan font-weight="normal">· {ids}</tspan>'
            t(c + dx, r, s, 10.5, anchor, tc, "bold")
        else:
            sgn = -1 if side == "u" else 1
            lines = ([n] if n else []) + (ids.split() if mirror else [])
            if sgn < 0:
                lines = lines[::-1]
            for i, s in enumerate(lines):
                bold = "bold" if s == n else "normal"
                t(c, r + sgn * .64, s, 9.5 if len(s) < 4 else 8.5, "middle", tc, bold, dy=sgn * i * 12)

    ky = H - 28
    if mirror:
        key = [("red", "3.3 V, battery +"), ("black", "GND"), ("yellow", "yellow"), ("blue", "blue"),
               ("white", "white"), ("turq", "turquoise"), (None, "no wire")]
        for i, (c, s) in enumerate(key):
            x = 30 + i * 118
            o.append(f'<circle cx="{x}" cy="{ky}" r="8" fill="{COL[c]}" stroke="#222"/>')
            o.append(f'<text x="{x + 13}" y="{ky + 4}" font-size="12" fill="#222">{s}</text>')
    o.append("</svg>")
    (IMG / name).write_text("\n".join(o))


# ------------------------------------------------------------ wiring diagram
def wiring():
    W, H = 1300, 850
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
         f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']

    def box(x, y, w, h, fill, stroke="#000", rx=8):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')

    def t(x, y, s, size=13, anchor="middle", fill="#111", weight="normal"):
        o.append(f'<text x="{x}" y="{y + size * .35:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{s}</text>')

    def wire(pts, col, tag=None, tagpos=None):
        d = " ".join(f"{x},{y}" for x, y in pts)
        o.append(f'<polyline points="{d}" fill="none" stroke="#333" stroke-width="6.5" stroke-linejoin="round"/>')
        o.append(f'<polyline points="{d}" fill="none" stroke="{COL[col]}" stroke-width="4" stroke-linejoin="round"/>')
        if tag:
            x, y = tagpos
            w = 12 + 7 * len(tag)
            o.append(f'<rect x="{x - w / 2}" y="{y - 10}" width="{w}" height="20" rx="5" fill="#fff" stroke="#333"/>')
            t(x, y, tag, 11.5, weight="bold")

    def chip(x, y, s, col, anchor="start"):
        w = 16 + 6.6 * len(s)
        x0 = x if anchor == "start" else x - w
        fg = "#fff"
        o.append(f'<rect x="{x0}" y="{y - 11}" width="{w}" height="22" rx="11" fill="{COL[col]}" stroke="#222"/>')
        t(x0 + w / 2, y, s, 11, fill=fg, weight="bold")

    def dot(x, y):
        o.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#222"/>')

    t(W / 2, 34, "Paata wiring", 22, weight="bold")
    t(W / 2, 60, "ESP32 pins are grouped by what they connect to, not by where they sit on the board. "
                 "The number on each wire matches the wire list.", 13, fill="#444")

    EL, ER = 560, 740
    box(EL, 95, ER - EL, 680, "#1f4f9c", "#0d2c5e")
    t(650, 430, "ESP32-S3-Zero", 17, fill="#fff", weight="bold")

    def epin(side, y, s):
        x = EL if side == "l" else ER
        o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#d9a441" stroke="#222"/>')
        t(x + (14 if side == "l" else -14), y, s, 13, "start" if side == "l" else "end", "#fff", "bold")

    # ---- power
    box(40, 105, 110, 60, "#b9bec6", "#6d7480")
    t(95, 135, "Battery", 13, weight="bold")
    box(200, 95, 150, 140, "#1f6aa8", "#0d3a61")
    t(275, 165, "Charger", 14, fill="#fff", weight="bold")
    t(275, 183, "TP4056", 11, fill="#dfe8f5")
    t(212, 122, "B+", 11, "start", "#fff", "bold"); t(212, 148, "B−", 11, "start", "#fff", "bold")
    t(338, 130, "OUT+", 11, "end", "#fff", "bold"); t(338, 210, "OUT−", 11, "end", "#fff", "bold")
    wire([(150, 122), (200, 122)], "red")
    wire([(150, 148), (200, 148)], "black")
    wire([(350, 130), (415, 130)], "red", "B1", (383, 130))
    box(415, 112, 60, 36, "#444", "#000", 5)
    t(445, 130, "switch", 11, fill="#fff")
    wire([(475, 130), (EL, 130)], "red", "B2", (517, 130))
    wire([(350, 210), (EL, 210)], "black", "K6", (455, 210))
    epin("l", 130, "5V"); epin("l", 170, "3V3"); epin("l", 210, "GND")
    chip(EL - 16, 170, "3.3 V out", "red", "end")

    # ---- DAC
    box(130, 262, 200, 150, "#1d1d22")
    t(190, 300, "DAC", 15, fill="#fff", weight="bold")
    t(190, 320, "PCM5102A", 11, fill="#ccc")
    for y, pin, name, col, tag in ((290, "5", "BCK", "blue", "11"), (330, "6", "WSEL", "yellow", "12"),
                                   (370, "7", "DIN", "turq", "13")):
        wire([(330, y), (EL, y)], col, tag, (445, y))
        t(318, y, name, 12, "end", "#fff", "bold"); epin("l", y, pin)
    chip(142, 360, "VIN  R1", "red"); chip(142, 388, "GND  K2", "black")

    # ---- encoder
    box(130, 442, 200, 150, "#16181c")
    t(190, 480, "Encoder", 15, fill="#fff", weight="bold")
    for y, pin, name, col, tag in ((470, "1", "CLK", "turq", "14"), (510, "2", "DT", "yellow", "15"),
                                   (550, "14", "SW", "white", "16")):
        wire([(330, y), (EL, y)], col, tag, (445, y))
        t(318, y, name, 12, "end", "#fff", "bold"); epin("l", y, pin)
    chip(142, 540, "+  R3", "red"); chip(142, 568, "GND  K5", "black")

    # ---- buttons
    for y, pin, name, col, tag, g in ((650, "15", "BACK", "blue", "17", "K4"), (715, "16", "OK", "yellow", "18", "K1")):
        box(230, y - 22, 100, 44, "#2d2d2d", "#000", 6)
        t(280, y, name, 13, fill="#fff", weight="bold")
        wire([(330, y), (EL, y)], col, tag, (445, y)); epin("l", y, pin)
        chip(218, y, f"GND  {g}", "black", "end")

    # ---- display + SD
    DX = 980
    box(DX, 95, 220, 300, "#c8372d", "#7d1d17")
    t(DX + 140, 130, "Display", 15, fill="#fff", weight="bold")
    t(DX + 140, 150, "8-pin header", 11, fill="#ffe1dd")
    box(DX, 402, 220, 185, "#a82a22", "#7d1d17")
    t(DX + 140, 440, "SD slot", 15, fill="#fff", weight="bold")
    t(DX + 140, 460, "4 pads, same board", 11, fill="#ffe1dd")
    rows = ((130, "10", "CS", "yellow", "3"), (170, "9", "A0", "turq", "4"), (210, "8", "RESET", "white", "5"),
            (250, "4", "LED", "white", "6"), (290, "12", "SCK", "yellow", "1"), (330, "11", "SDA", "blue", "2"))
    for y, pin, name, col, tag in rows:
        wire([(ER, y), (DX, y)], col, tag, (890, y))
        t(DX + 12, y, name, 12, "start", "#fff", "bold"); epin("r", y, pin)
    wire([(ER, 290), (810, 290), (810, 430), (DX, 430)], "yellow", "9", (890, 430))
    wire([(ER, 330), (780, 330), (780, 470), (DX, 470)], "blue", "10", (890, 470))
    
    for y, name in ((430, "SD_SCK"), (470, "SD_MOSI")):
        t(DX + 12, y, name, 12, "start", "#fff", "bold")
    for y, pin, name, col, tag in ((510, "13", "SD_MISO", "white", "8"), (550, "3", "SD_CS", "turq", "7")):
        wire([(ER, y), (DX, y)], col, tag, (800, y))
        t(DX + 12, y, name, 12, "start", "#fff", "bold"); epin("r", y, pin)
    chip(DX + 12, 362, "VCC  R2", "red"); chip(DX + 110, 362, "GND  K3", "black")

    # ---- notes
    nx, ny = 800, 640
    chip(nx, ny, "red pill", "red"); t(nx + 78, ny, "= 3.3 V, chained from the ESP32 3V3 pin (wires R1–R3)", 12.5, "start")
    chip(nx, ny + 32, "black pill", "black"); t(nx + 88, ny + 32, "= GND, chained from the ESP32 GND pin (wires K1–K5)", 12.5, "start")
    t(nx, ny + 64, "Pins 12 and 11 each take two wires: one to the display, one to the SD slot.", 12.5, "start")
    t(nx, ny + 96, "Flash through the ESP32's USB-C. Charge through the charger's USB-C.", 12.5, "start", "#444")
    o.append("</svg>")
    (IMG / "wiring-diagram.svg").write_text("\n".join(o))


wiring()
board("perfboard-layout.svg", False, "Perf board layout: component side",
      ["Columns 1–22 left to right, rows 1–35 top to bottom.", "Battery and charger are on the other side."])
board("perfboard-connections.svg", True, "Perf board connections: solder side",
      ["The board flipped left to right. Battery and charger sit on this side.",
       "Each pin shows its wire colour and wire numbers."])
print("ok")
