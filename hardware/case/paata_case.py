#!/usr/bin/env python3
"""Paata case: parametric model (concept stage).

Run from the repo root:
    uv run --python 3.12 --with build123d --with pyvista hardware/case/paata_case.py

Writes base.stl, lid.stl, two short test pieces for the port openings (test-usb-end.stl,
test-jack-end.stl) and concept renders into hardware/case/.

Coordinates, in mm: X to the right seen from the front, Y from the USB-C end (0) up to
the headphone jack end, Z from the lowest wire on the back of the board (0) towards
the screen. The board figures are caliper readings from hardware/assembly/; values
marked EST are read off photos and still need measuring.
"""
from pathlib import Path

from build123d import *

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- measured
BOARD_W = 59.1        # perf board plus the display's overhang
BOARD_L = 89.9        # USB-C sockets to the DAC edge; the jack tip is 1 mm further
STACK_H = 15.7        # back wires to the top of the battery
SCREEN_Z = 10.9       # EST: 8.4 above the back of the perf board, plus 2.5 of wires
ENC_BODY_Z = 15.4

# ---------------------------------------------------------------- case
GAP = 0.6             # clearance around the board
WALL = 2.0
FLOOR = 2.0
LID = 2.0
HEAD = 0.8            # clearance above the battery
X0, X1 = -GAP, BOARD_W + GAP
Y0, Y1 = -GAP, BOARD_L + GAP
ZTOP = STACK_H + HEAD                 # top of the base walls, underside of the lid
LUG_R = 5.0                           # corner lugs: M3 screw from the top into a captive hex nut
LUG_OFF = 3.6
NUT_AF, NUT_T = 5.5, 2.4              # M3 nut: across flats, thickness
NUT_DROP = 4.0                        # plastic between the lid and the nut slot

# positions, EST unless noted (y is measured down from the jack end in the photos)
yd = lambda y: BOARD_L - y
JACK_X, JACK_Z, JACK_D = X0 + 13.5, ZTOP - 4.5, 6.0     # from the inside of the left wall and the top of the wall; 1 mm towards the screen side after the second print
USB_ESP_X, USB_CHG_X, USB_Z = 11.3, 48.1, 9.8      # first print +2: the owner asked for 3 back from the second print, which was at +5
SD_Y0, SD_Y1, SD_Z = yd(46.8), yd(22.8), 5.6
ENC_X, ENC_Y = 27.5, yd(76.7)
WIN_X, WIN_Y, WIN_W, WIN_H = 41.9, yd(34.5), 30.0, 37.0      # screen window at the screen face

# slide switch pod on the right wall (switch: body 10.5 x 5.7 x 5.0, 20 across the ears)
# Owner's sizes are the inside of the pocket: 10 out from the wall, 20 long, 6 high.
# Walls are added on top. The pocket is open at the top and closed by the lid, so the
# switch drops in from above.
POCKET_D, POCKET_L, POCKET_H = 10.0, 20.4, 6.2
POD_WALL = 2.5                        # outer wall, which the ears screw to
POD_END = 2.0                         # end walls
POD_FLOOR = 2.0
POD_OUT = POCKET_D + POD_WALL         # how far the pod stands out from the case wall
SW_Y = 16.5
SW_Z = ZTOP - POCKET_H / 2
POD_Y0, POD_Y1 = SW_Y - POCKET_L / 2 - POD_END, SW_Y + POCKET_L / 2 + POD_END


def pod_footprint():
    xo = X1 + WALL
    return Pos(xo + POD_OUT / 2 - 1, (POD_Y0 + POD_Y1) / 2) * RectangleRounded(POD_OUT + 2, POD_Y1 - POD_Y0, 1.5)


