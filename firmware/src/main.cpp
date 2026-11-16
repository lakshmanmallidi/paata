/*
 * Paata firmware v1 — FLAC / MP3 / WAV / AAC / OGG player
 * Hardware: Waveshare ESP32-S3-Zero, Adafruit PCM5102A (I2S),
 *           1.8" ST7735 128x160 TFT with SD slot, KY-040/M274 encoder (its push switch is the only button).
 * Build:    PlatformIO, see ../platformio.ini  (pio run -t upload && pio device monitor)
 * Serial:   silent unless built with -DPAATA_LOG (folder, cover, track and audio library messages).
 */

#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <Audio.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <TJpg_Decoder.h>
#include <ESP32Encoder.h>
#include <vector>
#include "boot_logo.h"

#ifdef PAATA_LOG
#define LOG(...) Serial.printf(__VA_ARGS__)
#else
#define LOG(...) do {} while (0)
#endif

// ---------- pins ----------
#define I2S_BCLK   5
#define I2S_LRC    6
#define I2S_DOUT   7

#define SPI_SCK   12
#define SPI_MOSI  11
#define SPI_MISO  13

#define TFT_CS    10
#define TFT_DC     9
#define TFT_RST    8
#define TFT_BL     4
#define SD_CS      3

#define ENC_CLK    1
#define ENC_DT     2
#define ENC_SW    14   // inner pad 14

// ---------- objects ----------
Audio audio;
Adafruit_ST7735 tft(TFT_CS, TFT_DC, TFT_RST);
ESP32Encoder enc;

// ---------- state ----------
enum Mode { BROWSE, PLAYING };
Mode mode = BROWSE;

String rootDir = "/Music";       // falls back to "/" if the card has no /Music
String curDir = rootDir;
struct Entry { String name; bool isDir; };
std::vector<Entry> entries;
int sel = 0, top = 0;

std::vector<String> playlist;   // audio files in the folder being played
int trackIdx = -1;
String nowTitle, nowArtist;
int volume = 8;                 // 0..21
bool paused = false;
bool needRedraw = true;         // whole screen
bool needMeta = false, needVol = false, needStatus = false;   // parts of the player screen

const int ROWS = 12;            // 160px / 13px rows, minus header
// black, orange and grey
const uint16_t C_BG = ST77XX_BLACK, C_FG = ST77XX_WHITE, C_HL = 0xF447, C_DIM = 0x8C71, C_TRACK = 0x2965;

// ---------- album cover ----------
// cover.jpg from the album folder, decoded once per folder into an 84 x 84 buffer.
// Keep covers small (about 600 px, baseline JPEG): the decode blocks the player and
// takes longer the bigger the file is. Progressive JPEGs cannot be decoded.
const int COVER = 84, COVER_X = 22, COVER_Y = 17;
const uint32_t COVER_MAX_BYTES = 3000000;
uint16_t coverBuf[COVER * COVER];
bool coverOk = false;
String coverDir = "?";          // folder the buffer was loaded from
int cvW, cvH, cvSide, cvOx, cvOy;   // decoded size, and the centred square taken from it

bool coverBlock(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t* px) {
  for (int j = 0; j < h; j++) for (int i = 0; i < w; i++) {
    int sx = x + i - cvOx, sy = y + j - cvOy;
    if (sx < 0 || sy < 0 || sx >= cvSide || sy >= cvSide) continue;
    int tx, ty;
    if (cvSide >= COVER) { tx = sx * COVER / cvSide; ty = sy * COVER / cvSide; }     // shrink
    else { tx = sx + (COVER - cvSide) / 2; ty = sy + (COVER - cvSide) / 2; }         // small picture: centre it
    coverBuf[ty * COVER + tx] = px[j * w + i];
  }
  return true;
}

