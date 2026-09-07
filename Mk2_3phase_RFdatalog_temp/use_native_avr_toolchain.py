import os
import platform
from pathlib import Path


Import("env")


homebrew_prefix = Path(os.environ.get("HOMEBREW_PREFIX", "/opt/homebrew"))
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

tools = {
    "CC": gcc_bin / "avr-gcc",
    "CXX": gcc_bin / "avr-g++",
    "AR": gcc_bin / "avr-gcc-ar",
    "RANLIB": gcc_bin / "avr-gcc-ranlib",
    "AS": binutils_bin / "avr-as",
    "OBJCOPY": binutils_bin / "avr-objcopy",
    "SIZETOOL": binutils_bin / "avr-size",
}

if platform.system() == "Darwin" and platform.machine() == "arm64":
    missing_tools = [
        str(path)
        for path in tools.values()
        if not path.is_file() or not os.access(path, os.X_OK)
    ]
    if missing_tools:
        raise RuntimeError(
            "Native AVR toolchain is incomplete. Install it with "
            "'brew tap osx-cross/avr && brew install avr-gcc@12'. Missing: "
            + ", ".join(missing_tools)
        )

    env.PrependENVPath("PATH", str(gcc_bin))
    env.PrependENVPath("PATH", str(binutils_bin))
    print(f"Using native AVR toolchain from {gcc_bin}")
