# Paata (పాట) — project context for Claude Code

Paata is a pocket-sized open-source hi-res FLAC player built on the ESP32-S3.
Owner: Lakshman. This file carries the decisions made during the design phase so
every Claude Code session starts with full context. Keep it updated as things change.

## Goal
A tiny, offline, button-driven music player (no touchscreen) that plays the
owner's Telugu FLAC library, synced from a TrueNAS server. Comparison target is the
Snowsky Echo Mini (₹5,399): we aim to match its sound on IEMs and beat it on
features (playlists, Wi-Fi sync, no 8,192-track cap). Owner listens on IEMs only.

## Hardware (all parts in hand)
| Part | Notes |
|---|---|
| Waveshare ESP32-S3-Zero | ESP32-S3FH4R2, 4 MB flash, 2 MB QSPI PSRAM, USB-C. GPIO 21 = RGB LED (avoid). Header pins 1–16, TX(43), RX(44). |
| Adafruit PCM5102A I2S DAC | Pins: VIN GND WSEL DIN BCK Lout G Rout. Config pads DE/FIL/MCK/MU/FM/3V left open. Line-level out, fine for IEMs. |
| 1.8" ST7735 TFT 128×160 V1.1 (red board) | Display header: LED SCK SDA A0 RESET CS GND VCC. microSD slot on back with pads SD_CS SD_MOSI SD_MISO SD_SCK (must be soldered). |
| M274 / KY-040 rotary encoder | Pins: GND + SW DT CLK. 2 counts per detent. |
| TP4056 USB-C charger w/ protection | B+/B− to battery, OUT+/OUT− to switch → S3-Zero 5V/GND. |
| 3.7 V 950 mAh LiPo | Has its own protection PCB. Red = +, black = −. |
| 6×6 mm tactile buttons | PREV, NEXT (to GND, internal pull-ups). |

## Pin map (firmware must match this)
```
I2S:      BCK=5  WSEL/LRC=6  DIN=7
SPI:      SCK=12 MOSI=11 MISO=13
TFT:      CS=10 DC(A0)=9 RST=8 BL(LED)=4
SD:       CS=3  (shares SPI bus with TFT)
Encoder:  CLK=1 DT=2 SW=14
Buttons:  PREV=15 NEXT=16
```

## Firmware
- Arduino framework via **PlatformIO** (not Arduino IDE), project in `firmware/`
  (`platformio.ini`, `src/main.cpp`). Board `esp32-s3-devkitc-1`, QSPI PSRAM, 4 MB
  flash, USB CDC on boot. Platform is **pioarduino** (Arduino core 3.x), which
  ESP32-audioI2S 4.x requires.
- Libraries: ESP32-audioI2S (schreibfaul1), Adafruit ST7735/ST7789, Adafruit GFX,
  ESP32Encoder (madhephaestus).
- v1 (`firmware/src/main.cpp`): FLAC/MP3/WAV/AAC/OGG from
  `/Music` on SD; folder browser; encoder = scroll/volume, click = select/pause,
  long-press = up/back; PREV/NEXT buttons; auto-advance; progress bar.
- Build/flash/monitor from `firmware/`: `pio run -t upload && pio device monitor`. First flash:
  hold B, tap R, release B. Board appears as `/dev/cu.usbmodem*` on macOS.
- Known first-run tweaks: `INITR_BLACKTAB` vs `GREENTAB`/`REDTAB` for screen
  colours; swap ENC_CLK/ENC_DT if scroll direction is reversed.
- **Not** MicroPython (no FLAC decoder, timing issues). **Not** USB-host to a USB
  DAC dongle (ESP32-S3 is USB Full-Speed, UAC1 only, capped at 16-bit/48 kHz).

## Roadmap
- v1: play from SD, browse, basic UI  ← current
- v2: cover.jpg display (TJpg_Decoder), .m3u playlist support, backlight dimming,
  battery voltage on screen
- v3: Wi-Fi sync of `EchoMini/` folder from TrueNAS SMB share; optional DLNA/
  Navidrome client
- Later: 3D-printed case (~62×40×16 mm target), optional ES9038Q2M+TPA6138 I2S
  board upgrade with IP5306 power module instead of TP4056

## Library / NAS conventions
- Master library on TrueNAS share `storage/Music`, layout
  `Artist/Album (yyyy)/NN - Artist - Title.flac`. Separate `storage/Music/EchoMini/`
  holds the subset synced to the player.
- FLAC only for lossless. ALAC and WAV are converted with ffmpeg
  (`-c:a flac -map_metadata 0`), source deleted only on success. AAC/MP3 kept as is.
- Cover art: `cover.jpg` in each album folder, ~600 px, JPEG. `Back.jpg`, `CD.jpg`
  may also exist and are ignored by the player. `.cue .log .m3u .nfo .txt` deleted.
- Tags cleaned with MusicBrainz Picard (Scan + Discogs plugin); Mp3tag for stragglers.
  Keep tags in Latin script (player font has no Telugu glyphs).
- SD card: FAT32, `/Music/<Album>/` folders.
- Planned `tools/`: `nas-inbox.py` (extract/convert/tidy a drop folder) and
  `sync-to-player.py` (starred-in-Navidrome → EchoMini → SD/Wi-Fi). Python.
- Do not build anything that bulk-downloads from Telegram sharing channels.

## Repo layout & licensing
Note: repo was initialised with an MIT LICENSE at the root. Licence split below is the recommendation; revisit before shipping compiled binaries.

```
paata/
├── firmware/     PlatformIO project        GPL-3.0 (ESP32-audioI2S is GPL-3)
├── hardware/     WIRING.md, BOM.md, case   CERN-OHL-P-2.0
├── tools/        NAS-side Python scripts   MIT
├── README.md
├── LICENSE       GPL-3.0
├── CLAUDE.md     this file
└── docs/DESIGN_NOTES.md   full design history and the reasoning behind every choice — read it when a decision in this file needs context
```
Topics: esp32-s3 flac music-player dap audio i2s pcm5102 platformio arduino diy
open-hardware portable-audio

## Working style
- Flash and read the serial monitor yourself; iterate. Ask the owner only for what
  the screen shows or what they hear.
- Commit small, descriptive commits as features land.
- Owner is on macOS, uses VS Code with the Claude Code and PlatformIO extensions.
