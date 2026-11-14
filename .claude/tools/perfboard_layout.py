#!/usr/bin/env python3
"""Draws the three build drawings in hardware/images/:

  wiring-diagram.svg         what connects to what (pins grouped by job)
  perfboard-layout.svg       component side of the board (22 x 35 holes used)
  perfboard-connections.svg  solder side (mirrored) with every wire drawn, in three steps

Board coordinates are in hole pitches (2.54 mm); hole (c, r) = column c, row r,
always counted on the component side. The solder-side view mirrors c.
"""
from pathlib import Path

IMG = Path(__file__).resolve().parents[2] / "hardware/images"
COL = {"red": "#d92b2b", "black": "#222", "yellow": "#f2c81e", "blue": "#2f6fdd",
       "white": "#ffffff", "turq": "#22c7b8", None: "#d9a441"}
FONT = 'font-family="Helvetica, Arial, sans-serif"'
COLS, ROWS = 22, 35

# ------------------------------------------------------------------- pins
# (col, row, name, label side)
pins = []
pins += [(2, 27 + i, n, "r") for i, n in enumerate(["7", "8", "9", "10", "11", "12", "13", "RX", "TX"])]
pins += [(8, 27 + i, n, "l") for i, n in enumerate(["6", "5", "4", "3", "2", "1", "3V3", "GND", "5V"])]
pins += [(8, 4 + i, n, "l") for i, n in enumerate(["Rout", "G", "Lout", "BCK", "DIN", "WSEL", "GND", "VIN"])]
pins += [(12 + i, 2, n, "d") for i, n in enumerate(["LED", "SCK", "SDA", "A0", "RST", "CS", "GND", "VCC"])]
pins += [(14 + i, 23, n, "d") for i, n in enumerate(["SCK", "MISO", "MOSI", "CS"])]
pins += [(16 + i, 26, n, "u") for i, n in enumerate(["CLK", "DT", "SW", "+", "GND"])]
pins += [(2, 17, "BACK", "u"), (4, 20, "GND", "d"), (6, 17, "OK", "u"), (8, 20, "GND", "d"),
         (12, 33, "", "d"), (13, 33, "", "d"), (14, 33, "", "d"),
         (11, 27, "14", "r"), (2, 25, "15", "u"), (5, 25, "16", "u")]
back_pins = [(12.7, 14.7, "OUT−", "r"), (12.7, 16.5, "B−", "r"), (12.7, 18.3, "B+", "r"), (12.7, 20.1, "OUT+", "r")]

