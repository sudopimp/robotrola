#!/usr/bin/env python3
"""Validate firmware packages structure + protocol lockstep with host_serial.

If PlatformIO (``pio``) is on PATH, optionally build both envs
(``--build``). CI without pio still gets structural + token gates.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SAFETY = ROOT / "firmware" / "esp32_safety_mcu"
BRIDGE = ROOT / "firmware" / "stm32_dynamixel_bridge"

SAFETY_TOKENS = ("HEARTBEAT", "RESET", "FAULT", "STATUS", "PING", "PIN_ESTOP")
BRIDGE_TOKENS = ("GOAL", "HB", "SAFETY", "STATUS", "DXL", "BRIDGE_HB_TIMEOUT")


def check_package(pkg: Path, tokens: tuple[str, ...], main_rel: str) -> list[str]:
    errs: list[str] = []
    if not pkg.is_dir():
        return [f"missing_pkg:{pkg}"]
    main = pkg / main_rel
    ini = pkg / "platformio.ini"
    if not main.is_file():
        errs.append(f"missing_main:{main.relative_to(ROOT)}")
    if not ini.is_file():
        errs.append(f"missing_platformio:{ini.relative_to(ROOT)}")
    if main.is_file():
        text = main.read_text(encoding="utf-8", errors="replace")
        for t in tokens:
            if t not in text:
                errs.append(f"token_missing:{pkg.name}:{t}")
        if len(text.splitlines()) < 40:
            errs.append(f"too_thin:{pkg.name}")
    # Forbid legacy path
    if (ROOT / "firmware" / "micro_ros_safety_esp32").exists():
        errs.append("legacy_micro_ros_path")
    return errs


def try_pio_build(pkg: Path) -> list[str]:
    pio = shutil.which("pio") or shutil.which("platformio")
    if not pio:
        return []  # optional
    errs: list[str] = []
    r = subprocess.run(
        [pio, "run"],
        cwd=pkg,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if r.returncode != 0:
        errs.append(f"pio_build_failed:{pkg.name}:{(r.stderr or r.stdout)[-400:]}")
    return errs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--build",
        action="store_true",
        help="run PlatformIO build if pio is installed",
    )
    args = ap.parse_args(argv)

    errs: list[str] = []
    errs += check_package(SAFETY, SAFETY_TOKENS, "src/main.cpp")
    errs += check_package(BRIDGE, BRIDGE_TOKENS, "src/main.cpp")

    # Protocol lockstep with host_serial
    from robotrola.host_serial import SAFETY_CMDS, BRIDGE_CMDS

    safety_src = (SAFETY / "src/main.cpp").read_text(encoding="utf-8")
    for cmd in SAFETY_CMDS:
        if cmd not in safety_src:
            errs.append(f"safety_host_serial_mismatch:{cmd}")

    if args.build:
        errs += try_pio_build(SAFETY)
        errs += try_pio_build(BRIDGE)
    else:
        pio = shutil.which("pio") or shutil.which("platformio")
        print(f"pio_on_path={bool(pio)} (use --build to compile)")

    if errs:
        print("FIRMWARE_CHECK_FAIL")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("FIRMWARE_CHECK_OK")
    print(f"  safety={SAFETY.relative_to(ROOT)}")
    print(f"  bridge={BRIDGE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
