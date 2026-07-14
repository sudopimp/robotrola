"""Robotrola Core — complete open research platform helpers.

Heavy imports are lazy so lightweight modules (e.g. ``host_serial``) can load
without optional stack deps during firmware structure checks.
"""
from __future__ import annotations

__version__ = "0.4.2"  # maximize-software: lerobot bridge, mujoco step, optional CI fixes

__all__ = [
    "SafetySupervisor",
    "SafetyInputs",
    "JointCommand",
    "SafetyMode",
    "Platform",
    "demo_safe_path",
    "revolute_joints",
    "assert_full_humanoid",
    "SafetyMcuSim",
    "MotorBridgeSim",
    "full_cost_model",
    "JointCommandFilter",
    "__version__",
]


def __getattr__(name: str):
    if name in {
        "SafetySupervisor",
        "SafetyInputs",
        "JointCommand",
        "SafetyMode",
    }:
        from robotrola import safety as m

        return getattr(m, name)
    if name in {"Platform", "demo_safe_path"}:
        from robotrola import command_path as m

        return getattr(m, name)
    if name in {"revolute_joints", "assert_full_humanoid"}:
        from robotrola import description as m

        return getattr(m, name)
    if name in {"SafetyMcuSim", "MotorBridgeSim"}:
        from robotrola import protocol_sim as m

        return getattr(m, name)
    if name == "full_cost_model":
        from robotrola.cost_model import full_cost_model

        return full_cost_model
    if name == "JointCommandFilter":
        from robotrola.joint_filter import JointCommandFilter

        return JointCommandFilter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
