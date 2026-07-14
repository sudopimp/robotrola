"""Host-side serial protocol helpers shared with firmware / protocol_sim.

Command tokens must stay lockstep with:
- ``firmware/esp32_safety_mcu``
- ``firmware/stm32_dynamixel_bridge``
- ``robotrola.protocol_sim``
"""
from __future__ import annotations

# Safety MCU (esp32_safety_mcu)
SAFETY_CMDS = ("HEARTBEAT", "RESET", "FAULT", "STATUS", "PING")

# Motor bridge (stm32_dynamixel_bridge)
BRIDGE_CMDS = (
    "HB",
    "HEARTBEAT",
    "PING",
    "STATUS",
    "STOP",
    "DISABLE",
    "SCAN",
    "CLEAR",
    "SAFETY",
    "EN",
    "ENALL",
    "GOAL",
    "VEL",
)


def normalize_safety_cmd(line: str) -> str:
    return line.strip().upper()


def is_known_safety_cmd(line: str) -> bool:
    cmd = normalize_safety_cmd(line)
    if cmd in SAFETY_CMDS:
        return True
    return False


def is_known_bridge_cmd(line: str) -> bool:
    raw = line.strip()
    if not raw:
        return False
    head = raw.split()[0].upper()
    # GOAL id=1 pos=2048 → GOAL
    for c in BRIDGE_CMDS:
        if head == c or head.startswith(c):
            return True
    return False


def parse_status_kv(line: str) -> dict[str, str]:
    """Parse ``STATUS ok=1 estop=1 ...`` into a dict."""
    out: dict[str, str] = {}
    parts = line.strip().split()
    if not parts:
        return out
    if parts[0].upper() == "STATUS":
        parts = parts[1:]
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k] = v
    return out
