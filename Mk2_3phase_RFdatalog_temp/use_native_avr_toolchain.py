import os
import platform
from pathlib import Path


Import("env")


homebrew_prefix = Path(os.environ.get("HOMEBREW_PREFIX", "/opt/homebrew"))
homebrew_bin = Path(
    os.environ.get("PIO_HOMEBREW_BIN", homebrew_prefix / "bin")
)
gcc_bin = Path(
    os.environ.get(
        "PIO_AVR_GCC_BIN", homebrew_prefix / "opt" / "avr-gcc@12" / "bin"
    )
)
binutils_bin = Path(
    os.environ.get(
        "PIO_AVR_BINUTILS_BIN", homebrew_prefix / "opt" / "avr-binutils" / "bin"
    )
)
avrdude_config = Path(
    os.environ.get(
        "PIO_AVRDUDE_CONFIG", homebrew_prefix / "etc" / "avrdude.conf"
    )
)

tools = {
    "CC": gcc_bin / "avr-gcc",
    "CXX": gcc_bin / "avr-g++",
    "AR": gcc_bin / "avr-gcc-ar",
    "RANLIB": gcc_bin / "avr-gcc-ranlib",
    "AS": binutils_bin / "avr-as",
    "OBJCOPY": binutils_bin / "avr-objcopy",
    "SIZETOOL": binutils_bin / "avr-size",
    "UPLOADER": homebrew_bin / "avrdude",
}

if platform.system() == "Darwin" and platform.machine() == "arm64":
    missing_tools = [
        str(path)
        for path in tools.values()
        if not path.is_file() or not os.access(path, os.X_OK)
    ]
    if not avrdude_config.is_file():
        missing_tools.append(str(avrdude_config))
    if missing_tools:
        raise RuntimeError(
            "Native AVR tools are incomplete. Install them with "
            "'brew tap osx-cross/avr && brew install avr-gcc@12 avrdude'. "
            "Missing: "
            + ", ".join(missing_tools)
        )

    env.PrependENVPath("PATH", str(homebrew_bin))
    env.PrependENVPath("PATH", str(binutils_bin))
    env.PrependENVPath("PATH", str(gcc_bin))

    if "UPLOADERFLAGS" in env:
        uploader_flags = list(env["UPLOADERFLAGS"])
        if "-C" in uploader_flags:
            config_index = uploader_flags.index("-C") + 1
            uploader_flags[config_index] = str(avrdude_config)
            env.Replace(UPLOADERFLAGS=uploader_flags)
            print(f"Using native AVRDUDE configuration from {avrdude_config}")
    else:
        print(f"Using native AVR toolchain from {gcc_bin}")
