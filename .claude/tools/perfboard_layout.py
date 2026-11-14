#!/usr/bin/env python3
"""Draws the three build drawings in hardware/images/:

  wiring-diagram.svg         what connects to what (pins grouped by job)
  perfboard-layout.svg       component side of the board (22 x 34 holes, as cut and soldered by the owner)
  perfboard-connections.svg  solder side (mirrored) with every wire drawn, in three steps

Board coordinates are in hole pitches (2.54 mm); hole (c, r) = column c, row r,
always counted on the component side. The solder-side view mirrors c.
"""
from pathlib import Path

IMG = Path(__file__).resolve().parents[2] / "hardware/images"
COL = {"red": "#d92b2b", "black": "#222", "yellow": "#f2c81e", "blue": "#2f6fdd",
       "white": "#ffffff", "turq": "#22c7b8", None: "#d9a441"}
FONT = 'font-family="Helvetica, Arial, sans-serif"'
COLS, ROWS = 22, 34

# ------------------------------------------------------------------- pins
# (col, row, name, label side)
pins = []
pins += [(1, 25 + i, n, "r") for i, n in enumerate(["7", "8", "9", "10", "11", "12", "13", "RX", "TX"])]
pins += [(7, 25 + i, n, "l") for i, n in enumerate(["6", "5", "4", "3", "2", "1", "3V3", "GND", "5V"])]
pins += [(8, 2 + i, n, "l") for i, n in enumerate(["Rout", "G", "Lout", "BCK", "DIN", "WSEL", "GND", "VIN"])]
pins += [(2, 3 + i, "", "r") for i in range(6)]                       # DAC config pads, not wired
pins += [(13 + i, 1, n, "d") for i, n in enumerate(["LED", "SCK", "SDA", "A0", "RST", "CS", "GND", "VCC"])]
pins += [(15 + i, 22, n, "d") for i, n in enumerate(["SCK", "MISO", "MOSI", "CS"])]
pins += [(8 + i, 25, n, "u") for i, n in enumerate(["CLK", "DT", "SW", "+", "GND"])]
pins += [(16, 25, "OUT+", "d"), (17, 25, "B+", "d"), (20, 25, "B−", "d"), (21, 25, "OUT−", "d"),
         (16, 33, "", "d"), (21, 33, "", "d"),                         # charger's USB-end pads, not wired
         (15, 25, "?", "d"), (17, 21, "", "d"), (18, 21, "", "d")]     # joints seen in the photo, purpose unknown
back_pins = []

