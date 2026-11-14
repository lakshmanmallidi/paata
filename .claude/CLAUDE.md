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
| 1.8" ST7735 TFT 128×160 V1.1 (red board) | Display header: LED SCK SDA A0 RESET CS GND VCC. **Full-size SD** slot on back (not microSD; the card sticks out about 20 mm on one side) with pads SD_CS SD_MOSI SD_MISO SD_SCK (must be soldered). |
| M274 / KY-040 rotary encoder | Pins: GND + SW DT CLK. 2 counts per detent. |
| TP4056 USB-C charger w/ protection | B+/B− to battery, OUT+/OUT− to switch → S3-Zero 5V/GND. |
| 3.7 V 950 mAh LiPo, 102535 = 10.4 × 25 × 35 mm (measured) | Has its own protection PCB. Red = +, black = −. Thick; a 503450 (5 mm) cell is the slim swap. |
| 6×6 mm tactile buttons | BACK, OK (to GND, internal pull-ups). |

## Measured sizes (owner's calipers, 2026-11-14)
| Part | Size (mm) |
|---|---|
| Display board | 34 × 58.2; SD adapter sticks out 19 on the right seen from the front (53.0 across board + card). Header removed. |
| ESP32-S3-Zero | 17.9 × 23.8 incl. USB-C. Inner pads 14/15/16 sit beside pads 7/8/9. |
| DAC | 20.2 × 30.9 incl. jack |
| Encoder board | 21.7 × 26.0; 10 k pull-ups R1/R2 on the back. Owner will remove the header but **not** desolder the encoder from the board. |
| TP4056 charger | 17.3 × 26.7 |
| Battery | 10.9 thick; length and width not yet measured |

The card in use is a microSD in a full-size SD adapter.

## Pin map (firmware must match this)
```
I2S:      BCK=5  WSEL/LRC=6  DIN=7
SPI:      SCK=12 MOSI=11 MISO=13
TFT:      CS=10 DC(A0)=9 RST=8 BL(LED)=4
SD:       CS=3  (shares SPI bus with TFT)
Encoder:  CLK=1 DT=2 SW=14
Buttons:  BACK=15 OK=16
```

## Firmware
- Arduino framework via **PlatformIO** (not Arduino IDE), project in `firmware/`
  (`platformio.ini`, `src/main.cpp`). Board `esp32-s3-devkitc-1`, QSPI PSRAM, 4 MB
  flash, USB CDC on boot. Platform is **pioarduino** (Arduino core 3.x), which
  ESP32-audioI2S 4.x requires.
- Libraries: ESP32-audioI2S (schreibfaul1), Adafruit ST7735/ST7789, Adafruit GFX,
  ESP32Encoder (madhephaestus).
- v1 (`firmware/src/main.cpp`): FLAC/MP3/WAV/AAC/OGG from
  `/Music` on SD; folder browser; encoder = scroll (browser) / volume (playing);
  OK = select / play-pause (encoder click does the same); BACK = up a folder / back
  to browser; hold OK = next track, hold BACK = previous; auto-advance; progress bar.
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
- Later: 3D-printed case, optional ES9038Q2M+TPA6138 I2S
  board upgrade with IP5306 power module instead of TP4056

## Build: one perf board (decided 2026-11-14)
- Everything goes on the owner's 29 × 35 hole perf board (about 74 × 89 mm), parts on
  pin headers, wires on the copper side in the owner's six colours (red, black, yellow,
  blue, white, turquoise). Guide, hole positions and wire list: `hardware/PERFBOARD.md`
  (drawing from `.claude/tools/perfboard_layout.py`).
- Layout: DAC top-left (jack at top edge), ESP32 beside it (USB-C at top edge, pins in
  c10/c16 rows 1–9), display top-right (header row 2, SD card sticking out of the right
  side, deliberately outside the case), battery flat on the board below DAC/ESP32,
  TP4056 bottom-left (USB-C at bottom edge), BACK/OK bottom-middle, encoder bottom-right
  lying flat on a straight header, knob through the front face.
- Encoder board has been trimmed narrower by the owner (new width not measured).
- `hardware/DIRECT_WIRING.md` (header-less, pad to pad) and `hardware/BREADBOARD.md`
  are earlier alternatives, kept for other builders.

## Case (not designed yet)
- Follows the perf board: about 78 × 93 mm, roughly 18–19 mm thick (battery beside the
  parts, not under the board). Front face: screen, knob, two buttons. Earlier studies in
  `hardware/case/` (knob-placement options, top-controls draft) are superseded.
- Battery length and width still unmeasured; 35 × 25 mm assumed from the 102535 code.

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
└── .claude/      everything for Claude Code: this file, skills, and
                  docs/DESIGN_NOTES.md (full design history and the reasoning
                  behind every choice — read it when a decision here needs context)
```
Topics: esp32-s3 flac music-player dap audio i2s pcm5102 platformio arduino diy
open-hardware portable-audio

## Working style
- Flash and read the serial monitor yourself; iterate. Ask the owner only for what
  the screen shows or what they hear.
- Commit small, descriptive commits as features land.
- Owner is on macOS, uses VS Code with the Claude Code and PlatformIO extensions.