void loadCover(const String& dir) {
  coverDir = dir; coverOk = false;
  String path;
  for (const char* n : {"cover.jpg", "folder.jpg"}) {
    String p = dir.endsWith("/") ? dir + n : dir + "/" + n;
    if (SD.exists(p)) { path = p; break; }
  }
  if (!path.length()) return;
  File f = SD.open(path); uint32_t bytes = f.size(); f.close();
  if (bytes > COVER_MAX_BYTES) { LOG("cover: %s is %u bytes, skipped\n", path.c_str(), bytes); return; }
  uint16_t w = 0, h = 0;
  if (TJpgDec.getSdJpgSize(&w, &h, path) != JDR_OK || !w || !h) { LOG("cover: cannot read %s\n", path.c_str()); return; }
  int scale = 1;                                   // largest reduction that still leaves 84 px
  while (scale < 8 && min(w, h) / (scale * 2) >= COVER) scale *= 2;
  cvW = w / scale; cvH = h / scale; cvSide = min(cvW, cvH);
  cvOx = (cvW - cvSide) / 2; cvOy = (cvH - cvSide) / 2;
  memset(coverBuf, 0, sizeof(coverBuf));
  TJpgDec.setJpgScale(scale);
  TJpgDec.setCallback(coverBlock);
  [[maybe_unused]] uint32_t t0 = millis();
  JRESULT r = TJpgDec.drawSdJpg(0, 0, path);
  coverOk = r == JDR_OK;
  LOG("cover: %s %ux%u, %u bytes, 1/%d, %s in %lu ms\n", path.c_str(), w, h, bytes, scale,
                coverOk ? "decoded" : "failed", millis() - t0);
}

// ---------- helpers ----------
bool isAudio(const String& n) {
  String l = n; l.toLowerCase();
  return l.endsWith(".flac") || l.endsWith(".mp3") || l.endsWith(".wav") ||
         l.endsWith(".m4a")  || l.endsWith(".aac") || l.endsWith(".ogg") || l.endsWith(".opus");
}

// Folders above the current one, kept so that going back needs no card read
// and returns to the row it was left on.
struct DirState { String path; std::vector<Entry> entries; int sel, top; };
std::vector<DirState> dirStack;

// Folders and audio files in a folder: folders first, each group by name.
bool listDir(const String& path, std::vector<Entry>& out) {
  out.clear();
  File d = SD.open(path);
  if (!d || !d.isDirectory()) return false;
  bool isDir = false;                              // names only: opening every entry took seconds on a big folder
  for (String n = d.getNextFileName(&isDir); n.length(); n = d.getNextFileName(&isDir)) {
    int s = n.lastIndexOf('/'); if (s >= 0) n = n.substring(s + 1);
    if (n.startsWith(".") || n.startsWith("_")) continue;
    if (isDir || isAudio(n)) out.push_back({n, isDir});
  }
  d.close();
  std::sort(out.begin(), out.end(), [](const Entry& a, const Entry& b) {
    if (a.isDir != b.isDir) return a.isDir;
    return a.name.compareTo(b.name) < 0;
  });
  return true;
}

void loadDir(const String& path) {
  [[maybe_unused]] uint32_t t0 = millis();
  if (!listDir(path, entries)) return;
  sel = top = 0;
  needRedraw = true;
  LOG("dir: %s, %u entries, read in %lu ms\n", path.c_str(), (unsigned)entries.size(), millis() - t0);
}

String joinPath(const String& dir, const String& name) {
  return dir.endsWith("/") ? dir + name : dir + "/" + name;
}

String baseName(const String& p) {
  int s = p.lastIndexOf('/');
  String n = s >= 0 ? p.substring(s + 1) : p;
  int dot = n.lastIndexOf('.'); if (dot > 0) n = n.substring(0, dot);
  return n;
}

// ---------- drawing ----------
// One line of text in a fixed box. If it does not fit it scrolls round and round,
// drawn into an off-screen strip first so that it does not flicker.
const int STRIP_W = 124;
GFXcanvas16* strip;             // STRIP_W x 8, made in setup()
struct Marquee {
  String s; int16_t x = 0, y = 0, w = 0; uint16_t fg = 0, bg = 0;
  int off = 0; uint32_t due = 0; bool scrolls = false, shown = false;
};
Marquee mqHead, mqSel, mqTitle, mqSub;    // browser: folder name, selected row; player: title, artist and album