def B(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def outline():
    cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
    s = Pos(cx, cy) * RectangleRounded(X1 - X0 + 2 * WALL, Y1 - Y0 + 2 * WALL, 3.0)
    for x, y in lugs():
        s += Pos(x, y) * Circle(LUG_R)
    return s


def lugs():
    return [(x, y) for x in (X0 - LUG_OFF, X1 + LUG_OFF) for y in (Y0 - LUG_OFF, Y1 + LUG_OFF)]


def base():
    xo = X1 + WALL
    b = Pos(0, 0, -FLOOR) * extrude(outline(), FLOOR + ZTOP)
    zb = ZTOP - POCKET_H - POD_FLOOR                                      # underside of the pod
    b += Pos(0, 0, zb) * extrude(pod_footprint(), ZTOP - zb)
    gusset = extrude(Plane.XZ.offset(-POD_Y0) * Polygon((xo - 0.5, zb + 1), (xo + POD_OUT + 1, zb + 1), (xo - 0.5, zb - POD_OUT - 0.5), align=None),
                     POD_Y1 - POD_Y0)                                     # 45 degree underside, prints without support
    b += gusset & (Pos(0, 0, -FLOOR) * extrude(pod_footprint(), zb + 1 + FLOOR))
    b -= B(X0, X1, Y0, Y1, 0, ZTOP + 1)                                   # board cavity
    b -= B(X1 - 1, xo + POCKET_D, SW_Y - POCKET_L / 2, SW_Y + POCKET_L / 2, ZTOP - POCKET_H, ZTOP + 1)   # switch pocket, open at the top and into the cavity
    b -= B(xo + POCKET_D - 1, xo + POD_OUT + 1, SW_Y - 4.5, SW_Y + 4.5, SW_Z - 2.2, ZTOP + 1)            # slider slot, open at the top: no bridge, and the slider drops in
    for dy in (-8, 8):                                                    # pilot holes for the ear screws
        b -= Pos(xo + POCKET_D, SW_Y + dy, SW_Z) * Rot(0, 90, 0) * Cylinder(0.85, 4)
    b -= Pos(JACK_X, Y1 + WALL / 2, JACK_Z) * Rot(90, 0, 0) * Cylinder(JACK_D / 2, WALL + 2)   # headphone jack
    for x in (USB_ESP_X, USB_CHG_X):                                      # USB-C openings, sized for the plug shell
        b -= Pos(x, Y0 - WALL / 2, USB_Z) * Rot(90, 0, 0) * extrude(RectangleRounded(13.5, 6.8, 2.5), WALL + 2, both=True)
    b -= B(X1 - 1, xo + 1, SD_Y0 - 1, SD_Y1 + 1, SD_Z - 1.8, SD_Z + 1.8)  # SD card slot
    cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
    for x, y in lugs():
        b -= Pos(x, y, ZTOP - 6) * Cylinder(1.7, 12.2)                    # M3 clearance hole, 12 deep
        ang = {(True, True): 45, (False, True): 135, (False, False): 225, (True, False): 315}[(x > cx, y > cy)]
        L = 3.3 + LUG_R + 1                                               # slot runs from the screw axis out through the lug
        b -= (Pos(x, y, ZTOP - NUT_DROP - (NUT_T + 0.3) / 2) * Rot(0, 0, ang) * Pos(L / 2 - 3.3, 0, 0)
              * Box(L, NUT_AF + 0.2, NUT_T + 0.3))                        # the nut slides in from outside and cannot turn
    return b


def test_ends(depth=6.0):
    """Short slices of the base at each end, to check the port openings without printing the whole case."""
    b = base()
    xa, xb = X0 - WALL, X1 + WALL
    usb = b & B(xa, xb, Y0 - WALL, Y0 + depth, -FLOOR, ZTOP)
    jack = b & B(xa, xb, Y1 - depth, Y1 + WALL, -FLOOR, ZTOP)
    return usb, jack


def lid():
    l = Pos(0, 0, ZTOP) * extrude(outline() + pod_footprint(), LID)
    zb = SCREEN_Z + 0.5                                                   # the shroud stops just above the screen
    top_w, top_h, t = WIN_W + 3, WIN_H + 4, 1.2
    shroud = B(WIN_X - top_w / 2 - t, min(WIN_X + top_w / 2 + t, X1 - 0.2), WIN_Y - top_h / 2 - t, WIN_Y + top_h / 2 + t, zb, ZTOP)
    cut = loft([Pos(WIN_X, WIN_Y, zb - 0.1) * Rectangle(WIN_W, WIN_H),
                Pos(WIN_X, WIN_Y, ZTOP + LID + 0.1) * Rectangle(top_w, top_h)])
    l = l + shroud - cut
    l -= Pos(ENC_X, ENC_Y, ZTOP + LID / 2) * Cylinder(3.8, LID + 2)       # encoder bush
    for x, y in lugs():
        l -= Pos(x, y, ZTOP + LID / 2) * Cylinder(1.7, LID + 2)
        l -= Pos(x, y, ZTOP + LID - 0.6) * Cone(1.7, 3.1, 1.4)            # 90 degree countersink for a flat-head M3; prints face down without support
    return l


def dummies():
    """Simplified board and parts, for the renders only."""
    c = lambda x0, x1, y0, y1, z0, z1: B(x0, x1, yd(y1), yd(y0), z0, z1)
    return {
        "perf": (c(0, 56.6, 1.3, 88.4, 2.5, 4.1), "#c98f4a"),
        "dac": (c(1.7, 22.0, 0, 25.8, 6.6, 8.2) + c(8.2, 15.6, -1, 12, 8.2, 13.2), "#26262b"),
        "battery": (c(0.3, 24.0, 26.3, 61.4, 4.1, 15.0), "#c9ccd2"),
        "esp32": (c(0.3, 18.2, 61.9, 85.8, 6.6, 8.2) + c(5.2, 13.3, 81, 89.9, 8.2, 11.4), "#2a56a5"),
        "encoder": (c(18.6, 37.0, 62.1, 88.0, 6.6, 8.2) + c(21.5, 33.5, 70.7, 82.7, 8.2, ENC_BODY_Z)
                    + Pos(ENC_X, ENC_Y, ENC_BODY_Z + 3.5) * Cylinder(3.5, 7) + Pos(ENC_X, ENC_Y, 26) * Cylinder(3.0, 10), "#3a3d42"),
        "charger": (c(37.5, 54.7, 62.0, 88.9, 6.6, 8.2) + c(42.0, 50.2, 82, 89.9, 8.2, 11.4), "#1f6aa8"),
        "display": (c(24.6, 59.1, 1.2, 59.4, 6.6, 8.2), "#c8372d"),
        "screen": (c(25.5, 58.5, 10.9, 53.7, 8.2, SCREEN_Z), "#11161c"),
        "sdcard": (c(40.0, 78.0, 22.8, 46.8, 4.6, 6.7), "#e8eaee"),
        "switch": (B(X1 + WALL + POCKET_D - 5.0, X1 + WALL + POCKET_D, SW_Y - 5.25, SW_Y + 5.25, SW_Z - 2.85, SW_Z + 2.85)
                   + B(X1 + WALL + POCKET_D - 0.5, X1 + WALL + POCKET_D, SW_Y - 10, SW_Y + 10, SW_Z - 2.85, SW_Z + 2.85)
                   + B(X1 + WALL + POCKET_D, X1 + WALL + POD_OUT + 2.5, SW_Y - 3.5, SW_Y - 0.5, SW_Z - 1.5, SW_Z + 1.5), "#16181c"),
    }


def knob():
    return Pos(ENC_X, ENC_Y, ZTOP + LID + 6.5 + 7) * Cylinder(8.5, 13)


def render():
    import pyvista as pv
    tmp = OUT / "_tmp.stl"

    def mesh(shape):
        export_stl(shape, str(tmp), tolerance=0.03, angular_tolerance=0.15)
        return pv.read(str(tmp))

    b, l, k = mesh(base()), mesh(lid()), mesh(knob())
    parts = [(mesh(s), col) for s, col in dummies().values()]
    CASE, LIDC = "#e9e4d8", "#f3efe6"

    def shot(name, cam, lift=0.0, show_lid=True, show_parts=True, size=(1500, 1150), zoom=1.0):
        p = pv.Plotter(off_screen=True, window_size=size)
        p.set_background("#fbfaf7")
        edge = lambda m: p.add_mesh(m.extract_feature_edges(35), color="#5b574d", line_width=1.6)
        p.add_mesh(b, color=CASE, smooth_shading=False, specular=0.2)
        edge(b)
        if show_parts:
            for m, col in parts:
                p.add_mesh(m.translate((0, 0, lift * 0.45), inplace=False), color=col, specular=0.3)
        if show_lid:
            lm = l.translate((0, 0, lift), inplace=False)
            p.add_mesh(lm, color=LIDC, specular=0.2)
            edge(lm)
            p.add_mesh(k.translate((0, 0, lift), inplace=False), color="#2b2d31", specular=0.5)
        p.enable_anti_aliasing("ssaa")
        p.camera_position = cam
        p.camera.zoom(zoom)
        p.screenshot(str(OUT / name))
        p.close()

    mid = (32, 45, 8)
    shot("concept-1-closed.png", [(175, -95, 150), mid, (0, 0, 1)])
    shot("concept-2-exploded.png", [(210, -150, 150), (32, 45, 40), (0, 0, 1)], lift=70, size=(1500, 1500))
    shot("concept-3-open.png", [(150, -90, 175), mid, (0, 0, 1)], show_lid=False)
    shot("concept-4-switch-side.png", [(215, -40, 70), (55, 35, 8), (0, 0, 1)], zoom=1.25)
    shot("concept-7-nut-slot.png", [(-75, -60, 42), (-2, 2, 9), (0, 0, 1)], zoom=2.6)
    shot("concept-5-usb-end.png", [(32, -190, 60), mid, (0, 0, 1)])
    shot("concept-6-front.png", [(32, 45, 300), mid, (0, 1, 0)], size=(1150, 1500))
    tmp.unlink()


if __name__ == "__main__":
    export_stl(base(), str(OUT / "base.stl"), tolerance=0.02)
    for name, part in zip(("test-usb-end.stl", "test-jack-end.stl"), test_ends()):
        export_stl(part, str(OUT / name), tolerance=0.02)
    export_stl(Rot(180, 0, 0) * lid(), str(OUT / "lid.stl"), tolerance=0.02)      # print orientation: outside face on the bed
    bb, lb = base().bounding_box(), lid().bounding_box()
    print("base", [round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)], "lid", [round(v, 1) for v in (lb.size.X, lb.size.Y, lb.size.Z)])
    render()
