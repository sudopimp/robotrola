"""Host clients for safety MCU and motor bridge (sim or real serial).

Default path uses ``protocol_sim`` so diligence needs no hardware/USB.
Pass ``port=`` (e.g. ``/dev/ttyUSB0``) to use pyserial when installed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from robotrola.host_serial import (
    BRIDGE_CMDS,
    SAFETY_CMDS,
    is_known_bridge_cmd,
    is_known_safety_cmd,
    parse_status_kv,
)
from robotrola.protocol_sim import MotorBridgeSim, SafetyMcuSim


class LineTransport(Protocol):
    def write_line(self, line: str) -> str | None: ...


@dataclass
class SimTransport:
    """Line transport backed by SafetyMcuSim or MotorBridgeSim."""

    device: SafetyMcuSim | MotorBridgeSim
    tick_ms: int = 10

    def write_line(self, line: str) -> str | None:
        if hasattr(self.device, "tick"):
            self.device.tick(self.tick_ms)
        resp = self.device.handle(line)
        return resp if resp else None


@dataclass
class SerialTransport:
    """Optional real serial port (requires pyserial)."""

    port: str
    baud: int = 115200
    timeout_s: float = 0.2
    _ser: object | None = field(default=None, init=False, repr=False)

    def open(self) -> None:
        try:
            import serial  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "pyserial required for hardware serial: pip install pyserial"
            ) from exc
        self._ser = serial.Serial(self.port, self.baud, timeout=self.timeout_s)

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def write_line(self, line: str) -> str | None:
        if self._ser is None:
            self.open()
        assert self._ser is not None
        payload = (line.strip() + "\n").encode("ascii", errors="ignore")
        self._ser.write(payload)
        self._ser.flush()
        raw = self._ser.readline()
        if not raw:
            return None
        return raw.decode("utf-8", errors="replace").strip()


@dataclass
class SafetyMcuClient:
    """Host API for esp32_safety_mcu protocol."""

    transport: LineTransport

    @classmethod
    def sim(cls, mcu: SafetyMcuSim | None = None) -> "SafetyMcuClient":
        return cls(SimTransport(mcu or SafetyMcuSim()))

    @classmethod
    def serial(cls, port: str, baud: int = 115200) -> "SafetyMcuClient":
        return cls(SerialTransport(port=port, baud=baud))

    def send(self, cmd: str) -> str | None:
        cmd = cmd.strip()
        if cmd and not is_known_safety_cmd(cmd) and cmd.upper() not in SAFETY_CMDS:
            # still allow for forward-compat, but warn via return
            pass
        return self.transport.write_line(cmd)

    def heartbeat(self) -> None:
        self.send("HEARTBEAT")

    def reset(self) -> str | None:
        return self.send("RESET")

    def fault(self) -> str | None:
        return self.send("FAULT")

    def status(self) -> dict[str, str]:
        line = self.send("STATUS") or ""
        return parse_status_kv(line)

    def ping(self) -> str | None:
        return self.send("PING")

    def bringup_healthy(self) -> dict:
        """RESET → HEARTBEAT → STATUS; returns status dict + contactor ok flag."""
        self.reset()
        self.heartbeat()
        st = self.status()
        return {
            "status": st,
            "ok": st.get("ok") == "1",
            "contactor": st.get("contactor") == "1",
        }


@dataclass
class MotorBridgeClient:
    """Host API for stm32_dynamixel_bridge protocol."""

    transport: LineTransport

    @classmethod
    def sim(cls, bridge: MotorBridgeSim | None = None) -> "MotorBridgeClient":
        return cls(SimTransport(bridge or MotorBridgeSim(), tick_ms=5))

    @classmethod
    def serial(cls, port: str, baud: int = 115200) -> "MotorBridgeClient":
        return cls(SerialTransport(port=port, baud=baud))

    def send(self, line: str) -> str | None:
        return self.transport.write_line(line)

    def heartbeat(self) -> None:
        self.send("HB")

    def set_safety(self, ok: bool) -> None:
        self.send(f"SAFETY ok={1 if ok else 0}")

    def scan(self) -> str | None:
        return self.send("SCAN")

    def goal(self, motor_id: int, pos: int) -> str | None:
        return self.send(f"GOAL id={motor_id} pos={pos}")

    def status(self) -> dict[str, str]:
        line = self.send("STATUS") or ""
        return parse_status_kv(line)

    def path_demo(self) -> dict:
        """HB + SAFETY ok + SCAN + GOAL under sim (or hardware if wired)."""
        self.heartbeat()
        self.set_safety(True)
        self.heartbeat()
        scan = self.scan()
        goal = self.goal(1, 2100)
        st = self.status()
        return {
            "scan": scan,
            "goal": goal,
            "status": st,
            "ok": st.get("ok") == "1" and (goal or "").startswith("EVENT GOAL"),
        }


def demo_host_clients() -> dict:
    """End-to-end sim path for tests/demo scripts."""
    mcu = SafetyMcuSim()
    # healthy interlocks for bringup
    mcu.estop_ok = True
    mcu.deadman_ok = True
    mcu.leak_ok = True
    safety = SafetyMcuClient.sim(mcu)
    bringup = safety.bringup_healthy()
    bridge = MotorBridgeClient.sim()
    path = bridge.path_demo()
    return {
        "safety": bringup,
        "bridge": path,
        "HOST_CLIENTS_OK": bool(bringup.get("ok") and path.get("ok")),
    }
