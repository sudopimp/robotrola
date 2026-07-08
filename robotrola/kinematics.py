"""Lightweight kinematics helpers for fixture demos and tests (no ROS/Pinocchio)."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PlanarArm:
    """2R planar arm used for one-actuator / arm-fixture explanations."""

    upper_m: float = 0.28
    forearm_m: float = 0.25

    def fk(self, shoulder_rad: float, elbow_rad: float) -> tuple[float, float]:
        x1 = self.upper_m * math.cos(shoulder_rad)
        z1 = self.upper_m * math.sin(shoulder_rad)
        x2 = x1 + self.forearm_m * math.cos(shoulder_rad + elbow_rad)
        z2 = z1 + self.forearm_m * math.sin(shoulder_rad + elbow_rad)
        return x2, z2

    def reachable(self, x: float, z: float, tol: float = 1e-6) -> bool:
        r = math.hypot(x, z)
        return r <= (self.upper_m + self.forearm_m + tol) and r >= abs(
            self.upper_m - self.forearm_m
        ) - tol

    def ik(self, x: float, z: float) -> tuple[float, float] | None:
        """Analytic IK; elbow-up solution. Returns None if unreachable."""
        if not self.reachable(x, z):
            return None
        l1, l2 = self.upper_m, self.forearm_m
        r2 = x * x + z * z
        cos_e = (r2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)
        cos_e = max(-1.0, min(1.0, cos_e))
        elbow = math.acos(cos_e)
        # elbow-up: negative elbow in our shoulder-elbow convention for z-up-ish demos
        elbow = -elbow
        shoulder = math.atan2(z, x) - math.atan2(
            l2 * math.sin(elbow), l1 + l2 * math.cos(elbow)
        )
        return shoulder, elbow


def sample_joint_space_trajectory(
    joint_names: list[str],
    steps: int = 5,
    amplitude_rad: float = 0.1,
) -> list[dict[str, float]]:
    """Generate a small sinusoidal joint-space path for offline demos/tests."""
    if steps < 2:
        raise ValueError("steps must be >= 2")
    traj: list[dict[str, float]] = []
    for i in range(steps):
        t = i / (steps - 1)
        frame: dict[str, float] = {}
        for j, name in enumerate(joint_names):
            phase = (j % 7) * 0.3
            frame[name] = amplitude_rad * math.sin(2 * math.pi * t + phase)
        traj.append(frame)
    return traj


def trajectory_within_default_limits(
    traj: list[dict[str, float]],
    position_min: float = -1.57,
    position_max: float = 1.57,
) -> bool:
    for frame in traj:
        for v in frame.values():
            if v < position_min or v > position_max:
                return False
    return True