void mqDraw(Marquee& m) {
  strip->fillScreen(m.bg);
  strip->setTextColor(m.fg);
  strip->setCursor(-m.off, 0);
  strip->print(m.scrolls ? m.s + "    " + m.s : m.s);
  for (int r = 0; r < 8; r++) tft.drawRGBBitmap(m.x, m.y + r, strip->getBuffer() + r * STRIP_W, m.w, 1);
}

void mqSet(Marquee& m, const String& s, int x, int y, int w, uint16_t fg, uint16_t bg) {
  m.s = s; m.x = x; m.y = y; m.w = min(w, STRIP_W); m.fg = fg; m.bg = bg;
  m.off = 0; m.scrolls = (int)s.length() * 6 > m.w; m.shown = true;
  m.due = millis() + 1500;                         // hold still before the first move
  mqDraw(m);
}

void mqTick(Marquee& m) {
  if (!m.shown || !m.scrolls || millis() < m.due) return;
  m.off++;
  if (m.off >= ((int)m.s.length() + 4) * 6) { m.off = 0; m.due = millis() + 1500; }   // back at the start: rest
  else m.due = millis() + 40;
  mqDraw(m);
}

void drawBrowser() {
  tft.fillScreen(C_BG);
  tft.drawFastHLine(0, 13, 128, C_TRACK);
  mqSet(mqHead, curDir == rootDir ? "Music" : baseName(curDir), 2, 3, 124, C_HL, C_BG);
  mqSel.shown = false;
  tft.setTextSize(1);
  for (int i = 0; i < ROWS; i++) {
    int idx = top + i;
    if (idx >= (int)entries.size()) break;
    int y = 16 + i * 12;
    String n = entries[idx].name;
    if (entries[idx].isDir) n = "/" + n;
    if (idx == sel) {                               // only the selected row scrolls
      tft.fillRect(0, y - 2, 128, 11, C_HL);
      mqSet(mqSel, n, 2, y, 124, C_BG, C_HL);
      continue;
    }
    tft.setTextColor(entries[idx].isDir ? C_FG : C_DIM);
    tft.setCursor(2, y);
    tft.print(n.substring(0, 21));
  }
  if (entries.empty()) { tft.setTextColor(C_DIM); tft.setCursor(10, 70); tft.print("(empty)"); }
}

// Player screen: status line, cover, title, artist and album, progress bar, times and volume.
void drawStatus() {
  tft.fillRect(0, 0, 128, 14, C_BG);
  tft.setTextSize(1);
  tft.setTextColor(paused ? C_HL : C_DIM);
  tft.setCursor(6, 5); tft.print(paused ? "PAUSED" : "PLAYING");
  String n = String(trackIdx + 1) + "/" + String(playlist.size());
  tft.setTextColor(C_DIM);
  tft.setCursor(122 - n.length() * 6, 5); tft.print(n);
}

void drawCover() {
  if (coverOk) { tft.drawRGBBitmap(COVER_X, COVER_Y, coverBuf, COVER, COVER); return; }
  tft.fillRoundRect(COVER_X, COVER_Y, COVER, COVER, 4, C_TRACK);        // no cover: a plain tile with a note
  int cx = COVER_X + COVER / 2, cy = COVER_Y + COVER / 2;
  tft.fillCircle(cx - 5, cy + 10, 6, C_DIM);
  tft.fillRect(cx - 1, cy - 16, 3, 27, C_DIM);
  tft.fillRect(cx - 1, cy - 16, 12, 4, C_DIM);
}

void drawMeta() {
  tft.fillRect(0, 103, 128, 34, C_BG);
  mqSet(mqTitle, nowTitle.length() ? nowTitle : baseName(playlist[trackIdx]), 6, 109, 116, C_FG, C_BG);
  mqSet(mqSub, nowArtist.length() ? nowArtist + " - " + baseName(coverDir) : baseName(coverDir), 6, 123, 116, C_DIM, C_BG);
}

void drawVolume() {
  tft.fillRect(46, 149, 36, 9, C_BG);
  tft.fillRect(48, 152, 2, 3, C_DIM);                                   // speaker
  tft.fillTriangle(50, 153, 53, 150, 53, 156, C_DIM);
  tft.fillRect(57, 152, 22, 3, C_TRACK);
  tft.fillRect(57, 152, (22 * volume) / 21, 3, volume >= 19 ? C_HL : C_DIM);
}

