# Paata — design notes

Everything decided, measured and rejected during the design phase (Oct 27 – Nov 13, 2026),
organised by topic. `CLAUDE.md` is the short version; this is the reasoning behind it.

---

## 1. Where it started

The original question was "I have a TrueNAS box with my hi-res songs; is there a TrueNAS
app that syncs a library to a memory card for a Snowsky Echo Mini?"

Answer: no NAS app can write to a card sitting in a player. The workable pattern is a
**carry folder** on the NAS (`storage/Music/EchoMini/`) mirrored to the card from a PC
with FreeFileSync (Windows) or rsync (Mac/Linux). TrueNAS apps that help *around* this:
Navidrome (stream + browse the library at home), beets/Picard (tags), Syncthing (only if a
phone with a card slot does the copying).

### Snowsky Echo Mini facts (the benchmark)
- ₹5,399 at Headphone Zone (512 MB and 8 GB versions; card matters more than internal).
- Dual CS43131 DACs, 3.5 mm + 4.4 mm balanced, 24/192 PCM, DSD64/128/256, BT 5.3 (SBC only).
- microSD up to 256 GB, exFAT/FAT32 only (no NTFS).
- **Limits that matter:** 8,192-track cap, no playlist files at all (.m3u ignored),
  file browser sorts by copy order, library rescan needed after copying.
- 80 × 54.5 × 14.5 mm, ~15 h battery.

### Capacity maths (256 GB card, ~4 min songs)
| Format | per song | songs |
|---|---|---|
| CD FLAC 16/44.1 | ~30 MB | ~8,000 (hits the track cap) |
| 24/96 FLAC | ~90 MB | ~2,700 |
| 24/192 FLAC | ~180 MB | ~1,400 |
| DSD64 / 128 / 256 | 170 / 340 / 680 MB | 1,500 / 750 / 370 |
| MP3 320 | ~10 MB | 8,192 (cap) |

Owner's playlist is ~200 songs → 6 GB (CD FLAC) to 36 GB (24/192). A 64 GB card is plenty.

---

## 2. The owner's library (what we actually looked at)

| File | Finding |
|---|---|
| `Oy! (2009)` FLAC, 35 MB / 4:42 | ~1,000 kbps, 16/44.1, Spek shows content to 22 kHz → genuine CD rip. |
| `Andala Rakshasi (2012)` MP3 | 320 VBR, lossy. Every tag field polluted with `[www.Tollymp3z.com]`. |
| `ANIMAL (Telugu) Deluxe` .m4a, 65 MB / 4:35 | ~1,900 kbps at 48 kHz → ALAC 24/48, true hi-res, clean T-Series tags, embedded art. |
| `1-nenokkadine (2013)` | FLAC + `cover.jpg`, `Back.jpg`, `CD.jpg`. |

So the library is mostly CD-quality FLAC with some 24/48 ALAC and some MP3. This drove the
"CD and 24/96 must be perfect; 24/192 is a bonus; DSD not needed" requirement.

### Verifying files
- Spek spectrogram: content to ~20–22 kHz = real lossless; hard cut at 16 kHz = MP3 upsampled.
- `ffprobe -show_entries stream=codec_name,sample_rate,bits_per_raw_sample`.
- WAV vs FLAC sanity check: `ffmpeg -i x -f md5 -` on both; identical hash = bit-identical.

### Conventions decided
- **FLAC is the only lossless format kept.** ALAC → FLAC and WAV → FLAC via ffmpeg
  (`-c:a flac -map_metadata 0`, add `-map 0 -c:v copy -disposition:v attached_pic` to be
  sure embedded art carries over). Delete source only on ffmpeg success (`&& rm`). AAC
  `.m4a` and MP3 stay as they are (converting lossy to FLAC gains nothing).
- Check codec first: `ffprobe -select_streams a:0 -show_entries stream=codec_name` → only
  convert when it says `alac`.
- **Cover art:** `cover.jpg` in the album folder (also accepted: `folder.jpg`). Keep it
  ~500–600 px JPEG; the ESP32 must decode it in 2 MB PSRAM. `Back.jpg` / `CD.jpg` may sit
  alongside and are ignored. PNG → JPEG for the player (lighter decoder, smaller file).
- **Junk to delete:** `.cue` (only useful for single-file rips), `.log` (rip log, proof of
  quality, useless after), `.m3u` (album order, redundant), `.nfo .txt .url Thumbs.db .DS_Store`.
