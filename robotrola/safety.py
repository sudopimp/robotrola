
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import time
import yaml

class SafetyMode(str, Enum):
    BOOT = "BOOT"
    SAFE_IDLE = "SAFE_IDLE"
    ARMED = "ARMED"
    ACTIVE = "ACTIVE"
    FAULT = "FAULT"

@dataclass
class JointCommand:
    name: str
    position_rad: float
    velocity_rad_s: float
    effort_nm: float

@dataclass
class SafetyInputs:
    estop_ok: bool
    deadman_ok: bool
    leak_ok: bool = True
    thermal_ok: bool = True
    battery_ok: bool = True
    main_heartbeat_age_ms: int = 0

class SafetySupervisor:
    def __init__(self, limits_path: str | Path):
        self.limits = yaml.safe_load(Path(limits_path).read_text())
        self.mode = SafetyMode.BOOT
        self.last_fault: str | None = None

    def self_test(self) -> bool:
        self.mode = SafetyMode.SAFE_IDLE
        return True

    def evaluate_inputs(self, inputs: SafetyInputs) -> SafetyMode:
        if not inputs.estop_ok:
            return self._fault("estop_open")
        if not inputs.deadman_ok and self.mode in {SafetyMode.ARMED, SafetyMode.ACTIVE}:
            return self._fault("deadman_open")
        if not inputs.leak_ok:
            return self._fault("leak_detected")
        if not inputs.thermal_ok:
            return self._fault("thermal_fault")
        if not inputs.battery_ok:
            return self._fault("battery_fault")
        timeout = int(self.limits["watchdog"]["main_heartbeat_timeout_ms"])
        if self.mode == SafetyMode.ACTIVE and inputs.main_heartbeat_age_ms > timeout:
            return self._fault("heartbeat_timeout")
        return self.mode

    def arm(self, inputs: SafetyInputs) -> bool:
        self.evaluate_inputs(inputs)
        if self.mode == SafetyMode.SAFE_IDLE and inputs.estop_ok and inputs.deadman_ok:
            self.mode = SafetyMode.ARMED
            return True
        return False

    def activate(self, inputs: SafetyInputs) -> bool:
        self.evaluate_inputs(inputs)
        if self.mode == SafetyMode.ARMED and inputs.deadman_ok:
            self.mode = SafetyMode.ACTIVE
            return True
        return False

    def approve_joint_command(self, cmd: JointCommand) -> tuple[bool, str]:
        if self.mode != SafetyMode.ACTIVE:
            return False, f"mode_not_active:{self.mode.value}"
        joint_limits = self.limits["joint_limits"].get(cmd.name, self.limits["joint_limits"]["default"])
        if not (joint_limits["position_min_rad"] <= cmd.position_rad <= joint_limits["position_max_rad"]):
            return False, "position_limit"
        if abs(cmd.velocity_rad_s) > joint_limits["velocity_max_rad_s"]:
            return False, "velocity_limit"
        if abs(cmd.effort_nm) > joint_limits["effort_max_nm"]:
            return False, "effort_limit"
        return True, "approved"

    def _fault(self, reason: str) -> SafetyMode:
        self.mode = SafetyMode.FAULT
        self.last_fault = reason
        return self.mode