# ------------------------------------------------------------------ wires
# id: (colour, step, tag position along the longest segment, points)
wires = {
    # step 1: power
    "R1": ("red", 0, .82, [(8, 33), (8.35, 32.6), (8.35, 11.4), (8, 11)]),
    "R2": ("red", 0, .65, [(8, 11), (8.35, 10.6), (8.35, 3.45), (19, 3.45), (19, 2)]),
    "R3": ("red", 0, .3, [(8, 33), (10.7, 33), (10.7, 28.0), (19, 28.0), (19, 26)]),
    "K1": ("black", 0, .6, [(12.7, 14.7), (9.3, 14.7), (9.3, 33.6), (8, 34)]),
    "K2": ("black", 0, .5, [(12.7, 14.7), (12.3, 15.3), (8.8, 15.3), (8.8, 19.6), (8, 20)]),
    "K3": ("black", 0, .5, [(8, 20), (7.5, 19.4), (7.0, 19.4), (7.0, 10.4), (7.6, 10.4), (8, 10)]),
    "K4": ("black", 0, .3, [(8, 10), (7.5, 9.5), (7.5, 2.95), (18, 2.95), (18, 2)]),
    "K5": ("black", 0, .5, [(8, 20), (7.6, 20.5), (4.4, 20.5), (4, 20)]),
    "K6": ("black", 0, .65, [(8, 34), (8.5, 34.4), (11.3, 34.4), (11.3, 28.7), (20, 28.7), (20, 26)]),
    "B1": ("red", 0, .5, [(14, 33), (21.9, 33), (21.9, 21.6), (11.3, 21.6), (11.3, 20.1), (12.7, 20.1)]),
    "B2": ("red", 0, .5, [(8, 35), (13, 35), (13, 33)]),
    # step 2: display and SD
    "3": ("yellow", 1, .2, [(2, 30), (1.2, 30), (1.2, 0.55), (17, 0.55), (17, 2)]),
    "5": ("white", 1, .3, [(2, 28), (2.5, 28), (2.5, 0.85), (16, 0.85), (16, 2)]),
    "4": ("turq", 1, .42, [(2, 29), (2.85, 29), (2.85, 1.15), (15, 1.15), (15, 2)]),
    "2": ("blue", 1, .54, [(2, 31), (3.2, 31), (3.2, 1.45), (14, 1.45), (14, 2)]),
    "1": ("yellow", 1, .66, [(2, 32), (3.55, 32), (3.55, 1.72), (13, 1.72), (13, 2)]),
    "6": ("white", 1, .5, [(8, 29), (8.6, 29), (8.6, 25.5), (7.2, 25.5), (7.2, 3.35), (12, 3.35), (12, 2)]),
    "7": ("turq", 1, .2, [(8, 30), (9.3, 30), (9.3, 22.1), (17, 22.1), (17, 23)]),
    "10": ("blue", 1, .4, [(2, 31), (2.4, 31.5), (9.8, 31.5), (9.8, 22.5), (16, 22.5), (16, 23)]),
    "9": ("yellow", 1, .55, [(2, 32), (2.4, 32.5), (10.3, 32.5), (10.3, 24.0), (14, 24.0), (14, 23)]),
    "8": ("white", 1, .75, [(2, 33), (2.4, 33.5), (10.8, 33.5), (10.8, 24.5), (15, 24.5), (15, 23)]),
    # step 3: DAC, encoder, buttons
    "12": ("yellow", 2, .3, [(8, 27), (8.4, 27), (8.4, 26), (7.6, 26), (7.6, 9), (8, 9)]),
    "11": ("blue", 2, .5, [(8, 28), (8.8, 28), (8.8, 25.5), (7.2, 25.5), (7.2, 7), (8, 7)]),
    "13": ("turq", 2, .7, [(2, 27), (6.8, 27), (6.8, 8), (8, 8)]),
    "17": ("blue", 2, .5, [(2, 25), (2.4, 24.6), (2.4, 17.4), (2, 17)]),
    "18": ("yellow", 2, .5, [(5, 25), (5, 17), (6, 17)]),
    "15": ("yellow", 2, .6, [(8, 31), (9.4, 31), (9.4, 27.8), (17, 27.8), (17, 26)]),
    "14": ("turq", 2, .35, [(8, 32), (10, 32), (10, 28.5), (16, 28.5), (16, 26)]),
    "16": ("white", 2, .5, [(11, 27), (11, 24.8), (18, 24.8), (18, 26)]),
}
leads = [("red", [(13.7, 13.8), (13.7, 18.3), (12.7, 18.3)]), ("black", [(13.3, 13.8), (13.3, 16.5), (12.7, 16.5)])]
STEPS = ["Step 1: power (red and black)", "Step 2: display and SD card", "Step 3: DAC, encoder, buttons"]


