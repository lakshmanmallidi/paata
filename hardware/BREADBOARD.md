# Breadboard build

A layout for testing Paata on one full-size (830-point) breadboard before moving to perf board. The connections are the same as in [WIRING.md](WIRING.md); this page only says where each part sits and which hole each jumper goes in.

![Breadboard layout](images/breadboard-layout.svg)

Holes are written as row + column, so `61j` is row 61, column j. Rows that are joined by the breadboard: columns a–e of one row are one strip, columns f–j of the same row are another.

## Before you start

- **ESP32-S3-Zero**: solder pin headers to both long edges (9 pins each). Pads **14, 15 and 16** sit inside the board and will not reach the breadboard, so solder a loose wire about 15 cm long to each.
- **DAC**: solder a header to the 8-pin side only (VIN … Rout). Leave the six config pads on the other side empty.
- **Display**: solder a 4-pin header to the SD pads (SD_CS, SD_MOSI, SD_MISO, SD_SCK). These take male-to-female jumpers.
- **Jumpers**: 15 male-to-male and 4 male-to-female. Several runs are long, so use 20 cm jumpers.
- Power comes from the USB cable while on the breadboard. Leave the battery, charger and the 5V pin unconnected. The breadboard's power rails are not used.

## Where each part goes

| Part | Holes | Orientation |
|---|---|---|
| ESP32-S3-Zero | rows 55–63, pins in columns c and g | USB port hanging off the right end. Row 63 is 5V (column g) and TX (column c). |
| DAC | column a, rows 29–36 | Board hanging off the near edge, headphone jack pointing left. Row 29 = Rout, row 36 = VIN. |
| Encoder | column d, rows 35–39 | Standing upright, knob pointing toward you, over the DAC. Row 35 = GND, row 39 = CLK. |
| Display | column a, rows 43–50 | Screen up, board hanging off the near edge. Row 43 = LED, row 50 = VCC. |
| PREV button | across the centre gap, rows 28 and 30 | Legs in columns e and f. |
| NEXT button | across the centre gap, rows 49 and 51 | Legs in columns e and f. |

Three connections need no jumper because the parts share a breadboard row:

- **Rows 35 and 36**: the encoder's GND and + sit in the same rows as the DAC's GND and VIN, so one pair of power jumpers feeds both.
- **Row 30**: the PREV button's ground leg shares the row of the DAC's `G` (audio ground) pin.
- **Row 49**: the NEXT button's ground leg shares the row of the display's GND pin.

If the ESP32 board's pin rows do not land in columns c and g on your breadboard, use whichever columns fit; only the row numbers matter.

## Jumpers

### Male-to-male (15)

| # | From | To | Carries |
|---|---|---|---|
| 1 | 36e | 61j | 3.3 V to the DAC and encoder |
| 2 | 35e | 62j | GND to the DAC and encoder |
| 3 | 50d | 61i | 3.3 V to the display |
| 4 | 49d | 62i | GND to the display |
| 5 | 32e | 56h | DAC BCK → GPIO 5 |
| 6 | 34e | 55h | DAC WSEL → GPIO 6 |
| 7 | 33c | 55b | DAC DIN → GPIO 7 |
| 8 | 43e | 57j | Display LED (backlight) → GPIO 4 |
| 9 | 44b | 60b | Display SCK → GPIO 12 |
| 10 | 45c | 59b | Display SDA → GPIO 11 |
| 11 | 46c | 57b | Display A0 → GPIO 9 |
| 12 | 47d | 56b | Display RESET → GPIO 8 |
| 13 | 48c | 58b | Display CS → GPIO 10 |
| 14 | 38e | 59j | Encoder DT → GPIO 2 |
| 15 | 39e | 60j | Encoder CLK → GPIO 1 |

### Male-to-female (4), from the SD pads on the display

| # | From pad | To | Signal |
|---|---|---|---|
| 1 | SD_SCK | 60a | GPIO 12 |
| 2 | SD_MOSI | 59a | GPIO 11 |
| 3 | SD_MISO | 61a | GPIO 13 |
| 4 | SD_CS | 58j | GPIO 3 |

### Wires soldered to the ESP32 pads (3)

| From | To | Signal |
|---|---|---|
| pad 14 | 37e | Encoder SW (click) |
| pad 15 | 28g | PREV button |
| pad 16 | 51g | NEXT button |

## Check before plugging in USB

With a multimeter on continuity:

1. Confirm rows 61 (3V3) and 62 (GND) are **not** connected to each other.
2. Confirm 3V3 (row 61) reaches DAC VIN and encoder + (row 36) and display VCC (row 50).
3. Confirm the DAC's `G` pin (row 30) is connected to GND (row 62). If it is not, the PREV button will not work: run a jumper from 30d to 62h.

## If something does not work

- **"SD card not found"**: the SD jumpers are long. Lower the SD speed in `firmware/src/main.cpp` from `20000000` to `4000000` and try again.
- **Picture upside down**: change `tft.setRotation(0)` to `tft.setRotation(2)`.
- **Knob scrolls the wrong way**: swap the jumpers in 59j and 60j.
- **Encoder body touches the DAC's solder joints**: put a strip of tape over the joints, or use male-to-female jumpers on the encoder pins and leave it off the board.
- **Button does nothing**: turn the button a quarter turn; its legs are joined in pairs.
