#!/usr/bin/env python3
"""Launch the pure-Python safety + command path (no robot / ROS required)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robotrola.command_path import demo_safe_path, Platform
from robotrola.safety import SafetyInputs


def main() -> int:
    print("=== Robotrola pure-Python safety path (run 1) ===")
    r1 = demo_safe_path()
    print(json.dumps(r1, indent=2))

    print("=== Robotrola pure-Python safety path (run 2) ===")
    r2 = demo_safe_path()
    print(json.dumps(r2, indent=2))

    assert r1 == r2, "non-deterministic dual launch"
    assert r1["good_ok"] and not r1["bad_ok"]
    assert r1["dof"] >= 30

    print("=== estop fault + reset ===")
    p = Platform()
    p.boot()
    p.arm()
    p.activate()
    p.fault_from_estop()
    ok = p.reset_from_fault(SafetyInputs(estop_ok=True, deadman_ok=True))
    print(json.dumps({"reset_ok": ok, "mode": p.supervisor.mode.value}))
    assert ok

    print("SAFETY_PATH_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