// While the knob is held and turned the bar shows where the track will jump to.
const int SEEK_STEP = 5;        // seconds per notch
int32_t seekTo = -1;            // target in seconds, -1 when not seeking
uint32_t seekApplyAt = 0, seekShowUntil = 0;

void drawProgress() {
  uint32_t cur = seekTo >= 0 ? seekTo : audio.getAudioCurrentTime(), dur = audio.getAudioFileDuration();
  tft.fillRect(6, 143, 116, 3, C_TRACK);
  if (dur) tft.fillRect(6, 143, min(116UL, (116UL * cur) / dur), 3, C_HL);
  tft.fillRect(0, 149, 44, 9, C_BG); tft.fillRect(84, 149, 44, 9, C_BG);
  tft.setTextColor(C_DIM);
  char b[12];
  snprintf(b, sizeof b, "%u:%02u", (unsigned)(cur / 60), (unsigned)(cur % 60));
  tft.setCursor(6, 150); tft.print(b);
  snprintf(b, sizeof b, "%u:%02u", (unsigned)(dur / 60), (unsigned)(dur % 60));
  tft.setCursor(122 - strlen(b) * 6, 150); tft.print(b);
}

void drawPlayer() {
  tft.fillScreen(C_BG);
  drawStatus(); drawCover(); drawMeta(); drawVolume(); drawProgress();
}

// ---------- playback ----------
uint32_t trackStartMs = 0;
int failedInARow = 0;           // tracks that ended within seconds of starting

// Replace the playlist with the next (step = 1) or previous (step = -1) album: the
// neighbouring folder beside the one being played, in browser order, going round at the
// ends and passing over folders with no audio in them. False if there is no other album.
bool stepAlbum(int step) {
  String dir = playlist[0].substring(0, playlist[0].lastIndexOf('/'));
  if (dir.length() <= rootDir.length()) return false;              // tracks lying in the root folder
  String parent = dir.substring(0, dir.lastIndexOf('/'));
  if (!parent.length()) parent = "/";
  String name = dir.substring(dir.lastIndexOf('/') + 1);
  std::vector<Entry> sib, files;
  if (!listDir(parent, sib)) return false;
  sib.erase(std::remove_if(sib.begin(), sib.end(), [](const Entry& e) { return !e.isDir; }), sib.end());
  int n = sib.size(), cur = -1;
  for (int i = 0; i < n; i++) if (sib[i].name == name) cur = i;
  if (cur < 0) return false;
  for (int i = 1; i < n; i++) {
    String cand = joinPath(parent, sib[((cur + step * i) % n + n) % n].name);
    listDir(cand, files);
    std::vector<String> list;
    for (auto& e : files) if (!e.isDir) list.push_back(joinPath(cand, e.name));
    if (list.empty()) continue;
    playlist = std::move(list);
    LOG("album: %s\n", cand.c_str());
    return true;
  }
  return false;
}

void playTrack(int idx) {
  if (playlist.empty()) return;
  if (idx < 0) { stepAlbum(-1); idx = playlist.size() - 1; }                    // before the first: last track of the album before
  else if (idx >= (int)playlist.size()) { stepAlbum(1); idx = 0; }             // after the last: first track of the album after
  trackIdx = idx;
  seekTo = -1; seekApplyAt = seekShowUntil = 0;
  nowTitle = ""; nowArtist = "";
  paused = false;
  String dir = playlist[idx].substring(0, playlist[idx].lastIndexOf('/'));
  if (dir != coverDir) loadCover(dir);            // once per folder, before the track starts
  trackStartMs = millis();
  LOG("play: %s (free heap %u, largest block %u, psram %u)\n", playlist[idx].c_str(),
                (unsigned)ESP.getFreeHeap(), (unsigned)ESP.getMaxAllocHeap(), (unsigned)ESP.getFreePsram());
  audio.connecttoFS(SD, playlist[idx].c_str());
  mode = PLAYING; needRedraw = true;
}

