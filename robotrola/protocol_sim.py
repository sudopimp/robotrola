"""Host-side simulator of the safety MCU serial protocol.

Mirrors firmware/micro_ros_safety_esp32 behavior enough for unit tests and
investor demos without flashing hardware. Not a cycle-accurate emulator.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SafetyMcuSim:
    """Line-oriented protocol: HEARTBEAT | RESET | FAULT | STATUS | PING."""

    watchdog_timeout_ms: int = 250
    estop_ok: bool = True
    deadman_ok: bool = True
    leak_ok: bool = True
    fault_latched: bool = True
    last_heartbeat_ms: int | None = None
    now_ms: int = 0
    loop_count: int = 0
    fault_count: int = 0
    events: list[str] = field(default_factory=list)

    def tick(self, dt_ms: int = 10) -> None:
        self.now_ms += dt_ms
        self.loop_count += 1
        self._reevaluate()

    def _heartbeat_age(self) -> int:
        if self.last_heartbeat_ms is None:
            return 10**9
        return self.now_ms - self.last_heartbeat_ms

    def _heartbeat_ok(self) -> bool:
        if self.last_heartbeat_ms is None:
            return False
        return self._heartbeat_age() < self.watchdog_timeout_ms

    def path_healthy(self) -> bool:
        return (
            self.estop_ok
            and self.deadman_ok
            and self.leak_ok
            and self._heartbeat_ok()
            and not self.fault_latched
        )

    def contactor_enable(self) -> bool:
        return self.path_healthy()

    def _enter_fault(self, reason: str) -> None:
        if not self.fault_latched:
            self.fault_count += 1
        self.fault_latched = True
        self.events.append(f"FAULT:{reason}")

    def _reevaluate(self) -> None:
        if not self.estop_ok:
            self._enter_fault("estop_open")
        elif not self.deadman_ok:
            self._enter_fault("deadman_open")
        elif not self.leak_ok:
            self._enter_fault("leak_detected")
        elif self.last_heartbeat_ms is not None and not self._heartbeat_ok():
            self._enter_fault("heartbeat_timeout")

    def handle(self, line: str) -> str | None:
        """Process one host command; return response line or None."""
        cmd = line.strip().upper()
        if not cmd:
            return None
        if cmd == "HEARTBEAT":
            self.last_heartbeat_ms = self.now_ms
            return None
        if cmd == "RESET":
            if self.estop_ok:
                self.fault_latched = False
                self.last_heartbeat_ms = self.now_ms
                self.events.append("RESET:ok")
                return "EVENT RESET ok=1"
            self.events.append("RESET:fail")
            return "EVENT RESET ok=0 reason=estop_open"
        if cmd == "FAULT":
            self._enter_fault("host_command")
            return "EVENT FAULT reason=host_command"
        if cmd == "STATUS":
            return self.status_line()
        if cmd == "PING":
            return "PONG robotrola-safety-mcu"
        return f"EVENT UNKNOWN_CMD cmd={cmd}"

    def status_line(self) -> str:
        ok = 1 if self.path_healthy() else 0
        return (
            f"STATUS ok={ok} estop={int(self.estop_ok)} deadman={int(self.deadman_ok)} "
            f"leak={int(self.leak_ok)} fault={int(self.fault_latched)} "
            f"hb_age_ms={self._heartbeat_age()} contactor={int(self.contactor_enable())} "
            f"loops={self.loop_count} faults={self.fault_count}"
        )


@dataclass
class MotorBridgeSim:
    """Minimal host protocol mirror for STM32 DYNAMIXEL bridge."""

    hb_timeout_ms: int = 250
    safety_ok: bool = False
    fault_latched: bool = True
    last_hb_ms: int | None = None
    now_ms: int = 0
    n_ids: int = 0
    rejects: int = 0
    max_goal_delta: int = 512
    positions: dict[int, int] = field(default_factory=dict)

    def tick(self, dt_ms: int = 5) -> None:
        self.now_ms += dt_ms
        if self.last_hb_ms is not None and (self.now_ms - self.last_hb_ms) >= self.hb_timeout_ms:
            self.fault_latched = True

    def path_ready(self) -> bool:
        if self.fault_latched or not self.safety_ok:
            return False
        if self.last_hb_ms is None:
            return False
        return (self.now_ms - self.last_hb_ms) < self.hb_timeout_ms

    def handle(self, line: str) -> str:
        parts = line.strip().split()
        if not parts:
            return ""
        cmd = parts[0].upper()
        if cmd in {"HB", "HEARTBEAT"}:
            self.last_hb_ms = self.now_ms
            return ""
        if cmd == "PING":
            return "PONG bridge=stm32-dxl"
        if cmd == "SAFETY":
            # SAFETY ok=1
            for tok in parts[1:]:
                if tok.startswith("ok="):
                    self.safety_ok = tok.split("=", 1)[1] == "1"
                    if self.safety_ok:
                        self.fault_latched = False
                    else:
                        self.fault_latched = True
            return ""
        if cmd == "SCAN":
            self.n_ids = 12
            for i in range(1, 13):
                self.positions.setdefault(i, 2048)
            return f"EVENT SCAN n_ids={self.n_ids}"
        if cmd == "GOAL":
            if not self.path_ready():
                self.rejects += 1
                return "EVENT REJECT reason=path_not_ready cmd=GOAL"
            kv = dict(t.split("=", 1) for t in parts[1:] if "=" in t)
            mid = int(kv.get("id", "0"))
            pos = int(kv.get("pos", "0"))
            cur = self.positions.get(mid, 2048)
            delta = max(-self.max_goal_delta, min(self.max_goal_delta, pos - cur))
            self.positions[mid] = cur + delta
            return "EVENT GOAL ok=1"
        if cmd == "STATUS":
            age = 99999 if self.last_hb_ms is None else self.now_ms - self.last_hb_ms
            return (
                f"STATUS ok={int(self.path_ready())} safety={int(self.safety_ok)} "
                f"fault={int(self.fault_latched)} hb_age_ms={age} n_ids={self.n_ids} "
                f"rejects={self.rejects}"
            )
        if cmd == "DISABLE":
            return "EVENT DISABLE"
        return f"EVENT UNKNOWN_CMD cmd={cmd}"
