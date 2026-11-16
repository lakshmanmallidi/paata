# Paata (పాట) — project context for Claude Code

Paata is a pocket-sized open-source hi-res FLAC player built on the ESP32-S3.
This file carries the decisions made so far, so that anyone developing the project
further (with or without Claude Code) starts with full context. Keep it updated as
things change. "The owner" below means the project's maintainer. Do not put personal
details, network addresses or private paths in this folder.

## Goal
A tiny, offline, button-driven music player (no touchscreen) that plays a FLAC
library from an SD card. Comparison target is the
Snowsky Echo Mini (₹5,399): we aim to match its sound on IEMs and beat it on
features (playlists, Wi-Fi sync, no 8,192-track cap). The output is meant for IEMs.

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
  volume (playing); click = select / play-pause; hold 600 ms and release = up a folder /
  back to browser (decided on release, so a slow hold-and-turn is not taken as back;
  owner's request 2026-11-16); hold and turn was next / previous track until the control change below; auto-advance.
  After the last track the next album folder starts, and back from the first track plays
  the last track of the album before, going round at the ends of the library (owner's
  request 2026-11-16; flashed, not yet confirmed on hardware). The owner tried double
  click for next track and preferred hold and turn, so there is no double click.
- Serial output is off unless built with `-DPAATA_LOG` (folder, cover, track start with
  free memory, audio library messages). One play that hung on 2026-11-16 was never
  explained: its log was lost and it did not recur. Free heap at a track start was 257 KB.
- Build/flash/monitor from `firmware/`: `pio run -t upload && pio device monitor`. First flash:
  hold B, tap R, release B. Board appears as `/dev/cu.usbmodem*` on macOS.
- First run on hardware 2026-11-15: flashed, boots, screen, SD,
  browser and playback work (owner played two 16-bit FLAC albums). Read serial without
  resetting via pyserial (`uv run --with pyserial`).
- **Embedded cover art broke playback:** ESP32-audioI2S 4.0.1 reads through FLAC PICTURE
  blocks and gives up after 8 s ("audioHeader reading timeout"); an album with a 9.7 MB
  picture in every track never played. `firmware/patch_audio_lib.py` (a `pre:` script)
  patches the library to seek past pictures over 32 KB in local files. Confirmed
  on hardware 2026-11-16: that album starts and 24-bit/48 kHz plays in real time.
  Stripping big pictures before copying albums to the card is still worth doing.
- **Crackling on loud passages into IEMs (2026-11-16):** not a firmware fault. Serial
  diagnostics over 135 s of a 24/48 track showed no I2S underruns, a full input buffer and
  no decode errors, and the same track is clean into headphones with a high-impedance aux
  input. The PCM5102A line output (meant for loads of 1 kΩ or more) distorts on peaks into
  16–32 Ω IEMs at higher volume steps. Fix is a headphone amp board after the DAC
  (TPA6132A2 / MAX97220), or a volume cap in firmware as a stopgap.
- **Now-playing screen (2026-11-16, owner approved on hardware):** black, orange and grey
  theme (owner's choice). Status and track count, 84 × 84 cover, title, artist and album,
  thin progress bar, times and a small volume bar. The cover is `cover.jpg` (or
  `folder.jpg`) decoded with TJpg_Decoder once per folder, before the track starts, into
  an 84 × 84 buffer (centre square, shrunk); a 600 px cover of about 100 KB takes 0.4 s.
  Missing, progressive or over 3 MB covers show a grey tile. Text that does not fit
  scrolls continuously (owner's request): title and artist line in the player, the
  selected row and the folder name in the browser; the owner found a 9 pt bold title too
  big, so all text is the built-in 6 × 8 font. Volume and pause redraw only their own part.
- **Folder listing (2026-11-16):** reading `/Music` with 142 album folders took 5.6 s with
  `openNextFile()`, which made going back out of an album slow. `getNextFileName(&isDir)`
  reads the same folder in 79 ms. Parent folder lists are also kept in memory, so going
  back needs no card read and returns to the row it was left on.
- **Controls changed 2026-11-16 (owner's idea, flashed, awaiting his confirmation):**
  double click = next track, triple click = previous track (player screen only, so a
  single click there waits 350 ms), hold and turn = move within the track, 5 s per notch
  (`audio.setTimeOffset`, applied once the knob rests; not while paused; position is
  approximate on FLAC). Opening the track that is already playing only shows the player.
- **Logo and boot screen (2026-11-16, owner approved):** a four-petal muggu in orange with
  grey dots and the word "paata" in English; the owner did not want Telugu lettering in
  the logo. `.claude/tools/logo.py` writes `assets/logo.svg`, `assets/logo-mark.svg` and
  `firmware/src/boot_logo.h` (128 × 160 RGB565, shown 1.5 s at boot).
- If every track in a folder fails within 10 s, the player returns to the browser
  instead of looping (added 2026-11-15, not yet seen working on hardware).
- Known first-run tweaks: `INITR_BLACKTAB` vs `GREENTAB`/`REDTAB` for screen
  colours; swap ENC_CLK/ENC_DT if scroll direction is reversed.
- **Not** MicroPython (no FLAC decoder, timing issues). **Not** USB-host to a USB
  DAC dongle (ESP32-S3 is USB Full-Speed, UAC1 only, capped at 16-bit/48 kHz).

## Roadmap (owner's order, 2026-11-16; README's Roadmap says the same)
- v1: play from SD, browse, album art (cover.jpg done 2026-11-16), screen, knob  ← current
- v2: headphone amplifier after the DAC (TPA6138 or similar, low-impedance IEMs), battery
  percentage on screen, and a **Settings menu** (owner's idea, 2026-11-16, for later):
  a long press on the main menu (the top folder, where a hold has nothing to go up to
  today) opens Settings; first entry: **Shuffle on/off**, kept across reboots (NVS). Deeper
  in the browser a hold stays "up one folder". Not designed further yet.
- v3: copy songs onto the card over Wi-Fi. Bluetooth audio was on the list and the owner
  removed it 2026-11-17: the ESP32-S3 has Bluetooth LE only, no Bluetooth Classic, so no
  A2DP for headphones and speakers without an added transmitter module or a second chip.
- In progress: 3D-printed case with the knob
- Later: .m3u playlist support, backlight dimming, optional ES9038Q2M+TPA6138 I2S
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
  Pod made shallower after the second print (owner: too much gap behind the switch
  terminals): pocket 6 out instead of 10, so the pod stands 8.5 out and the case is about
  79 wide. The terminals sit in the wall opening and the gap beside the charger.
  Lid after the second print (owner): encoder hole 2 mm towards the USB-C end; the
  screen shroud wall touched the battery, so it is 1.0 thick on all sides (was 1.2) and the window is
  0.5 further from the battery. The owner describes directions with the USB-C end on top,
  so his left is +X and his top is −Y in the model.
  Third base print (2026-11-16): the owner confirms it works with the USB-C openings at
  x 11.3 / 48.1, the jack hole 13.5 from the inside of the left wall, and the 6 mm pod
  pocket. Treat those positions as verified. The matching lid was printed the same day.
  Lid plate is 1.5 mm thick (was 2.0; owner, 2026-11-16) so that a clear filament shows
  the charger and ESP32 lights; case is 20.0 tall. `hardware/case/transparency_coupons.py`
  makes 2.0 / 1.5 / 1.0 mm test plates for judging a clear filament.
  Knob (2026-11-16): `knob.stl`, 10 mm radius (owner's figure), 16 tall, push fit on the
  D-shaft, printed top face down, 1 mm above the lid. Owner's readings: shaft tip 15 above
  the 1.5 mm lid, of which 2 is threaded bush and 13 is shaft; 4.5 across the flat; 6.9
  (taken as the bush thread; shaft assumed 6.0). The flat is only on the upper half of the
  shaft (about 7, read from a photo), so the bore is round below and D-shaped for the top
  6.5. Not yet tried on the encoder.
  Support-free printing (2026-11-15): base prints floor down, lid prints outside face down
  (`lid.stl` is exported in that orientation). Pod underside is a real 45° slope (it was
  missing from the model before), slider slot is open to the top, jack hole has a 45°
  roof, lid screw recesses are 90° countersinks, so the lid screws are flat-head M3 × 10.
  What is left are bridges: nut slots 5.7 mm, USB-C openings 7.5 mm, SD slot 26 mm.
  First test print (2026-11-16, owner's findings): the jack hole was missing (the 45° roof
  cut was extruded the wrong way and never reached the wall); the USB-C sockets sat against
  the charger-side edge of their openings. Now: jack hole 6 mm, centre 12.5 from the inside
  of the left wall and 4.5 below the top of the base wall (owner's measurements); both
  USB-C openings: the first print (centres x 9.3, 46.1) had the sockets against the
  charger-side edge, the second (+5.0, owner's figure) against the opposite edge. Now +2.0
  (x 11.3, 48.1; the owner asked for 3 back from the second print) and 13.5 wide. Jack hole
  moved 1 towards the screen side after the second print: centre now 13.5 from the inside
  of the left wall.

## Library conventions the firmware assumes
- Track files are named `NN - Artist - Title.flac`, one folder per album.
- FLAC only for lossless. ALAC and WAV are converted with ffmpeg
  (`-c:a flac -map_metadata 0`), source deleted only on success. AAC/MP3 kept as is.
- Cover art: `cover.jpg` in each album folder, baseline (not progressive) JPEG, longer
  side 600 px. `CD.jpg` (disc picture, same format) may also exist; the player ignores it
  for now, the owner may want it on screen later. `.cue .log .m3u .nfo .txt` deleted.
- Keep tags and file names in Latin script (the player font has no other glyphs).
- SD card: FAT32, `/Music/<Album>/` folders.

## Repo layout & licensing
Note: repo was initialised with an MIT LICENSE at the root. Licence split below is the recommendation; revisit before shipping compiled binaries.

```
paata/
├── firmware/     PlatformIO project        GPL-3.0 (ESP32-audioI2S is GPL-3)
├── hardware/     components/, wiring/, assembly/  CERN-OHL-P-2.0
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
- Developed on macOS in VS Code with the Claude Code and PlatformIO extensions.
