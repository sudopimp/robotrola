#!/usr/bin/env python3
"""Demo host clients against protocol_sim (default) or real serial ports.

Examples::

  python scripts/host_serial_demo.py
  python scripts/host_serial_demo.py --safety-port /dev/ttyUSB0
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robotrola.host_client import (  # noqa: E402
    MotorBridgeClient,
    SafetyMcuClient,
    demo_host_clients,
)
from robotrola.protocol_sim import SafetyMcuSim  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--safety-port", default=None, help="real serial for safety MCU")
    ap.add_argument("--bridge-port", default=None, help="real serial for motor bridge")
    ap.add_argument("--baud", type=int, default=115200)
    args = ap.parse_args(argv)

    if not args.safety_port and not args.bridge_port:
        out = demo_host_clients()
        print(json.dumps(out, indent=2))
        if out.get("HOST_CLIENTS_OK"):
            print("HOST_CLIENTS_OK")
            return 0
        print("HOST_CLIENTS_FAIL")
        return 1

    result: dict = {}
    if args.safety_port:
        client = SafetyMcuClient.serial(args.safety_port, baud=args.baud)
        result["safety"] = client.bringup_healthy()
    if args.bridge_port:
        client = MotorBridgeClient.serial(args.bridge_port, baud=args.baud)
        result["bridge"] = client.path_demo()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
