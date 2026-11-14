/*
 * Paata firmware v1 — FLAC / MP3 / WAV / AAC / OGG player
 * Hardware: Waveshare ESP32-S3-Zero, Adafruit PCM5102A (I2S),
 *           1.8" ST7735 128x160 TFT with SD slot, KY-040/M274 encoder (its push switch is the only button).
 * Build:    PlatformIO, see ../platformio.ini  (pio run -t upload && pio device monitor)
 */

#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <Audio.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <ESP32Encoder.h>
#include <vector>

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
#define ENC_SW    44   // header pin RX; UART0 is unused because serial goes over USB

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
bool needRedraw = true;

const int ROWS = 12;            // 160px / 13px rows, minus header
const uint16_t C_BG = ST77XX_BLACK, C_FG = ST77XX_WHITE, C_HL = 0x051F, C_DIM = 0x7BEF;

// ---------- helpers ----------
bool isAudio(const String& n) {
  String l = n; l.toLowerCase();
  return l.endsWith(".flac") || l.endsWith(".mp3") || l.endsWith(".wav") ||
         l.endsWith(".m4a")  || l.endsWith(".aac") || l.endsWith(".ogg") || l.endsWith(".opus");
}

void loadDir(const String& path) {
  entries.clear();
  File d = SD.open(path);
  if (!d || !d.isDirectory()) return;
  for (File f = d.openNextFile(); f; f = d.openNextFile()) {
    String n = f.name();
    int s = n.lastIndexOf('/'); if (s >= 0) n = n.substring(s + 1);
    if (n.startsWith(".") || n.startsWith("_")) { f.close(); continue; }
    if (f.isDirectory() || isAudio(n)) entries.push_back({n, (bool)f.isDirectory()});
    f.close();
  }
  d.close();
  std::sort(entries.begin(), entries.end(), [](const Entry& a, const Entry& b) {
    if (a.isDir != b.isDir) return a.isDir;
    return a.name.compareTo(b.name) < 0;
  });
  sel = top = 0;
  needRedraw = true;
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
void drawHeader(const String& t) {
  tft.fillRect(0, 0, 128, 13, C_HL);
  tft.setTextColor(C_FG); tft.setTextSize(1);
  tft.setCursor(2, 3); tft.print(t.substring(0, 20));
}

void drawBrowser() {
  tft.fillScreen(C_BG);
  String h = curDir == rootDir ? "Music" : baseName(curDir);
  drawHeader(h);
  tft.setTextSize(1);
  for (int i = 0; i < ROWS; i++) {
    int idx = top + i;
    if (idx >= (int)entries.size()) break;
    int y = 15 + i * 12;
    bool hl = idx == sel;
    if (hl) tft.fillRect(0, y - 1, 128, 11, C_DIM);
    tft.setTextColor(hl ? C_BG : C_FG);
    tft.setCursor(2, y);
    String n = entries[idx].name;
    if (entries[idx].isDir) n = "/" + n;
    tft.print(n.substring(0, 21));
  }
  if (entries.empty()) { tft.setTextColor(C_DIM); tft.setCursor(10, 70); tft.print("(empty)"); }
}

void drawPlayer() {
  tft.fillScreen(C_BG);
  drawHeader(paused ? "|| paused" : "> playing");
  tft.setTextColor(C_FG); tft.setTextSize(1);
  // title, wrapped to 3 lines
  String t = nowTitle.length() ? nowTitle : baseName(playlist[trackIdx]);
  for (int l = 0; l < 3 && t.length(); l++) {
    tft.setCursor(2, 22 + l * 11); tft.print(t.substring(0, 21)); t = t.substring(21);
  }
  tft.setTextColor(C_DIM);
  tft.setCursor(2, 60); tft.print(nowArtist.substring(0, 21));
  tft.setCursor(2, 76); tft.printf("Track %d / %d", trackIdx + 1, playlist.size());
  tft.setCursor(2, 88); tft.print(baseName(curDir).substring(0, 21));
  // volume bar
  tft.setTextColor(C_FG);
  tft.setCursor(2, 140); tft.printf("Vol %2d", volume);
  tft.drawRect(44, 140, 82, 8, C_FG);
  tft.fillRect(45, 141, (80 * volume) / 21, 6, C_HL);
}

void drawProgress() {
  uint32_t cur = audio.getAudioCurrentTime(), dur = audio.getAudioFileDuration();
  tft.fillRect(0, 120, 128, 14, C_BG);
  tft.setTextColor(C_DIM); tft.setCursor(2, 122);
  tft.printf("%02u:%02u / %02u:%02u", cur / 60, cur % 60, dur / 60, dur % 60);
  if (dur) { tft.drawRect(2, 131, 124, 3, C_DIM); tft.fillRect(2, 131, (124UL * cur) / dur, 3, C_HL); }
}

// ---------- playback ----------
void playTrack(int idx) {
  if (playlist.empty()) return;
  if (idx < 0) idx = playlist.size() - 1;
  if (idx >= (int)playlist.size()) idx = 0;
  trackIdx = idx;
  nowTitle = ""; nowArtist = "";
  paused = false;
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
      if (s.startsWith("Title: "))       { nowTitle  = s.substring(7); needRedraw = true; }
      else if (s.startsWith("Artist: ")) { nowArtist = s.substring(8); needRedraw = true; }
      break;
    }
    case Audio::evt_eof:  trackEnded = true; break;   // advance from loop(), not from inside the library
    case Audio::evt_info: Serial.printf("audio: %s\n", m.msg); break;
    case Audio::evt_log:  Serial.printf("audio log: %s\n", m.msg); break;
    default: break;
  }
}

