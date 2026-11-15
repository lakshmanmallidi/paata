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
| DAC | 20.2 × 30.9 board only, without the jack (owner's correction, 2026-11-15); published 20.3 × 32.5 with the jack |
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
  wiring diagram. `PERFBOARD.md` (layout notes and wire list) was removed 2026-11-15: the
  owner sees the perf board as personal learning, not something to teach repo readers, so
  do not write perf board guides into the repo. The two perf board drawings stay in
  `hardware/wiring/`; the wire routes and hole positions live in the generator. All three drawings come from
  `.claude/tools/perfboard_layout.py`, which writes into `hardware/wiring/`.
- `hardware/components/` holds one photo per part with its published (standard) size drawn on it
  and the owner's caliper reading in the caption (owner's request, 2026-11-15). Published:
  ESP32 18 × 23.5, DAC 20.3 × 32.5, display 34.5 × 58, charger 17 × 28, battery
  10 × 25 × 35; the encoder has no consistent published size. They are made by `.claude/tools/component_dims.py`
  (`uv run --with pillow`), which reads the untouched photos from git commit 558b775.
  Update the sizes there when a part is re-measured.
  `slide-switch.jpg` is the exception: drawn by a one-off script from an owner photo that
  is not in git (measured only, no published size looked up).
- Headers are soldered (2026-11-14); hole positions in the generator were read from the owner's photo of the back, so treat them as fixed:
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

## Case (not designed yet; next job is a 3D-printed enclosure with the slide switch)
Board is built and wired (2026-11-15). Owner's caliper readings of the finished board, mm
(photos in `hardware/assembly/`):
| What | mm |
|---|---|
| Length incl. USB-C sockets, excl. the jack, which sticks out about 1 more (owner, 2026-11-15) | 89.9 |
| Overall width, perf board + display overhang | 59.1 |
| Back wires to top of encoder body, excl. threaded bush and shaft | 15.4 |
| Greatest thickness: back wires to battery top | 15.7 |
| Perf board back to screen face | 8.4 |
| Perf board back to top of display PCB | 5.7 |
| Lower edge of screen to USB-C end (my reading of the photo; confirm) | 36.2 |
| Slide switch body (3 pins), without pins, slider and ears: length × depth × pin face to slider face (owner confirmed) | 10.5 × 5.7 × 5.0 |
- Perf board alone: 22 × 34 holes, about 56 × 87. Battery is the tallest part apart from
  the encoder shaft. Front face: screen and knob; slide switch in a side wall; jack on
  the top edge; two USB-C openings on the bottom edge; SD card out of the right side.
- The switch keeps its two mounting ears: it is screwed to the case wall from inside
  (owner, 2026-11-15). Owner's figures: 20 mm across the ears, holes 2 mm diameter, hole
  edge 1 mm from the ear's end. From those I derive 16 mm between hole centres.
- Not measured yet (ask before modelling): encoder shaft height above the perf board and
  shaft diameter, slider size and travel, jack centre and USB-C centre positions, perf
  board thickness, screen window position from the top and side edges.
- The assembly photos were cropped and captioned by a one-off script (not kept in the repo).
- **Concept v1 (2026-11-15, awaiting the owner's verdict):** `hardware/case/paata_case.py`
  (build123d model + pyvista renders; run with
  `uv run --python 3.12 --with build123d --with pyvista hardware/case/paata_case.py`)
  writes `concept-*.png` and git-ignored STLs. Base tray + flat lid held by four M3
  screws in outside corner lugs (owner asked for M3). Owner's idea (2026-11-15): each lug
  has a side slot holding a captive M3 hex nut, the screw comes down from the lid into
  it. Lugs are 10 mm across for that; slot 5.7 × 2.7, 4 mm below the lid; M3 × 10 screws; screen seen through a tapered well
  in the lid; knob through the lid; jack hole in the top wall, two USB-C openings in the
  bottom wall, SD slot in the right wall; switch in a pod on the right wall beside the
  charger. Owner's rules for the pod (2026-11-15): its sizes are the inside of the pocket
  (10 out, 20 long, 6 high) and walls are added on top; the pod is level with the lid and
  the lid forms its top, so the switch drops in from above. Outside: 12.5 out, 24.4 long,
  8.2 tall plus the lid, 45° underside so it prints without support. Slider out sideways,
  ears screwed to the pod's outer wall. About
  83 × 108 × 20.5 mm over lugs and pod. Port, window and knob positions are estimates
  from photos; no board supports yet. Not printable until those are measured.

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
├── hardware/     components/, wiring/, assembly/  CERN-OHL-P-2.0
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
