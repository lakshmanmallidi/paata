#!/usr/bin/env python3
"""Generate hardware/images/breadboard-layout.svg (Paata breadboard build).

Run from the repo root:  python3 .claude/tools/breadboard_layout.py

Coordinates: x = breadboard row number (1..63), y = "units" of one hole pitch.
The MCU sits at the right end with its USB port pointing right.
"""
import os

P = 14           # pixels per hole pitch (2.54 mm)
X0, Y0 = 62, 150  # pixel position of row 1 / y-unit 0

# y-units of each breadboard line
Y = {"T+": 0, "T-": 1, "j": 3.5, "i": 4.5, "h": 5.5, "g": 6.5, "f": 7.5,
     "e": 10.5, "d": 11.5, "c": 12.5, "b": 13.5, "a": 14.5, "B+": 17, "B-": 18}


def px(x):
    return round(X0 + (x - 1) * P, 1)


def py(y):
    return round(Y0 + (Y[y] if isinstance(y, str) else y) * P, 1)


out = []


def add(s):
    out.append(s)


def rect(x1, y1, x2, y2, **kw):
    style = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    add(f'<rect x="{px(x1)}" y="{py(y1)}" width="{round((x2 - x1) * P, 1)}" '
        f'height="{round((yv(y2) - yv(y1)) * P, 1)}" {style}/>')


def yv(y):
    return Y[y] if isinstance(y, str) else y


def text(x, y, s, size=9, anchor="middle", rot=None, fill="#222", weight="normal", dx=0, dy=0):
    X, Yp = px(x) + dx, py(y) + dy
    tr = f' transform="rotate({rot} {X} {Yp})"' if rot is not None else ""
    add(f'<text x="{X}" y="{Yp}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
        f'font-weight="{weight}"{tr}>{s}</text>')