// ---------- input ----------
struct Btn { int pin; bool last = true; uint32_t downAt = 0; bool longFired = false; };
Btn bSw{ENC_SW};

// returns 0 none, 1 short press, 2 long press
int pollBtn(Btn& b) {
  bool v = digitalRead(b.pin);
  int r = 0;
  if (!v && b.last) { b.downAt = millis(); b.longFired = false; }
  if (!v && !b.last && !b.longFired && millis() - b.downAt > 600) { b.longFired = true; r = 2; }
  if (v && !b.last && !b.longFired && millis() - b.downAt > 30) r = 1;
  b.last = v;
  return r;
}

void goBack() {
  if (mode == PLAYING) { mode = BROWSE; needRedraw = true; }   // music keeps playing
  else if (curDir != rootDir) {
    String up = curDir.substring(0, curDir.lastIndexOf('/'));
    if (up.length() < rootDir.length()) up = rootDir;
    curDir = up; loadDir(curDir);
  }
}

// One control, the encoder:
//   turn           scroll (browser) / volume (playing)
//   click          open folder, play file / play-pause
//   hold           back: up a folder, or from the player to the browser
//   hold and turn  next / previous track
void handleInput() {
  long d = enc.getCount();
  int steps = d / 2;                         // KY-040 gives 2 counts per detent
  if (steps) enc.setCount(d - steps * 2);    // keep a half-step for the next pass

  int sw = pollBtn(bSw);
  bool held = !bSw.last;

  if (steps && held) {
    bSw.longFired = true;                    // this press is a skip, not a click or a hold
    if (trackIdx >= 0) {
      if (steps > 0) playTrack(trackIdx + 1);
      else if (audio.getAudioCurrentTime() > 3) playTrack(trackIdx);   // restart the current track
      else playTrack(trackIdx - 1);
    }
  } else if (steps) {
    if (mode == BROWSE && !entries.empty()) {
      sel = constrain(sel + steps, 0, (int)entries.size() - 1);
      if (sel < top) top = sel;
      if (sel >= top + ROWS) top = sel - ROWS + 1;
    } else if (mode == PLAYING) {
      volume = constrain(volume + steps, 0, 21);
      audio.setVolume(volume);
    }
    needRedraw = true;
  }

  if (sw == 1) {
    if (mode == BROWSE && !entries.empty()) {
      Entry& e = entries[sel];
      if (e.isDir) { curDir = joinPath(curDir, e.name); loadDir(curDir); }
      else playFolderFrom(joinPath(curDir, e.name));
    } else if (mode == PLAYING) {
      audio.pauseResume(); paused = !paused; needRedraw = true;
    }
  } else if (sw == 2) {
    goBack();
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
  tft.fillScreen(C_BG);
  tft.setTextColor(C_FG); tft.setCursor(10, 70); tft.print("Starting...");

  ESP32Encoder::useInternalWeakPullResistors = puType::up;
  enc.attachHalfQuad(ENC_DT, ENC_CLK);
  enc.clearCount();

  if (!SD.begin(SD_CS, SPI, 20000000)) {
    tft.fillScreen(C_BG); tft.setCursor(10, 70); tft.print("SD card not found");
    while (true) delay(1000);
  }
  if (!SD.exists(rootDir)) { rootDir = "/"; curDir = rootDir; }

  Audio::audio_info_callback = onAudioInfo;
  audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  audio.setVolumeSteps(21);
  audio.setVolume(volume);

  loadDir(curDir);
}

void loop() {
  audio.loop();
  if (trackEnded) { trackEnded = false; playTrack(trackIdx + 1); }
  handleInput();

  static uint32_t lastProg = 0;
  if (needRedraw) {
    needRedraw = false;
    if (mode == BROWSE) drawBrowser(); else { drawPlayer(); drawProgress(); }
  } else if (mode == PLAYING && millis() - lastProg > 1000) {
    lastProg = millis(); drawProgress();
  }
}