# ------------------------------------------------------------------ wires
# id: (colour, step, tag position along the longest segment, points)
wires = {
    # step 1: power
    "R1": ("red", 0, .3, [(7, 31), (5.9, 31), (5.9, 9), (8, 9)]),
    "R3": ("red", 0, .5, [(7, 31), (11, 31), (11, 25)]),
    "R2": ("red", 0, .5, [(11, 25), (11.5, 25.7), (11.5, 26.7), (22, 26.7), (22, 1), (20, 1)]),
    "K1": ("black", 0, .5, [(21, 25), (20.5, 26), (12.5, 26), (12, 25)]),
    "K2": ("black", 0, .65, [(12, 25), (12, 32), (7, 32)]),
    "K3": ("black", 0, .6, [(7, 32), (5.3, 32), (5.3, 8), (8, 8)]),
    "K4": ("black", 0, .35, [(21, 25), (21, 2.2), (19, 2.2), (19, 1)]),
    "B2": ("red", 0, .5, [(7, 33), (7, 35.2)]),            # flying lead from the switch
    # step 2: display and SD
    "5": ("white", 1, .35, [(1, 26), (1.8, 26), (1.8, 12), (17, 12), (17, 1)]),
    "4": ("turq", 1, .5, [(1, 27), (2.4, 27), (2.4, 13), (16, 13), (16, 1)]),
    "3": ("yellow", 1, .65, [(1, 28), (3.0, 28), (3.0, 14), (18, 14), (18, 1)]),
    "9": ("yellow", 1, .25, [(1, 30), (3.6, 30), (3.6, 23.0), (15, 23.0), (15, 22)]),
    "8": ("white", 1, .45, [(1, 31), (4.2, 31), (4.2, 23.4), (16, 23.4), (16, 22)]),
    "10": ("blue", 1, .65, [(1, 29), (4.8, 29), (4.8, 23.8), (17, 23.8), (17, 22)]),
    "7": ("turq", 1, .5, [(7, 28), (14, 28), (14, 24.2), (18, 24.2), (18, 22)]),
    "1": ("yellow", 1, .75, [(15, 22), (14, 21.2), (14, 1)]),
    "2": ("blue", 1, .25, [(17, 22), (16.5, 21.4), (16.5, 20.4), (15, 20.4), (15, 1)]),
    "6": ("white", 1, .8, [(7, 27), (13, 27), (13, 1)]),
    # step 3: DAC and encoder
    "12": ("yellow", 2, .35, [(7, 25), (7, 10.7), (9.4, 10.7), (9.4, 7), (8, 7)]),
    "11": ("blue", 2, .65, [(7, 26), (6.3, 26), (6.3, 10), (10.1, 10), (10.1, 5), (8, 5)]),
    "13": ("turq", 2, .5, [(1, 25), (1, 9.6), (3.5, 9.6), (3.5, 6), (8, 6)]),
    "15": ("yellow", 2, .5, [(7, 29), (9, 29), (9, 25)]),
    "14": ("turq", 2, .5, [(7, 30), (8, 30), (8, 25)]),
    "16": ("white", 2, .45, [(1, 32), (1.6, 32.5), (10, 32.5), (10, 25)]),
}
leads = []
STEPS = ["Step 1: power (red and black)", "Step 2: display and SD card", "Step 3: DAC and encoder"]


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
    for r in range(1, ROWS + 1):
        xx = ox + (COLS + 1) * P + 9 if mirror else ox - 9
        if r % 2 or not mirror:
            o.append(f'<text x="{xx}" y="{Y(r) + 3.5:.1f}" font-size="10" text-anchor="middle" fill="#555">{r}</text>')

    op = 0.16 if mirror else 0.93
    lab = "#111" if mirror else "#fff"
    soft = "#333" if mirror else "#dfe8f5"
    metal = .3 if mirror else 1.0
    if not mirror:
        box(23.4, 8.3, 30.9, 17.8, "#e9edf2", "#7a8799", 4)
        t(27.2, 12.5, "SD card", 13, fill="#333", weight="bold")
        t(27.2, 13.5, "sticks out of the case", 11, fill="#555")
    box(10.0, 0.33, 23.4, 23.2, "#c8372d", "#7d1d17", 4, op, mirror)                # display
    if not mirror:
        box(10.8, 3.6, 22.6, 19.6, "#15171a", "#000", 3)
        t(16.7, 10.6, "Display", 18, fill=lab, weight="bold")
        t(16.7, 11.7, "screen up, header at the top", 11.5, fill=soft)
    box(1.0, -0.9, 9.0, 10.0, "#1d1d22", "#000", 4, op, mirror)                     # DAC
    box(3.5, -1.7, 6.5, 1.3, "#9a9a9a", "#555", 3, metal, mirror)
    if not mirror:
        t(5.0, -0.8, "jack", 11)
        t(5.0, 5.5, "DAC", 17, fill=lab, weight="bold")
    else:
        t(5.0, 3.0, "DAC", 12, fill="#555")
    box(0.4, 10.2, 9.9, 24.0, "#b9bec6", "#6d7480", 6, op, mirror)                  # battery, on the front
    if not mirror:
        t(5.15, 16.6, "Battery", 17, weight="bold")
        t(5.15, 17.8, "leads soldered to the charger from above", 10.5, fill="#333")
    else:
        t(5.15, 17.0, "Battery", 12, fill="#555")
    box(0.48, 24.2, 7.52, 33.63, "#1f4f9c", "#0d2c5e", 4, op, mirror)               # ESP32
    box(2.4, 31.5, 5.6, 34.2, "#c9c9c9", "#666", 3, metal, mirror)
    if not mirror:
        t(4, 33.0, "USB-C", 10.5)
        t(4, 28.5, "ESP32", 15, fill=lab, weight="bold")
        t(4, 29.6, "flashing port", 10.5, fill=soft)
    else:
        t(4, 34.1, "ESP32", 12, fill="#555", halo=False)
    box(7.55, 24.3, 14.9, 34.5, "#16181c", "#000", 4, op, mirror)                   # encoder, 19 x 26 mm
    box(15.1, 24.2, 21.9, 34.6, "#1f6aa8", "#0d3a61", 4, op, mirror)                # charger
    box(16.7, 32.3, 20.3, 35.2, "#c9c9c9", "#666", 3, metal, mirror)
    if not mirror:
        for rad, f in ((2.6, "#9aa0a8"), (1.1, "#d5d8dc")):
            o.append(f'<circle cx="{X(11.3):.1f}" cy="{Y(30.0):.1f}" r="{rad * P}" fill="{f}" stroke="#444"/>')
        t(11.3, 33.7, "Encoder, knob up", 12, fill=lab, weight="bold")
        t(18.5, 33.8, "USB-C", 10.5)
        t(18.5, 28.5, "Charger", 15, fill=lab, weight="bold")
        t(18.5, 29.6, "charging port", 10.5, fill=soft)
    else:
        t(10.5, 33.4, "Encoder", 12, fill="#555")
        t(18.5, 30.0, "Charger", 12, fill="#555")

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

    dark = set()
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
        if not mirror and r == 25 and c >= 8:
            side = "d"
        tc = "#111" if mirror or (c, r) in dark else "#fff"
        size = 10.5 if not mirror else 10
        if side in "lr":
            dx = .42 if side == "r" else -.42
            anchor = "start" if (dx > 0) != mirror else "end"
            t(c + dx, r, n, size, anchor, tc, "bold")
        else:
            t(c, r + (-.64 if side == "u" else .64), n, size - 1 if len(n) > 3 else size, "middle", tc, "bold")
    for c in range(1, COLS + 1):                                                     # column numbers, on top of the parts
        if c % 2 or not mirror:
            o.append(f'<text x="{X(c):.1f}" y="{oy + 9}" font-size="10" text-anchor="middle" fill="#333" '
                     f'stroke="#f1e2c6" stroke-width="3" paint-order="stroke">{c}</text>')


