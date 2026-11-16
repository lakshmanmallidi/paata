<p align="center"><img src="assets/logo.svg" width="480" alt="Paata"></p>

# Paata (పాట)

A pocket-sized, open-source FLAC player built on the ESP32-S3. *Paata* is Telugu for "song". The logo is a *muggu*, the dot-and-line pattern drawn at the doorstep of Telugu homes.

It plays music from an SD card through an I2S DAC, with a small colour screen and a single rotary knob. No touchscreen, no phone app, no account.

> **Status: early.** The board is built and the v1 firmware runs on it: browsing and FLAC playback from the SD card work. The 3D-printed case, lid and knob are printed and fit the board. The line output is clean into headphones but distorts into low-impedance IEMs until the planned amplifier is added. Expect changes to the code.

## Features (v1)

- Plays FLAC, MP3, WAV, AAC and Ogg files from the `/Music` folder of an SD card
- Folder browser on a 1.8" 128×160 screen
- One rotary encoder does everything: turn, click, hold, hold and turn
- Automatic advance to the next track in the folder
- Title, artist, track number, elapsed time and progress bar
- Runs from a single LiPo cell, charged over USB-C

Planned next: a headphone amplifier and a battery percentage on the screen, then copying songs onto the card over Wi-Fi. See the [roadmap](#roadmap).

## Hardware

| Part | Used for |
|---|---|
| Waveshare ESP32-S3-Zero (4 MB flash, 2 MB PSRAM) | Microcontroller |
| Adafruit PCM5102A I2S DAC breakout | Audio out (line level, 3.5 mm jack) |
| 1.8" ST7735 TFT, 128×160, with SD card slot on the back | Screen and storage |
| KY-040 / M274 rotary encoder | Scroll, volume, select, back, skip |
| TP4056 USB-C charger module with protection | Charging |
| 3.7 V LiPo cell (950 mAh used here) with protection PCB | Power |
| Slide switch | On / off |

The PCM5102A has a line-level output. It drives in-ear monitors well; high-impedance headphones would need a separate headphone amplifier.

Full pin-by-pin wiring is in [hardware/wiring/WIRING.md](hardware/wiring/WIRING.md). Photos of every part with its size are in [hardware/components](hardware/components/). In short:

```
I2S DAC:   BCK=5   WSEL=6  DIN=7
SPI bus:   SCK=12  MOSI=11 MISO=13
Screen:    CS=10   DC=9    RST=8   Backlight=4
SD card:   CS=3    (shares the SPI bus with the screen)
Encoder:   CLK=1   DT=2    SW=14
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
- Album art is read from `cover.jpg` in the album folder. Keep it a baseline (not progressive) JPEG of about 600 px: larger files slow the start of an album, and progressive ones are not shown. With ffmpeg: `ffmpeg -i in.jpg -vf "scale='min(600,iw)':'min(600,ih)':force_original_aspect_ratio=decrease" -pix_fmt yuvj420p -q:v 3 cover.jpg`.

## Controls

| | Browsing | Playing |
|---|---|---|
| Turn knob | Scroll | Volume |
| Click knob | Open folder / play file | Pause / resume |
| Double click | | Next track |
| Triple click | | Previous track |
| Hold knob 0.6 s, then release | Up one folder | Back to browser (music keeps playing) |
| Hold and turn | Move within the track, 5 s per notch | same |

After the last track of an album the next album starts, and going back from the first track plays the last track of the album before. Names that do not fit on the screen scroll.

## Roadmap

- **v1** (current): play from SD, browse folders, album art from `cover.jpg`, the screen and the knob
- **v2**: headphone amplifier after the DAC for low-impedance IEMs, and the battery percentage on the screen
- **v3**: copy songs onto the card over Wi-Fi
- **Done**: 3D-printed case with a knob ([hardware/case](hardware/case/)), prints without supports
- **Later**: `.m3u` playlists, backlight dimming, optional higher-end DAC board

## Repository layout

```
assets/     logo
firmware/   PlatformIO project (src/main.cpp, platformio.ini)
hardware/   components/ (part photos with sizes), wiring/ (wiring diagram and pin tables),
            assembly/ (finished board and its measurements), case/ (3D-printed case and knob)
.claude/    Project notes used by the Claude Code assistant; not needed to build
```

## Licence

The code in this repository is released under the [MIT licence](LICENSE).

The firmware links against [ESP32-audioI2S](https://github.com/schreibfaul1/ESP32-audioI2S), which is GPL-3.0, so compiled firmware binaries are subject to the GPL-3.0.

## Credits

Built on [ESP32-audioI2S](https://github.com/schreibfaul1/ESP32-audioI2S), [Adafruit GFX](https://github.com/adafruit/Adafruit-GFX-Library) and [Adafruit ST7735](https://github.com/adafruit/Adafruit-ST7735-Library), [ESP32Encoder](https://github.com/madhephaestus/ESP32Encoder), and the [pioarduino](https://github.com/pioarduino/platform-espressif32) platform.