- **Naming:** `Artist/Album (yyyy)/NN - Artist - Title.flac`. Owner prefers no trailing
  spaces and `(yyyy)` suffix. Do it with MusicBrainz Picard file-naming:
  `%albumartist%/%album% (%date:0:4%)/%tracknumber% - %artist% - %title%`.
- **Tagging:** Picard with *Scan* (AcoustID fingerprint beats spam tags) + Discogs plugin.
  Telugu coverage is ~60–80 %; unmatched albums still get renamed from existing tags.
  Keep tags in Latin script (player font has no Telugu glyphs). Mp3tag for stragglers.
- **ALAC is not supported** by ESP32-audioI2S; convert, don't try to play it.

### NAS automation (planned, `tools/`)
Watch folder `Inbox/` on TrueNAS → script extracts zip/rar/7z, converts ALAC/WAV→FLAC,
flattens `Covers/`/`Scans/` up one level, renames `*front*`→`cover.jpg`, `*cd*`→`CD.jpg`,
`*back*`→`Back.jpg`, deletes junk, moves album to `Music/Review/`. Owner stars tracks in
Navidrome; a second script copies starred tracks + cover into `EchoMini/` and moves the
album into the main library. **Explicitly out of scope: anything that bulk-downloads from
Telegram sharing channels.**

---

## 3. Player alternatives considered

| Option | Why not |
|---|---|
| HiBy R1 / R2 II (₹9–9.5k) | Rich HiByOS, Wi-Fi, MSEB EQ, LDAC. Owner: "feels like going back to a smartphone", touchscreen. |
| Hidizs AP30 Music Boy (₹11–12k) | CS43198, 4.4 mm, D-pad, mini-games. Offline-only, SBC BT, no playlists. Expensive. |
| Tangara (open hardware, $249) | WM8523 + INA1620, SD to 2 TB, Lua UI. Proof a DIY player works, but $249 and firmware ships at 16-bit/48 kHz only. |
| Rockbox | Mature hi-res firmware but runs on old iPods/Sansas, not ESP32. |
| Raspberry Pi Zero + DAC HAT + Volumio/moOde | Good audio, but Linux boot times, power draw, size. |

Decision: build our own on ESP32-S3; keep Echo Mini as the quality/size benchmark.

---

## 4. Hardware decisions and the dead ends

### Microcontroller
- **Seeed Xiao ESP32-C3 (owned) — rejected.** 11 GPIOs (need ~15), single core, 400 KB RAM,
  no PSRAM; FLAC decoding runs out of memory.
- **Heltec WiFi LoRa 32 V3 (owned) — usable for prototyping.** ESP32-S3, built-in OLED and
  LiPo charger, 20+ GPIOs, but no PSRAM (24-bit FLAC risky) and LoRa radio is dead weight.
- **Seeed Xiao ESP32-S3** — fine (8 MB PSRAM), ~₹750–900. Xiao pin notes: SCK=D8/GPIO7,
  MISO=D9/GPIO8, MOSI=D10/GPIO9; GPIO19/20 are the USB pins, not on the header.
- **Waveshare ESP32-S3-Zero — chosen.** ESP32-S3FH4R2, 4 MB flash, 2 MB QSPI PSRAM, USB-C
  onboard, 24 header GPIOs, 25 × 18 mm, ~₹549. GPIO 21 = WS2812 LED. Watch out for the
  near-identical "ESP32-S3-Tiny" (FPC connector only, needs adapter). An N8R8 variant
  (8 MB/8 MB) exists if found. No battery charger on board → TP4056. A Home Assistant forum
  user confirms a 2 MB-PSRAM super-mini S3 decodes FLAC fine.
  Board pin labels (from photo): left 5V GND 3V3 B 1 2 3 4 5 6; right TX RX 13 12 11 10 9 8 7;
  inner 16 15 14.

### DAC — the big dead end
An early plan (from another assistant) proposed driving the owner's **Headphone Zone ×
ddHiFi USB-C dongle (CX31993 + MAX97220)** from the ESP32 as a USB host. Rejected because:
- ESP32-S3 USB is Full-Speed (12 Mbps), UAC 1.0 only; Espressif's `usb_host_uac` /
  `usb_stream` driver is capped at **16-bit/48 kHz**. Many hi-res dongles are UAC 2.0 only.
