# Paata (పాట)

A pocket-sized, open-source FLAC player built on the ESP32-S3. *Paata* is Telugu for "song".

It plays music from an SD card through an I2S DAC, with a small colour screen, a rotary knob and two buttons. No touchscreen, no phone app, no account.

> **Status: early.** The v1 firmware compiles, but has not yet been tested on assembled hardware. Expect changes to the wiring and the code.

## Features (v1)

- Plays FLAC, MP3, WAV, AAC and Ogg files from the `/Music` folder of an SD card
- Folder browser on a 1.8" 128×160 screen
- Rotary encoder for scrolling and volume
- BACK and OK buttons, automatic advance to the next track in the folder
- Title, artist, track number, elapsed time and progress bar
- Runs from a single LiPo cell, charged over USB-C

Planned next: album art, `.m3u` playlists, backlight dimming, battery level, and Wi-Fi sync from a NAS. See the [roadmap](#roadmap).

## Hardware

| Part | Used for |
|---|---|
| Waveshare ESP32-S3-Zero (4 MB flash, 2 MB PSRAM) | Microcontroller |
| Adafruit PCM5102A I2S DAC breakout | Audio out (line level, 3.5 mm jack) |
| 1.8" ST7735 TFT, 128×160, with SD card slot on the back | Screen and storage |
| KY-040 / M274 rotary encoder | Scroll, volume, select |
| 2 × 6×6 mm tactile buttons | Back, OK |
| TP4056 USB-C charger module with protection | Charging |
| 3.7 V LiPo cell (950 mAh used here) with protection PCB | Power |
| Slide switch | On / off |

The PCM5102A has a line-level output. It drives in-ear monitors well; high-impedance headphones would need a separate headphone amplifier.

Full pin-by-pin wiring is in [hardware/WIRING.md](hardware/WIRING.md). For a first build there are two guides: [hardware/DIRECT_WIRING.md](hardware/DIRECT_WIRING.md) (no headers, wires soldered pad to pad) and [hardware/BREADBOARD.md](hardware/BREADBOARD.md) (everything on a breadboard). In short:

```
I2S DAC:   BCK=5   WSEL=6  DIN=7
SPI bus:   SCK=12  MOSI=11 MISO=13
Screen:    CS=10   DC=9    RST=8   Backlight=4
SD card:   CS=3    (shares the SPI bus with the screen)
Encoder:   CLK=1   DT=2    SW=14
Buttons:   BACK=15 OK=16
```

The SD pads on the back of the screen board are not connected to the display header; they need their own four wires.

## Build and flash

The firmware is a [PlatformIO](https://platformio.org/) project in [firmware/](firmware/).

1. Install PlatformIO Core, using Python 3.10 to 3.14:
   ```sh
   pip install platformio
   ```
   The PlatformIO IDE extension for VS Code also works.
2. Build:
   ```sh
   cd firmware
   pio run
   ```
   The first build downloads the ESP32 toolchain and libraries, so it takes a few minutes.
3. Connect the ESP32-S3-Zero over USB-C. For the first flash, put it in download mode: hold **B**, tap **R**, release **B**.
4. Flash and open the serial monitor:
   ```sh
   pio run -t upload && pio device monitor
   ```

If the screen colours look wrong, change `INITR_BLACKTAB` in [firmware/src/main.cpp](firmware/src/main.cpp) to `INITR_GREENTAB` or `INITR_REDTAB`. If the knob scrolls the wrong way, swap `ENC_CLK` and `ENC_DT`.

## Preparing the SD card

- Format the card as FAT32.
- Put music in a `/Music` folder, one folder per album: `/Music/<Album>/01 - Artist - Title.flac`.
- Files and folders starting with `.` or `_` are hidden from the browser.
- The built-in font covers Latin characters only, so tags and file names in other scripts will not display correctly.

## Controls

| | Browsing | Playing |
|---|---|---|
| Turn knob | Scroll | Volume |
| Click knob | Same as OK | Same as OK |
| OK | Open folder / play file | Pause / resume |
| BACK | Up one folder | Back to browser (music keeps playing) |
| Hold OK | Next track | Next track |
| Hold BACK | Previous track (restarts the current one after 3 s) | same |

## Roadmap

- **v1**: play from SD, browse folders, basic screen (current)
- **v2**: album art from `cover.jpg`, `.m3u` playlists, backlight dimming, battery level
- **v3**: Wi-Fi sync of a music folder from a NAS
- **Later**: 3D-printed case (about 62 × 40 × 16 mm), optional higher-end DAC board

## Repository layout

```
firmware/   PlatformIO project (src/main.cpp, platformio.ini)
hardware/   Wiring guide
.claude/    Project notes used by the Claude Code assistant; not needed to build
```

## Licence

The code in this repository is released under the [MIT licence](LICENSE).

The firmware links against [ESP32-audioI2S](https://github.com/schreibfaul1/ESP32-audioI2S), which is GPL-3.0, so compiled firmware binaries are subject to the GPL-3.0.

## Credits

Built on [ESP32-audioI2S](https://github.com/schreibfaul1/ESP32-audioI2S), [Adafruit GFX](https://github.com/adafruit/Adafruit-GFX-Library) and [Adafruit ST7735](https://github.com/adafruit/Adafruit-ST7735-Library), [ESP32Encoder](https://github.com/madhephaestus/ESP32Encoder), and the [pioarduino](https://github.com/pioarduino/platform-espressif32) platform.
