# Perf board build

Everything except the power switch sits on one perf board, 22 columns × 34 rows of holes (about 56 × 87 mm). The switch goes in the case wall. There are no push buttons: the encoder's own switch does their job. What connects to what is in [WIRING.md](WIRING.md); this page says which hole each pin is in and where each wire is soldered.

Holes are written as column and row: `c7 r31` is column 7, row 31, counted from the top-left corner of the component side. All parts sit on the component side; the back carries only wires.

## Layout

![Perf board layout, component side](images/perfboard-layout.svg)

The positions below were read from a photo of the soldered board.

| Part | Holes | Notes |
|---|---|---|
| DAC | 8-pin side in c8, rows 2–9; 6-pin side in c2, rows 3–8 | Jack over the top edge. Row 2 = Rout, row 9 = VIN. The 6-pin side is not wired. |
| Display | 8-pin header in row 1, c13–c20; SD pads in row 22, c15–c18 | Screen up. c13 = LED, c20 = VCC. The SD card sticks out of the right side. |
| Battery | lies flat in c1–c9, rows 11–23 | Between the DAC and the ESP32, left of the display. Held with tape, no holes used. |
| ESP32-S3-Zero | pins in c1 and c7, rows 25–33 | Bottom-left, USB-C at the bottom edge. Row 25 is GPIO 7 (c1) and GPIO 6 (c7). |
| Encoder (19 × 26 mm) | 5-pin header in row 25, c8–c12 | Bottom-middle, knob up. c8 = CLK, c12 = GND. |
| Charger (TP4056) | top pads in row 25: c16, c17, c20, c21; USB-end pads in row 33: c16, c21 | USB-C at the bottom edge. Left to right: OUT+, B+, B−, OUT−. The row 33 pads are not wired. |

Ports: headphone jack on the top edge, flashing port and charging port on the bottom edge, SD card on the right side.

## Check these first

- **Charger pads**: the order OUT+ `c16`, B+ `c17`, B− `c20`, OUT− `c21` was read from photos. Confirm it against the labels printed on the charger before soldering any power wire.
- **Unidentified joints**: the photo shows solder at `c15 r25` (beside OUT+) and at `c17 r21` and `c18 r21` (above the SD pads). Check with a multimeter that none of them is bridged to the pin next to it.
- **Neighbouring pins**: check that no two neighbouring header pins are bridged, above all on the ESP32 columns.

## Connections on the back

The drawing shows the back of the board three times, one group of wires each, in the order to solder them. Seen from the back, left and right are swapped, so column 1 is on the right. The white tag on each wire is its number in the tables below.

![Perf board connections, back of the board](images/perfboard-connections.svg)

No joint takes more than two wires. The routes are a guide: they keep wires in lanes and as short as the pin positions allow. Wires cross where the display wires pass the DAC wires; that cannot be avoided with this pin map and does no harm with insulated wire.

### Step 1: power

| Wire | Colour | From | To |
|---|---|---|---|
| R1 | red | ESP32 3V3 `c7 r31` | DAC VIN `c8 r9` |
| R3 | red | ESP32 3V3 `c7 r31` | Encoder + `c11 r25` |
| R2 | red | Encoder + `c11 r25` | Display VCC `c20 r1`, along the right edge |
| K1 | black | Charger OUT− `c21 r25` | Encoder GND `c12 r25` |
| K2 | black | Encoder GND `c12 r25` | ESP32 GND `c7 r32` |
| K3 | black | ESP32 GND `c7 r32` | DAC GND `c8 r8` |
| K4 | black | Charger OUT− `c21 r25` | Display GND `c19 r1`, along the right edge |
| B2 | red | ESP32 5V `c7 r33` | Power switch, either outer pin (loose lead) |

The DAC gets its 3.3 V and ground straight from the ESP32, on the shortest run.

### Step 2: display and SD card

SCK and MOSI go from the ESP32 to the SD pads and carry on from there to the display.

| # | Colour | From | To |
|---|---|---|---|
| 9 | yellow | GPIO 12 `c1 r30` | SD_SCK `c15 r22` |
| 1 | yellow | SD_SCK `c15 r22` | Display SCK `c14 r1` |
| 10 | blue | GPIO 11 `c1 r29` | SD_MOSI `c17 r22` |
| 2 | blue | SD_MOSI `c17 r22` | Display SDA `c15 r1` |
| 8 | white | GPIO 13 `c1 r31` | SD_MISO `c16 r22` |
| 7 | turquoise | GPIO 3 `c7 r28` | SD_CS `c18 r22` |
| 3 | yellow | GPIO 10 `c1 r28` | Display CS `c18 r1` |
| 4 | turquoise | GPIO 9 `c1 r27` | Display A0 `c16 r1` |
| 5 | white | GPIO 8 `c1 r26` | Display RESET `c17 r1` |
| 6 | white | GPIO 4 `c7 r27` | Display LED `c13 r1` |

### Step 3: DAC and encoder

| # | Colour | From | To |
|---|---|---|---|
| 11 | blue | GPIO 5 `c7 r26` | DAC BCK `c8 r5` |
| 12 | yellow | GPIO 6 `c7 r25` | DAC WSEL `c8 r7` |
| 13 | turquoise | GPIO 7 `c1 r25` | DAC DIN `c8 r6` |
| 14 | turquoise | GPIO 1 `c7 r30` | Encoder CLK `c8 r25` |
| 15 | yellow | GPIO 2 `c7 r29` | Encoder DT `c9 r25` |

## Connections on the front

These are soldered from above, after the back is done and tested.

| Wire | Colour | From | To |
|---|---|---|---|
| 16 | white | ESP32 pad 14 | Encoder SW, top of the pin at `c10 r25` |
| B1 | red | Charger OUT+ pad | Power switch, middle pin |
| | red | Battery + | Charger B+ pad |
| | black | Battery − | Charger B− pad |

The switch's third pin stays empty. Keep the power switch off while a USB cable is plugged into the ESP32.

**Battery**: fit it last. It must not be wedged against header pins or the pad wires: put a strip of thin card or tape along the DAC and ESP32 edges and tape the cell down. Nothing sharp should press on it.

## Check before powering up

With a multimeter on continuity:

1. 3V3 (`c7 r31`) and GND (`c7 r32`) are **not** connected to each other.
2. 3V3 reaches DAC VIN, display VCC and encoder +.
3. GND reaches DAC GND, display GND, encoder GND and charger OUT−.
4. Pad 14 connects to GND only while the knob is pressed.

Then plug USB into the ESP32 with the power switch off, and flash.
