"""Transparency test coupons for the clear filament, before printing the lid in it.

Three 30 x 20 mm plates at 2.0 mm (the lid thickness when they were printed),
1.5 mm and 1.0 mm, each with its thickness embossed 0.3 mm on top so they can
be told apart after printing. Writes transparency_coupons.stl beside this file.

Print flat with the settings the lid will use (layer height, walls, top and
bottom layers, speed), then hold each over the charging board's LED and the
ESP32's to pick the thickness that shows them best. Clear filament is clearest
with few, fat layers and no infill gaps: try 100 % infill, a slightly higher
nozzle temperature and slower speed if the 2 mm plate is too milky.
"""

from pathlib import Path

from build123d import *

PLATE_W, PLATE_D, GAP = 30.0, 20.0, 8.0
THICKNESSES = (2.0, 1.5, 1.0)
LABEL_H = 0.3

OUT = Path(__file__).resolve().parent


def coupons():
    parts = None
    for i, t in enumerate(THICKNESSES):
        x = i * (PLATE_W + GAP)
        plate = Pos(x + PLATE_W / 2, PLATE_D / 2, t / 2) * Box(PLATE_W, PLATE_D, t)
        label = Pos(x + PLATE_W / 2, PLATE_D / 2, t) * extrude(
            Text(f"{t:g}", font_size=6, align=(Align.CENTER, Align.CENTER)), LABEL_H
        )
        part = plate + label
        parts = part if parts is None else parts + part
    return parts


if __name__ == "__main__":
    shape = coupons()
    export_stl(shape, str(OUT / "transparency_coupons.stl"), tolerance=0.02)
    bb = shape.bounding_box()
    print("coupons", [round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)], "mm")