void playFolderFrom(const String& file) {
  playlist.clear();
  for (auto& e : entries) if (!e.isDir) playlist.push_back(joinPath(curDir, e.name));
  int i = 0;
  for (; i < (int)playlist.size(); i++) if (playlist[i] == file) break;
  playTrack(i);
}

// library callback: dispatched from audio.loop(), so it runs on the main task
bool trackEnded = false;
void onAudioInfo(Audio::msg_t m) {
  switch (m.e) {
    case Audio::evt_id3data: {
      String s = m.msg;
      if (s.startsWith("Title: "))       { nowTitle  = s.substring(7); needMeta = true; }
      else if (s.startsWith("Artist: ")) { nowArtist = s.substring(8); needMeta = true; }
      break;
    }
    case Audio::evt_eof:  trackEnded = true; break;   // advance from loop(), not from inside the library
    case Audio::evt_info: LOG("audio: %s\n", m.msg); break;
    case Audio::evt_log:  LOG("audio log: %s\n", m.msg); break;
    default: break;
  }
}

// ---------- input ----------
struct Btn { int pin; bool last = true; uint32_t downAt = 0; bool longFired = false; };   // longFired: this press was used for a skip
Btn bSw{ENC_SW};

// returns 0 none, 1 short press, 2 long press (held 0.6 s, reported when released)
int pollBtn(Btn& b) {
  bool v = digitalRead(b.pin);
  int r = 0;
  if (!v && b.last) { b.downAt = millis(); b.longFired = false; }
  if (v && !b.last && !b.longFired) {               // decided on release, so a hold can still become a hold-and-turn
    uint32_t held = millis() - b.downAt;
    if (held > 600) r = 2; else if (held > 30) r = 1;
  }
  b.last = v;
  return r;
}

void goBack() {
  if (mode == PLAYING) { mode = BROWSE; needRedraw = true; }   // music keeps playing
  else if (curDir != rootDir) {
    String up = curDir.substring(0, curDir.lastIndexOf('/'));
    if (up.length() < rootDir.length()) up = rootDir;
    curDir = up;
    if (!dirStack.empty() && dirStack.back().path == up) {          // kept list: no card read
      entries = std::move(dirStack.back().entries);
      sel = dirStack.back().sel; top = dirStack.back().top;
      dirStack.pop_back();
      needRedraw = true;
    } else { dirStack.clear(); loadDir(curDir); }
  }
}

// One control, the encoder:
//   turn           scroll (browser) / volume (playing)
//   click          open folder, play file / play-pause
//   double click   next track          (player screen; a click there waits CLICK_MS for more clicks)
//   triple click   previous track
//   hold, release  back: up a folder, or from the player to the browser
//   hold and turn  move within the track, SEEK_STEP seconds per notch
const uint32_t CLICK_MS = 350;
int clicks = 0; uint32_t lastClickAt = 0;

void applySeek() {
  uint32_t cur = audio.getAudioCurrentTime();
  if (seekTo != (int32_t)cur) audio.setTimeOffset(seekTo - (int32_t)cur);
  seekApplyAt = 0; seekShowUntil = millis() + 800;   // keep showing the target until the library has caught up
}

