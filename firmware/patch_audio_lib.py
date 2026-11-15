# Runs before each build (see extra_scripts in platformio.ini).
#
# ESP32-audioI2S 4.0.1 skips an embedded FLAC cover picture by reading through it a
# block at a time. A multi-megabyte picture takes longer than the library's 8 s
# header timeout, so the track never starts. This patch makes it seek past the
# picture instead when playing a local file. It is applied in place and only once.
import os

Import("env")  # noqa: F821  (provided by PlatformIO)

path = os.path.join(env.subst("$PROJECT_LIBDEPS_DIR"), env.subst("$PIOENV"), "ESP32-audioI2S", "src", "Audio.cpp")
MARK = "// paata: seek past large embedded pictures"
OLD = """        m_controlCounter = FLAC_MBH;
        m_rflh.retvalue = m_rflh.picLen + 3;
        m_rflh.headerSize += m_rflh.retvalue;
        return 0;
"""
NEW = """        m_controlCounter = FLAC_MBH;
        """ + MARK + """
        if (m_dataMode == AUDIO_LOCALFILE && m_rflh.picLen > 32768) {
            uint32_t next = m_audioFilePosition - InBuff.bufferFilled() + 3 + m_rflh.picLen; // first byte after the picture
            m_rflh.headerSize += m_rflh.picLen + 3;
            m_rflh.retvalue = 0;
            InBuff.reset();
            audioFileSeek(next);
            m_f_allDataReceived = false;
            return 0;
        }
        m_rflh.retvalue = m_rflh.picLen + 3;
        m_rflh.headerSize += m_rflh.retvalue;
        return 0;
"""
if not os.path.isfile(path):
    print("patch_audio_lib: library not installed yet, build once more to apply the patch")
else:
    src = open(path, encoding="utf-8").read()
    if MARK in src:
        pass
    elif OLD in src:
        open(path, "w", encoding="utf-8").write(src.replace(OLD, NEW, 1))
        print("patch_audio_lib: patched", path)
    else:
        print("patch_audio_lib: WARNING, expected code not found; library version changed?")