- It needs ESP-IDF, not Arduino; "EspUsbHost" is a HID library, not audio.
- The suggested wiring (GPIO 19/20 on a Xiao header, wrong SPI pins) didn't match the board.
- "Raw audio pins → USB dongle" is a category error: a USB DAC speaks only USB; the ESP32's
  audio pins are I2S and need a bare DAC chip.

**I2S DAC chosen: Adafruit PCM5102A (₹779).** 32-bit/384 kHz capable, 112 dB SNR,
line-level 2.1 V out, no SCK needed (internal PLL), config pads pre-set (no H1L–H4L jumper
fiddling like the generic purple GY boards, ₹150–300). Weakness: line-out, not a headphone
amp. **Owner uses IEMs only, so this is fine.** On CD and 24/96 FLAC into IEMs the audible
difference vs the Echo Mini is small to none; the Echo Mini's balanced output matters for
power-hungry headphones, not IEMs.

### Upgrade path if wanted later
1. Keep PCM5102A, add TPA6132A2/TPA6130A2 headphone amp board (₹200–350).
2. **ES9038Q2M I2S board with TPA6138 amp** (AliExpress ~$20–25, 35 × 60 mm, 5 V). Must be
   hardware-mode (no I2C config). Needs 5 V on battery → swap TP4056 for an **IP5306**
   power-bank module (charges + boosts to 5 V). This is the "beats the Echo Mini" tier.
3. Pi DAC HATs (e.g. InnoMaker ES9038Q2M, ₹3–4k) work over I2S if they use the generic
   hifiberry-dac overlay (no I2C setup); bigger boards.
4. Skip: UDA1334A (sideways, not up), desktop DACs (USB/optical input, no I2S).

Advice given: build with the PCM5102A, listen for a week, only then decide.

### Display + storage
- **1.8" ST7735 128×160 V1.1 red board (₹309)** with full-size SD slot on the back. Replaces the
  earlier 1.44" screen + separate SD module. Display header: LED SCK SDA A0 RESET CS GND VCC
  (U1 regulator → 3.3 or 5 V OK). SD pads SD_CS SD_MOSI SD_MISO SD_SCK must be soldered;
  they are NOT internally joined to the display's SDA/SCK, join them at the ESP32.
  The slot is full-size SD (confirmed 2026-11-14 with a Samsung microSD→SD adapter in it);
  the card protrudes ~20 mm from the board edge, which the case must allow for.
- SD over SPI reads ~10–20 Mbit/s; 16/44.1 FLAC needs ~1 Mbit/s, 24/96 ~3 Mbit/s. Not the
  bottleneck; FLAC decode CPU is. Shared SPI with the display is fine because audio is
  buffered in PSRAM. SDIO (4-bit) is not possible on this board; irrelevant for now.
- SD module alternatives looked at: Robu "Mini Micro SD Card Reader" (₹23, 3.3 V, often out
  of stock), Robu "Micro SD SPI/SDIO breakout 3 V" (₹99), Probots TF mini (₹25), generic
  ₹39 5 V module (bulky, level shifter holds MISO — keep on its own SPI bus, 5 V only).
- Card: FAT32 (use SD Formatter or a Mac for >32 GB), `/Music/<Album>/`.

### Controls
- **M274 (KY-040) rotary encoder**: GND + SW DT CLK. Volume, scroll, click = select/pause.
  Chosen over a potentiometer (analog scratchiness, no menu use). **Owner keeps it on its
  26 × 19 mm breakout** (decided 2026-11-14); R1–R3 on the back are 10 kΩ pull-ups, not
  diodes, so a bare encoder would work on the ESP32's internal pull-ups, but it's not worth
  the desoldering. Headers may be removed and wires soldered to the encoder pins.
- Two 6 × 6 mm tactile buttons: PREV, NEXT.

### Power
- **TP4056 USB-C 1 A with protection (₹19)**: B+/B− battery, OUT+/OUT− → slide switch →
  S3-Zero 5V. Charge via the TP4056's port; flash via the S3-Zero's port. 1 A is a bit high
  for a 950 mAh cell; R3 1.2 kΩ → 2 kΩ drops it to ~0.5 A (optional).
- **3.7 V 950 mAh LiPo, size code 102535 → 10.4 × 25 × 35 mm (caliper-measured
  2026-11-14)**, with its own protection PCB. Thicker than the 6 mm first assumed; the slim
  alternative is a 503450 cell (5 × 34 × 50 mm, 1000 mAh, ~₹250). ESP32+DAC+TFT draw
  ~80–100 mA → ~10 h. Li-ion 18650 (2,500–3,500 mAh, 25–35 h) or 14500 (~800 mAh) are electrically
  identical options but change the case size; LiPo pouch keeps it thin.
