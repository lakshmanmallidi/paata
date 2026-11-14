# Perf board build

Everything on one perf board, 22 columns × 35 rows of holes (about 56 × 89 mm). What connects to what is in [WIRING.md](WIRING.md); this page says which hole each part goes in and where each wire is soldered.

Holes are written as column and row: `c8 r33` is column 8, row 33, counted from the top-left corner of the component side. The DAC, ESP32, display, buttons and encoder sit on the component side. The battery and charger sit on the solder side, behind the display.

## Layout

![Perf board layout, component side](images/perfboard-layout.svg)

| Part | Holes | Notes |
|---|---|---|
| DAC | 8-pin side in c8, rows 4–11 | Jack at the top edge. Row 4 = Rout, row 11 = VIN. |
| Display | 8-pin header in row 2, c12–c19; SD pads in row 23, c14–c17 | Screen up. c12 = LED, c19 = VCC. The SD card sticks out of the right side. |
| BACK button | c2–c4, rows 17–20 | |
| OK button | c6–c8, rows 17–20 | |
| ESP32-S3-Zero | pins in c2 and c8, rows 27–35 | USB-C at the bottom edge. Row 27 is GPIO 7 (c2) and GPIO 6 (c8). |
| Power switch | c10–c12, row 29 | |
| Encoder | 5-pin header in row 35, c17–c21 | Knob up. c17 = GND, c21 = CLK. |
| Charger (TP4056) | solder side, behind c12–c22, rows 4–10 | USB-C at the right edge, above the SD card. |
| Battery | solder side, behind c9–c22, rows 12–21 | |

Ports: headphone jack on the top edge, flashing port on the bottom edge, charging port and SD card on the right side.

## Before soldering

- Fit pin headers to the ESP32 (2 × 9), the DAC (8-pin side), the display (8-pin and 4-pin) and the encoder (5-pin, straight). Test-fit every part in its holes before soldering anything.
- **Display**: check that the 8-pin header and the SD pads both drop into holes at the same time. If the SD pads are off the grid, leave them without pins and use four short wires.
- **Encoder**: only one end has pins. Put a piece of foam tape under the other end.
- **ESP32 pads 14, 15, 16**: these are flat pads on top of the board. Solder a wire to each and pass it down through c3, c4 and c5 in row 25.
- **Battery and charger**: fit them last, after all wires are soldered and tested. Trim the solder joints flat, keep wires out from under the battery where possible, and put a piece of thin card between the board and the battery before taping it down. Nothing sharp should press on the cell.
- If the DAC's jack does not clear the top edge, move the DAC up one row.

## Connections

All wires run on the solder side, pad to pad. The drawing shows that side, so left and right are swapped compared with the layout above. Each pin is filled with the colour of its wire and labelled with the wire numbers from the tables below.

![Perf board connections, solder side](images/perfboard-connections.svg)

### Power

| Wire | Colour | From | To |
|---|---|---|---|
| R1 | red | ESP32 3V3 `c8 r33` | DAC VIN `c8 r11` |
| R2 | red | DAC VIN `c8 r11` | Display VCC `c19 r2` |
| R3 | red | ESP32 3V3 `c8 r33` | Encoder + `c18 r35` |
| K1 | black | ESP32 GND `c8 r34` | OK button `c8 r20` |
| K2 | black | OK button `c8 r20` | DAC GND `c8 r10` |
| K3 | black | DAC GND `c8 r10` | Display GND `c18 r2` |
| K4 | black | OK button `c8 r20` | BACK button `c4 r20` |
| K5 | black | ESP32 GND `c8 r34` | Encoder GND `c17 r35` |
| K6 | black | Charger OUT− | ESP32 GND `c8 r34` |
| B1 | red | Charger OUT+ | Switch `c11 r29` |
| B2 | red | Switch `c10 r29` | ESP32 5V `c8 r35` |

Three wires meet at ESP32 GND and at the OK button's ground leg. Bridge each to an empty neighbouring hole with solder (`c9 r34`, `c8 r21`) to get a second landing point.

The battery's red wire goes to charger **B+** and its black wire to **B−**.

Keep the power switch off while a USB cable is plugged into the ESP32.

### Signals

| # | Colour | From | To |
|---|---|---|---|
| 1 | yellow | GPIO 12 `c2 r32` | Display SCK `c13 r2` |
| 2 | blue | GPIO 11 `c2 r31` | Display SDA `c14 r2` |
| 3 | yellow | GPIO 10 `c2 r30` | Display CS `c17 r2` |
| 4 | turquoise | GPIO 9 `c2 r29` | Display A0 `c15 r2` |
| 5 | white | GPIO 8 `c2 r28` | Display RESET `c16 r2` |
| 6 | white | GPIO 4 `c8 r29` | Display LED `c12 r2` |
| 7 | turquoise | GPIO 3 `c8 r30` | SD_CS `c17 r23` |
| 8 | white | GPIO 13 `c2 r33` | SD_MISO `c15 r23` |
| 9 | yellow | GPIO 12 `c2 r32` | SD_SCK `c14 r23` |
| 10 | blue | GPIO 11 `c2 r31` | SD_MOSI `c16 r23` |
| 11 | blue | GPIO 5 `c8 r28` | DAC BCK `c8 r7` |
| 12 | yellow | GPIO 6 `c8 r27` | DAC WSEL `c8 r9` |
| 13 | turquoise | GPIO 7 `c2 r27` | DAC DIN `c8 r8` |
| 14 | turquoise | GPIO 1 `c8 r32` | Encoder CLK `c21 r35` |
| 15 | yellow | GPIO 2 `c8 r31` | Encoder DT `c20 r35` |
| 16 | white | Pad 14 `c3 r25` | Encoder SW `c19 r35` |
| 17 | blue | Pad 15 `c4 r25` | BACK button `c2 r17` |
| 18 | yellow | Pad 16 `c5 r25` | OK button `c6 r17` |

Each button uses two diagonally opposite legs, so its orientation does not matter.

Run the display and DAC wires up the left side of the board (columns 1–8), clear of the area the battery and charger will cover.

## Check before powering up

With a multimeter on continuity:

1. 3V3 (`c8 r33`) and GND (`c8 r34`) are **not** connected to each other.
2. 3V3 reaches DAC VIN, display VCC and encoder +.
3. GND reaches DAC GND, display GND, encoder GND and one leg of each button.

Then plug USB into the ESP32 with the power switch off, and flash.
