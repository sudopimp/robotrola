#!/usr/bin/env python3
"""Hardware-free sim smoke: URDF joints + safety filter trajectory."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robotrola.sim_core import run_sim_smoke  # noqa: E402


def main() -> int:
    result = run_sim_smoke()
    print(json.dumps(result.to_dict(), indent=2))
    if result.ok:
        print("SIM_SMOKE_OK")
        return 0
    print("SIM_SMOKE_FAIL", result.errors)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