def wire(points, color, dashed=False, width=3):
    pts = [(px(x), py(y)) for x, y in points]
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    add(f'<path d="{d}" fill="none" stroke="#1b1b1b" stroke-opacity="0.55" stroke-width="{width + 1.6}" '
        f'stroke-linejoin="round" stroke-linecap="round"{dash}/>')
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"{dash}/>')
    for x, y in (pts[0], pts[-1]):
        add(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{color}" stroke="#1b1b1b" stroke-width="1"/>')


def pin(x, y, color="#c9a227"):
    add(f'<circle cx="{px(x)}" cy="{py(y)}" r="3.3" fill="{color}" stroke="#5a4a10" stroke-width="0.8"/>')


W, H = 1010, 730
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'font-family="Helvetica, Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
add(f'<text x="{W / 2}" y="30" font-size="19" text-anchor="middle" font-weight="bold" fill="#111">'
    f'Paata — breadboard layout (830-point board, top view)</text>')
add(f'<text x="{W / 2}" y="50" font-size="11.5" text-anchor="middle" fill="#444">'
    f'Numbers are breadboard rows, letters are columns. Every wire end sits in the hole shown; '
    f'board outlines are approximate.</text>')

# ---------- breadboard ----------
rect(-0.6, -1.2, 64.6, 19.2, fill="#f3efe4", stroke="#b9b29c", rx=6)
rect(0.2, 8.15, 63.8, 9.85, fill="#e2dccb")                      # centre trench
for name, col in (("T+", "#d62728"), ("T-", "#1f4fb4"), ("B+", "#d62728"), ("B-", "#1f4fb4")):
    off = -0.5 if name.endswith("+") else 0.5
    add(f'<line x1="{px(1.5)}" y1="{py(Y[name] + off)}" x2="{px(62.5)}" y2="{py(Y[name] + off)}" '
        f'stroke="{col}" stroke-width="1.2"/>')
    text(0.3, name, name[1].replace("-", "−"), size=11, fill=col, weight="bold", dy=4)
    for r in range(2, 63):
        add(f'<circle cx="{px(r)}" cy="{py(name)}" r="1.9" fill="#55524a"/>')
for letter in "jihgfedcba":
    text(0.0, letter, letter, size=9, fill="#777", dy=3)
    text(64.0, letter, letter, size=9, fill="#777", dy=3)
    for r in range(1, 64):
        add(f'<circle cx="{px(r)}" cy="{py(letter)}" r="1.9" fill="#55524a"/>')
for r in [1] + list(range(5, 64, 5)):
    text(r, 9.0, str(r), size=8, fill="#8a8473", dy=3)

# ---------- wires that run underneath raised parts go first ----------
RED, BLK = "#d62728", "#2b2b2b"
C = dict(bck="#1f77b4", wsel="#17becf", din="#8e44ad", sck="#ff7f0e", sda="#2ca02c", a0="#b5a400",
         rst="#8c564b", cs="#e377c2", led="#f5d000", dt="#00897b", clk="#5fbf00", sd="#6c3fc4",
         lead="#7a7a7a")

# ---------- modules ----------
# DAC: header in column a rows 29-36, body hanging off the near edge, jack pointing left
rect(27.4, 13.9, 37.6, 20.9, fill="#22252b", stroke="#000", rx=4)
rect(25.6, 15.9, 28.6, 18.9, fill="#3a3a3a", stroke="#000", rx=2)
rect(14.6, 15.5, 25.6, 19.3, fill="#ffffff", fill_opacity="0.6", stroke="#888", stroke_dasharray="5 4", rx=6)
text(20.1, 17.4, "headphone plug", size=9, fill="#555", dy=3)
for r, n in zip(range(29, 37), ["Rout", "G", "Lout", "BCK", "DIN", "WSEL", "GND", "VIN"]):
    pin(r, "a")
    text(r, 15.25, n, size=8, anchor="end", rot=-90, fill="#fff", dx=3)
text(32.5, 19.6, "PCM5102A DAC", size=10, fill="#fff", weight="bold")
text(32.5, 20.5, "header on the 8-pin side only", size=7.5, fill="#cfcfcf")

# MCU: rows 55-63, pins in columns g and c, USB to the right
rect(54.4, 5.95, 63.6, 13.05, fill="#1f4e8c", stroke="#0c2a52", rx=4)
rect(62.6, 8.0, 65.4, 11.0, fill="#c8c8c8", stroke="#666", rx=2)
text(66.0, 9.5, "USB-C", size=9, anchor="start", fill="#444", dy=-2)
text(66.0, 9.5, "to Mac", size=9, anchor="start", fill="#444", dy=9)
top = ["6", "5", "4", "3", "2", "1", "3V3", "GND", "5V"]
bot = ["7", "8", "9", "10", "11", "12", "13", "RX", "TX"]
for i, r in enumerate(range(55, 64)):
    pin(r, "g")
    pin(r, "c")
    text(r, 7.1, top[i], size=8, anchor="end", rot=-90, fill="#fff", dx=3)
    text(r, 11.9, bot[i], size=8, anchor="start", rot=-90, fill="#fff", dx=3)
text(59.6, 9.7, "ESP32-S3-Zero", size=10, fill="#fff", weight="bold")
for x, n in ((55.0, "14"), (56.0, "15"), (57.0, "16")):
    add(f'<circle cx="{px(x)}" cy="{py(10.55)}" r="3.4" fill="#e8c34a" stroke="#fff" stroke-width="1"/>')
    text(x, 10.55, n, size=6.5, fill="#fff", dy=-6)

# buttons across the trench
for r, n in ((28, "PREV"), (49, "NEXT")):
    rect(r - 0.25, 7.25, r + 2.25, 10.75, fill="#2d2d2d", stroke="#000", rx=2)
    add(f'<circle cx="{px(r + 1)}" cy="{py(9.0)}" r="9" fill="#555" stroke="#111"/>')
    for rr in (r, r + 2):
        pin(rr, "e", "#bbb")
        pin(rr, "f", "#bbb")
    text(r + 1, 9.0, n, size=8, weight="bold", fill="#fff", dy=3)

# display: header in column a rows 43-50, body hanging off the near edge
rect(39.6, 13.9, 53.4, 36.3, fill="#c62828", stroke="#7f1010", rx=4)
rect(41.0, 19.3, 52.0, 33.4, fill="#101418", stroke="#000", rx=2)
text(46.5, 25.6, "1.8\" ST7735 TFT", size=12, fill="#e8e8e8", weight="bold")
text(46.5, 26.8, "screen facing up", size=9.5, fill="#bdbdbd")
text(46.5, 28.0, "(microSD slot underneath)", size=9.5, fill="#bdbdbd")
for r, n in zip(range(43, 51), ["LED", "SCK", "SDA", "A0", "RESET", "CS", "GND", "VCC"]):
    pin(r, "a")
    text(r, 15.25, n, size=8, anchor="end", rot=-90, fill="#fff", dx=3)
sd_pads = {"SD_SCK": 44.8, "SD_MISO": 45.9, "SD_MOSI": 46.9, "SD_CS": 48.0}
for n, x in sd_pads.items():
    pin(x, 35.3)
    text(x, 34.75, n, size=7, anchor="start", rot=-90, fill="#fff", dx=2.5)

# ---------- wires ----------
# power: the DAC and encoder share rows 35/36, fed straight from the MCU's GND and 3V3 rows
wire([(35, "e"), (35, 1.4), (62, 1.4), (62, "j")], BLK)
wire([(36, "e"), (36, 1.8), (61, 1.8), (61, "j")], RED)
wire([(49, "d"), (48.4, 11.5), (48.4, 4.0), (62, 4.0), (62, "i")], BLK)
wire([(50, "d"), (51.7, 11.5), (51.7, 4.5), (61, "i")], RED)
# I2S
wire([(34, "e"), (34, 5.5), (55, "h")], C["wsel"])
wire([(32, "e"), (32, 5.05), (56, 5.05), (56, "h")], C["bck"])
wire([(33, "c"), (33, 13.2), (42.0, 13.2), (42.0, 11.1), (54.0, 11.1), (54.0, 13.5), (55, "b")], C["din"])
# display: signals to the near side of the MCU
outl = [("sck", 44, "b", 13.5, 51.0, 16.6, 60), ("sda", 45, "c", 13.1, 51.6, 16.2, 59),
        ("cs", 48, "c", 12.7, 52.2, 15.8, 58), ("a0", 46, "c", 12.3, 52.8, 15.4, 57),
        ("rst", 47, "d", 11.9, 53.4, 15.0, 56)]
for key, r, hole, lane, xd, lane2, rm in outl:
    wire([(r, hole), (r, lane), (xd, lane), (xd, lane2), (rm - 0.45, lane2), (rm - 0.45, 13.5), (rm, "b")], C[key])
wire([(43, "e"), (43, 3.0), (57, 3.0), (57, "j")], C["led"])
# encoder signals
wire([(38, "e"), (38, 2.6), (59, 2.6), (59, "j")], C["dt"])
wire([(39, "e"), (39, 2.2), (60, 2.2), (60, "j")], C["clk"])
# SD card: female-to-male jumpers from the pads
wire([(46.9, 35.3), (46.9, 37.2), (59, 37.2), (59, "a")], C["sd"], dashed=True)
wire([(45.9, 35.3), (45.9, 37.8), (61, 37.8), (61, "a")], C["sd"], dashed=True)
wire([(44.8, 35.3), (44.8, 38.4), (60, 38.4), (60, "a")], C["sd"], dashed=True)
# flying leads shown as tagged stubs
for x, yh, label, col in ((37, "e", "◂ pad 14 (SW)", C["lead"]), (58, "j", "◂ SD_CS pad", C["sd"]),
                          (28, "g", "◂ pad 15", C["lead"]), (51, "g", "◂ pad 16", C["lead"])):
    wire([(x, yh), (x, -1.5)], col, dashed=True, width=2.4)
    text(x, -1.8, label, size=9, anchor="start", rot=-90, fill="#333", dx=3, weight="bold")
add(f'<circle cx="{px(48.0)}" cy="{py(35.3)}" r="3.6" fill="{C["sd"]}" stroke="#1b1b1b" stroke-width="1"/>')
text(48.7, 35.3, "→ row 58 j", size=8.5, fill="#fff", anchor="start", dy=3, weight="bold")

# ---------- encoder (drawn last: it stands above the wires) ----------
rect(34.6, 11.75, 39.4, 14.4, fill="#9aa0a6", fill_opacity="0.4", stroke="#555", rx=2)
rect(36.3, 14.4, 37.7, 19.4, fill="#c8ccd0", fill_opacity="0.25", stroke="#666", stroke_dasharray="4 3", rx=3)
rect(32.9, 11.25, 41.1, 11.75, fill="#111", stroke="#000")
for r, n in zip(range(35, 40), ["GND", "+", "SW", "DT", "CLK"]):
    pin(r, "d")
    text(r, 12.05, n, size=7.5, anchor="end", rot=-90, fill="#111", dx=3, weight="bold")
text(37, 18.9, "knob", size=7.5, fill="#fff")
text(32.5, 12.0, "Encoder", size=9, weight="bold", fill="#222", anchor="end", dy=3)

# ---------- legend ----------
LX, LY = 30, 492
add(f'<rect x="{LX - 12}" y="{LY - 22}" width="548" height="182" fill="#fafafa" stroke="#ccc" rx="6"/>')
add(f'<text x="{LX}" y="{LY - 4}" font-size="12" font-weight="bold" fill="#111">Wire colours</text>')
items = [("3.3 V", RED, 0), ("GND", BLK, 0), ("I2S BCK", C["bck"], 0), ("I2S WSEL", C["wsel"], 0),
         ("I2S DIN", C["din"], 0), ("TFT SCK", C["sck"], 0), ("TFT SDA", C["sda"], 0),
         ("TFT A0", C["a0"], 0), ("TFT RESET", C["rst"], 0), ("TFT CS", C["cs"], 0),
         ("TFT LED", C["led"], 0), ("Encoder DT", C["dt"], 0), ("Encoder CLK", C["clk"], 0),
         ("SD card (female–male jumper)", C["sd"], 1), ("Wire soldered to pad 14/15/16", C["lead"], 1)]
for i, (name, col, dashed) in enumerate(items):
    cx, cy = LX + (i // 5) * 165, LY + 16 + (i % 5) * 19
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    add(f'<line x1="{cx}" y1="{cy}" x2="{cx + 30}" y2="{cy}" stroke="#1b1b1b" stroke-opacity="0.55" stroke-width="4.6"{dash}/>')
    add(f'<line x1="{cx}" y1="{cy}" x2="{cx + 30}" y2="{cy}" stroke="{col}" stroke-width="3"{dash}/>')
    add(f'<text x="{cx + 37}" y="{cy + 4}" font-size="10.5" fill="#222">{name}</text>')
notes = ["Dashed tags at the top: plug the loose end of that wire into the hole below the tag.",
         "Pads 14, 15, 16 on the ESP32 board do not reach the breadboard: solder a wire to each.",
         "Power comes from USB. The power rails, 5V pin, battery and charger are not used."]
for i, n in enumerate(notes):
    add(f'<text x="{LX}" y="{LY + 118 + i * 14}" font-size="10" fill="#444">{n}</text>')

add("</svg>")
dst = os.path.join(os.path.dirname(__file__), "..", "..", "hardware", "images", "breadboard-layout.svg")
with open(dst, "w") as f:
    f.write("\n".join(out))
print("wrote", os.path.normpath(dst))
