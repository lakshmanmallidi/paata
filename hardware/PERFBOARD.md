# Perf board build

Everything on one 29 × 35 hole perf board (about 74 × 89 mm). The connections are the same as in [WIRING.md](WIRING.md); this page says which hole each part goes in and lists the wires.

![Perf board layout](images/perfboard-layout.svg)

Holes are written as column and row: `c10 r3` is column 10, row 3, counted from the top-left corner of the component side. Parts sit on the plain side and are soldered on the copper side. The right-hand drawing shows the copper side, where left and right are swapped.

## Where each part goes

| Part | Holes | Notes |
|---|---|---|
| ESP32-S3-Zero | pins in c10 and c16, rows 1–9 | USB-C at the top edge. Row 1 is 5V (c10) and TX (c16). |
| DAC | 8-pin side in c8, rows 4–11 | Jack at the top edge. Row 4 = Rout, row 11 = VIN. |
| Display | 8-pin header in row 2, c20–c27; SD pads in row 23, c22–c25 | Screen up. c20 = LED, c27 = VCC. Its right edge hangs about 2 mm past the board, and the SD card sticks out beyond that. |
| Battery | c2–c15, rows 14–23 | Lying flat, on double-sided foam tape. |
| Charger (TP4056) | c1–c7, rows 25–35 | USB-C at the bottom edge, battery pads towards the battery. Foam tape; its pads do not sit on the hole grid. |
| Power switch | c9–c11, row 26 | |
| BACK button | c11–c13, rows 29–32 | |
| OK button | c16–c18, rows 29–32 | |
| Encoder | 5-pin header in row 35, c24–c28 | Knob up. c24 = GND, c28 = CLK. |

Why this arrangement:

- **Ports**: headphone jack and the ESP32's USB-C (flashing) on the top edge, charging port on the bottom edge, SD card out of the right side. Nothing blocks a port.
- **Short wires**: the ESP32 sits between the DAC and the display with the right pins facing each one. The three audio wires are one or two holes long, and the display wires are 3–4 cm.
- **Thin**: the battery lies beside the parts instead of under the board, so the build is about 13 mm thick without a case.

## Before soldering

- Fit pin headers to the ESP32 (2 × 9), the DAC (8-pin side), the display (8-pin and 4-pin) and the encoder (5-pin, straight). Test-fit every part in its holes before soldering anything.
- **Display**: check that the 8-pin header and the SD pads both drop into holes at the same time. If the SD pads are off the grid, leave them without pins and use four short wires. The display rests on its SD socket, so the pins only need to reach through the board.
- **Encoder**: only one end has pins. Put a piece of foam tape under the other end.
- **ESP32 pads 14, 15, 16**: these are flat pads on top of the board. Solder a wire to each and pass it down through c14, c15 and c16 in row 11.
- If the DAC's jack does not clear the top edge, move the DAC up one row.

## Wires

All wires run on the copper side, pad to pad.

### Power

| Wire | Colour | From | To |
|---|---|---|---|
| R1 | red | ESP32 3V3 `c10 r3` | DAC VIN `c8 r11` |
| R2 | red | ESP32 3V3 `c10 r3` | Display VCC `c27 r2` |
| R3 | red | Display VCC `c27 r2` | Encoder + `c25 r35` |
| K1 | black | ESP32 GND `c10 r2` | DAC GND `c8 r10` |
| K2 | black | ESP32 GND `c10 r2` | Display GND `c26 r2` |
| K3 | black | Display GND `c26 r2` | Encoder GND `c24 r35` |
| K4 | black | Encoder GND `c24 r35` | OK button `c18 r32` |
| K5 | black | OK button `c18 r32` | BACK button `c13 r32` |
| K6 | black | Charger OUT− | ESP32 GND `c10 r2` |
| B1 | red | Charger OUT+ | Switch `c10 r26` |
| B2 | red | Switch `c9 r26` | ESP32 5V `c10 r1` |

Three wires meet at ESP32 GND. Bridge `c10 r2` to the empty hole `c9 r2` with solder to get a second landing point; do the same at `c9 r3` for 3V3.

The battery's red wire goes to charger **B+** and its black wire to **B−**.

Keep the power switch off while a USB cable is plugged into the ESP32.

### Signals

| # | Colour | From | To |
|---|---|---|---|
| 1 | yellow | GPIO 12 `c16 r4` | Display SCK `c21 r2` |
| 2 | blue | GPIO 11 `c16 r5` | Display SDA `c22 r2` |
| 3 | yellow | GPIO 10 `c16 r6` | Display CS `c25 r2` |
| 4 | turquoise | GPIO 9 `c16 r7` | Display A0 `c23 r2` |
| 5 | white | GPIO 8 `c16 r8` | Display RESET `c24 r2` |
| 6 | white | GPIO 4 `c10 r7` | Display LED `c20 r2` |
| 7 | turquoise | GPIO 3 `c10 r6` | SD_CS `c25 r23` |
| 8 | white | GPIO 13 `c16 r3` | SD_MISO `c23 r23` |
| 9 | yellow | Display SCK `c21 r2` | SD_SCK `c22 r23` |
| 10 | blue | Display SDA `c22 r2` | SD_MOSI `c24 r23` |
| 11 | blue | GPIO 5 `c10 r8` | DAC BCK `c8 r7` |
| 12 | yellow | GPIO 6 `c10 r9` | DAC WSEL `c8 r9` |
| 13 | turquoise | GPIO 7 `c16 r9` | DAC DIN `c8 r8` |
| 14 | turquoise | GPIO 1 `c10 r4` | Encoder CLK `c28 r35` |
| 15 | yellow | GPIO 2 `c10 r5` | Encoder DT `c27 r35` |
| 16 | white | Pad 14 `c14 r11` | Encoder SW `c26 r35` |
| 17 | blue | Pad 15 `c15 r11` | BACK button `c11 r29` |
| 18 | yellow | Pad 16 `c16 r11` | OK button `c16 r29` |

Each button uses two diagonally opposite legs, so its orientation does not matter.

## Check before powering up

With a multimeter on continuity:

1. 3V3 (`c10 r3`) and GND (`c10 r2`) are **not** connected to each other.
2. 3V3 reaches DAC VIN, display VCC and encoder +.
3. GND reaches DAC GND, display GND, encoder GND and one leg of each button.

Then plug USB into the ESP32 with the power switch off, and flash.
