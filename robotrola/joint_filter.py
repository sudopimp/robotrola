"""Guarded joint-command filter shared by pure-Python demos and ROS nodes.

All motion proposals pass through ``robotrola.command_path.Platform`` so
feature flags + joint limits + mode machine stay single-sourced.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from robotrola.command_path import CommandResult, Platform
from robotrola.msgs import CommandResultMsg, JointCommandMsg, SafetyStateMsg
from robotrola.safety import SafetyInputs, SafetyMode


@dataclass
class JointCommandFilter:
    """Approve or reject joint setpoints via the shipped safety library."""

    platform: Platform = field(default_factory=Platform)
    auto_boot: bool = True

    def __post_init__(self) -> None:
        if self.auto_boot and self.platform.supervisor.mode == SafetyMode.BOOT:
            self.platform.boot()

    def arm(self, inputs: SafetyInputs | None = None) -> bool:
        return self.platform.arm(inputs)

    def activate(self, inputs: SafetyInputs | None = None) -> bool:
        return self.platform.activate(inputs)

    def reset_from_fault(self, inputs: SafetyInputs | None = None) -> bool:
        return self.platform.reset_from_fault(inputs)

    def fault_from_estop(self) -> SafetyMode:
        return self.platform.fault_from_estop()

    def safety_state(self, inputs: SafetyInputs | None = None) -> SafetyStateMsg:
        inputs = inputs or SafetyInputs(estop_ok=True, deadman_ok=True)
        self.platform.supervisor.evaluate_inputs(inputs)
        return SafetyStateMsg(
            mode=self.platform.supervisor.mode.value,
            estop_ok=inputs.estop_ok,
            deadman_ok=inputs.deadman_ok,
            leak_ok=inputs.leak_ok,
            thermal_ok=inputs.thermal_ok,
            last_fault=self.platform.supervisor.last_fault or "",
        )

    def filter_command(self, cmd: JointCommandMsg) -> CommandResultMsg:
        r: CommandResult = self.platform.command(
            cmd.name,
            cmd.position_rad,
            cmd.velocity_rad_s,
            cmd.effort_nm,
        )
        return CommandResultMsg(
            ok=r.ok,
            reason=r.reason,
            mode=r.mode,
            joint=cmd.name,
        )

    def filter_dict(self, d: dict) -> CommandResultMsg:
        return self.filter_command(JointCommandMsg.from_dict(d))

    def snapshot(self) -> dict:
        return self.platform.snapshot()


def demo_filter_path() -> dict:
    """Canonical filter path for tests: arm → activate → good/bad/hand."""
    f = JointCommandFilter()
    f.arm()
    f.activate()
    joint = "neck_yaw"
    if joint not in f.platform.joint_names:
        joint = f.platform.joint_names[0]
    good = f.filter_command(JointCommandMsg(joint, 0.1, 0.05, 0.1))
    bad = f.filter_command(JointCommandMsg(joint, 0.1, 99.0, 0.1))
    hand = f.filter_command(JointCommandMsg("left_index_curl", 0.2, 0.1, 0.05))
    return {
        "joint": joint,
        "good_ok": good.ok,
        "bad_ok": bad.ok,
        "bad_reason": bad.reason,
        "hand_ok": hand.ok,
        "hand_reason": hand.reason,
        "mode": f.platform.supervisor.mode.value,
        "dof": len(f.platform.joint_names),
    }
