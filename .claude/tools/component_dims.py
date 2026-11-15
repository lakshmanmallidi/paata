#!/usr/bin/env python3
"""Draws the measured dimensions onto the component photos in hardware/components/.

The untouched photos are read from git (commit SRC), so this can be re-run when a
measurement changes.  Run with:  uv run --with pillow .claude/tools/component_dims.py
"""
import io
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hardware/components"
SRC = "558b775:hardware/images/"
FONT = "/System/Library/Fonts/Helvetica.ttc"

# name: (part box l, t, r, b in photo pixels, width label, height label, caption)
PARTS = {
    "esp32-s3-zero": ((245, 515, 1160, 1850), "17.9 mm", "23.8 mm with USB-C",
                      "Waveshare ESP32-S3-Zero: 17.9 × 23.8 mm including the USB-C socket."),
    "pcm5102a-dac": ((330, 575, 1225, 2095), "20.2 mm", "30.9 mm with jack",
                     "Adafruit PCM5102A I2S DAC: 20.2 × 30.9 mm including the headphone jack."),
    "st7735-tft-back": ((350, 625, 1240, 2085), "34 mm", "58.2 mm",
                        "1.8\" ST7735 display, back side: board 34 × 58.2 mm. A full-size SD card "
                        "(or microSD adapter) sticks out 19 mm, making it 53 mm across."),
    "ky040-encoder": ((195, 825, 910, 1665), "21.7 mm (19 after trimming)", "26.0 mm",
                      "KY-040 / M274 rotary encoder: board 21.7 × 26.0 mm without the header pins, "
                      "trimmed to 19 mm wide for this build."),
    "tp4056-charger": ((395, 820, 985, 1760), "17.3 mm", "26.7 mm",
                       "TP4056 USB-C charger with protection: 17.3 × 26.7 mm."),
    "lipo-battery": ((375, 800, 1100, 1835), "25 mm (nominal)", "35 mm (nominal)",
                     "3.7 V 950 mAh LiPo, type 102535: 10.9 mm thick (measured). "
                     "25 × 35 mm is the nominal size; length and width are not measured yet."),
}


def label(text, size):
    f = ImageFont.truetype(FONT, size)
    w, h = f.getbbox(text)[2:]
    im = Image.new("RGBA", (w + 36, h + 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 14, fill=(20, 20, 20, 235), outline="white", width=3)
    d.text((18, 9), text, font=f, fill="white")
    return im


def dim_line(d, a, b):
    """Line from a to b with end ticks, white on a dark outline."""
    (x0, y0), (x1, y1) = a, b
    horiz = y0 == y1
    ticks = [((x, y0 - 28), (x, y0 + 28)) for x in (x0, x1)] if horiz else [((x0 - 28, y), (x0 + 28, y)) for y in (y0, y1)]
    for col, w in (("black", 14), ("white", 7)):
        d.line((a, b), fill=col, width=w)
        for t in ticks:
            d.line(t, fill=col, width=w)


for name, ((l, t, r, b), wl, hl, cap) in PARTS.items():
    raw = subprocess.run(["git", "-C", str(ROOT), "show", SRC + name + ".jpg"], capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    d = ImageDraw.Draw(im)
    ty, rx = t - 90, r + (160 if name == "ky040-encoder" else 90)   # width line above, height line to the right (clear of the knob)
    dim_line(d, (l, ty), (r, ty))
    dim_line(d, (rx, t), (rx, b))
    lw = label(wl, 54)
    im.paste(lw, ((l + r - lw.width) // 2, ty - lw.height - 34), lw)
    lh = label(hl, 54).rotate(90, expand=True)
    im.paste(lh, (rx + 34, (t + b - lh.height) // 2), lh)
    box = (max(0, l - 130), max(0, ty - lw.height - 80), min(im.width, rx + lh.width + 80), min(im.height, b + 110))
    im = im.crop(box)
    im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
    f = ImageFont.truetype(FONT, 26)
    lines = textwrap.wrap(cap, 66)
    out = Image.new("RGB", (900, im.height + 30 + 36 * len(lines)), (24, 24, 24))
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    for i, s in enumerate(lines):
        d.text((24, im.height + 16 + 36 * i), s, font=f, fill="white")
    out.save(OUT / f"{name}.jpg", quality=88)
print("ok")