def layout():
    P = 30
    W, H = (COLS + 1) * P + 330, (ROWS + 1) * P + 200
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
         f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>',
         f'<text x="{W / 2}" y="38" font-size="21" text-anchor="middle" font-weight="bold">Perf board layout: component side</text>',
         f'<text x="{W / 2}" y="62" font-size="13" text-anchor="middle" fill="#444">Columns 1–22 left to right, rows 1–34 top to bottom, matching the soldered board. The power switch goes in the case wall.</text>']
    draw_board(o, 50, 145, P, False)
    o.append("</svg>")
    (IMG / "perfboard-layout.svg").write_text("\n".join(o))


def connections():
    P = 27
    pw = (COLS + 1) * P + 70
    W, H = 3 * pw + 40, (ROWS + 1) * P + 270
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
         f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>',
         f'<text x="{W / 2}" y="38" font-size="22" text-anchor="middle" font-weight="bold">Perf board connections: back of the board</text>',
         f'<text x="{W / 2}" y="63" font-size="13.5" text-anchor="middle" fill="#444">The same board three times, seen from the solder side (flipped left to right, so column 1 is on the right). '
         f'Each drawing shows one group of wires. Parts on the front are shown faintly.</text>']
    for i, title in enumerate(STEPS):
        ox = 40 + i * pw
        o.append(f'<text x="{ox + (COLS + 1) * P / 2}" y="104" font-size="17" text-anchor="middle" font-weight="bold">{title}</text>')
        draw_board(o, ox, 170, P, True, i)
    ky = H - 30
    key = [("red", "red: 3.3 V and switch leads"), ("black", "black: GND"), ("yellow", "yellow"), ("blue", "blue"),
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
    W, H = 1300, 790
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
    box(EL, 95, ER - EL, 500, "#1f4f9c", "#0d2c5e")
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
    wire([(350, 210), (EL, 210)], "black", "K1 + K2", (455, 210))
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
                                   (550, "RX", "SW", "white", "16")):
        wire([(330, y), (EL, y)], col, tag, (445, y))
        t(318, y, name, 12, "end", "#fff", "bold"); epin("l", y, pin)
    chip(142, 540, "+  R3", "red"); chip(142, 568, "GND  K1", "black")

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

    nx, ny = 130, 650
    chip(nx, ny, "red pill", "red"); t(nx + 78, ny, "= 3.3 V, chained from the ESP32 3V3 pin (wires R1–R3)", 12.5, "start")
    chip(nx, ny + 32, "black pill", "black"); t(nx + 88, ny + 32, "= GND, chained from the charger OUT− pad (wires K1–K4)", 12.5, "start")
    t(nx, ny + 64, "Pins 12 and 11: one wire to the SD slot (9, 10), which carries on to the display (1, 2).", 12.5, "start")
    t(nx, ny + 96, "Flash through the ESP32's USB-C. Charge through the charger's USB-C.", 12.5, "start", "#444")
    o.append("</svg>")
    (IMG / "wiring-diagram.svg").write_text("\n".join(o))


wiring()
layout()
connections()
print("ok")