void handleInput() {
  long d = enc.getCount();
  int steps = d / 2;                         // KY-040 gives 2 counts per detent
  if (steps) enc.setCount(d - steps * 2);    // keep a half-step for the next pass

  int sw = pollBtn(bSw);
  bool held = !bSw.last;

  if (steps && held) {
    bSw.longFired = true;                    // this press is a seek, not a click or a hold
    uint32_t dur = audio.getAudioFileDuration();
    if (trackIdx >= 0 && !paused && dur > 5) {
      if (seekTo < 0) seekTo = audio.getAudioCurrentTime();
      seekTo = constrain(seekTo + steps * SEEK_STEP, 0, (int32_t)dur - 3);
      seekApplyAt = millis() + 300;          // one jump once the knob rests
      seekShowUntil = 0;
      if (mode == PLAYING) drawProgress();
    }
  } else if (steps) {
    if (mode == BROWSE && !entries.empty()) {
      sel = constrain(sel + steps, 0, (int)entries.size() - 1);
      if (sel < top) top = sel;
      if (sel >= top + ROWS) top = sel - ROWS + 1;
      needRedraw = true;
    } else if (mode == PLAYING) {
      volume = constrain(volume + steps, 0, 21);
      audio.setVolume(volume);
      needVol = true;
    }
  }
  if (seekApplyAt && millis() >= seekApplyAt) applySeek();
  if (seekShowUntil && millis() >= seekShowUntil) { seekShowUntil = 0; seekTo = -1; }

  if (sw == 1) {
    if (mode == BROWSE && !entries.empty()) {
      Entry& e = entries[sel];
      if (e.isDir) {
        String next = joinPath(curDir, e.name);
        dirStack.push_back({curDir, std::move(entries), sel, top});
        curDir = next; loadDir(curDir);
      }
      else {
        String file = joinPath(curDir, e.name);
        if (trackIdx >= 0 && trackIdx < (int)playlist.size() && playlist[trackIdx] == file) {
          mode = PLAYING; needRedraw = true;       // already the current track: show the player, leave it playing
        } else playFolderFrom(file);
      }
    } else if (mode == PLAYING) {
      clicks++; lastClickAt = millis();      // counted; acted on when no further click follows
    }
  } else if (sw == 2) {
    clicks = 0;
    goBack();
  }
  if (clicks && millis() - lastClickAt >= CLICK_MS) {
    int n = clicks; clicks = 0;
    if (mode != PLAYING) return;
    if (n == 1) { audio.pauseResume(); paused = !paused; needStatus = true; }
    else if (n == 2) playTrack(trackIdx + 1);
    else playTrack(trackIdx - 1);
  }
}

// ---------- setup / loop ----------
void setup() {
  Serial.begin(115200);
  pinMode(ENC_SW, INPUT_PULLUP);

  pinMode(TFT_BL, OUTPUT); digitalWrite(TFT_BL, HIGH);
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
  tft.initR(INITR_BLACKTAB);
  tft.setRotation(0);
  tft.drawRGBBitmap(0, 0, BOOT_LOGO, 128, 160);   // logo while the card is read
  uint32_t logoAt = millis();
  strip = new GFXcanvas16(STRIP_W, 8);
  strip->setTextWrap(false);

  ESP32Encoder::useInternalWeakPullResistors = puType::up;
  enc.attachHalfQuad(ENC_DT, ENC_CLK);
  enc.clearCount();

  if (!SD.begin(SD_CS, SPI, 20000000)) {
    tft.fillScreen(C_BG); tft.setTextColor(C_FG); tft.setCursor(10, 70); tft.print("SD card not found");
    while (true) delay(1000);
  }
  if (!SD.exists(rootDir)) { rootDir = "/"; curDir = rootDir; }

  Audio::audio_info_callback = onAudioInfo;
  audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  audio.setVolumeSteps(21);
  audio.setVolume(volume);

  loadDir(curDir);
  while (millis() - logoAt < 1500) delay(10);     // leave the logo up long enough to be seen
}

void loop() {
  audio.loop();
  if (trackEnded) {
    trackEnded = false;
    // A track that ends within 10 s of starting did not play (unreadable file, header timeout).
    failedInARow = (millis() - trackStartMs < 10000) ? failedInARow + 1 : 0;
    if (failedInARow >= (int)playlist.size()) {       // the whole folder failed: stop instead of looping forever
      failedInARow = 0; trackIdx = -1; mode = BROWSE; needRedraw = true;
      LOG("no playable track in this folder\n");
    } else playTrack(trackIdx + 1);
  }
  handleInput();

  static uint32_t lastProg = 0;
  if (needRedraw) {
    needRedraw = needMeta = needVol = needStatus = false;
    if (mode == BROWSE) drawBrowser(); else drawPlayer();
  } else if (mode == PLAYING) {
    if (needMeta)   { needMeta = false;   drawMeta(); }
    if (needVol)    { needVol = false;    drawVolume(); }
    if (needStatus) { needStatus = false; drawStatus(); }
    if (millis() - lastProg > 1000) { lastProg = millis(); drawProgress(); }
    mqTick(mqTitle); mqTick(mqSub);
  } else {
    needMeta = needVol = needStatus = false;
    mqTick(mqHead); mqTick(mqSel);
  }
}