def draw_board(o, ox, oy, P, mirror, step=None):
    X = lambda c: ox + ((COLS + 1 - c) if mirror else c) * P
    Y = lambda r: oy + r * P

    def box(c0, r0, c1, r1, fill, stroke="#000", rx=4, op=1.0, dash=False):
        x0, x1 = sorted((X(c0), X(c1)))
        d = ' stroke-dasharray="6 4"' if dash else ""
        o.append(f'<rect x="{x0:.1f}" y="{Y(r0):.1f}" width="{x1 - x0:.1f}" height="{Y(r1) - Y(r0):.1f}" '
                 f'rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="1.2"{d}/>')

    def t(c, r, s, size=11, anchor="middle", fill="#111", weight="normal", halo=None):
        halo = mirror if halo is None else halo
        h = ' stroke="#f1e2c6" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round"' if halo else ""
        o.append(f'<text x="{X(c):.1f}" y="{Y(r) + size * .35:.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'fill="{fill}" font-weight="{weight}"{h}>{s}</text>')

    box(0.35, 0.35, COLS + .65, ROWS + .65, "#d8b98a", "#8a6a3a", 6)
    for c in range(1, COLS + 1):
        for r in range(1, ROWS + 1):
            o.append(f'<circle cx="{X(c):.1f}" cy="{Y(r):.1f}" r="{P * .075:.1f}" fill="#8a6a3a"/>')
        if c % 2 or not mirror:
            o.append(f'<text x="{X(c):.1f}" y="{oy - 6}" font-size="10" text-anchor="middle" fill="#555">{c}</text>')
    for r in range(1, ROWS + 1):
        xx = ox + (COLS + 1) * P + 9 if mirror else ox - 9
        if r % 2 or not mirror:
            o.append(f'<text x="{xx}" y="{Y(r) + 3.5:.1f}" font-size="10" text-anchor="middle" fill="#555">{r}</text>')

    op = 0.16 if mirror else 0.93
    lab = "#111" if mirror else "#fff"
    soft = "#333" if mirror else "#dfe8f5"
    metal = .3 if mirror else 1.0
    if not mirror:
        box(22.5, 9.3, 30.0, 18.8, "#e9edf2", "#7a8799", 4)
        t(26.3, 13.5, "SD card", 13, fill="#333", weight="bold")
        t(26.3, 14.5, "sticks out of the case", 11, fill="#555")
    box(9.2, 1.33, 22.6, 24.2, "#c8372d", "#7d1d17", 4, op, mirror)                 # display
    if not mirror:
        box(10.0, 4.6, 21.8, 20.6, "#15171a", "#000", 3)
        t(15.9, 11.6, "Display", 18, fill=lab, weight="bold")
        t(15.9, 12.7, "screen up, header at the top", 11.5, fill=soft)
    box(0.52, 1.0, 8.48, 12.0, "#1d1d22", "#000", 4, op, mirror)                    # DAC
    box(3.0, -0.4, 6.0, 3.3, "#9a9a9a", "#555", 3, metal, mirror)
    if not mirror:
        t(4.5, 1.4, "jack", 11)
        t(3.0, 7.5, "DAC", 17, fill=lab, weight="bold")
    else:
        t(4.3, 5.0, "DAC", 12, fill="#555")
    box(1.48, 26.2, 8.52, 35.63, "#1f4f9c", "#0d2c5e", 4, op, mirror)               # ESP32
    box(3.4, 33.5, 6.6, 36.2, "#c9c9c9", "#666", 3, metal, mirror)
    if not mirror:
        t(5, 35.0, "USB-C", 10.5)
        t(5, 30.5, "ESP32", 15, fill=lab, weight="bold")
        t(5, 31.6, "flashing port", 10.5, fill=soft)
        t(3.6, 26.75, "pads 14 15 16", 8.5, "start", soft)
    else:
        t(5, 36.0, "ESP32", 12, fill="#555", halo=False)
    box(11.4, 32.35, 14.6, 33.65, "#444", "#000", 2, op, mirror)                    # switch
    t(13, 31.6, "switch" if mirror else "power switch", 10.5, fill="#333")
    for c0 in (1.6, 5.6):                                                             # buttons
        box(c0, 16.6, c0 + 2.8, 20.4, "#2d2d2d", "#000", 4, op, mirror)
        if not mirror:
            o.append(f'<circle cx="{X(c0 + 1.4):.1f}" cy="{Y(18.5):.1f}" r="{.75 * P}" fill="#777" stroke="#000"/>')
    box(14.9, 25.4, 22.4, 35.6, "#16181c", "#000", 4, op, mirror)                   # encoder, 19 x 26 mm
    if not mirror:
        for rad, f in ((2.6, "#9aa0a8"), (1.1, "#d5d8dc")):
            o.append(f'<circle cx="{X(18.65):.1f}" cy="{Y(31.0):.1f}" r="{rad * P}" fill="{f}" stroke="#444"/>')
        t(18.65, 34.6, "Encoder, knob up", 12.5, fill=lab, weight="bold")
    else:
        t(18.65, 32.0, "Encoder", 12, fill="#555")
        box(9.0, 4.0, 22.8, 13.8, "#b9bec6", "#6d7480", 6, .9)                      # battery (this side)
        t(15.9, 8.6, "Battery", 15, weight="bold", halo=False)
        t(15.9, 9.8, "on this side", 10.5, fill="#333", halo=False)
        box(11.8, 14.2, 22.3, 21.0, "#1f6aa8", "#0d3a61", 4, .92)                   # charger (this side)
        box(19.6, 15.8, 23.0, 19.4, "#c9c9c9", "#666", 3)
        t(21.3, 17.6, "USB-C", 9.5, halo=False)
        t(17.3, 17.2, "Charger", 14, fill="#fff", weight="bold", halo=False)
        t(17.3, 18.3, "on this side", 10, fill="#dfe8f5", halo=False)

    used = {}
    if step is not None:
        def poly(pts, col, w):
            d = " ".join(f"{X(c):.1f},{Y(r):.1f}" for c, r in pts)
            o.append(f'<polyline points="{d}" fill="none" stroke="#2a2a2a" stroke-width="{w + 2.2}" stroke-linejoin="round" stroke-linecap="round"/>')
            o.append(f'<polyline points="{d}" fill="none" stroke="{COL[col]}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>')
        if step == 0:
            for col, pts in leads:
                poly(pts, col, 2.6)
        tags = []
        for wid, (col, st, frac, pts) in wires.items():
            if st != step:
                continue
            poly(pts, col, 2.6)
            used[pts[0]] = col
            used[pts[-1]] = col
            seg = max(zip(pts, pts[1:]), key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
            (c0, r0), (c1, r1) = seg
            tags.append((X(c0 + (c1 - c0) * frac), Y(r0 + (r1 - r0) * frac), wid))
        for x, y, wid in tags:
            w = 9 + 6.4 * len(wid)
            o.append(f'<rect x="{x - w / 2:.1f}" y="{y - 8:.1f}" width="{w}" height="16" rx="4" fill="#fff" stroke="#222"/>')
            o.append(f'<text x="{x:.1f}" y="{y + 3.6:.1f}" font-size="10.5" text-anchor="middle" font-weight="bold">{wid}</text>')

    dark = {(2, 17), (4, 20), (6, 17), (8, 20), (11, 27), (2, 25), (5, 25)}
    for c, r, n, side in pins + (back_pins if mirror else []):
        hit = (c, r) in used
        if mirror and not hit:
            o.append(f'<circle cx="{X(c):.1f}" cy="{Y(r):.1f}" r="{P * .15:.1f}" fill="#d9a441" fill-opacity=".55" stroke="#555" stroke-width=".8"/>')
            if (c, r, n, side) not in back_pins:
                continue
        else:
            o.append(f'<circle cx="{X(c):.1f}" cy="{Y(r):.1f}" r="{P * .23:.1f}" fill="{COL[used.get((c, r))]}" stroke="#222" stroke-width="1.2"/>')
        if not n:
            continue
        if not mirror and r == 26:
            side = "d"
        tc = "#111" if mirror or (c, r) in dark else "#fff"
        size = 10.5 if not mirror else 10
        if side in "lr":
            dx = .42 if side == "r" else -.42
            anchor = "start" if (dx > 0) != mirror else "end"
            t(c + dx, r, n, size, anchor, tc, "bold")
        else:
            t(c, r + (-.64 if side == "u" else .64), n, size - 1 if len(n) > 3 else size, "middle", tc, "bold")


def layout():
    P = 30
    W, H = (COLS + 1) * P + 330, (ROWS + 1) * P + 170
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
         f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>',
         f'<text x="{W / 2}" y="38" font-size="21" text-anchor="middle" font-weight="bold">Perf board layout: component side</text>',
         f'<text x="{W / 2}" y="62" font-size="13" text-anchor="middle" fill="#444">Columns 1–22 left to right, rows 1–35 top to bottom. Battery and charger are on the other side.</text>']
    draw_board(o, 50, 110, P, False)
    o.append("</svg>")
    (IMG / "perfboard-layout.svg").write_text("\n".join(o))


def connections():
    P = 27
    pw = (COLS + 1) * P + 70
    W, H = 3 * pw + 40, (ROWS + 1) * P + 230
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
         f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>',
         f'<text x="{W / 2}" y="38" font-size="22" text-anchor="middle" font-weight="bold">Perf board connections: back of the board</text>',
         f'<text x="{W / 2}" y="63" font-size="13.5" text-anchor="middle" fill="#444">The same board three times, seen from the solder side (flipped left to right, so column 1 is on the right). '
         f'Each drawing shows one group of wires. Parts on the front are shown faintly.</text>']
    for i, title in enumerate(STEPS):
        ox = 40 + i * pw
        o.append(f'<text x="{ox + (COLS + 1) * P / 2}" y="104" font-size="17" text-anchor="middle" font-weight="bold">{title}</text>')
        draw_board(o, ox, 135, P, True, i)
    ky = H - 30
    key = [("red", "red: 3.3 V and battery +"), ("black", "black: GND"), ("yellow", "yellow"), ("blue", "blue"),
           ("white", "white"), ("turq", "turquoise")]
    for i, (c, s) in enumerate(key):
        x = 60 + i * 210
        o.append(f'<line x1="{x}" y1="{ky}" x2="{x + 34}" y2="{ky}" stroke="#2a2a2a" stroke-width="5.5" stroke-linecap="round"/>')
        o.append(f'<line x1="{x}" y1="{ky}" x2="{x + 34}" y2="{ky}" stroke="{COL[c]}" stroke-width="3.2" stroke-linecap="round"/>')
        o.append(f'<text x="{x + 44}" y="{ky + 4}" font-size="13" fill="#222">{s}</text>')
    o.append(f'<text x="{60 + 6 * 210}" y="{ky + 4}" font-size="13" fill="#222">White tag = wire number in the wire list. Wires may cross; they are insulated.</text>')
    o.append("</svg>")
    (IMG / "perfboard-connections.svg").write_text("\n".join(o))


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
        o.append(f'<rect x="{x0}" y="{y - 11}" width="{w}" height="22" rx="11" fill="{COL[col]}" stroke="#222"/>')
        t(x0 + w / 2, y, s, 11, fill="#fff", weight="bold")

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

    # power
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
    wire([(350, 210), (EL, 210)], "black", "K1", (455, 210))
    epin("l", 130, "5V"); epin("l", 170, "3V3"); epin("l", 210, "GND")
    chip(EL - 16, 170, "3.3 V out", "red", "end")

    # DAC
    box(130, 262, 200, 150, "#1d1d22")
    t(190, 300, "DAC", 15, fill="#fff", weight="bold")
    t(190, 320, "PCM5102A", 11, fill="#ccc")
    for y, pin, name, col, tag in ((290, "5", "BCK", "blue", "11"), (330, "6", "WSEL", "yellow", "12"),
                                   (370, "7", "DIN", "turq", "13")):
        wire([(330, y), (EL, y)], col, tag, (445, y))
        t(318, y, name, 12, "end", "#fff", "bold"); epin("l", y, pin)
    chip(142, 360, "VIN  R1", "red"); chip(142, 388, "GND  K3", "black")

    # encoder
    box(130, 442, 200, 150, "#16181c")
    t(190, 480, "Encoder", 15, fill="#fff", weight="bold")
    for y, pin, name, col, tag in ((470, "1", "CLK", "turq", "14"), (510, "2", "DT", "yellow", "15"),
                                   (550, "14", "SW", "white", "16")):
        wire([(330, y), (EL, y)], col, tag, (445, y))
        t(318, y, name, 12, "end", "#fff", "bold"); epin("l", y, pin)
    chip(142, 540, "+  R3", "red"); chip(142, 568, "GND  K6", "black")

    # buttons
    for y, pin, name, col, tag, g in ((650, "15", "BACK", "blue", "17", "K5"), (715, "16", "OK", "yellow", "18", "K2")):
        box(230, y - 22, 100, 44, "#2d2d2d", "#000", 6)
        t(280, y, name, 13, fill="#fff", weight="bold")
        wire([(330, y), (EL, y)], col, tag, (445, y)); epin("l", y, pin)
        chip(218, y, f"GND  {g}", "black", "end")

    # display + SD
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
        wire([(ER, y), (DX, y)], col, tag, (890, y))
        t(DX + 12, y, name, 12, "start", "#fff", "bold"); epin("r", y, pin)
    chip(DX + 12, 362, "VCC  R2", "red"); chip(DX + 110, 362, "GND  K4", "black")

    nx, ny = 800, 640
    chip(nx, ny, "red pill", "red"); t(nx + 78, ny, "= 3.3 V, chained from the ESP32 3V3 pin (wires R1–R3)", 12.5, "start")
    chip(nx, ny + 32, "black pill", "black"); t(nx + 88, ny + 32, "= GND, chained from the charger OUT− pad (wires K1–K6)", 12.5, "start")
    t(nx, ny + 64, "Pins 12 and 11 each take two wires: one to the display, one to the SD slot.", 12.5, "start")
    t(nx, ny + 96, "Flash through the ESP32's USB-C. Charge through the charger's USB-C.", 12.5, "start", "#444")
    o.append("</svg>")
    (IMG / "wiring-diagram.svg").write_text("\n".join(o))


wiring()
layout()
connections()
print("ok")
