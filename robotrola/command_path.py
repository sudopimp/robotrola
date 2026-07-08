"""Runnable pure-Python safety + motion path (no physical robot required)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from robotrola.safety import (
    SafetySupervisor,
    SafetyInputs,
    JointCommand,
    SafetyMode,
)
from robotrola.description import revolute_joints, DEFAULT_URDF
from robotrola.features import FeatureFlags

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIMITS = ROOT / "configs" / "safety_limits.yaml"
DEFAULT_FLAGS = ROOT / "configs" / "feature_flags.yaml"

# Commands that require human_contact_mode feature flag at runtime
CONTACT_SENSITIVE_PREFIXES = (
    "left_thumb",
    "left_index",
    "left_middle",
    "left_ring",
    "left_pinky",
    "right_thumb",
    "right_index",
    "right_middle",
    "right_ring",
    "right_pinky",
)


@dataclass
class CommandResult:
    ok: bool
    reason: str
    mode: str


@dataclass
class Platform:
    """Single entry for arm/activate/command against shipped safety library."""

    limits_path: Path = DEFAULT_LIMITS
    urdf_path: Path = DEFAULT_URDF
    flags_path: Path = DEFAULT_FLAGS
    supervisor: SafetySupervisor = field(init=False)
    joint_names: list[str] = field(init=False)
    features: FeatureFlags = field(init=False)
    require_contact_flag_for_hands: bool = True

    def __post_init__(self) -> None:
        self.supervisor = SafetySupervisor(self.limits_path)
        self.joint_names = [j.name for j in revolute_joints(self.urdf_path)]
        self.features = FeatureFlags(self.flags_path)

    def boot(self) -> SafetyMode:
        self.supervisor.self_test()
        return self.supervisor.mode

    def arm(self, inputs: SafetyInputs | None = None) -> bool:
        inputs = inputs or SafetyInputs(estop_ok=True, deadman_ok=True)
        return self.supervisor.arm(inputs)

    def activate(self, inputs: SafetyInputs | None = None) -> bool:
        inputs = inputs or SafetyInputs(estop_ok=True, deadman_ok=True)
        return self.supervisor.activate(inputs)

    def fault_from_estop(self) -> SafetyMode:
        return self.supervisor.evaluate_inputs(
            SafetyInputs(estop_ok=False, deadman_ok=True)
        )

    def reset_from_fault(self, inputs: SafetyInputs | None = None) -> bool:
        """Clear FAULT to SAFE_IDLE when interlocks healthy (software mirror of MCU RESET)."""
        inputs = inputs or SafetyInputs(estop_ok=True, deadman_ok=True)
        if self.supervisor.mode != SafetyMode.FAULT:
            return False
        if not inputs.estop_ok:
            return False
        self.supervisor.mode = SafetyMode.SAFE_IDLE
        self.supervisor.last_fault = None
        return True

    def _contact_blocked(self, name: str) -> bool:
        if not self.require_contact_flag_for_hands:
            return False
        if self.features.enabled("human_contact_mode"):
            return False
        return any(name.startswith(p) for p in CONTACT_SENSITIVE_PREFIXES)

    def command(
        self,
        name: str,
        position_rad: float = 0.0,
        velocity_rad_s: float = 0.0,
        effort_nm: float = 0.0,
    ) -> CommandResult:
        if self._contact_blocked(name):
            return CommandResult(
                ok=False,
                reason="feature_flag_blocked:human_contact_mode",
                mode=self.supervisor.mode.value,
            )
        if self.features.enabled("autonomous_locomotion") is False:
            # locomotion joints still allowed in ACTIVE for fixture/teleop research;
            # autonomous flag is validated separately by policy layer.
            pass
        ok, reason = self.supervisor.approve_joint_command(
            JointCommand(name, position_rad, velocity_rad_s, effort_nm)
        )
        return CommandResult(ok=ok, reason=reason, mode=self.supervisor.mode.value)

    def command_all_zero(self) -> list[CommandResult]:
        return [self.command(n, 0.0, 0.0, 0.0) for n in self.joint_names]

    def snapshot(self) -> dict:
        return {
            "mode": self.supervisor.mode.value,
            "dof": len(self.joint_names),
            "last_fault": self.supervisor.last_fault,
            "human_contact_mode": self.features.enabled("human_contact_mode"),
            "cloud_connectivity": self.features.enabled("cloud_connectivity"),
            "autonomous_locomotion": self.features.enabled("autonomous_locomotion"),
        }


def demo_safe_path() -> dict:
    """Canonical launch path used by tests and scripts/run_safety_path.py."""
    p = Platform()
    p.boot()
    assert p.arm()
    assert p.activate()
    joint = "neck_yaw" if "neck_yaw" in p.joint_names else p.joint_names[0]
    good = p.command(joint, 0.1, 0.05, 0.1)
    bad = p.command(joint, 0.1, 99.0, 0.1)
    # hand curl blocked while human_contact_mode is false
    hand = p.command("left_index_curl", 0.2, 0.1, 0.05)
    return {
        "joint": joint,
        "dof": len(p.joint_names),
        "good_ok": good.ok,
        "good_reason": good.reason,
        "bad_ok": bad.ok,
        "bad_reason": bad.reason,
        "hand_ok": hand.ok,
        "hand_reason": hand.reason,
        "mode": p.supervisor.mode.value,
        "flags": {
            "human_contact_mode": p.features.enabled("human_contact_mode"),
            "cloud_connectivity": p.features.enabled("cloud_connectivity"),
        },
    }
