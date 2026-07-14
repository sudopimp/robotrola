"""Hardware-free simulation smoke: joint-space steps under safety filter.

Not Gazebo/MuJoCo physics — a deterministic digital-stub that proves the
description + safety gate path before optional full-physics stacks.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from robotrola.description import revolute_joints, DEFAULT_URDF
from robotrola.joint_filter import JointCommandFilter
from robotrola.kinematics import sample_joint_space_trajectory
from robotrola.msgs import JointCommandMsg


@dataclass
class SimSmokeResult:
    ok: bool
    steps: int
    approved: int
    rejected: int
    joint: str
    final_positions: dict[str, float]
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "steps": self.steps,
            "approved": self.approved,
            "rejected": self.rejected,
            "joint": self.joint,
            "final_positions": self.final_positions,
            "errors": self.errors,
            "SIM_SMOKE_OK": self.ok,
        }


def run_sim_smoke(
    urdf_path: str | Path = DEFAULT_URDF,
    steps: int = 5,
    amplitude_rad: float = 0.1,
) -> SimSmokeResult:
    """Arm/activate, step a small joint trajectory through the filter."""
    revs = revolute_joints(urdf_path)
    names = [j.name for j in revs]
    errors: list[str] = []
    if len(names) < 30:
        errors.append(f"dof_too_low:{len(names)}")

    filt = JointCommandFilter()
    if not filt.arm():
        errors.append("arm_failed")
    if not filt.activate():
        errors.append("activate_failed")

    primary = "neck_yaw" if "neck_yaw" in names else names[0]
    # Joints with symmetric-ish limits around 0 (avoid one-sided elbows/knees)
    drive = [primary]
    for cand in ("left_shoulder_pitch", "waist_yaw", "right_shoulder_pitch"):
        if cand in names and cand not in drive:
            drive.append(cand)
    traj = sample_joint_space_trajectory(drive, steps=steps, amplitude_rad=amplitude_rad)
    approved = 0
    rejected = 0
    positions = {n: 0.0 for n in names}

    for frame in traj:
        for jname in drive:
            if jname not in frame:
                continue
            cmd = JointCommandMsg(
                name=jname,
                position_rad=float(frame[jname]),
                velocity_rad_s=0.05,
                effort_nm=0.1,
            )
            res = filt.filter_command(cmd)
            if res.ok:
                approved += 1
                positions[jname] = cmd.position_rad
            else:
                rejected += 1
                # illegal should not happen for small amplitude on drive set
                if "velocity" in res.reason or "position" in res.reason:
                    errors.append(f"unexpected_reject:{jname}:{res.reason}")

    # Prove rejection path still works mid-sim
    bad = filt.filter_command(JointCommandMsg(primary, 0.0, 99.0, 0.0))
    if bad.ok:
        errors.append("bad_velocity_was_approved")
    else:
        rejected += 1

    ok = not errors and approved > 0 and not bad.ok
    return SimSmokeResult(
        ok=ok,
        steps=len(traj),
        approved=approved,
        rejected=rejected,
        joint=primary,
        final_positions={k: positions[k] for k in drive[:2] if k in positions},
        errors=errors,
    )
