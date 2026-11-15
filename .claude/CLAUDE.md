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
| M274 / KY-040 rotary encoder | Pins: GND + SW DT CLK. 2 counts per detent. Its switch is the only button. |
| TP4056 USB-C charger w/ protection | B+/B− to battery, OUT+/OUT− to switch → S3-Zero 5V/GND. |
| 3.7 V 950 mAh LiPo, 102535 = 10.4 × 25 × 35 mm (measured) | Has its own protection PCB. Red = +, black = −. Thick; a 503450 (5 mm) cell is the slim swap. |

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
No push buttons; inner pads 15/16 unused (owner's decision, 2026-11-15). SW stays on
inner pad 14: the owner turned down moving it to the RX header pin.
```

## Firmware
- Arduino framework via **PlatformIO** (not Arduino IDE), project in `firmware/`
  (`platformio.ini`, `src/main.cpp`). Board `esp32-s3-devkitc-1`, QSPI PSRAM, 4 MB
  flash, USB CDC on boot. Platform is **pioarduino** (Arduino core 3.x), which
  ESP32-audioI2S 4.x requires.
- Libraries: ESP32-audioI2S (schreibfaul1), Adafruit ST7735/ST7789, Adafruit GFX,
  ESP32Encoder (madhephaestus).
- v1 (`firmware/src/main.cpp`): FLAC/MP3/WAV/AAC/OGG from
  `/Music` on SD; folder browser; encoder only: turn = scroll (browser) /
  volume (playing); click = select / play-pause; hold (600 ms) = up a folder / back to
  browser; hold and turn = next / previous track; auto-advance; progress bar.
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
- Everything except the power switch goes on the owner's perf board (cut to 22 × 34 holes, about 56 × 87 mm), parts on pin headers, wires on the solder side in the owner's six
  colours (red, black, yellow, blue, white, turquoise). `hardware/wiring/WIRING.md` has the one
  wiring diagram; `hardware/wiring/PERFBOARD.md` has the layout, the back-side connections
  drawing and the wire list. All three drawings come from
  `.claude/tools/perfboard_layout.py`, which writes into `hardware/wiring/`.
- `hardware/components/` holds one photo per part with its published (standard) size drawn on it
  and the owner's caliper reading in the caption (owner's request, 2026-11-15). Published:
  ESP32 18 × 23.5, DAC 20.3 × 32.5, display 34.5 × 58, charger 17 × 28, battery
  10 × 25 × 35; the encoder has no consistent published size. They are made by `.claude/tools/component_dims.py`
  (`uv run --with pillow`), which reads the untouched photos from git commit 558b775.
  Update the sizes there when a part is re-measured.
- Headers are soldered (2026-11-14); hole positions in `hardware/wiring/PERFBOARD.md` and the
  generator were read from the owner's photo of the back, so treat them as fixed:
  display header r1 c13–20, SD pads r22 c15–18, DAC c8 r2–9 (and c2 r3–8, unwired),
  ESP32 c1/c7 r25–33 (USB-C at bottom edge), encoder header r25 c8–12, charger pads r25
  c16/17/20/21 (OUT+ B+ B− OUT−, read from photos, owner to confirm). Battery lies flat
  on the front between DAC and ESP32. Unidentified joints at c15 r25, c17 r21, c18 r21.
- Back: wires only. SCK/MOSI run ESP32 → SD pads → display. Front (soldered from
  above): pad 14 → encoder SW, charger OUT+ → slide switch in a case wall →
  ESP32 5V, battery leads → B+/B−.
- The owner wants wires drawn as actual runs on the back view (a pin-tag-only drawing
  "made no sense"); the connections drawing is three back views, one wire group each.
- Breadboard, direct-wiring and case-study drawings were removed at the owner's request
  (2026-11-14); do not re-add alternative layouts.

## Case (not designed yet)
- Follows the perf board: about 60 × 91 mm. The battery (10.9 mm) is the tallest part
  on the front, so the lid sits about 12 mm above the board. Front face: screen and
  knob; slide switch in a side wall.

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
├── hardware/     components/, wiring/      CERN-OHL-P-2.0
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