- S3-Zero's LDO accepts 3.6–5 V on the 5V pin, so no boost converter is needed. Never use a
  LiFePO4 cell with a TP4056.

### Size — measured 2026-11-14 (ruler / caliper)
| Part | L × W × H mm |
|---|---|
| 1.8" TFT board | 57 × 34 × 4 (≈8 at the SD slot; card adds ~20 mm beyond the edge) |
| ESP32-S3 Zero | 25 × 18 × 4 |
| Adafruit PCM5102A | 27 × 19 × 3 (+6 for the jack) |
| Encoder breakout | 26 × 19, shaft 20 |
| TP4056 | 27 × 17 × 3 |
| Battery 102535 | 35 × 25 × 10.4 |

Credit card = 85.6 × 54 × 0.8 mm. Echo Mini = 80 × 54.5 × 14.5.
The earlier "62 × 40 × 16" target assumed a 6 mm cell and ignored the display board; it
does not hold. With the parts in hand, stacking TFT / (S3 + DAC side by side, 52 × 19) /
battery gives roughly 70 × 40 × 22 mm; putting the battery beside the display instead gives
roughly 85–95 × 40 × 14 mm. A 503450 cell brings the stacked version to about 16 mm thick.

### Case (later)
**Superseded 2026-11-14:** the case now follows the single perf board build
(`hardware/PERFBOARD.md`): about 62 × 93 mm, all parts including the battery on the front of the board, buttons on a small board under the lid, slide switch in a side wall, knob and buttons on the front face,
SD card sticking out of the right side. An earlier choice of a top-edge knob
(40 × 70 × 16 mm) was dropped once the full-size SD slot and the encoder board were
measured. The layout sketched below predates all of this.

3D-print. The 1.8" ST7735 is common enough that Printables/MakerWorld ESP32-MP3-player
cases can be remixed. Layout: screen + knob + 2 buttons on the front; two USB-C openings
(charge / flash) and the 3.5 mm jack on the side; S3-Zero, DAC and LiPo stacked behind
the screen. Card can live inside permanently since sync will be over Wi-Fi.

---

## 5. Firmware decisions
- **C++/Arduino, not MicroPython**: no FLAC decoder exists for MicroPython on ESP32, and the
  interpreter/GC causes dropouts once a screen and UI are added.
- **PlatformIO, not Arduino IDE**: command-line build/flash/monitor so Claude Code can
  iterate (`pio run -t upload && pio device monitor`). First flash: hold B, tap R.
- Arduino IDE equivalents if ever needed: ESP32S3 Dev Module, PSRAM "QSPI PSRAM", Flash 4 MB,
  USB CDC On Boot enabled.
- Libraries: ESP32-audioI2S (decoding + I2S; GPL-3), Adafruit ST7735/GFX, ESP32Encoder.
- Open-source projects reviewed: **ESP32MediaBox** (mikedeblin; same TFT + PCM5102A, album
  art, VU meters, DLNA — needs 8 MB PSRAM, extra hardware to strip), ESP32_radio_player_v2
  (sarunia; FLAC + PCM5102A + encoders, OLED), squeezelite-esp32 (network streamer, ST7735
  support), esphome-libs/micro-flac (lean FLAC decoder, ESP-IDF). Decision: write a lean
  firmware on ESP32-audioI2S; borrow ideas from ESP32MediaBox.
- v1 behaviour: see CLAUDE.md. Known tweak points: ST7735 tab variant, encoder direction,
  `d/2` detent divisor.

## 6. Project / repo
- Name **Paata** (Telugu "song"). Alternatives: Raagam (crowded with raga projects),
  Sruthi (common personal name), Pocketflac, Chinni, Zeroplay. Web search found no audio
  project named paata; owner to confirm on GitHub.
- Licence: repo was initialised MIT. Note ESP32-audioI2S is GPL-3; for source-only
  distribution MIT on our code is fine, but if we ever ship compiled `.bin` files the
  firmware should be GPL-3. Suggested: firmware GPL-3, tools MIT, hardware CERN-OHL-P-2.0.
- Workflow: VS Code + Claude Code extension + PlatformIO extension; board on
  `/dev/cu.usbmodem*`.
