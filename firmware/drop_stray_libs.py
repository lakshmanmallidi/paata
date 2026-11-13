# Runs before each build (see extra_scripts in platformio.ini).
#
# The Adafruit ST7735 library declares a dependency on the generic Arduino "SD"
# library, which does not support ESP32 and shadows the ESP32 core's own SD.
# PlatformIO cannot exclude a transitive dependency, and lib_ignore = SD also
# drops the core's SD, so delete the stray copies after they are installed.
import os
import shutil

Import("env")  # noqa: F821  (provided by PlatformIO)

libdeps = os.path.join(env.subst("$PROJECT_LIBDEPS_DIR"), env.subst("$PIOENV"))
for name in ("SD", "Adafruit seesaw Library"):
    path = os.path.join(libdeps, name)
    if os.path.isdir(path):
        print("drop_stray_libs: removing", path)
        shutil.rmtree(path)
