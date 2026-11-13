# Direct wiring (no headers)

A way to build and test Paata without soldering headers that have to come off again for the case. The ESP32 and DAC get wires soldered straight to their pads; the display and encoder keep the pins they came with and take push-on jumper sockets; only the two buttons and the power rails sit on a small breadboard.

The connections are the same as in [WIRING.md](WIRING.md). If you would rather use headers and a full breadboard, see [BREADBOARD.md](BREADBOARD.md).

![Direct wiring card](images/direct-wiring.svg)

## Wires

Standard 20 cm jumper wires work for everything. Where a wire is soldered, cut the connector off that end and strip about 3 mm.

### Solder at the ESP32, socket at the other end (9)

| ESP32 pad | Other end | Signal |
|---|---|---|
| 4 | Display LED pin | Backlight |
| 12 | Display SCK pin | SPI clock |
| 11 | Display SDA pin | SPI data out |
| 9 | Display A0 pin | Data / command |
| 8 | Display RESET pin | Reset |
| 10 | Display CS pin | Display select |
| 1 | Encoder CLK pin | Encoder A |
| 2 | Encoder DT pin | Encoder B |
| 14 (inner pad) | Encoder SW pin | Encoder click |

### Solder at both ends (5)

| From | To | Signal |
|---|---|---|
| ESP32 5 | DAC BCK | I2S bit clock |
| ESP32 6 | DAC WSEL | I2S word select |
| ESP32 7 | DAC DIN | I2S data |
| ESP32 3 | Display SD_CS pad | SD card select |
| ESP32 13 | Display SD_MISO pad | SD data in |

### Short links on the display board (2)

The SD slot shares the display's clock and data lines, so join them on the display itself instead of running two more wires to the ESP32:

| From | To |
|---|---|
| SD_SCK pad | solder joint of the SCK header pin |
| SD_MOSI pad | solder joint of the SDA header pin |

### To the breadboard (12)

| From | To | Wire |
|---|---|---|
| ESP32 3V3 | + rail | soldered at the ESP32, pin into the rail |
| ESP32 GND | − rail | soldered at the ESP32, pin into the rail |
| DAC VIN | + rail | soldered at the DAC, pin into the rail |
| DAC GND | − rail | soldered at the DAC, pin into the rail |
| Display VCC pin | + rail | socket-to-pin jumper |
| Display GND pin | − rail | socket-to-pin jumper |
| Encoder + pin | + rail | socket-to-pin jumper |
| Encoder GND pin | − rail | socket-to-pin jumper |
| ESP32 15 (inner pad) | one side of the BACK button | soldered at the ESP32, pin into the breadboard |
| ESP32 16 (inner pad) | one side of the OK button | soldered at the ESP32, pin into the breadboard |
| other side of BACK | − rail | pin-to-pin jumper |
| other side of OK | − rail | pin-to-pin jumper |

Place each button across the breadboard's centre gap and connect to diagonally opposite legs, so it works whichever way the legs are paired inside.

## Working tips

- Tape each board to a piece of card or wood before soldering to it, and keep them taped down while testing. Loose boards touching each other is the usual way to short something.
- Solder the ESP32's wires first, then check each one with a multimeter before connecting the other end.
- A soldered stranded wire breaks where the solder ends if it is flexed. Tape the wires down a centimetre or two from each joint.
- Power from USB only. Leave the battery, charger and 5V pad unconnected for now.

## Check before plugging in USB

With a multimeter on continuity:

1. The + rail and − rail are **not** connected to each other.
2. The + rail reaches DAC VIN, display VCC and encoder +.
3. No two neighbouring ESP32 pads are bridged by solder.

## If something does not work

- **"SD card not found"**: lower the SD speed in `firmware/src/main.cpp` from `20000000` to `4000000`. If it still fails, check the three small resistors next to the SD slot (R1–R3); on some of these boards they are too large for a 3.3 V bus and need bridging.
- **Picture upside down**: change `tft.setRotation(0)` to `tft.setRotation(2)`.
- **Knob scrolls the wrong way**: swap the sockets on the encoder's DT and CLK pins.

## Moving to the case later

The ESP32 and DAC wiring is already final apart from length: shorten each wire once the case layout is known. The display's header and the encoder's breakout board still come off at that point, but those are 8 and 5 joints, not 26.
